"""
SQLite Database Layer for Tracking Sent Papers and Run Audits.
"""

import sqlite3
import hashlib
import re
from datetime import datetime
from typing import List, Dict, Optional, Any
from config import DB_PATH, logger


def get_connection() -> sqlite3.Connection:
    """Returns a connection to the SQLite database with Row factory enabled."""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def normalize_title(title: str) -> str:
    """Normalizes a title for robust deduplication comparison."""
    # Lowercase, strip punctuation and extra spaces
    cleaned = re.sub(r"[^a-zA-Z0-9\s]", "", title.lower())
    return " ".join(cleaned.split())


def compute_title_hash(title: str) -> str:
    """Computes MD5 hash of normalized title."""
    return hashlib.md5(normalize_title(title).encode("utf-8")).hexdigest()


def init_db() -> None:
    """Initializes SQLite database tables if they do not exist."""
    with get_connection() as conn:
        cursor = conn.cursor()
        
        # Sent papers table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sent_papers (
                paper_id TEXT PRIMARY KEY,
                title_hash TEXT NOT NULL,
                title TEXT NOT NULL,
                authors TEXT,
                published_date TEXT,
                url TEXT,
                source TEXT,
                sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_title_hash ON sent_papers(title_hash)")
        
        # Run logs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS run_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT NOT NULL,
                papers_count INTEGER NOT NULL,
                details TEXT,
                error_message TEXT
            )
        """)
        
        conn.commit()
    logger.debug("Database initialized successfully at %s", DB_PATH)


def is_paper_sent(paper_id: str, title: str) -> bool:
    """
    Checks if a paper has already been sent, checking both paper_id and title_hash.
    """
    title_hash = compute_title_hash(title)
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT 1 FROM sent_papers WHERE paper_id = ? OR title_hash = ? LIMIT 1",
            (paper_id, title_hash)
        )
        return cursor.fetchone() is not None


def save_sent_papers(papers: List[Dict[str, Any]]) -> None:
    """
    Records newly sent papers in the database.
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        for p in papers:
            title = p.get("title", "")
            title_hash = compute_title_hash(title)
            paper_id = p.get("paper_id") or title_hash
            authors = ", ".join(p.get("authors", [])) if isinstance(p.get("authors"), list) else str(p.get("authors", ""))
            
            cursor.execute("""
                INSERT OR REPLACE INTO sent_papers 
                (paper_id, title_hash, title, authors, published_date, url, source, sent_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                paper_id,
                title_hash,
                title,
                authors,
                str(p.get("published_date", "")),
                p.get("url", ""),
                p.get("source", "arXiv/Scholar"),
                datetime.utcnow().isoformat()
            ))
        conn.commit()
    logger.info("Saved %d papers to sent_papers database.", len(papers))


def log_run(status: str, papers_count: int, details: str = "", error_message: str = "") -> None:
    """
    Records workflow execution status in run_logs table.
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO run_logs (run_time, status, papers_count, details, error_message)
            VALUES (?, ?, ?, ?, ?)
        """, (
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            status,
            papers_count,
            details,
            error_message
        ))
        conn.commit()
    logger.info("Logged run status: %s, papers: %d", status, papers_count)


def get_sent_papers_count() -> int:
    """Returns total count of sent papers."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM sent_papers")
        row = cursor.fetchone()
        return row[0] if row else 0


def get_recent_runs(limit: int = 10) -> List[Dict[str, Any]]:
    """Fetches recent run logs."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM run_logs ORDER BY id DESC LIMIT ?", (limit,))
        return [dict(row) for row in cursor.fetchall()]
