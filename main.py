#!/usr/bin/env python3
"""
HN Daily Summary - Main Entry Point

Supports two modes:
1. Classic mode: HN-only summary sent via email (backwards compatible)
2. Multi-topic mode: Crawl multiple sources, generate summaries, build website
"""

import os
import sys
import argparse
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv


def run_classic_mode():
    """
    Classic HN-only mode with email delivery.
    Backwards compatible with original functionality.
    """
    from src.hn_fetcher import fetch_top_stories
    from src.summarizer import summarize_stories
    from src.emailer import send_email, format_summary_as_html
    
    # Configuration
    stories_count = int(os.getenv("STORIES_COUNT", "30"))
    language = os.getenv("SUMMARY_LANGUAGE", "zh")
    output_mode = os.getenv("OUTPUT_MODE", "email")
    
    print(f"[{datetime.now().isoformat()}] Starting HN Daily Summary (classic mode)...")
    
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
    
    # Step 3: Output
    date_str = datetime.now().strftime("%Y-%m-%d")
    success = True
    
    # Save to file
    if output_mode in ("file", "both"):
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        filepath = output_dir / f"hn-summary-{date_str}.md"
        content = f"# HN Daily Summary - {date_str}\n\n{summary}\n"
        filepath.write_text(content, encoding="utf-8")
        print(f"Summary saved to: {filepath}")
    
    # Send email
    if output_mode in ("email", "both"):
        subject = f"🔥 Hacker News Daily Summary - {date_str}"
        html_body = format_summary_as_html(summary, len(stories))
        
        print("Sending email...")
        success = send_email(subject=subject, body=summary, html_body=html_body)
        
        if not success:
            print("Email sending failed")
            if output_mode == "email":
                sys.exit(1)
    
    print("Done!")


def run_multi_topic_mode(crawl_only: bool = False, summarize_only: bool = False):
    """
    Multi-topic mode: crawl multiple sources and generate topic summaries.
    """
    from src.topic_crawler import TopicCrawler, crawl_all_and_save
    from src.summarizer import summarize_all_topics
    from src.config_loader import get_config
    
    print(f"[{datetime.now().isoformat()}] Starting HN Daily Summary (multi-topic mode)...")
    
    config = get_config()
    language = config.get_setting('summary_language', 'zh')
    
    # Step 1: Crawl (unless summarize-only)
    if not summarize_only:
        print("\n=== Crawling all topics ===")
        try:
            saved_paths = crawl_all_and_save()
            print(f"Crawled {len(saved_paths)} topics")
        except Exception as e:
            print(f"Error crawling: {e}")
            sys.exit(1)
    
    # Step 2: Summarize (unless crawl-only)
    if not crawl_only:
        print("\n=== Generating summaries ===")
        try:
            summarize_all_topics(language=language)
            print("Summaries generated")
        except Exception as e:
            print(f"Error summarizing: {e}")
            sys.exit(1)
    
    print("\nDone!")


def main():
    # Load environment variables
    load_dotenv()
    
    # Parse arguments
    parser = argparse.ArgumentParser(description='HN Daily Summary')
    parser.add_argument('--mode', choices=['classic', 'multi'], default='classic',
                        help='Run mode: classic (HN + email) or multi (multi-topic + website)')
    parser.add_argument('--crawl-only', action='store_true',
                        help='Only crawl, skip summarization (multi mode only)')
    parser.add_argument('--summarize-only', action='store_true',
                        help='Only summarize existing data (multi mode only)')
    
    args = parser.parse_args()
    
    if args.mode == 'classic':
        run_classic_mode()
    else:
        run_multi_topic_mode(
            crawl_only=args.crawl_only,
            summarize_only=args.summarize_only
        )


if __name__ == "__main__":
    main()
