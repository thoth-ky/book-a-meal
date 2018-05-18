'''email support'''
import os
from threading import Thread
from flask import render_template, current_app
from flask_mail import Message

# local imports
from .. import MAIL
from ..models.models import User
# app_context = current_app.app_context()
# app_context.push()

def send_async_email(msg):
    '''send asynchronous emails'''
    with current_app.app_context():
        with MAIL.connect() as conn:
            conn.send(msg)


def send_email(subject, sender, recipients, html_body):
    '''create email and send it using a thread'''
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.html = html_body
    MAIL.send(msg)
    # Thread(target=send_async_email, args=(msg,)).start()


def send_updated_menu(menu):
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
            html_body=render_template('email/menu.html', menu=menu, user=user)
            )
