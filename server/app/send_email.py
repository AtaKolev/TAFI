# Import smtplib for the actual sending function
from smtplib import SMTP_SSL, SMTP_SSL_PORT
import os

if os.path.exists('passwords.env'):
    from dotenv import load_dotenv
    load_dotenv('passwords.env')

def send_email(subject, message, recipients, test = False, test_recipients = []):
    
    sender_email = os.environ['email_sender']
    email_password = os.environ['email_password']
    SMTP_HOST = 'smtp-mail.outlook.com'
    # Create the plain-text and HTML version of your message
    text = f"""Hello,

{message}

BR,
Atanas Kolev's automated message bot

NOTE: Do not reply or write to me! I'm a bot and your message will be lost to the void. 
"""
    from_email = sender_email
    to_emails = recipients
    body = text
    headers = subject
    email_message = headers + "\r\n" + body

    smtp_server = SMTP_SSL(SMTP_HOST, port = SMTP_SSL_PORT)#, keyfile=)
    smtp_server.set_debuglevel(1)
    smtp_server.login(sender_email, email_password)
    smtp_server.sendmail(from_email, to_emails, email_message)

if __name__ == "__main__":
    pass