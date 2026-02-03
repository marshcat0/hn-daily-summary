# AI Assistant Instructions

> This file provides context and instructions for AI assistants (Claude, GPT, Copilot, etc.) working on this project.

## Project Context

**What is this?**
A multi-topic tech news aggregation platform that:

1. Crawls articles from HN, Reddit, RSS feeds (configurable)
2. Aggregates by topic (tech, AI, design, etc.)
3. Generates AI summaries using DeepSeek
4. Builds a static website with Next.js
5. Deploys to GitHub Pages daily

**Created:** February 2026
**Author:** Built collaboratively with Claude AI in Cursor IDE

## Project Structure

```
hn-daily-summary/
├── src/
│   ├── crawlers/           # Multi-source crawlers
│   │   ├── base.py         # Article + BaseCrawler
│   │   ├── hn_crawler.py   # Hacker News
│   │   ├── reddit_crawler.py
│   │   └── rss_crawler.py
│   ├── config_loader.py    # YAML config
│   ├── topic_crawler.py    # Topic aggregation
│   ├── summarizer.py       # DeepSeek AI
│   └── emailer.py          # SMTP email
├── config/
│   └── topics.yaml         # Topic definitions
├── data/                   # Generated JSON
├── web/                    # Next.js site
│   ├── src/app/            # Pages
│   └── src/components/     # React components
├── main.py                 # Entry point
└── requirements.txt
```

## Key Files

| File                       | Purpose               | Modify When           |
| -------------------------- | --------------------- | --------------------- |
| `config/topics.yaml`       | Topic & source config | Adding topics/sources |
| `src/crawlers/*.py`        | Data fetchers         | Adding new sources    |
| `src/summarizer.py`        | AI prompts            | Improving summaries   |
| `web/src/components/*.tsx` | UI components         | Changing design       |
| `web/src/lib/data.ts`      | Data loading          | Changing data format  |
| `.github/workflows/*.yml`  | Automation            | Changing schedule     |

## Common Tasks

### Add a New Topic

Edit `config/topics.yaml`:

```yaml
topics:
  newtopic:
    name: "New Topic Name"
    description: "What this topic covers"
    sources:
      - type: hackernews
        filter: "keyword1|keyword2"
        count: 15
      - type: reddit
        subreddit: subreddit_name
        count: 10
```

### Add a New Source Type

1. Create `src/crawlers/newsource_crawler.py`:

```python
from .base import BaseCrawler, Article

class NewSourceCrawler(BaseCrawler):
    @property
    def source_name(self) -> str:
        return "New Source"

    def fetch(self, config: dict) -> list[Article]:
        # Implement fetching logic
        pass
```

2. Register in `src/crawlers/__init__.py`
3. Add to CRAWLER_MAP in `src/topic_crawler.py`
4. **Update this AGENTS.md** with new source info

### Improve AI Summary Quality

Edit `src/summarizer.py`:

- Modify `summarize_topic()` prompt
- Adjust `temperature` or `max_tokens`
- Change categorization instructions

### Modify Website UI

Edit files in `web/src/`:

- `components/*.tsx` - UI components
- `app/globals.css` - Global styles
- `app/page.tsx` - Home page
- `app/[topic]/page.tsx` - Topic pages

### Debug Locally

```bash
cd /Users/lion/Projects/hn-daily-summary

# Set up Python
source venv/bin/activate
pip install -r requirements.txt

# With proxy (if needed)
export https_proxy=http://127.0.0.1:7890
export http_proxy=http://127.0.0.1:7890
export all_proxy=socks5://127.0.0.1:7890

# Test crawling
python main.py --mode multi --crawl-only

# Test summarizing (requires DEEPSEEK_API_KEY in .env)
python main.py --mode multi --summarize-only

# Test website
cd web
npm install
npm run dev
# Visit http://localhost:3000
```

### Run Classic Mode (HN + Email)

```bash
# Set OUTPUT_MODE=file to skip email
OUTPUT_MODE=file python main.py --mode classic
```

## Code Conventions

- **Python**: 3.9+ compatible (use `Optional[str]`, not `str | None`)
- **TypeScript**: Strict mode, proper typing
- **Components**: Functional React with hooks
- **Styling**: Tailwind CSS

## Documentation Maintenance

**IMPORTANT for AI assistants:**

When you make changes, update relevant docs:

1. **ARCHITECTURE.md** - Technical changes:

   - New files or modules
   - Data flow changes
   - New configuration options

2. **AGENTS.md** (this file) - AI context:

   - New common tasks
   - Changed file purposes
   - New debugging steps

3. **README.md** - User-facing changes:

   - New features
   - Changed setup steps
   - New environment variables

4. **Code comments** - Implementation details

## Known Issues

### Python 3.9 Compatibility

Use `Optional[str]` instead of `str | None`

### Gmail in China

Requires proxy. GitHub Actions works without proxy.

### RSS Feed Variations

Some feeds may need custom parsing. Check `rss_crawler.py`.

## File Locations

```
Project:    /Users/lion/Projects/hn-daily-summary
Python env: /Users/lion/Projects/hn-daily-summary/venv
Data:       /Users/lion/Projects/hn-daily-summary/data/
Web output: /Users/lion/Projects/hn-daily-summary/web/out/
```
