import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

def send_email(subject, html_content, to_email):
    """
    Sends an HTML email using SMTP credentials from environment variables.
    """
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    sender_email = os.getenv("EMAIL_SENDER")
    sender_password = os.getenv("EMAIL_PASSWORD") # App Password for Gmail
    
    if not sender_email or not sender_password:
        print("Error: EMAIL_SENDER or EMAIL_PASSWORD not set in environment.")
        return False

    # Linter safety: assert these are strings now
    sender_email = str(sender_email)
    sender_password = str(sender_password)

    try:
        msg = MIMEMultipart()
        msg["From"] = sender_email
        msg["To"] = to_email
        msg["Subject"] = subject

        msg.attach(MIMEText(html_content, "html"))

        print(f"Connecting to {smtp_server}...")
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, to_email, msg.as_string())
        server.quit()
        
        print("Email sent successfully!")
        return True
        
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False

if __name__ == "__main__":
    # Test run (will fail without env vars)
    print("Testing email sender...")
    send_email("Test Subject", "<h1>Hello</h1><p>This is a test.</p>", "test@example.com")
