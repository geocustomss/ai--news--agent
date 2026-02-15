import os
from dotenv import load_dotenv
from news_fetcher import fetch_news, format_news_for_email, deduplicate_news
from email_sender import send_email
from ai_summarizer import summarize_news
import datetime

# Load environment variables from the script's directory
from pathlib import Path
script_dir = Path(__file__).parent
load_dotenv(dotenv_path=script_dir / '.env')

def job():
    print(f"Starting AI News Agent Job at {datetime.datetime.now()}...")
    
    # 1. Fetch News
    news_items = fetch_news()
    
    if not news_items:
        print("No news items found. Aborting.")
        return

    # 1.5 Deduplicate
    news_items = deduplicate_news(news_items)

    # 1.8 AI Summary
    ai_summary = summarize_news(news_items)

    # 2. Format News
    email_body = format_news_for_email(news_items, ai_summary)
    
    # 3. Send Email
    recipient = os.getenv("EMAIL_RECIPIENT")
    if recipient:
        subject = f"Daily AI News - {datetime.date.today()}"
        send_email(subject, email_body, recipient)
    else:
        print("No EMAIL_RECIPIENT defined in .env. Skipping email.")
        print("Generated Body Preview:")
        print(email_body[:500] + "...")

if __name__ == "__main__":
    job()
