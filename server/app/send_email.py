# Import smtplib for the actual sending function
import smtplib
import ssl
import constants as const
import os

# Import the email modules we'll need
from email.message import EmailMessage
from email.mime.text import MIMEText

if os.path.exists('passwords.env'):
    from dotenv import load_dotenv
    load_dotenv('passwords.env')

def send_email(subject, message, recipient, test = False, test_recipients = []):
    
    sender_email = os.environ['email_sender']
    email_password = os.environ['email_password']
    # Create the plain-text and HTML version of your message
    text = f"""Hello,

{message}

BR,
Atanas Kolev's automated message bot

NOTE: Do not reply or write to me! I'm a bot and your message will be lost to the void. 
"""
    msg = MIMEText(text, 'plain')
    msg['Subject'] = subject
    port = 993

    with smtplib.SMTP(host = 'outlook.office365.com', port = port) as server:
        server.starttls()
        server.login(sender_email, email_password)
        server.sendmail(sender_email, recipient, msg.as_string())

if __name__ == "__main__":
    pass