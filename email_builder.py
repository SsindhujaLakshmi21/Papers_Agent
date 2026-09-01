"""
HTML and Plain Text Email Builder for Daily CS Research Papers.
Produces clean, responsive, skimmable email layouts.
"""

from datetime import datetime
from typing import List, Dict, Any


def get_email_subject(date_str: str = "") -> str:
    """Generates the subject line: '5 New CS Papers — [Date]'."""
    if not date_str:
        date_str = datetime.now().strftime("%B %d, %Y")
    return f"5 New CS Papers — {date_str}"


def build_plain_text_email(papers: List[Dict[str, Any]], date_str: str = "") -> str:
    """Generates a plain-text version of the email digest."""
    if not date_str:
        date_str = datetime.now().strftime("%B %d, %Y")
        
    lines = [
        "=" * 70,
        f"  5 NEW COMPUTER SCIENCE RESEARCH PAPERS — {date_str.upper()}",
        "=" * 70,
        "\nHere is your daily curated digest of 5 new Computer Science research papers.\n",
    ]
    
    for idx, p in enumerate(papers, 1):
        lines.append("-" * 70)
        lines.append(f"PAPER #{idx}: {p.get('title')}")
        lines.append("-" * 70)
        lines.append(f"Authors:     {p.get('authors_str', ', '.join(p.get('authors', [])))}")
        lines.append(f"Venue/Date:  {p.get('venue', 'CS')} | {p.get('published_date', '')}")
        lines.append(f"Link:        {p.get('url', '')}")
        lines.append(f"PDF Link:    {p.get('pdf_url', '')}")
        lines.append("")
        lines.append(f"1. ONE-LINE SUMMARY:\n   {p.get('one_line_summary', '')}\n")
        lines.append(f"2. REAL-WORLD RELEVANCE:\n   {p.get('real_world_relevance', '')}\n")
        
        lines.append("3. PRIOR TECH VS. PROPOSED (Comparison):")
        for bullet in p.get("comparison_bullets", []):
            lines.append(f"   • {bullet}")
        lines.append("")
        
        lines.append(f"4. CRITICAL MOTIVATION (Gap/Problem):\n   {p.get('critical_motivation', '')}\n")
        lines.append(f"5. BUSINESS & INDUSTRY IMPACT:\n   {p.get('business_impact', '')}\n")
        lines.append("\n")
        
    lines.append("=" * 70)
    lines.append("Automated Daily CS Papers Agent | deduplicated & powered by SQLite")
    lines.append("=" * 70)
    
    return "\n".join(lines)


def build_html_email(papers: List[Dict[str, Any]], date_str: str = "") -> str:
    """
    Builds a modern, mobile-responsive, highly legible HTML email.
    Designed for fast reading (< 2 min) with clear badges, cards, and contrasting sections.
    """
    if not date_str:
        date_str = datetime.now().strftime("%A, %B %d, %Y")
        
    cards_html = []
    
    for idx, p in enumerate(papers, 1):
        # Format bullets
        bullets_html = "".join([
            f"<li style='margin-bottom: 6px; line-height: 1.45; color: #2d3748;'>{b}</li>"
            for b in p.get("comparison_bullets", [])
        ])
        
        venue = p.get("venue", "CS Research")
        date_pub = p.get("published_date", "")
        authors = p.get("authors_str", "")
        
        card = f"""
        <div style="background-color: #ffffff; border: 1px solid #e2e8f0; border-radius: 10px; margin-bottom: 24px; padding: 24px; box-shadow: 0 2px 5px rgba(0,0,0,0.03);">
            
            <!-- Card Header: Number + Category + Title -->
            <div style="margin-bottom: 12px;">
                <div style="display: flex; align-items: center; margin-bottom: 8px;">
                    <span style="background-color: #2563eb; color: #ffffff; font-size: 11px; font-weight: 700; padding: 3px 8px; border-radius: 4px; text-transform: uppercase; margin-right: 8px; letter-spacing: 0.5px;">Paper #{idx}</span>
                    <span style="background-color: #f1f5f9; color: #475569; font-size: 11px; font-weight: 600; padding: 3px 8px; border-radius: 4px; border: 1px solid #cbd5e1;">{venue}</span>
                    <span style="color: #94a3b8; font-size: 11px; margin-left: auto;">{date_pub}</span>
                </div>
                <h2 style="font-size: 17px; line-height: 1.35; font-weight: 700; color: #0f172a; margin: 0 0 6px 0;">
                    <a href="{p.get('url')}" style="color: #0f172a; text-decoration: none; border-bottom: 1px solid #cbd5e1;" target="_blank">
                        {p.get('title')}
                    </a>
                </h2>
                <div style="font-size: 12px; color: #64748b; font-style: italic;">
                    Authors: {authors}
                </div>
            </div>

            <hr style="border: none; border-top: 1px solid #f1f5f9; margin: 14px 0;" />

            <!-- 1. One-line Abstract Summary Callout -->
            <div style="background-color: #f8fafc; border-left: 4px solid #3b82f6; padding: 10px 14px; border-radius: 0 6px 6px 0; margin-bottom: 14px;">
                <div style="font-size: 10px; font-weight: 700; text-transform: uppercase; color: #3b82f6; letter-spacing: 0.6px; margin-bottom: 3px;">
                    One-Line Summary
                </div>
                <div style="font-size: 13.5px; line-height: 1.45; color: #1e293b; font-weight: 500;">
                    {p.get('one_line_summary')}
                </div>
            </div>

            <!-- 2. Real-World Relevance -->
            <div style="margin-bottom: 14px;">
                <div style="font-size: 11px; font-weight: 700; text-transform: uppercase; color: #475569; letter-spacing: 0.5px; margin-bottom: 3px;">
                    Real-World Relevance
                </div>
                <div style="font-size: 13px; line-height: 1.45; color: #334155;">
                    {p.get('real_world_relevance')}
                </div>
            </div>

            <!-- 3. Point-by-Point Comparison -->
            <div style="background-color: #fcfcfc; border: 1px solid #f1f5f9; border-radius: 6px; padding: 12px 14px; margin-bottom: 14px;">
                <div style="font-size: 11px; font-weight: 700; text-transform: uppercase; color: #475569; letter-spacing: 0.5px; margin-bottom: 6px;">
                    Existing Tech vs. What's Proposed (Factual Comparison)
                </div>
                <ul style="margin: 0; padding-left: 18px; font-size: 12.5px;">
                    {bullets_html}
                </ul>
            </div>

            <!-- 4 & 5. Motivation & Business Impact in 2-column style -->
            <div style="display: grid; grid-template-columns: 1fr; gap: 10px; margin-bottom: 16px;">
                <div style="background-color: #fffbeb; border: 1px solid #fef3c7; padding: 9px 12px; border-radius: 6px;">
                    <div style="font-size: 10.5px; font-weight: 700; text-transform: uppercase; color: #92400e; margin-bottom: 2px;">
                        Critical Motivation & Core Gap
                    </div>
                    <div style="font-size: 12.5px; line-height: 1.4; color: #78350f;">
                        {p.get('critical_motivation')}
                    </div>
                </div>
                <div style="background-color: #f0fdf4; border: 1px solid #dcfce7; padding: 9px 12px; border-radius: 6px;">
                    <div style="font-size: 10.5px; font-weight: 700; text-transform: uppercase; color: #166534; margin-bottom: 2px;">
                        Practical Business & Industry Impact
                    </div>
                    <div style="font-size: 12.5px; line-height: 1.4; color: #14532d;">
                        {p.get('business_impact')}
                    </div>
                </div>
            </div>

            <!-- Action Button -->
            <div style="text-align: right;">
                <a href="{p.get('pdf_url', p.get('url'))}" target="_blank" style="display: inline-block; background-color: #0f172a; color: #ffffff; text-decoration: none; font-size: 11.5px; font-weight: 600; padding: 6px 14px; border-radius: 5px;">
                    Read Full Paper (PDF) &rarr;
                </a>
            </div>
        </div>
        """
        cards_html.append(card)

    all_cards = "\n".join(cards_html)
    
    full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>5 New CS Papers</title>
</head>
<body style="margin: 0; padding: 0; background-color: #f4f6f8; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; color: #1e293b;">
    <div style="max-width: 660px; margin: 0 auto; padding: 24px 12px;">
        
        <!-- Header Banner -->
        <div style="background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); color: #ffffff; border-radius: 12px; padding: 28px 24px; margin-bottom: 20px; text-align: center; box-shadow: 0 4px 12px rgba(0,0,0,0.08);">
            <div style="font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 1.2px; color: #60a5fa; margin-bottom: 6px;">
                Daily Research Intelligence
            </div>
            <h1 style="font-size: 22px; font-weight: 800; margin: 0 0 8px 0; letter-spacing: -0.3px;">
                5 New CS Research Papers
            </h1>
            <div style="font-size: 13px; color: #cbd5e1;">
                {date_str} &bull; Curated, Deduplicated &amp; Factually Summarized
            </div>
        </div>

        <!-- Digest Stats Banner -->
        <div style="background-color: #e0f2fe; border: 1px solid #bae6fd; border-radius: 8px; padding: 10px 16px; margin-bottom: 20px; font-size: 12.5px; color: #0369a1; text-align: center;">
            &#9889; <strong>2-Minute Skim:</strong> Fresh computer science papers verified not sent in previous runs.
        </div>

        <!-- Paper Cards List -->
        {all_cards}

        <!-- Footer -->
        <div style="text-align: center; font-size: 11px; color: #94a3b8; padding: 20px 0 10px 0; border-top: 1px solid #e2e8f0;">
            <p style="margin: 0 0 6px 0;">
                Delivered automatically by your <strong>Antigravity CS Papers Agent</strong>.
            </p>
            <p style="margin: 0; font-size: 10px; color: #cbd5e1;">
                Sources: Google Scholar &bull; arXiv API &bull; SQLite Deduplicated
            </p>
        </div>

    </div>
</body>
</html>
"""
    return full_html
