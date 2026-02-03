# Architecture Overview

## How This Project Was Built

This project was created through a conversation with an AI assistant (Claude) in Cursor IDE. It has evolved from a simple HN email digest to a multi-topic news aggregation platform.

### Evolution

1. **v1 (Classic)**: HN-only crawler → DeepSeek summary → Email delivery
2. **v2 (Multi-topic)**: Multiple sources → Topic aggregation → AI summaries → Static website

## Project Structure

```
hn-daily-summary/
├── .github/workflows/
│   └── daily-summary.yml    # GitHub Actions: crawl + summarize + deploy
├── config/
│   └── topics.yaml          # Topic and source configuration
├── data/                    # Generated JSON data (by date)
│   └── 2026-02-03/
│       ├── tech.json
│       ├── ai.json
│       └── design.json
├── src/
│   ├── crawlers/            # Multi-source crawlers
│   │   ├── base.py          # Article dataclass + BaseCrawler ABC
│   │   ├── hn_crawler.py    # Hacker News (Firebase API)
│   │   ├── reddit_crawler.py # Reddit (public JSON API)
│   │   └── rss_crawler.py   # Generic RSS/Atom feeds
│   ├── config_loader.py     # YAML config parser
│   ├── topic_crawler.py     # Topic-based aggregation
│   ├── summarizer.py        # DeepSeek AI summarization
│   ├── emailer.py           # SMTP email sender
│   └── hn_fetcher.py        # Legacy HN fetcher (backwards compat)
├── web/                     # Next.js static site
│   ├── src/
│   │   ├── app/             # Pages (App Router)
│   │   ├── components/      # React components
│   │   └── lib/             # Data loading utilities
│   ├── package.json
│   └── next.config.js       # Static export config
├── main.py                  # Entry point (supports both modes)
├── requirements.txt
├── AGENTS.md                # AI assistant instructions
└── README.md
```

## Data Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    GitHub Actions (Daily)                    │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     1. CRAWL PHASE                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                  │
│  │    HN    │  │  Reddit  │  │   RSS    │                  │
│  │ Firebase │  │   JSON   │  │  Feeds   │                  │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘                  │
│       │             │             │                         │
│       └─────────────┼─────────────┘                         │
│                     ▼                                       │
│              TopicCrawler                                   │
│         (aggregates by topic)                               │
│                     │                                       │
│                     ▼                                       │
│           data/{date}/{topic}.json                          │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   2. SUMMARIZE PHASE                        │
│                                                             │
│           data/{date}/{topic}.json                          │
│                     │                                       │
│                     ▼                                       │
│              DeepSeek API                                   │
│         (generates summaries)                               │
│                     │                                       │
│                     ▼                                       │
│     data/{date}/{topic}.json (with summary)                 │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    3. BUILD PHASE                           │
│                                                             │
│               Next.js Static Export                         │
│                     │                                       │
│           ┌─────────┼─────────┐                            │
│           ▼         ▼         ▼                            │
│       index.html  /tech/   /archive/                        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   4. DEPLOY PHASE                           │
│                                                             │
│              GitHub Pages (gh-pages)                        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Key Components

### Crawlers (`src/crawlers/`)

All crawlers inherit from `BaseCrawler` and return `Article` objects:

```python
@dataclass
class Article:
    id: str           # e.g., "hn-12345", "reddit-abc123"
    title: str
    url: str | None
    source: str       # e.g., "Hacker News", "r/programming"
    score: int
    comments_count: int
    comments_url: str | None
    published_at: datetime
    author: str
    text: str | None
    summary: str | None  # AI-generated per-article summary
```

Crawlers support filtering:
- `filter`: Regex pattern to INCLUDE articles (by title)
- `exclude`: Regex pattern to EXCLUDE articles (by title)

### Topic Configuration (`config/topics.yaml`)

```yaml
topics:
  tech:
    name: "Technology"
    sources:
      - type: hackernews
        count: 25
        exclude: "AI|GPT|LLM|..."  # Avoid overlap with 'ai' topic
      - type: reddit
        subreddit: programming
        count: 10
  ai:
    name: "AI & Machine Learning"
    sources:
      - type: hackernews
        filter: "AI|GPT|LLM|..."   # Include only AI articles
        count: 20
```

Source options:
- `type`: hackernews | reddit | rss
- `count`: Number of articles to fetch
- `filter`: Regex to INCLUDE (HN only)
- `exclude`: Regex to EXCLUDE (HN only)
- `subreddit`: Subreddit name (Reddit only)
- `url`, `name`: Feed URL and display name (RSS only)

### Data Output (`data/{date}/{topic}.json`)

```json
{
  "topic_id": "tech",
  "topic_name": "Technology",
  "date": "2026-02-03",
  "articles": [
    {
      "id": "hn-12345",
      "title": "Article Title",
      "url": "https://...",
      "source": "Hacker News",
      "summary": "Per-article AI summary (1-2 sentences)"
    }
  ],
  "summary": "Topic-level AI summary (full analysis)"
}
```

Two levels of AI summaries:
- **Topic summary**: Comprehensive analysis of all articles, grouped by themes
- **Article summary**: Brief 1-2 sentence summary for each individual article

### Web Pages

| Route                 | Description                 |
| --------------------- | --------------------------- |
| `/`                   | Home - all topics for today |
| `/zh/tech`            | Single topic view (Chinese) |
| `/en/tech`            | Single topic view (English) |
| `/zh/archive/2026-02-03` | Historical data          |

### UI Components (`web/src/components/`)

| Component         | Purpose                                      |
| ----------------- | -------------------------------------------- |
| `Header`          | Site header with date and language switcher  |
| `TopicNav`        | Topic navigation tabs                        |
| `SummarySection`  | Collapsible topic-level AI summary           |
| `SourceCard`      | Groups articles by source (HN, Reddit, etc.) |
| `ArticleCard`     | Individual article with summary              |

Topic page layout:
```
Topic Name
├── 🤖 AI Summary (topic-level, collapsible)
└── 📰 All Articles
    ├── [Hacker News]     [r/LocalLLaMA]    <- 2 columns on desktop
    │   • Article 1         • Article 1     <- 1 column on mobile
    │     [summary]           [summary]
    └── [r/MachineLearning]
        • Article 1
          [summary]
```

## Configuration

### Environment Variables

| Variable           | Required  | Default        | Description      |
| ------------------ | --------- | -------------- | ---------------- |
| `DEEPSEEK_API_KEY` | Yes       | -              | DeepSeek API key |
| `SMTP_SERVER`      | For email | smtp.gmail.com | SMTP server      |
| `SMTP_PORT`        | For email | 587            | SMTP port        |
| `SMTP_USERNAME`    | For email | -              | Sender email     |
| `SMTP_PASSWORD`    | For email | -              | App password     |
| `EMAIL_TO`         | For email | -              | Recipients       |

### Topic Settings (`config/topics.yaml` → `settings`)

| Setting                  | Default | Description      |
| ------------------------ | ------- | ---------------- |
| `max_articles_per_topic` | 30      | Limit per topic  |
| `summary_language`       | zh      | Summary language |

## Run Modes

```bash
# Classic mode (HN + email)
python main.py --mode classic

# Multi-topic mode (website)
python main.py --mode multi

# Crawl only (no summarization)
python main.py --mode multi --crawl-only

# Summarize only (use existing data)
python main.py --mode multi --summarize-only
```

## Extending

### Adding a New Crawler

1. Create `src/crawlers/new_crawler.py`:

   ```python
   from .base import BaseCrawler, Article

   class NewCrawler(BaseCrawler):
       @property
       def source_name(self) -> str:
           return "New Source"

       def fetch(self, config: dict) -> list[Article]:
           # Implementation
           pass
   ```

2. Register in `src/crawlers/__init__.py`

3. Add to `src/topic_crawler.py` CRAWLER_MAP

4. Use in `config/topics.yaml`:
   ```yaml
   sources:
     - type: newsource
       option: value
   ```

### Adding a New Topic

Edit `config/topics.yaml`:

```yaml
topics:
  newtopic:
    name: "New Topic"
    description: "Description here"
    sources:
      - type: hackernews
        filter: "keyword1|keyword2"
        count: 15
```
