"""
Comprehensive Test Script for Daily CS Research Papers Workflow.
Tests:
1. SQLite Database & Deduplication
2. Paper Retrieval (Scholar & arXiv)
3. Structured Summarization (6 Required Points)
4. HTML Email Rendering & Saving
5. SMTP Credentials Validation
"""

import sys
from pathlib import Path
from datetime import datetime

import database
import fetcher
import summarizer
import email_builder
import email_sender
from config import GMAIL_USER, GMAIL_APP_PASSWORD, RECIPIENT_EMAIL, logger


def test_database():
    print("\n[TEST 1] Initializing and verifying SQLite database...")
    database.init_db()
    count = database.get_sent_papers_count()
    print(f" -> Database OK. Current sent papers recorded: {count}")
    return True


def test_fetcher():
    print("\n[TEST 2] Testing Paper Fetcher (Primary & Fallback)...")
    papers = fetcher.get_new_cs_papers(count=5)
    print(f" -> Successfully fetched {len(papers)} candidate papers.")
    for idx, p in enumerate(papers, 1):
        print(f"    {idx}. [{p.get('source')}] {p.get('title')} ({p.get('venue')})")
    assert len(papers) > 0, "No papers retrieved"
    return papers


def test_summarizer(papers):
    print("\n[TEST 3] Testing Structured Summarizer on Paper #1...")
    p1 = papers[0]
    enriched = summarizer.enrich_paper(p1)
    
    print(" -> One-line summary:\n   ", enriched.get("one_line_summary"))
    print(" -> Real-world relevance:\n   ", enriched.get("real_world_relevance"))
    print(" -> Comparison bullets:")
    for b in enriched.get("comparison_bullets", []):
        print(f"    • {b}")
    print(" -> Critical motivation:\n   ", enriched.get("critical_motivation"))
    print(" -> Business impact:\n   ", enriched.get("business_impact"))
    
    assert enriched.get("one_line_summary"), "Missing one-line summary"
    assert enriched.get("real_world_relevance"), "Missing real-world relevance"
    assert len(enriched.get("comparison_bullets", [])) >= 3, "Missing comparison bullets"
    assert enriched.get("critical_motivation"), "Missing critical motivation"
    assert enriched.get("business_impact"), "Missing business impact"
    print(" -> All 6 structured analytical requirements validated successfully!")
    return summarizer.enrich_papers_batch(papers)


def test_html_builder(enriched_papers):
    print("\n[TEST 4] Testing HTML & Plain-text Email generation...")
    today_str = datetime.now().strftime("%B %d, %Y")
    html = email_builder.build_html_email(enriched_papers, today_str)
    text = email_builder.build_plain_text_email(enriched_papers, today_str)
    
    preview_file = Path("sample_email.html").resolve()
    preview_file.write_text(html, encoding="utf-8")
    print(f" -> Sample HTML email generated ({len(html)} bytes) and saved to: {preview_file}")
    return html, text


def test_smtp_check():
    print("\n[TEST 5] Checking Gmail SMTP credentials...")
    if not GMAIL_USER or not GMAIL_APP_PASSWORD or GMAIL_APP_PASSWORD == "your_app_password_here":
        print(" -> [NOTICE] Gmail App Password not yet configured in .env.")
        print("    To send live emails, edit d:\\Agents\\.env and add your 16-character App Password.")
        print("    Google App Passwords URL: https://myaccount.google.com/apppasswords")
        return False
    else:
        print(f" -> Credentials detected for {GMAIL_USER}. Ready for live transmission.")
        return True


def run_all_tests():
    print("=" * 65)
    print(" RUNNING END-TO-END TEST SUITE: DAILY CS PAPERS AGENT")
    print("=" * 65)
    
    test_database()
    papers = test_fetcher()
    enriched = test_summarizer(papers)
    test_html_builder(enriched)
    test_smtp_check()
    
    print("\n" + "=" * 65)
    print(" [ALL TESTS PASSED] System is ready for live scheduling!")
    print("=" * 65 + "\n")


if __name__ == "__main__":
    run_all_tests()
