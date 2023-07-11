# Import smtplib for the actual sending function
import smtplib
import ssl
import constants as const

# Import the email modules we'll need
from email.message import EmailMessage

def send_email(subject, message, recipient, test = False, test_recipients = []):
    sender_email = const.email_sender
    email_password = const.email_password
    # Create the plain-text and HTML version of your message
    text = f"""Hello,

{message}

BR,
Atanas Kolev's automated message bot

NOTE: Do not reply or write to me! I'm a bot and your message will be lost to the void. 
"""
    
    em = EmailMessage()
    em['From'] = sender_email
    em['To'] = recipient
    em['Subject'] = subject
    em.set_content(text)

    context = ssl.create_default_context()

    with smtplib.SMTP_SSL(host = 'smtp.gmail.com', port = 465, context = context) as smtp:
        smtp.login(user = sender_email, password = email_password)
        smtp.sendmail(sender_email, recipient, em.as_string())

if __name__ == "__main__":
    pass