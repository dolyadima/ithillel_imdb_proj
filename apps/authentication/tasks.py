import os
from celery import shared_task
from django.conf import settings
from apps.authentication.models import ActivationToken
from apps.authentication.mail.SendSMTPEmail import send_email


@shared_task
def send_invitation_email(token_id):
    activation_token = ActivationToken.objects.get(id=token_id)
    user = activation_token.user
    text = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Activate account</title>
</head>
<body>
    Hi, '''+user.name+'''!<br/><br/>
    To activate your account please follow a <a href="'''+settings.SITE_URL+'''/authentication/registration-activate/'''+activation_token.token+'''/">link.</a>
</body>
</html>'''
    smtp_user = os.getenv('SMTP_USER', '')
    smtp_password = os.getenv('SMTP_PASS', '')
    smtp_from = 'Dolya Dima <dolya.d.wt@gmail.com>'
    smtp_subject = 'Activate your account please'
    send_email(smtp_user, smtp_password, smtp_from, str(user.email), smtp_subject, text)
