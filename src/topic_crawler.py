"""
Topic-based crawler that aggregates articles from multiple sources.

Uses the topic configuration to fetch and combine articles.
"""

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

from .config_loader import get_config, ConfigLoader
from .crawlers import Article, HackerNewsCrawler, RedditCrawler, RSSCrawler


class TopicCrawler:
    """
    Crawls articles for a specific topic by aggregating from multiple sources.
    """
    
    # Map source types to crawler classes
    CRAWLER_MAP = {
        'hackernews': HackerNewsCrawler,
        'reddit': RedditCrawler,
        'rss': RSSCrawler,
    }
    
    def __init__(self, config: Optional[ConfigLoader] = None):
        """
        Initialize topic crawler.
        
        Args:
            config: ConfigLoader instance. Uses global instance if None.
        """
        self.config = config or get_config()
        self._crawlers: Dict[str, Any] = {}
    
    def _get_crawler(self, source_type: str):
        """Get or create a crawler instance for a source type"""
        if source_type not in self._crawlers:
            crawler_class = self.CRAWLER_MAP.get(source_type)
            if crawler_class is None:
                raise ValueError(f"Unknown source type: {source_type}")
            self._crawlers[source_type] = crawler_class()
        return self._crawlers[source_type]
    
    def crawl_topic(self, topic_id: str) -> Dict[str, Any]:
        """
        Crawl all sources for a topic and return aggregated data.
        
        Args:
            topic_id: Topic identifier (e.g., 'tech', 'ai')
        
        Returns:
            Dict with topic data including articles and metadata
        """
        topic_config = self.config.get_topic(topic_id)
        if topic_config is None:
            raise ValueError(f"Unknown topic: {topic_id}")
        
        print(f"Crawling topic: {topic_config['name']}")
        
        all_articles: List[Article] = []
        
        # Crawl each source
        for source_config in topic_config.get('sources', []):
            source_type = source_config.get('type')
            if not source_type:
                continue
            
            try:
                crawler = self._get_crawler(source_type)
                articles = crawler.fetch(source_config)
                print(f"  - {crawler.source_name}: {len(articles)} articles")
                all_articles.extend(articles)
            except Exception as e:
                print(f"  - Error crawling {source_type}: {e}")
        
        # Sort by score (descending) and limit
        all_articles.sort(key=lambda a: a.score, reverse=True)
        max_articles = self.config.get_setting('max_articles_per_topic', 30)
        all_articles = all_articles[:max_articles]
        
        # Build result
        return {
            'topic_id': topic_id,
            'topic_name': topic_config['name'],
            'description': topic_config.get('description', ''),
            'date': datetime.now().strftime('%Y-%m-%d'),
            'crawled_at': datetime.now().isoformat(),
            'article_count': len(all_articles),
            'articles': [a.to_dict() for a in all_articles],
            'summary': None,  # To be filled by summarizer
        }
    
    def crawl_all_topics(self) -> Dict[str, Dict[str, Any]]:
        """
        Crawl all configured topics.
        
        Returns:
            Dict mapping topic_id to topic data
        """
        results = {}
        topic_ids = self.config.get_topic_ids()
        
        for i, topic_id in enumerate(topic_ids):
            try:
                results[topic_id] = self.crawl_topic(topic_id)
                
                # Add delay between topics to avoid rate limiting
                if i < len(topic_ids) - 1:
                    print("  Waiting 3s before next topic...")
                    time.sleep(3)
                    
            except Exception as e:
                print(f"Error crawling topic {topic_id}: {e}")
        return results
    
    def save_topic_data(self, topic_data: Dict[str, Any], output_dir: Optional[Path] = None):
        """
        Save topic data to JSON file.
        
        Args:
            topic_data: Topic data dict from crawl_topic()
            output_dir: Output directory. Defaults to data/{date}/
        """
        if output_dir is None:
            project_root = Path(__file__).parent.parent
            date_str = topic_data['date']
            output_dir = project_root / 'data' / date_str
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        topic_id = topic_data['topic_id']
        output_path = output_dir / f"{topic_id}.json"
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(topic_data, f, ensure_ascii=False, indent=2)
        
        print(f"Saved {topic_id} data to {output_path}")
        return output_path


def crawl_all_and_save() -> Dict[str, Path]:
    """
    Convenience function to crawl all topics and save to files.
    
    Returns:
        Dict mapping topic_id to output file path
    """
    crawler = TopicCrawler()
    results = crawler.crawl_all_topics()
    
    saved_paths = {}
    for topic_id, topic_data in results.items():
        path = crawler.save_topic_data(topic_data)
        saved_paths[topic_id] = path
    
    return saved_paths


if __name__ == '__main__':
    # Test crawling
    crawl_all_and_save()
