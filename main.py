"""
Main Workflow Controller for Daily CS Research Papers Digest.
"""

import sys
import argparse
from datetime import datetime
from pathlib import Path

from config import (
    PAPERS_PER_DAY,
    BASE_DIR,
    logger
)
from database import (
    init_db,
    save_sent_papers,
    log_run,
    get_sent_papers_count,
    get_recent_runs
)
from fetcher import get_new_cs_papers
from summarizer import enrich_papers_batch
from email_builder import (
    build_html_email,
    build_plain_text_email,
    get_email_subject
)
from email_sender import send_email


def run_daily_workflow(dry_run: bool = False, force_save_preview: bool = True) -> bool:
    """
    Executes the end-to-end workflow:
    1. Initialize database
    2. Fetch 5 new unseen CS papers
    3. Enrich papers with 6 analytical criteria
    4. Build HTML & plain-text email digests
    5. Save local HTML sample
    6. Send via Gmail SMTP
    7. Record sent papers in SQLite & audit log
    """
    logger.info("=== Starting Daily CS Papers Agent Workflow ===")
    init_db()
    
    # 1. Fetch fresh unseen papers
    logger.info("Fetching %d new papers...", PAPERS_PER_DAY)
    raw_papers = get_new_cs_papers(count=PAPERS_PER_DAY)
    
    if not raw_papers:
        msg = "No new papers found today. All fetched candidates may have already been sent."
        logger.warning(msg)
        log_run("SKIPPED", 0, details=msg)
        return True
        
    logger.info("Found %d papers. Proceeding to structured analysis...", len(raw_papers))
    
    # 2. Enrich & Summarize
    enriched_papers = enrich_papers_batch(raw_papers)
    
    # 3. Build Email Content
    today_str = datetime.now().strftime("%B %d, %Y")
    subject = get_email_subject(today_str)
    html_content = build_html_email(enriched_papers, today_str)
    text_content = build_plain_text_email(enriched_papers, today_str)
    
    # Save local sample HTML file for review / auditing
    if force_save_preview:
        sample_path = BASE_DIR / "sample_email.html"
        sample_path.write_text(html_content, encoding="utf-8")
        logger.info("Saved sample HTML preview to: %s", sample_path)
        
    if dry_run:
        logger.info("[DRY RUN] Workflow completed successfully. No emails sent and database untouched.")
        print("\n" + "=" * 60)
        print("  DRY RUN COMPLETED: SAMPLE EMAIL PREVIEW SAVED")
        print("=" * 60)
        print(f"Preview file: {BASE_DIR / 'sample_email.html'}")
        print(f"Total papers processed: {len(enriched_papers)}")
        print("\nSample Paper #1 Summary:\n", enriched_papers[0].get("one_line_summary"))
        print("\nSample Paper #1 Real-world Relevance:\n", enriched_papers[0].get("real_world_relevance"))
        print("\nSample Paper #1 Comparison:\n" + "\n".join([f"  • {b}" for b in enriched_papers[0].get("comparison_bullets", [])]))
        return True
        
    # 4. Dispatch Email
    logger.info("Dispatching email via Gmail SMTP...")
    success, message = send_email(subject, html_content, text_content)
    
    if success:
        # 5. Persist to database only upon successful transmission
        save_sent_papers(enriched_papers)
        log_run("SUCCESS", len(enriched_papers), details=f"Subject: {subject}")
        logger.info("Workflow finished successfully!")
        return True
    else:
        log_run("FAILED", 0, error_message=message)
        logger.error("Workflow encountered a transmission error: %s", message)
        return False


def show_history() -> None:
    """Displays audit logs and sent papers statistics."""
    init_db()
    total_sent = get_sent_papers_count()
    recent = get_recent_runs(10)
    
    print("\n" + "=" * 60)
    print("  DAILY CS PAPERS WORKFLOW - HISTORY & AUDIT LOG")
    print("=" * 60)
    print(f"Total distinct papers sent to date: {total_sent}\n")
    print("Recent Executions:")
    print(f"{'Run Time':<22} | {'Status':<10} | {'Papers':<8} | {'Details'}")
    print("-" * 65)
    for r in recent:
        print(f"{r['run_time']:<22} | {r['status']:<10} | {r['papers_count']:<8} | {r.get('error_message') or r.get('details') or ''}")
    print("=" * 60 + "\n")


def send_test_email() -> None:
    """Sends a quick test verification message to verify credentials."""
    logger.info("Sending test verification email...")
    subject = "CS Papers Agent — Test Configuration Verification"
    html = """
    <div style="font-family: sans-serif; padding: 20px; background: #f8fafc; border-radius: 8px;">
        <h2 style="color: #2563eb;">Antigravity CS Papers Agent</h2>
        <p>This is a test verification email from your automated CS research paper workflow.</p>
        <p>Your Gmail SMTP connection is working properly and configured for daily delivery at 7:00 AM IST.</p>
    </div>
    """
    text = "Antigravity CS Papers Agent - SMTP verification test succeeded!"
    success, msg = send_email(subject, html, text)
    if success:
        print("Success! Test verification email was delivered successfully.")
    else:
        print(f"Failed: {msg}")


def main():
    parser = argparse.ArgumentParser(description="Daily CS Research Papers Digest Agent")
    parser.add_argument("--dry-run", action="store_true", help="Run workflow without sending email or modifying DB")
    parser.add_argument("--preview", action="store_true", help="Generate and save sample_email.html preview")
    parser.add_argument("--history", action="store_true", help="View past execution history and sent paper statistics")
    parser.add_argument("--test-email", action="store_true", help="Send a test verification email to confirm credentials")
    
    args = parser.parse_args()
    
    if args.history:
        show_history()
    elif args.test_email:
        send_test_email()
    else:
        success = run_daily_workflow(dry_run=args.dry_run or args.preview)
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
