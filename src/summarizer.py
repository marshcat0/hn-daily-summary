"""
AI Summarizer using DeepSeek API
DeepSeek API is OpenAI-compatible

Supports both single-source (HN only) and multi-topic summarization.
"""

import os
import json
from pathlib import Path
from typing import List, Dict, Any, Optional, Union
from openai import OpenAI

from .crawlers.base import Article


def create_deepseek_client() -> OpenAI:
    """Create DeepSeek API client"""
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        raise ValueError("DEEPSEEK_API_KEY environment variable is required")
    
    return OpenAI(
        api_key=api_key,
        base_url="https://api.deepseek.com"
    )


def format_articles_for_prompt(articles: List[Union[Article, Dict[str, Any]]]) -> str:
    """
    Format articles list for AI prompt, including source and discussion links.
    
    Accepts both Article objects and dicts (from JSON).
    """
    lines = []
    for i, article in enumerate(articles, 1):
        # Handle both Article objects and dicts
        if isinstance(article, dict):
            title = article.get('title', '')
            score = article.get('score', 0)
            comments_count = article.get('comments_count', 0)
            url = article.get('url', 'N/A')
            comments_url = article.get('comments_url', '')
            source = article.get('source', '')
            text = article.get('text')
        else:
            title = article.title
            score = article.score
            comments_count = article.comments_count
            url = article.url or 'N/A'
            comments_url = article.comments_url or ''
            source = article.source
            text = article.text
        
        lines.append(f"{i}. {title}")
        lines.append(f"   Source: {source} | Score: {score} | Comments: {comments_count}")
        lines.append(f"   Article: {url}")
        if comments_url:
            lines.append(f"   Discussion: {comments_url}")
        if text:
            # Truncate long text
            text = text[:500] + "..." if len(text) > 500 else text
            lines.append(f"   Content: {text}")
        lines.append("")
    return "\n".join(lines)


def summarize_topic(
    topic_name: str,
    topic_description: str,
    articles: List[Union[Article, Dict[str, Any]]],
    language: str = "zh"
) -> str:
    """
    Generate AI summary for a specific topic.
    
    Args:
        topic_name: Human-readable topic name (e.g., "AI & Machine Learning")
        topic_description: Topic description
        articles: List of Article objects or dicts
        language: Output language ('zh' for Chinese, 'en' for English)
    
    Returns:
        AI-generated summary text
    """
    client = create_deepseek_client()
    
    articles_text = format_articles_for_prompt(articles)
    
    lang_instruction = "请用中文回复" if language == "zh" else "Please respond in English"
    
    prompt = f"""你是一个技术新闻分析师。以下是今天 "{topic_name}" 主题的热门文章列表。
主题描述：{topic_description}

请对这些内容进行分析和总结。{lang_instruction}。

要求：
1. 文章来自不同来源（Hacker News、Reddit、RSS订阅等），请综合分析
2. 按子主题或关键词对文章进行分组
3. 每篇文章必须包含：
   - 标题和简要说明（为什么值得关注）
   - 原文链接（Article URL）
   - 讨论链接（如果有）
4. 确保覆盖全部 {len(articles)} 篇文章，不要遗漏
5. 最后给出 3-5 个今日最值得阅读的文章推荐，附上理由和链接

今日 {topic_name} Top {len(articles)} 文章：

{articles_text}
"""

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": f"你是一个专业的技术新闻分析师，擅长分析和总结 {topic_name} 领域的热门内容。输出时保留所有链接，方便读者点击访问。"},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=4000,
    )
    
    return response.choices[0].message.content


def summarize_topic_data(topic_data: Dict[str, Any], language: str = "zh") -> Dict[str, Any]:
    """
    Add AI summary to topic data dict.
    
    Args:
        topic_data: Topic data dict from TopicCrawler.crawl_topic()
        language: Output language
    
    Returns:
        Updated topic_data with 'summary' field populated
    """
    summary = summarize_topic(
        topic_name=topic_data['topic_name'],
        topic_description=topic_data.get('description', ''),
        articles=topic_data['articles'],
        language=language
    )
    
    topic_data['summary'] = summary
    topic_data['summary_language'] = language
    return topic_data


def summarize_all_topics(data_dir: Optional[Path] = None, language: str = "zh") -> Dict[str, Path]:
    """
    Summarize all topic JSON files in a data directory.
    
    Args:
        data_dir: Directory containing topic JSON files. Defaults to data/{today}/
        language: Output language
    
    Returns:
        Dict mapping topic_id to updated file path
    """
    from datetime import datetime
    
    if data_dir is None:
        project_root = Path(__file__).parent.parent
        date_str = datetime.now().strftime('%Y-%m-%d')
        data_dir = project_root / 'data' / date_str
    
    if not data_dir.exists():
        raise FileNotFoundError(f"Data directory not found: {data_dir}")
    
    results = {}
    
    for json_file in data_dir.glob('*.json'):
        topic_id = json_file.stem
        print(f"Summarizing topic: {topic_id}")
        
        try:
            # Load topic data
            with open(json_file, 'r', encoding='utf-8') as f:
                topic_data = json.load(f)
            
            # Generate summary
            topic_data = summarize_topic_data(topic_data, language)
            
            # Save updated data
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(topic_data, f, ensure_ascii=False, indent=2)
            
            print(f"  - Summary generated and saved")
            results[topic_id] = json_file
            
        except Exception as e:
            print(f"  - Error summarizing {topic_id}: {e}")
    
    return results


# ============== Backwards Compatibility ==============
# Keep old interface working for existing code

def format_stories_for_prompt(stories) -> str:
    """
    Backwards-compatible function for HN stories.
    Converts old HNStory format to new Article format.
    """
    # Convert HNStory to dict format
    articles = []
    for story in stories:
        articles.append({
            'title': story.title,
            'score': story.score,
            'comments_count': getattr(story, 'descendants', 0),
            'url': story.url,
            'comments_url': f"https://news.ycombinator.com/item?id={story.id}",
            'source': 'Hacker News',
            'text': getattr(story, 'text', None),
        })
    return format_articles_for_prompt(articles)


def summarize_stories(stories, language: str = "zh") -> str:
    """
    Backwards-compatible function for HN-only summarization.
    """
    return summarize_topic(
        topic_name="Hacker News",
        topic_description="Top stories from Hacker News",
        articles=[{
            'title': s.title,
            'score': s.score,
            'comments_count': getattr(s, 'descendants', 0),
            'url': s.url,
            'comments_url': f"https://news.ycombinator.com/item?id={s.id}",
            'source': 'Hacker News',
            'text': getattr(s, 'text', None),
        } for s in stories],
        language=language
    )


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    
    # Test multi-topic summarization
    summarize_all_topics()
