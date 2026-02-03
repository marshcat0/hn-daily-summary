#!/usr/bin/env python3
"""
Hacker News Daily Summary

Fetches top 30 stories from Hacker News, summarizes them using Claude API,
and sends the summary via email.
"""

import os
import smtplib
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from anthropic import Anthropic

# Configuration from environment variables
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
EMAIL_SENDER = os.environ.get("EMAIL_SENDER")  # Your Gmail address
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD")  # Gmail App Password
EMAIL_RECIPIENT = os.environ.get("EMAIL_RECIPIENT")  # Where to send the summary

HN_API_BASE = "https://hacker-news.firebaseio.com/v0"
TOP_N = 30


def fetch_top_stories() -> list[dict]:
    """Fetch top 30 stories from Hacker News API."""
    print(f"Fetching top {TOP_N} stories from Hacker News...")

    # Get top story IDs
    response = requests.get(f"{HN_API_BASE}/topstories.json", timeout=10)
    response.raise_for_status()
    story_ids = response.json()[:TOP_N]

    # Fetch each story's details
    stories = []
    for story_id in story_ids:
        story_response = requests.get(f"{HN_API_BASE}/item/{story_id}.json", timeout=10)
        story_response.raise_for_status()
        story = story_response.json()
        if story and story.get("type") == "story":
            stories.append({
                "id": story_id,
                "title": story.get("title", ""),
                "url": story.get("url", f"https://news.ycombinator.com/item?id={story_id}"),
                "score": story.get("score", 0),
                "by": story.get("by", ""),
                "descendants": story.get("descendants", 0),  # comment count
                "hn_url": f"https://news.ycombinator.com/item?id={story_id}",
            })

    print(f"Fetched {len(stories)} stories")
    return stories


def summarize_stories(stories: list[dict]) -> str:
    """Use Claude to categorize and summarize the stories."""
    print("Summarizing stories with Claude...")

    # Prepare stories text for Claude
    stories_text = "\n\n".join([
        f"#{i+1}. {s['title']}\n"
        f"   Score: {s['score']} | Comments: {s['descendants']} | By: {s['by']}\n"
        f"   URL: {s['url']}\n"
        f"   HN Discussion: {s['hn_url']}"
        for i, s in enumerate(stories)
    ])

    client = Anthropic(api_key=ANTHROPIC_API_KEY)

    prompt = f"""Please analyze and summarize today's top 30 Hacker News stories.

Here are the stories:

{stories_text}

Please provide:

1. **Executive Summary** (2-3 sentences): What are the main themes and trends today?

2. **Categorized Stories**: Group the stories into categories (e.g., AI/ML, Programming, Startups, Science, Security, etc.). For each category:
   - List the story titles with their scores
   - Provide a brief (1-2 sentence) summary of each story's significance

3. **Must-Read Recommendations**: Pick 3-5 stories that are particularly noteworthy and explain why.

4. **Notable Discussions**: Identify 2-3 stories with high comment counts that might have interesting community discussions.

Format the output in clean Markdown suitable for an email newsletter.
Use Chinese for the summary content, but keep original English titles.
"""

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}]
    )

    summary = message.content[0].text
    print("Summary generated successfully")
    return summary


def send_email(summary: str, stories: list[dict]) -> None:
    """Send the summary via email using Gmail SMTP."""
    print(f"Sending email to {EMAIL_RECIPIENT}...")

    today = datetime.now().strftime("%Y-%m-%d")
    subject = f"🔥 Hacker News Daily Summary - {today}"

    # Create email
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = EMAIL_SENDER
    msg["To"] = EMAIL_RECIPIENT

    # Plain text version
    plain_text = f"Hacker News Daily Summary - {today}\n\n{summary}"

    # HTML version with better formatting
    html_content = f"""
    <html>
    <head>
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #333; max-width: 800px; margin: 0 auto; padding: 20px; }}
            h1 {{ color: #ff6600; border-bottom: 2px solid #ff6600; padding-bottom: 10px; }}
            h2 {{ color: #444; margin-top: 30px; }}
            h3 {{ color: #666; }}
            a {{ color: #ff6600; text-decoration: none; }}
            a:hover {{ text-decoration: underline; }}
            .story {{ margin: 10px 0; padding: 10px; background: #f9f9f9; border-radius: 5px; }}
            .meta {{ color: #888; font-size: 0.9em; }}
            code {{ background: #f0f0f0; padding: 2px 6px; border-radius: 3px; }}
            blockquote {{ border-left: 3px solid #ff6600; margin-left: 0; padding-left: 15px; color: #666; }}
        </style>
    </head>
    <body>
        <h1>🔥 Hacker News Daily Summary</h1>
        <p style="color: #888;">Generated on {today}</p>

        {_markdown_to_html(summary)}

        <hr style="margin-top: 40px; border: none; border-top: 1px solid #ddd;">
        <p style="color: #888; font-size: 0.9em;">
            This summary was automatically generated by Claude AI.<br>
            <a href="https://news.ycombinator.com">Visit Hacker News</a>
        </p>
    </body>
    </html>
    """

    msg.attach(MIMEText(plain_text, "plain", "utf-8"))
    msg.attach(MIMEText(html_content, "html", "utf-8"))

    # Send via Gmail SMTP
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_SENDER, EMAIL_RECIPIENT, msg.as_string())

    print("Email sent successfully!")


def _markdown_to_html(markdown: str) -> str:
    """Simple markdown to HTML conversion."""
    import re

    html = markdown

    # Headers
    html = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
    html = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
    html = re.sub(r'^# (.+)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)

    # Bold and italic
    html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
    html = re.sub(r'\*(.+?)\*', r'<em>\1</em>', html)

    # Links
    html = re.sub(r'\[(.+?)\]\((.+?)\)', r'<a href="\2">\1</a>', html)

    # Code
    html = re.sub(r'`(.+?)`', r'<code>\1</code>', html)

    # Line breaks
    html = html.replace('\n\n', '</p><p>')
    html = f'<p>{html}</p>'

    # Lists (simple handling)
    html = re.sub(r'^- (.+)$', r'<li>\1</li>', html, flags=re.MULTILINE)
    html = re.sub(r'(<li>.*</li>)+', r'<ul>\g<0></ul>', html, flags=re.DOTALL)

    return html


def main():
    """Main entry point."""
    print("=" * 50)
    print("Hacker News Daily Summary")
    print(f"Time: {datetime.now().isoformat()}")
    print("=" * 50)

    # Validate environment variables
    required_vars = ["ANTHROPIC_API_KEY", "EMAIL_SENDER", "EMAIL_PASSWORD", "EMAIL_RECIPIENT"]
    missing = [v for v in required_vars if not os.environ.get(v)]
    if missing:
        raise ValueError(f"Missing required environment variables: {', '.join(missing)}")

    # Fetch, summarize, and send
    stories = fetch_top_stories()
    summary = summarize_stories(stories)
    send_email(summary, stories)

    print("=" * 50)
    print("Done!")
    print("=" * 50)


if __name__ == "__main__":
    main()
