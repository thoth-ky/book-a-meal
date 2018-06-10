'''Email support'''
import os
from threading import Thread
from flask import render_template, current_app
from flask_mail import Message
# local imports
from .. import MAIL, CELERY
from ..models.models import User


def send_async_email(app, msg):  
    '''send asynchronous emails'''

    MAIL.send(msg)


def send_email(subject, sender, recipients, html_body):
    '''create email and send it using a thread'''
    print('at entry')
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.html = html_body
    with current_app.app_context():
        MAIL.send(msg)
    
@CELERY.task
def send_updated_menu(): 
    print('at entry')
    '''Send updated menu, to all clients'''
    # introduce option to opt out of notifications in User model
    users = User.get_all()
    subject = "Today's Menu Updates"
    sender = current_app.config.get('ADMINS')[0]
    for user in users:
        send_email(
            sender=sender,
            subject=subject,
            recipients=[user.email],
            html_body=render_template('email/menu.html', user=user)
            )
