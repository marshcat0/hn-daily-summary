"""
Reddit crawler using the public JSON API.

No authentication required for public subreddits.
Uses .json endpoint: https://www.reddit.com/r/{subreddit}/hot.json

Note: Reddit has aggressive rate limiting. This crawler includes:
- Retry logic with exponential backoff
- Delays between requests
- Proper User-Agent header
"""

import requests
import time
import random
from datetime import datetime
from typing import Optional, List, Dict, Any

from .base import BaseCrawler, Article


class RedditCrawler(BaseCrawler):
    """
    Crawler for Reddit using the public JSON API.
    
    Config options:
        - subreddit: Subreddit name without r/ prefix (required)
        - count: Number of posts to fetch (default: 25)
        - filter: Regex pattern to filter titles (optional)
        - sort: Sort order - "hot", "new", "top", "rising" (default: "hot")
        - time: Time filter for "top" - "hour", "day", "week", "month", "year", "all" (default: "day")
    """
    
    # Reddit requires a descriptive User-Agent
    USER_AGENT = "python:HNDailySummary:v1.0 (by /u/marshcat0)"
    
    # Rate limiting settings
    MAX_RETRIES = 3
    BASE_DELAY = 5  # seconds between requests
    
    def __init__(self):
        self._subreddit = None
        self._last_request_time = 0
    
    @property
    def source_name(self) -> str:
        if self._subreddit:
            return f"r/{self._subreddit}"
        return "Reddit"
    
    def fetch(self, config: Dict[str, Any]) -> List[Article]:
        """Fetch posts from a subreddit"""
        subreddit = config.get('subreddit')
        if not subreddit:
            raise ValueError("Reddit crawler requires 'subreddit' in config")
        
        self._subreddit = subreddit
        count = config.get('count', 25)
        sort = config.get('sort', 'hot')
        time_filter = config.get('time', 'day')
        filter_pattern = config.get('filter')
        
        # Fetch more if filtering
        fetch_count = min(count * 3, 100) if filter_pattern else min(count, 100)
        
        articles = self._fetch_posts(subreddit, sort, time_filter, fetch_count)
        
        # Apply filter if specified
        if filter_pattern:
            articles = self.filter_articles(articles, filter_pattern)
        
        return articles[:count]
    
    def _wait_for_rate_limit(self):
        """Ensure minimum delay between requests"""
        elapsed = time.time() - self._last_request_time
        if elapsed < self.BASE_DELAY:
            sleep_time = self.BASE_DELAY - elapsed + random.uniform(0.5, 1.5)
            time.sleep(sleep_time)
    
    def _fetch_posts(self, subreddit: str, sort: str, time_filter: str, limit: int) -> List[Article]:
        """Fetch posts from Reddit API with retry logic"""
        # Use old.reddit.com which can have different rate limits
        url = f"https://old.reddit.com/r/{subreddit}/{sort}.json"
        params = {
            'limit': limit,
            'raw_json': 1,  # Prevent HTML entity encoding
        }
        if sort == 'top':
            params['t'] = time_filter
        
        headers = {'User-Agent': self.USER_AGENT}
        
        for attempt in range(self.MAX_RETRIES):
            try:
                # Rate limiting
                self._wait_for_rate_limit()
                self._last_request_time = time.time()
                
                resp = requests.get(url, params=params, headers=headers, timeout=15)
                
                # Handle rate limiting
                if resp.status_code == 429:
                    retry_after = resp.headers.get('Retry-After', '60')
                    try:
                        wait_time = max(int(retry_after), 10)  # Minimum 10 seconds
                    except ValueError:
                        wait_time = 30
                    wait_time = min(wait_time, 60)  # Cap at 60 seconds
                    print(f"  Rate limited by Reddit. Waiting {wait_time}s (attempt {attempt + 1}/{self.MAX_RETRIES})...")
                    time.sleep(wait_time)
                    continue
                
                resp.raise_for_status()
                data = resp.json()
                
                articles = []
                for post in data.get('data', {}).get('children', []):
                    article = self._parse_post(post.get('data', {}), subreddit)
                    if article:
                        articles.append(article)
                
                return articles
                
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 429:
                    wait_time = (attempt + 1) * 10  # Exponential backoff
                    print(f"  Rate limited. Waiting {wait_time}s (attempt {attempt + 1}/{self.MAX_RETRIES})...")
                    time.sleep(wait_time)
                    continue
                print(f"Failed to fetch Reddit r/{subreddit}: {e}")
                return []
            except Exception as e:
                print(f"Failed to fetch Reddit r/{subreddit}: {e}")
                return []
        
        print(f"  Giving up on r/{subreddit} after {self.MAX_RETRIES} attempts")
        return []
    
    def _parse_post(self, post: Dict[str, Any], subreddit: str) -> Optional[Article]:
        """Parse a Reddit post into an Article"""
        try:
            post_id = post.get('id', '')
            
            # Get URL - either external link or Reddit self post
            url = post.get('url')
            if post.get('is_self'):
                url = f"https://www.reddit.com{post.get('permalink', '')}"
            
            return Article(
                id=f"reddit-{post_id}",
                title=post.get('title', ''),
                url=url,
                source=f"r/{subreddit}",
                score=post.get('score', 0),
                comments_count=post.get('num_comments', 0),
                comments_url=f"https://www.reddit.com{post.get('permalink', '')}",
                published_at=datetime.fromtimestamp(post.get('created_utc', 0)),
                author=post.get('author', 'unknown'),
                text=post.get('selftext') if post.get('is_self') else None,
            )
        except Exception as e:
            print(f"Failed to parse Reddit post: {e}")
            return None
