"""
Generic RSS/Atom feed crawler.

Uses feedparser library for parsing various feed formats.
"""

import requests
import feedparser
from datetime import datetime
from time import mktime
from typing import Optional, List, Dict, Any
import hashlib

from .base import BaseCrawler, Article


class RSSCrawler(BaseCrawler):
    """
    Generic crawler for RSS and Atom feeds.
    
    Config options:
        - url: Feed URL (required)
        - count: Number of articles to fetch (default: 20)
        - filter: Regex pattern to filter titles (optional)
        - name: Custom source name (optional, defaults to feed title)
    """
    
    def __init__(self):
        self._source_name = "RSS Feed"
    
    @property
    def source_name(self) -> str:
        return self._source_name
    
    def fetch(self, config: Dict[str, Any]) -> List[Article]:
        """Fetch articles from an RSS/Atom feed"""
        url = config.get('url')
        if not url:
            raise ValueError("RSS crawler requires 'url' in config")
        
        count = config.get('count', 20)
        filter_pattern = config.get('filter')
        custom_name = config.get('name')
        
        articles = self._fetch_feed(url, custom_name)
        
        # Apply filter if specified
        if filter_pattern:
            articles = self.filter_articles(articles, filter_pattern)
        
        return articles[:count]
    
    def _fetch_feed(self, url: str, custom_name: Optional[str] = None) -> List[Article]:
        """Fetch and parse RSS/Atom feed"""
        try:
            # Fetch feed content
            resp = requests.get(url, timeout=15, headers={
                'User-Agent': 'HNDailySummary/1.0'
            })
            resp.raise_for_status()
            
            # Parse with feedparser
            feed = feedparser.parse(resp.content)
            
            # Set source name
            if custom_name:
                self._source_name = custom_name
            elif feed.feed.get('title'):
                self._source_name = feed.feed.get('title')
            else:
                self._source_name = url
            
            articles = []
            for entry in feed.entries:
                article = self._parse_entry(entry, url)
                if article:
                    articles.append(article)
            
            return articles
            
        except Exception as e:
            print(f"Failed to fetch RSS feed {url}: {e}")
            return []
    
    def _parse_entry(self, entry: Dict[str, Any], feed_url: str) -> Optional[Article]:
        """Parse a feed entry into an Article"""
        try:
            # Generate unique ID from link or title
            link = entry.get('link', '')
            entry_id = entry.get('id', link)
            if not entry_id:
                entry_id = hashlib.md5(entry.get('title', '').encode()).hexdigest()
            
            # Create short hash for ID
            id_hash = hashlib.md5(entry_id.encode()).hexdigest()[:12]
            
            # Parse published date
            published = None
            if entry.get('published_parsed'):
                published = datetime.fromtimestamp(mktime(entry.published_parsed))
            elif entry.get('updated_parsed'):
                published = datetime.fromtimestamp(mktime(entry.updated_parsed))
            else:
                published = datetime.now()
            
            # Get author
            author = entry.get('author', '')
            if not author and entry.get('authors'):
                author = entry.authors[0].get('name', 'unknown')
            if not author:
                author = 'unknown'
            
            # Get content/summary
            text = None
            if entry.get('summary'):
                text = entry.summary
            elif entry.get('content'):
                text = entry.content[0].get('value', '')
            
            return Article(
                id=f"rss-{id_hash}",
                title=entry.get('title', 'Untitled'),
                url=link,
                source=self._source_name,
                score=0,  # RSS feeds don't have scores
                comments_count=0,
                comments_url=None,
                published_at=published,
                author=author,
                text=text,
            )
        except Exception as e:
            print(f"Failed to parse RSS entry: {e}")
            return None
