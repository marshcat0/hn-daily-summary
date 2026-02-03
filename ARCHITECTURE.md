# Architecture Overview

## How This Project Was Built

This project was created through a conversation with an AI assistant (Claude) in Cursor IDE. Here's the development process:

### 1. Requirements Gathering

**User Request:**

- Daily automated crawl of Hacker News top stories
- AI-powered summarization (using DeepSeek API)
- Email delivery of summaries
- Run as a scheduled task via GitHub Actions

### 2. Technology Decisions

| Component | Choice         | Reason                             |
| --------- | -------------- | ---------------------------------- |
| Language  | Python 3.9+    | Simple, good library support       |
| HN API    | Firebase API   | Official, no auth required         |
| AI        | DeepSeek       | User preference, OpenAI-compatible |
| Email     | SMTP (Gmail)   | Free, reliable                     |
| Scheduler | GitHub Actions | Free, no server needed             |

### 3. Project Structure

```
hn-daily-summary/
├── .github/workflows/
│   └── daily-summary.yml    # GitHub Actions cron job
├── src/
│   ├── __init__.py
│   ├── hn_fetcher.py        # HN API client
│   ├── summarizer.py        # DeepSeek AI integration
│   └── emailer.py           # SMTP email sender
├── output/                   # Local file output (gitignored)
├── main.py                   # Entry point
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
├── ARCHITECTURE.md           # This file
└── AGENTS.md                 # AI assistant instructions
```

## Component Details

### hn_fetcher.py

**Purpose:** Fetch top stories from Hacker News

**Key Features:**

- Uses official HN Firebase API (`https://hacker-news.firebaseio.com/v0`)
- Concurrent fetching with `ThreadPoolExecutor` for performance
- Returns `HNStory` dataclass with: id, title, url, score, comments, etc.

**API Endpoints Used:**

```
GET /topstories.json     → List of top story IDs
GET /item/{id}.json      → Individual story details
```

### summarizer.py

**Purpose:** Generate AI summary using DeepSeek

**Key Features:**

- DeepSeek API is OpenAI-compatible (uses `openai` SDK)
- Custom prompt engineering for:
  - Topic categorization (AI, Programming, Security, etc.)
  - Including article links and HN discussion links
  - Covering all 30 stories without omission
- Bilingual support (Chinese/English via `SUMMARY_LANGUAGE`)

**Prompt Strategy:**

1. Provide structured story data with URLs
2. Request categorization by topic
3. Require links for each article
4. Ask for top 5 recommendations with reasoning

### emailer.py

**Purpose:** Send summary via SMTP email

**Key Features:**

- Supports multiple recipients (comma/semicolon separated)
- Dual format: plain text + HTML
- Gmail-compatible (tested with App Password)

### main.py

**Purpose:** Orchestrate the pipeline

**Flow:**

```
1. Load .env configuration
2. Fetch top N stories from HN
3. Generate AI summary via DeepSeek
4. Output (email / file / both based on OUTPUT_MODE)
```

## Configuration

### Environment Variables

| Variable           | Required | Default        | Description                  |
| ------------------ | -------- | -------------- | ---------------------------- |
| `DEEPSEEK_API_KEY` | Yes      | -              | DeepSeek API key             |
| `SMTP_SERVER`      | Yes      | smtp.gmail.com | SMTP server                  |
| `SMTP_PORT`        | Yes      | 587            | SMTP port                    |
| `SMTP_USERNAME`    | Yes      | -              | Sender email                 |
| `SMTP_PASSWORD`    | Yes      | -              | App password                 |
| `EMAIL_TO`         | Yes      | -              | Recipients (comma-separated) |
| `STORIES_COUNT`    | No       | 30             | Number of stories to fetch   |
| `SUMMARY_LANGUAGE` | No       | zh             | Summary language (zh/en)     |
| `OUTPUT_MODE`      | No       | email          | Output: email/file/both      |

## Extending the Project

### Adding New Output Channels

1. Create new module in `src/` (e.g., `src/telegram_sender.py`)
2. Implement send function with same interface
3. Add new option to `OUTPUT_MODE` in `main.py`
4. Update `.env.example` with new config

### Modifying AI Prompt

Edit `summarizer.py`:

- `format_stories_for_prompt()` - Change input format
- `summarize_stories()` - Modify prompt template

### Changing Data Source

Replace `hn_fetcher.py` with alternative:

- Reddit API
- RSS feeds
- Other news APIs

Keep same `HNStory` dataclass interface for compatibility.

## Troubleshooting

### Gmail SMTP Blocked (China)

Use proxy:

```bash
export https_proxy=http://127.0.0.1:7890
export http_proxy=http://127.0.0.1:7890
export all_proxy=socks5://127.0.0.1:7890
pip install "httpx[socks]"
```

Or use alternative SMTP (QQ Mail, 163 Mail).

### DeepSeek API Timeout

- Check API key validity
- Increase timeout in `openai` client
- Verify network connectivity

### Missing Articles in Summary

- Increase `max_tokens` in `summarizer.py`
- Strengthen prompt: "Ensure all N articles are covered"
