import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def send_email(user: str, password: str, from_addr: str, recipient_addr: str, subject: str, body: str):
    msg = MIMEMultipart()
    msg['From'] = from_addr
    msg['To'] = recipient_addr
    msg['Bcc'] = recipient_addr
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'html'))

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(user, password)
        smtp.send_message(msg)
