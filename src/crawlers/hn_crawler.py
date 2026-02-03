"""
Hacker News crawler using the official Firebase API.

API Documentation: https://github.com/HackerNews/API
"""

import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from typing import Optional, List, Dict, Any

from .base import BaseCrawler, Article


HN_API_BASE = "https://hacker-news.firebaseio.com/v0"


class HackerNewsCrawler(BaseCrawler):
    """
    Crawler for Hacker News using the official Firebase API.
    
    Config options:
        - count: Number of stories to fetch (default: 30)
        - filter: Regex pattern to INCLUDE titles (optional)
        - exclude: Regex pattern to EXCLUDE titles (optional)
        - endpoint: API endpoint - "top", "new", "best" (default: "top")
    """
    
    @property
    def source_name(self) -> str:
        return "Hacker News"
    
    def fetch(self, config: Dict[str, Any]) -> List[Article]:
        """Fetch top stories from Hacker News"""
        count = config.get('count', 30)
        endpoint = config.get('endpoint', 'top')
        filter_pattern = config.get('filter')
        exclude_pattern = config.get('exclude')
        
        # Fetch more if filtering, to ensure we get enough results
        has_filter = filter_pattern or exclude_pattern
        fetch_count = count * 3 if has_filter else count
        
        # Get story IDs
        story_ids = self._fetch_story_ids(endpoint, fetch_count)
        
        # Fetch stories concurrently
        articles = self._fetch_stories_concurrent(story_ids)
        
        # Apply filters if specified
        if has_filter:
            articles = self.filter_articles(articles, filter_pattern, exclude_pattern)
        
        # Sort by score and limit
        articles.sort(key=lambda a: a.score, reverse=True)
        return articles[:count]
    
    def _fetch_story_ids(self, endpoint: str, limit: int) -> List[int]:
        """Fetch story IDs from specified endpoint"""
        endpoint_map = {
            'top': 'topstories',
            'new': 'newstories',
            'best': 'beststories',
        }
        api_endpoint = endpoint_map.get(endpoint, 'topstories')
        
        resp = requests.get(f"{HN_API_BASE}/{api_endpoint}.json", timeout=10)
        resp.raise_for_status()
        return resp.json()[:limit]
    
    def _fetch_story(self, story_id: int) -> Optional[Article]:
        """Fetch a single story by ID"""
        try:
            resp = requests.get(f"{HN_API_BASE}/item/{story_id}.json", timeout=10)
            resp.raise_for_status()
            data = resp.json()
            
            if not data or data.get("type") != "story":
                return None
            
            return Article(
                id=f"hn-{data['id']}",
                title=data.get("title", ""),
                url=data.get("url"),
                source=self.source_name,
                score=data.get("score", 0),
                comments_count=data.get("descendants", 0),
                comments_url=f"https://news.ycombinator.com/item?id={data['id']}",
                published_at=datetime.fromtimestamp(data.get("time", 0)),
                author=data.get("by", "unknown"),
                text=data.get("text"),
            )
        except Exception as e:
            print(f"Failed to fetch HN story {story_id}: {e}")
            return None
    
    def _fetch_stories_concurrent(self, story_ids: List[int]) -> List[Article]:
        """Fetch multiple stories concurrently"""
        articles = []
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            future_to_id = {executor.submit(self._fetch_story, sid): sid for sid in story_ids}
            for future in as_completed(future_to_id):
                article = future.result()
                if article:
                    articles.append(article)
        
        return articles


# Backwards compatibility - expose functions matching old interface
def fetch_top_stories(limit: int = 30) -> List[Article]:
    """
    Backwards-compatible function for fetching HN stories.
    
    Returns Article objects instead of HNStory for consistency.
    """
    crawler = HackerNewsCrawler()
    return crawler.fetch({'count': limit})
