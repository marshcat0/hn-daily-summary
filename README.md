# Daily Tech Summary 📰

Multi-topic tech news aggregation platform powered by AI. Crawls articles from Hacker News, Reddit, RSS feeds, generates summaries using DeepSeek, and publishes a beautiful static website.

## Features

- 🔥 **Multi-source crawling**: Hacker News, Reddit, RSS feeds
- 📂 **Topic organization**: Tech, AI/ML, Design (configurable)
- 🤖 **AI summaries**: Topic-level analysis + per-article summaries
- 🔗 **Rich links**: Article URLs + discussion links
- 🌐 **Static website**: Next.js site with responsive design
- 📱 **Mobile-friendly**: Adaptive layout for phone and desktop
- 📧 **Email digest**: Optional daily email (classic mode)
- ⏰ **Automated**: GitHub Actions runs daily at 8 AM Beijing time

## Quick Start

### Prerequisites

- Python 3.9+
- Node.js 18+ (for website)
- DeepSeek API key

### Installation

```bash
git clone https://github.com/marshcat0/hn-daily-summary.git
cd hn-daily-summary

# Python setup
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Web setup
cd web
npm install
cd ..

# Configure
cp .env.example .env
# Edit .env with your API keys
```

### Run Locally

```bash
# Multi-topic mode (crawl + summarize)
python main.py --mode multi

# Classic mode (HN only + email)
python main.py --mode classic

# Just crawl (skip AI summary)
python main.py --mode multi --crawl-only

# Preview website
cd web && npm run dev
```

### With Proxy (China)

```bash
export https_proxy=http://127.0.0.1:7890
export http_proxy=http://127.0.0.1:7890
export all_proxy=socks5://127.0.0.1:7890
python main.py --mode multi
```

## Configuration

### Topics (`config/topics.yaml`)

```yaml
topics:
  tech:
    name: "Technology"
    sources:
      - type: hackernews
        count: 25
        exclude: "AI|GPT|LLM|..."  # Avoid overlap with AI topic
      - type: reddit
        subreddit: programming
        count: 10
  ai:
    name: "AI & ML"
    sources:
      - type: hackernews
        filter: "AI|ML|GPT|LLM"    # Include only AI articles
        count: 20
      - type: reddit
        subreddit: LocalLLaMA
        count: 10
```

Source options:
- `filter`: Regex to include articles (by title)
- `exclude`: Regex to exclude articles (avoid topic overlap)

### Environment Variables

| Variable           | Required  | Description      |
| ------------------ | --------- | ---------------- |
| `DEEPSEEK_API_KEY` | Yes       | DeepSeek API key |
| `SMTP_SERVER`      | For email | SMTP server      |
| `SMTP_PORT`        | For email | SMTP port (587)  |
| `SMTP_USERNAME`    | For email | Sender email     |
| `SMTP_PASSWORD`    | For email | App password     |
| `EMAIL_TO`         | For email | Recipients       |

## GitHub Actions Deployment

1. **Create repository** and push code

2. **Add Secrets** (Settings → Secrets → Actions):

   - `DEEPSEEK_API_KEY`
   - `SMTP_SERVER`, `SMTP_PORT`, `SMTP_USERNAME`, `SMTP_PASSWORD`, `EMAIL_TO` (for email)

3. **Enable GitHub Pages** (Settings → Pages → Source: gh-pages)

4. **Run workflow** (Actions → HN Daily Summary → Run workflow)

The site will be available at `https://username.github.io/hn-daily-summary/`

## Project Structure

```
hn-daily-summary/
├── src/
│   ├── crawlers/        # HN, Reddit, RSS crawlers
│   ├── summarizer.py    # DeepSeek AI (topic + article summaries)
│   └── topic_crawler.py # Topic aggregation
├── config/
│   └── topics.yaml      # Topic & source definitions
├── data/                # Generated JSON (by date)
├── web/                 # Next.js static site
│   └── src/components/  # SourceCard, ArticleCard, etc.
├── main.py              # CLI entry point
└── requirements.txt
```

## UI Preview

```
Topic: AI & Machine Learning
├── 🤖 AI Summary (collapsible)
└── 📰 Articles by Source
    ├── [Hacker News]     [r/LocalLLaMA]
    │   • Article 1         • Article 1
    │     [summary]           [summary]
    └── [r/MachineLearning]
```

## Documentation

- [ARCHITECTURE.md](./ARCHITECTURE.md) - Technical architecture
- [AGENTS.md](./AGENTS.md) - AI assistant guide

## License

MIT
