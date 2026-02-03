#!/usr/bin/env python3
"""
HN Daily Summary - Main Entry Point

Fetches top stories from Hacker News, summarizes them using DeepSeek,
and sends the summary via email (or saves to file).
"""

import os
import sys
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

from src.hn_fetcher import fetch_top_stories
from src.summarizer import summarize_stories
from src.emailer import send_email, format_summary_as_html


def save_to_file(summary: str, stories_count: int) -> str:
    """Save summary to local file"""
    date_str = datetime.now().strftime("%Y-%m-%d")
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    filepath = output_dir / f"hn-summary-{date_str}.md"
    
    content = f"""# 🔥 Hacker News Daily Summary - {date_str}

> Top {stories_count} Stories

{summary}

---
*Generated at {datetime.now().isoformat()}*
"""
    filepath.write_text(content, encoding="utf-8")
    return str(filepath)


def main():
    # Load environment variables
    load_dotenv()
    
    # Configuration
    stories_count = int(os.getenv("STORIES_COUNT", "30"))
    language = os.getenv("SUMMARY_LANGUAGE", "zh")  # 'zh' or 'en'
    output_mode = os.getenv("OUTPUT_MODE", "email")  # 'email', 'file', or 'both'
    
    print(f"[{datetime.now().isoformat()}] Starting HN Daily Summary...")
    
    # Step 1: Fetch stories
    print(f"Fetching top {stories_count} stories from Hacker News...")
    try:
        stories = fetch_top_stories(stories_count)
        print(f"Fetched {len(stories)} stories")
    except Exception as e:
        print(f"Error fetching stories: {e}")
        sys.exit(1)
    
    if not stories:
        print("No stories fetched, exiting")
        sys.exit(1)
    
    # Step 2: Summarize with DeepSeek
    print("Generating summary with DeepSeek...")
    try:
        summary = summarize_stories(stories, language=language)
        print("Summary generated successfully")
    except Exception as e:
        print(f"Error generating summary: {e}")
        sys.exit(1)
    
    # Step 3: Output (email, file, or both)
    date_str = datetime.now().strftime("%Y-%m-%d")
    success = True
    
    # Save to file
    if output_mode in ("file", "both"):
        filepath = save_to_file(summary, len(stories))
        print(f"Summary saved to: {filepath}")
    
    # Send email
    if output_mode in ("email", "both"):
        subject = f"🔥 Hacker News Daily Summary - {date_str}"
        html_body = format_summary_as_html(summary, len(stories))
        
        print("Sending email...")
        success = send_email(
            subject=subject,
            body=summary,
            html_body=html_body,
        )
        
        if not success:
            print("Email sending failed")
            if output_mode == "email":
                sys.exit(1)
    
    print("Done!")


if __name__ == "__main__":
    main()
