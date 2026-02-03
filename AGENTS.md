# AI Assistant Instructions

> This file provides context and instructions for AI assistants (Claude, GPT, Copilot, etc.) working on this project.

## Project Context

**What is this?**
An automated Hacker News daily digest system that:

1. Fetches top 30 stories from HN API
2. Summarizes them using DeepSeek AI
3. Sends the digest via email
4. Runs daily via GitHub Actions

**Created:** February 2026
**Author:** Built collaboratively with Claude AI in Cursor IDE

## Key Files to Understand

| File                                  | Purpose                   | When to Modify                 |
| ------------------------------------- | ------------------------- | ------------------------------ |
| `src/hn_fetcher.py`                   | HN API client             | Changing data source or fields |
| `src/summarizer.py`                   | AI prompt & DeepSeek call | Improving summary quality      |
| `src/emailer.py`                      | SMTP email sending        | Adding recipients or format    |
| `main.py`                             | Pipeline orchestration    | Adding new features            |
| `.github/workflows/daily-summary.yml` | Cron schedule             | Changing run time              |

## Common Tasks

### Improve Summary Quality

Edit `src/summarizer.py`:

```python
# Modify the prompt in summarize_stories()
prompt = f"""..."""

# Adjust model parameters
response = client.chat.completions.create(
    model="deepseek-chat",
    temperature=0.7,      # Lower = more focused
    max_tokens=4000,      # Increase for longer output
)
```

### Add New Output Channel

1. Create `src/new_channel.py` with `send()` function
2. Import in `main.py`
3. Add to `OUTPUT_MODE` handling
4. Update `.env.example`
5. **Update this AGENTS.md** with new file info

### Change Schedule

Edit `.github/workflows/daily-summary.yml`:

```yaml
on:
  schedule:
    - cron: "0 8 * * *" # UTC time: minute hour day month weekday
```

### Debug Locally

```bash
cd /Users/lion/Projects/hn-daily-summary
source venv/bin/activate

# With proxy (if in China)
export https_proxy=http://127.0.0.1:7890 http_proxy=http://127.0.0.1:7890 all_proxy=socks5://127.0.0.1:7890

# Test with file output (skip email)
OUTPUT_MODE=file python3 main.py

# Full test with email
python3 main.py
```

## Code Conventions

- **Python version:** 3.9+ (avoid `str | None` syntax, use `Optional[str]`)
- **Type hints:** Use `typing` module for compatibility
- **Error handling:** Print errors clearly, exit with code 1 on failure
- **Config:** All config via environment variables, with sensible defaults

## Documentation Maintenance

**IMPORTANT for AI assistants:**

When you make changes to this project, please:

1. **Update ARCHITECTURE.md** if you:

   - Add new files or modules
   - Change the data flow
   - Add new configuration options
   - Modify the project structure

2. **Update this AGENTS.md** if you:

   - Add new common tasks
   - Change how to debug/test
   - Discover new gotchas or troubleshooting tips

3. **Update README.md** if you:

   - Change user-facing behavior
   - Add new features users need to know
   - Change setup instructions

4. **Keep comments in code** explaining:
   - Why a particular approach was chosen
   - Any non-obvious behavior
   - Links to relevant documentation

## Known Issues & Solutions

### Python 3.9 Compatibility

- Don't use `str | None`, use `Optional[str]` from `typing`
- Don't use `match` statements, use `if/elif`

### Gmail SMTP in China

- Requires proxy (see Debug Locally section)
- Or use QQ/163 Mail as alternative
- GitHub Actions runs from US, no proxy needed there

### DeepSeek API

- Base URL: `https://api.deepseek.com`
- Model: `deepseek-chat`
- OpenAI SDK compatible

## File Locations

```
Project root: /Users/lion/Projects/hn-daily-summary
Virtual env:  /Users/lion/Projects/hn-daily-summary/venv
Output files: /Users/lion/Projects/hn-daily-summary/output/
```

## Questions?

If unclear about any aspect:

1. Read ARCHITECTURE.md for technical details
2. Check existing code comments
3. Look at git history for context on past changes
4. Ask the user for clarification
