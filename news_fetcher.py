import feedparser
from datetime import datetime
import time

# RSS Feeds for Major AI News Sources
RSS_FEEDS = {
    "Wired AI": "https://www.wired.com/feed/tag/ai/latest/rss",
    "The Verge AI": "https://www.theverge.com/rss/ai/index.xml",
    "TechCrunch AI": "https://techcrunch.com/category/artificial-intelligence/feed/",
    "MIT Tech Review AI": "https://www.technologyreview.com/topic/artificial-intelligence/feed"
}

def fetch_news() -> list[dict]:
    """
    Fetches news from the defined RSS feeds.
    Returns a list of dictionaries containing 'title', 'link', 'source', and 'published'.
    """
    news_items = []
    
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
            
    return news_items

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
    if ai_summary:
        summary_section = f"""
        <div style="background-color: #f8f9fa; border-left: 4px solid #007bff; padding: 20px; margin-bottom: 30px; border-radius: 8px;">
            <h2 style="margin-top: 0; color: #333; font-family: 'Segoe UI', Arial, sans-serif;">Executive Summary</h2>
            <div style="color: #555; line-height: 1.6; font-size: 16px;">
                {ai_summary.replace('\n', '<br>')}
            </div>
        </div>
        """
        
    articles_html = ""
    for item in news_items:
        articles_html += f"""
        <div style="margin-bottom: 25px; background: white; border: 1px solid #e1e4e8; border-radius: 12px; overflow: hidden; font-family: 'Segoe UI', Arial, sans-serif;">
            <div style="padding: 20px;">
                <span style="display: inline-block; background: #e7f3ff; color: #007bff; padding: 4px 10px; border-radius: 20px; font-size: 12px; font-weight: bold; margin-bottom: 10px;">{item['source']}</span>
                <h3 style="margin: 0 0 10px 0; font-size: 20px; color: #1a1a1a;">
                    <a href="{item['link']}" style="color: #1a1a1a; text-decoration: none;">{item['title']}</a>
                </h3>
                <p style="color: #666; font-size: 14px; margin-bottom: 15px; line-height: 1.5;">{item['summary']}</p>
                <div style="font-size: 12px; color: #999;">{item['published']}</div>
            </div>
        </div>
        """
        
    full_html = f"""
    <html>
        <body style="background-color: #ffffff; margin: 0; padding: 20px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;">
            <div style="max-width: 600px; margin: 0 auto;">
                <h1 style="color: #1a1a1a; text-align: center; margin-bottom: 30px; font-size: 28px;">Daily AI Intelligence</h1>
                <p style="text-align: center; color: #666; margin-bottom: 40px;">Selected news for {datetime.now().strftime('%B %d, %Y')}</p>
                
                {summary_section}
                
                <h2 style="border-bottom: 2px solid #eee; padding-bottom: 10px; color: #333; margin-bottom: 20px;">Top Stories</h2>
                {articles_html}
                
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
