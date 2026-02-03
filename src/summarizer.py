"""
AI Summarizer using DeepSeek API
DeepSeek API is OpenAI-compatible
"""

import os
from openai import OpenAI
from .hn_fetcher import HNStory


def create_deepseek_client() -> OpenAI:
    """Create DeepSeek API client"""
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        raise ValueError("DEEPSEEK_API_KEY environment variable is required")
    
    return OpenAI(
        api_key=api_key,
        base_url="https://api.deepseek.com"
    )


def format_stories_for_prompt(stories: list[HNStory]) -> str:
    """Format stories list for AI prompt, including HN discussion links"""
    lines = []
    for i, story in enumerate(stories, 1):
        hn_link = f"https://news.ycombinator.com/item?id={story.id}"
        lines.append(f"{i}. {story.title}")
        lines.append(f"   Score: {story.score} | Comments: {story.descendants}")
        lines.append(f"   Article: {story.url or 'N/A'}")
        lines.append(f"   HN Discussion: {hn_link}")
        if story.text:
            # Truncate long text
            text = story.text[:500] + "..." if len(story.text) > 500 else story.text
            lines.append(f"   Content: {text}")
        lines.append("")
    return "\n".join(lines)


def summarize_stories(stories: list[HNStory], language: str = "zh") -> str:
    """
    Use DeepSeek to summarize HN stories
    
    Args:
        stories: List of HN stories to summarize
        language: Output language ('zh' for Chinese, 'en' for English)
    """
    client = create_deepseek_client()
    
    stories_text = format_stories_for_prompt(stories)
    
    lang_instruction = "请用中文回复" if language == "zh" else "Please respond in English"
    
    prompt = f"""你是一个技术新闻分析师。以下是今天 Hacker News 上的热门文章列表。
请对这些内容进行分析和总结。{lang_instruction}。

要求：
1. 按主题分类（如：AI/ML、编程语言、创业、开源项目、科技新闻等）
2. 每个分类下列出相关文章，每篇文章必须包含：
   - 标题和简要说明
   - 原文链接（Article URL）
   - HN 讨论链接（方便查看评论）
3. 确保覆盖全部 {len(stories)} 篇文章，不要遗漏
4. 最后给出 3-5 个今日最值得阅读的文章推荐，附上理由和链接

今日 Hacker News Top {len(stories)} 文章：

{stories_text}
"""

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": "你是一个专业的技术新闻分析师，擅长分析和总结 Hacker News 上的热门技术内容。输出时保留所有链接，方便读者点击访问。"},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=4000,  # Increased for full 30 articles with links
    )
    
    return response.choices[0].message.content


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    
    from .hn_fetcher import fetch_top_stories
    
    stories = fetch_top_stories(30)
    summary = summarize_stories(stories)
    print(summary)
