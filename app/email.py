from threading import Thread
from flask import current_app
from flask_mail import Message
from . import mail


def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_mail(subject, recipient, body):
    app = current_app._get_current_object()
    msg = Message(subject=subject, recipients=[recipient])
    msg.body = body
    thr = Thread(target=send_async_email, args=[app, msg])
    thr.start()
    return thr
