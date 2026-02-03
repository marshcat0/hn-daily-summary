"""
Base crawler interface for all data sources.

All crawlers should inherit from BaseCrawler and implement the fetch() method.
This ensures consistent data format across different sources.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional, List, Dict, Any
import re


@dataclass
class Article:
    """
    Unified article data structure used across all crawlers.
    
    Attributes:
        id: Unique identifier (prefixed by source, e.g., "hn-12345", "reddit-abc123")
        title: Article title
        url: Link to the original article
        source: Human-readable source name (e.g., "Hacker News", "r/programming")
        score: Popularity score (upvotes, points, etc.)
        comments_count: Number of comments
        comments_url: Link to discussion/comments page
        published_at: Publication timestamp
        author: Author username
        text: Article body text (for self-posts, optional)
    """
    id: str
    title: str
    url: Optional[str]
    source: str
    score: int
    comments_count: int
    comments_url: Optional[str]
    published_at: datetime
    author: str
    text: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        data = asdict(self)
        # Convert datetime to ISO format string
        data['published_at'] = self.published_at.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Article':
        """Create Article from dictionary"""
        data = data.copy()
        # Parse ISO format string back to datetime
        if isinstance(data.get('published_at'), str):
            data['published_at'] = datetime.fromisoformat(data['published_at'])
        return cls(**data)


class BaseCrawler(ABC):
    """
    Abstract base class for all crawlers.
    
    Subclasses must implement:
        - fetch(config): Fetch articles from the source
        - source_name: Property returning the source name
    """
    
    @property
    @abstractmethod
    def source_name(self) -> str:
        """Return the human-readable name of this source"""
        pass
    
    @abstractmethod
    def fetch(self, config: Dict[str, Any]) -> List[Article]:
        """
        Fetch articles from the source.
        
        Args:
            config: Source-specific configuration dict, may include:
                - count: Number of articles to fetch
                - filter: Regex pattern to filter titles
                - Other source-specific options
        
        Returns:
            List of Article objects
        """
        pass
    
    def filter_articles(self, articles: List[Article], pattern: Optional[str]) -> List[Article]:
        """
        Filter articles by title using regex pattern.
        
        Args:
            articles: List of articles to filter
            pattern: Regex pattern (case-insensitive), or None to skip filtering
        
        Returns:
            Filtered list of articles
        """
        if not pattern:
            return articles
        
        regex = re.compile(pattern, re.IGNORECASE)
        return [a for a in articles if regex.search(a.title)]
