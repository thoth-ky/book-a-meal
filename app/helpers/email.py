'''Email support'''
import os
from threading import Thread
from flask import render_template, current_app
from flask_mail import Message
# local imports
from .. import MAIL
from ..models.models import User


def send_email(subject, sender, recipients, html_body, app):  # pragma: no cover
    '''create email and send it using a thread'''
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.html = html_body
    with app.app_context():
        MAIL.send(msg)

def send_updated_menu():  # pragma: no cover
    '''Send updated menu, to all clients'''
    # introduce option to opt out of notifications in User model
    users = User.get_all()
    subject = "Today's Menu Updates"
    sender = current_app.config.get('ADMINS')[0]
    
    for user in users:
        recipients = [user.email]
        html_body = render_template('email/menu.html', user=user)  # pragma: no cover

        t = Thread(target=send_email,
                   args=[subject, sender, recipients, html_body],
                   kwargs={'app': current_app._get_current_object()})
        t.start()
