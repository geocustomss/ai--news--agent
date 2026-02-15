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

    # 4. Archive for Web
    archive_report(email_body)

def archive_report(html_content):
    """
    Saves the report to an archive folder and updates the index.
    """
    archive_dir = Path(__file__).parent / "archive"
    archive_dir.mkdir(exist_ok=True)
    
    today_str = datetime.date.today().strftime("%Y-%m-%d")
    report_path = archive_dir / f"{today_str}.html"
    
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    
    # Update Index
    reports = sorted([f for f in archive_dir.glob("*.html") if f.name != "index.html"], reverse=True)
    
    index_html = f"""
    <html>
    <head>
        <title>AI News Archive</title>
        <style>
            body {{ font-family: sans-serif; max-width: 800px; margin: 40px auto; padding: 20px; line-height: 1.6; color: #333; }}
            h1 {{ border-bottom: 2px solid #eee; padding-bottom: 10px; }}
            ul {{ list-style: none; padding: 0; }}
            li {{ margin-bottom: 10px; padding: 15px; border: 1px solid #eee; border-radius: 8px; }}
            a {{ color: #007bff; text-decoration: none; font-weight: bold; font-size: 18px; }}
            a:hover {{ text-decoration: underline; }}
            .date {{ color: #999; font-size: 14px; margin-left: 10px; }}
        </style>
    </head>
    <body>
        <h1>AI News Intelligence Archive</h1>
        <p>Your daily intelligence reports, archived for history.</p>
        <ul>
    """
    
    for report in reports:
        date_name = report.stem
        index_html += f'<li><a href="{report.name}">{date_name}</a><span class="date">Daily AI Intelligence Report</span></li>\n'
        
    index_html += """
        </ul>
    </body>
    </html>
    """
    
    with open(archive_dir / "index.html", "w", encoding="utf-8") as f:
        f.write(index_html)
    
    print(f"Report archived to {report_path.name}")

if __name__ == "__main__":
    job()
