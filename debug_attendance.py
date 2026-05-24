# test_email.py
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

print("Testing SMTP Configuration...")
print("=" * 50)

smtp_server = os.getenv('SMTP_SERVER')
smtp_port = int(os.getenv('SMTP_PORT', 587))
smtp_username = os.getenv('SMTP_USERNAME')
smtp_password = os.getenv('SMTP_PASSWORD')
smtp_from_email = os.getenv('SMTP_FROM_EMAIL', smtp_username)

print(f"Server: {smtp_server}")
print(f"Port: {smtp_port}")
print(f"Username: {smtp_username}")
print(f"Password: {'*' * len(smtp_password) if smtp_password else 'NOT SET'}")
print(f"From Email: {smtp_from_email}")

try:
    # Create test email
    msg = MIMEMultipart()
    msg['From'] = smtp_from_email
    msg['To'] = smtp_username  # Send to yourself
    msg['Subject'] = 'SMTP Test - Tap & Pay'
    
    body = "This is a test email from your Tap & Pay system. SMTP is working!"
    msg.attach(MIMEText(body, 'plain'))
    
    # Connect and send
    print("\nConnecting to SMTP server...")
    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()
    print("Logging in...")
    server.login(smtp_username, smtp_password)
    print("Sending email...")
    server.send_message(msg)
    server.quit()
    
    print("\n✅ Email sent successfully!")
    
except Exception as e:
    print(f"\n❌ Error: {e}")