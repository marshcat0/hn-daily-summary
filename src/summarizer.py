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


def summarize_articles_batch(
    articles: List[Union[Article, Dict[str, Any]]],
    topic_name: str,
    language: str = "zh",
    batch_size: int = 10
) -> Dict[str, str]:
    """
    Generate individual summaries for multiple articles in batches.
    
    Uses batch processing to minimize API calls while generating
    a 1-2 sentence summary for each article.
    
    Args:
        articles: List of Article objects or dicts
        topic_name: Topic name for context
        language: Output language ('zh' for Chinese, 'en' for English)
        batch_size: Number of articles per API call (default 10)
    
    Returns:
        Dict mapping article ID to its summary
    """
    client = create_deepseek_client()
    summaries = {}
    
    lang_instruction = "请用中文回复" if language == "zh" else "Please respond in English"
    
    # Process articles in batches
    for i in range(0, len(articles), batch_size):
        batch = articles[i:i + batch_size]
        
        # Build prompt for this batch
        articles_text = []
        article_ids = []
        for idx, article in enumerate(batch, 1):
            if isinstance(article, dict):
                article_id = article.get('id', f'article-{i+idx}')
                title = article.get('title', '')
                url = article.get('url', 'N/A')
                source = article.get('source', '')
                text = article.get('text', '')
            else:
                article_id = article.id
                title = article.title
                url = article.url or 'N/A'
                source = article.source
                text = article.text or ''
            
            article_ids.append(article_id)
            
            # Truncate text if too long
            if text and len(text) > 300:
                text = text[:300] + "..."
            
            article_info = f"{idx}. [ID: {article_id}]\n   Title: {title}\n   Source: {source}\n   URL: {url}"
            if text:
                article_info += f"\n   Content: {text}"
            articles_text.append(article_info)
        
        prompt = f"""你是一个技术新闻分析师。以下是 "{topic_name}" 主题的文章列表。

请为每篇文章生成一个简短的摘要（1-2句话），说明这篇文章的主要内容和为什么值得关注。{lang_instruction}。

请严格按照以下JSON格式输出，不要添加任何其他内容：
{{
  "article_id_1": "摘要内容1",
  "article_id_2": "摘要内容2"
}}

文章列表：

{chr(10).join(articles_text)}
"""
        
        try:
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": "你是一个专业的技术新闻分析师。请严格按照JSON格式输出文章摘要，不要添加任何markdown标记或额外文字。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=2000,
            )
            
            response_text = response.choices[0].message.content.strip()
            
            # Parse JSON response - handle potential markdown code blocks
            if response_text.startswith("```"):
                # Remove markdown code block markers
                lines = response_text.split("\n")
                response_text = "\n".join(lines[1:-1] if lines[-1] == "```" else lines[1:])
            
            batch_summaries = json.loads(response_text)
            summaries.update(batch_summaries)
            
            print(f"  - Batch {i//batch_size + 1}: Generated {len(batch_summaries)} article summaries")
            
        except json.JSONDecodeError as e:
            print(f"  - Batch {i//batch_size + 1}: JSON parse error: {e}")
            # Fallback: assign empty summaries for this batch
            for article_id in article_ids:
                summaries[article_id] = ""
        except Exception as e:
            print(f"  - Batch {i//batch_size + 1}: Error generating summaries: {e}")
            for article_id in article_ids:
                summaries[article_id] = ""
    
    return summaries


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


def summarize_topic_data(
    topic_data: Dict[str, Any], 
    language: str = "zh",
    include_article_summaries: bool = True
) -> Dict[str, Any]:
    """
    Add AI summary to topic data dict, including per-article summaries.
    
    Args:
        topic_data: Topic data dict from TopicCrawler.crawl_topic()
        language: Output language
        include_article_summaries: Whether to generate individual article summaries
    
    Returns:
        Updated topic_data with 'summary' field populated and each article
        having its own 'summary' field
    """
    topic_name = topic_data['topic_name']
    articles = topic_data['articles']
    
    # Generate per-article summaries first (if enabled)
    if include_article_summaries and articles:
        print(f"  - Generating per-article summaries...")
        article_summaries = summarize_articles_batch(
            articles=articles,
            topic_name=topic_name,
            language=language
        )
        
        # Add summary to each article
        for article in articles:
            article_id = article.get('id') if isinstance(article, dict) else article.id
            if article_id in article_summaries:
                if isinstance(article, dict):
                    article['summary'] = article_summaries[article_id]
                else:
                    article.summary = article_summaries[article_id]
    
    # Generate topic-level summary
    print(f"  - Generating topic summary...")
    summary = summarize_topic(
        topic_name=topic_name,
        topic_description=topic_data.get('description', ''),
        articles=articles,
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
