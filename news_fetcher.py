import feedparser
from datetime import datetime, timedelta
import time
import requests
import os

# RSS Feeds for Major AI News Sources
RSS_FEEDS = {
    "Wired AI": "https://www.wired.com/feed/tag/ai/latest/rss",
    "The Verge AI": "https://www.theverge.com/rss/ai/index.xml",
    "TechCrunch AI": "https://techcrunch.com/category/artificial-intelligence/feed/",
    "MIT Tech Review AI": "https://www.technologyreview.com/topic/artificial-intelligence/feed",
    "OpenAI News": "https://openai.com/news/rss.xml",
    "Google DeepMind": "https://deepmind.google/blog/rss.xml",
    "Hugging Face Blog": "https://huggingface.co/blog/feed.xml",
    "ArXiv AI": "https://rss.arxiv.org/rss/cs.AI"
}

def fetch_news() -> list[dict]:
    """
    Fetches news from the defined RSS feeds + GitHub Trending Radar.
    """
    news_items = []
    
    # 1. RSS Feeds
    print("Fetching news from major sources...")
    
    for source, url in RSS_FEEDS.items():
        try:
            print(f"Parsing {source}...")
            feed = feedparser.parse(url)
            
            # Get top 3 articles from each source
            import itertools
            for entry in itertools.islice(feed.entries, 3):
                # Try to find a published date
                published = entry.get("published", entry.get("updated", "Unknown Date"))
                
                item = {
                    "source": source,
                    "title": entry.title,
                    "link": entry.link,
                    "published": published,
                    "summary": entry.get("summary", "No summary available.")[:200] + "..." # Truncate summary
                }
                news_items.append(item)
                
        except Exception as e:
            print(f"Error fetching {source}: {e}")
            
    # 2. GitHub Trending Radar
    github_repos = fetch_github_trending_repos()
    news_items.extend(github_repos)
            
    return news_items

def fetch_github_trending_repos():
    """
    Fetch top 3 most-starred AI repos created in the last 7 days.
    """
    print("Fetching GitHub Trending Radar...")
    repos_list = []
    try:
        seven_days_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        query = f"topic:ai+topic:llm+created:>{seven_days_ago}"
        url = f"https://api.github.com/search/repositories?q={query}&sort=stars&order=desc&per_page=3"
        
        # Optional Token
        headers = {}
        token = os.getenv("GITHUB_TOKEN") or os.getenv("GITHUB_API_KEY") # Check common secret names
        if token:
            headers["Authorization"] = f"token {token}"
            
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            for repo in data.get('items', []):
                repos_list.append({
                    "source": "GitHub Radar",
                    "title": f"HOT REPO: {repo['name']}",
                    "link": repo['html_url'],
                    "published": f"Created: {repo['created_at'][:10]}",
                    "summary": f"{repo['description']} (Stars: {repo['stargazers_count']})",
                    "badge": "Tool"
                })
        else:
            print(f"GitHub API Error: {response.status_code}")
    except Exception as e:
        print(f"Failed to fetch GitHub Radar: {e}")
    
    return repos_list

def deduplicate_news(news_items):
    """
    Remove duplicate articles based on title.
    """
    seen_titles = set()
    unique_items = []
    for item in news_items:
        clean_title = item['title'].lower().strip()
        if clean_title not in seen_titles:
            seen_titles.add(clean_title)
            unique_items.append(item)
    return unique_items

def format_news_for_email(news_items, ai_summary=None):
    """
    Formats the list of news items into a Premium HTML string for email.
    """
    if not news_items:
        return "<p>No news found today.</p>"

    summary_section = ""
    deep_dive_section = ""
    
    if ai_summary and isinstance(ai_summary, dict):
        if ai_summary.get('deep_dive'):
            formatted_deep_dive = ai_summary['deep_dive'].replace('\n', '<br>')
            deep_dive_section = f"""
            <div style="background-color: #1a1a1a; color: #ffffff; padding: 25px; margin-bottom: 30px; border-radius: 12px; font-family: 'Segoe UI', Arial, sans-serif; box-shadow: 0 4px 15px rgba(0,0,0,0.1);">
                <div style="text-transform: uppercase; font-size: 11px; letter-spacing: 1px; color: #007bff; font-weight: bold; margin-bottom: 10px;">Deep Dive: Industry Impact</div>
                <h2 style="margin-top: 0; color: #ffffff; font-size: 22px; margin-bottom: 15px;">The Big Picture</h2>
                <div style="color: #cccccc; line-height: 1.6; font-size: 15px;">
                    {formatted_deep_dive}
                </div>
            </div>
            """
            
        if ai_summary.get('summary'):
            formatted_summary = ai_summary['summary'].replace('\n', '<br>')
            summary_section = f"""
            <div style="background-color: #f8f9fa; border-left: 4px solid #007bff; padding: 20px; margin-bottom: 30px; border-radius: 8px;">
                <h2 style="margin-top: 0; color: #333; font-family: 'Segoe UI', Arial, sans-serif; font-size: 18px;">Executive Summary</h2>
                <div style="color: #555; line-height: 1.6; font-size: 15px;">
                    {formatted_summary}
                </div>
            </div>
            """
    elif ai_summary:
        # Fallback for old string format
        formatted_summary = ai_summary.replace('\n', '<br>')
        summary_section = f"""
        <div style="background-color: #f8f9fa; border-left: 4px solid #007bff; padding: 20px; margin-bottom: 30px; border-radius: 8px;">
            <h2 style="margin-top: 0; color: #333; font-family: 'Segoe UI', Arial, sans-serif; font-size: 18px;">Executive Summary</h2>
            <div style="color: #555; line-height: 1.6; font-size: 15px;">
                {formatted_summary}
            </div>
        </div>
        """
        
    news_html = ""
    research_html = ""
    code_html = ""
    
    for item in news_items:
        # Badge Logic
        badge_html = ""
        badge = item.get('badge', '')
        if not badge:
            if item['source'] == "ArXiv AI":
                badge = "Breakthrough" # Fallback for research
            elif item['source'] == "GitHub Radar":
                badge = "Tool"

        if badge:
            badge_colors = {
                "Breakthrough": "#d4edda; color: #155724; border: 1px solid #c3e6cb;",
                "Policy": "#fff3cd; color: #856404; border: 1px solid #ffeeba;",
                "Market": "#d1ecf1; color: #0c5460; border: 1px solid #bee5eb;",
                "Tool": "#e2e3e5; color: #383d41; border: 1px solid #d6d8db;",
            }
            color_style = badge_colors.get(badge, "background-color: #f8f9fa; color: #333; border: 1px solid #ddd;")
            # Ensure color_style is properly prefixed if it's from the dict (which it is)
            if not color_style.startswith("background-color:"):
                color_style = "background-color: " + color_style
            badge_html = f'<span style="display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 10px; font-weight: bold; margin-bottom: 8px; {color_style}">{badge.upper()}</span>'

        card_html = f"""
        <div style="margin-bottom: 25px; background: white; border: 1px solid #e1e4e8; border-radius: 12px; overflow: hidden; font-family: 'Segoe UI', Arial, sans-serif;">
            <div style="padding: 20px;">
                <div style="margin-bottom: 10px;">
                    <span style="display: inline-block; background: #e7f3ff; color: #007bff; padding: 4px 10px; border-radius: 20px; font-size: 12px; font-weight: bold;">{item['source']}</span>
                    {badge_html}
                </div>
                <h3 style="margin: 0 0 10px 0; font-size: 18px; color: #1a1a1a;">
                    <a href="{item['link']}" style="color: #1a1a1a; text-decoration: none;">{item['title']}</a>
                </h3>
                <p style="color: #666; font-size: 14px; margin-bottom: 15px; line-height: 1.5;">{item['summary']}</p>
                <div style="font-size: 12px; color: #999;">{item['published']}</div>
            </div>
        </div>
        """
        
        if item['source'] == "ArXiv AI":
            research_html += card_html
        elif item['source'] == "GitHub Radar":
            code_html += card_html
        else:
            news_html += card_html

    sections_html = ""
    if news_html:
        sections_html += '<h2 style="border-bottom: 2px solid #eee; padding-bottom: 10px; color: #333; margin-bottom: 20px; font-size: 20px;">📰 Industry Headlines</h2>' + news_html
    if research_html:
        sections_html += '<h2 style="border-bottom: 2px solid #eee; padding-bottom: 10px; color: #333; margin: 40px 0 20px 0; font-size: 20px;">🔬 Science & Research Spotlight</h2>' + research_html
    if code_html:
        sections_html += '<h2 style="border-bottom: 2px solid #eee; padding-bottom: 10px; color: #333; margin: 40px 0 20px 0; font-size: 20px;">⚙️ Trending Code & Tools</h2>' + code_html
        
    full_html = f"""
    <html>
        <body style="background-color: #ffffff; margin: 0; padding: 20px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;">
            <div style="max-width: 600px; margin: 0 auto;">
                <h1 style="color: #1a1a1a; text-align: center; margin-bottom: 30px; font-size: 28px;">Daily AI Intelligence</h1>
                <p style="text-align: center; color: #666; margin-bottom: 40px;">Selected news for {datetime.now().strftime('%B %d, %Y')}</p>
                
                {deep_dive_section}
                {summary_section}
                
                {sections_html}
                
                <div style="text-align: center; margin-top: 40px; padding-top: 20px; border-top: 1px solid #eee; color: #999; font-size: 12px;">
                    Sent by your automated AI News Agent.
                </div>
            </div>
        </body>
    </html>
    """
    return full_html

if __name__ == "__main__":
    # Test run
    import itertools
    items = fetch_news()
    print(f"Found {len(items)} items.")
    for item in itertools.islice(items, 3):
        print(f"- {item['title']} ({item['source']})")
