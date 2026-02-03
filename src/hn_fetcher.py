"""
Hacker News API Fetcher
Using official HN Firebase API: https://github.com/HackerNews/API
"""

import requests
from dataclasses import dataclass
from typing import Optional
from concurrent.futures import ThreadPoolExecutor, as_completed


@dataclass
class HNStory:
    """Hacker News story data"""
    id: int
    title: str
    url: Optional[str]
    score: int
    by: str
    time: int
    descendants: int  # comment count
    text: Optional[str] = None  # for Ask HN, Show HN posts


HN_API_BASE = "https://hacker-news.firebaseio.com/v0"


def fetch_top_story_ids(limit: int = 30) -> list[int]:
    """Fetch top story IDs from HN"""
    resp = requests.get(f"{HN_API_BASE}/topstories.json", timeout=10)
    resp.raise_for_status()
    return resp.json()[:limit]


def fetch_story(story_id: int) -> Optional[HNStory]:
    """Fetch a single story by ID"""
    try:
        resp = requests.get(f"{HN_API_BASE}/item/{story_id}.json", timeout=10)
        resp.raise_for_status()
        data = resp.json()
        
        if not data or data.get("type") != "story":
            return None
        
        return HNStory(
            id=data["id"],
            title=data.get("title", ""),
            url=data.get("url"),
            score=data.get("score", 0),
            by=data.get("by", "unknown"),
            time=data.get("time", 0),
            descendants=data.get("descendants", 0),
            text=data.get("text"),
        )
    except Exception as e:
        print(f"Failed to fetch story {story_id}: {e}")
        return None


def fetch_top_stories(limit: int = 30) -> list[HNStory]:
    """
    Fetch top N stories from Hacker News
    Uses concurrent requests for better performance
    """
    story_ids = fetch_top_story_ids(limit)
    stories = []
    
    # Fetch stories concurrently
    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_id = {executor.submit(fetch_story, sid): sid for sid in story_ids}
        for future in as_completed(future_to_id):
            story = future.result()
            if story:
                stories.append(story)
    
    # Sort by score (highest first)
    stories.sort(key=lambda s: s.score, reverse=True)
    return stories


if __name__ == "__main__":
    # Test fetching
    stories = fetch_top_stories(10)
    for i, story in enumerate(stories, 1):
        print(f"{i}. [{story.score}] {story.title}")
        print(f"   URL: {story.url or 'N/A'}")
        print(f"   Comments: {story.descendants}")
        print()
