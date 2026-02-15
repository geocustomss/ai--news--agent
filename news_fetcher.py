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

def format_news_for_email(news_items):
    """
    Formats the list of news items into a HTML string for email.
    """
    if not news_items:
        return "<p>No news found today.</p>"
        
    html_content = "<h2>Daily AI News Summary</h2>"
    
    # Sort simple logic: just group by source for now (or could sort by date if parsed)
    # For now, we return as is.
    
    for item in news_items:
        html_content += f"""
        <div style="margin-bottom: 20px; border-bottom: 1px solid #ccc; padding-bottom: 10px;">
            <h3 style="margin-bottom: 5px;"><a href="{item['link']}">{item['title']}</a></h3>
            <p style="font-size: 0.8em; color: gray;">{item['source']} - {item['published']}</p>
            <p>{item['summary']}</p>
        </div>
        """
        
    return html_content

if __name__ == "__main__":
    # Test run
    import itertools
    items = fetch_news()
    print(f"Found {len(items)} items.")
    for item in itertools.islice(items, 3):
        print(f"- {item['title']} ({item['source']})")
