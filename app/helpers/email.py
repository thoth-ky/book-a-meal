'''Email support'''
import os
from threading import Thread
from flask import render_template, current_app
from flask_mail import Message
# local imports
from .. import MAIL
from ..models.authmodels import User


def send_email(message, app):  # pragma: no cover
    '''create email and send it using a thread'''
    with app.app_context():
        MAIL.send(message)

def send_updated_menu(menu):  # pragma: no cover
    '''Send updated menu, to all clients'''
    # introduce option to opt out of notifications in User model
    users = User.get_all()
    subject = "Today's Menu Updates"
    sender = current_app.config.get('ADMINS')[0]  
    for user in users:
        recipients = [user.email]
        html_body = render_template('email/menu.html', user=user, menu=menu)  # pragma: no cover
        # create message
        msg = Message(subject, sender=sender, recipients=recipients)
        msg.html = html_body

        t = Thread(target=send_email,
                   args=[msg],
                   kwargs={'app': current_app._get_current_object()})
        t.start()
