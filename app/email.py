from threading import Thread
from flask import current_app, render_template
from flask_mail import Message
from . import mail


def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_mail(subject, recipient, template, **kwargs):
    app = current_app._get_current_object()
    msg = Message(subject=subject, recipients=[recipient])
    msg.html = render_template(template, **kwargs)
    thr = Thread(target=send_async_email, args=[app, msg])
    thr.start()
    return thr


def send_confirm_mail(subject, recipient, name, token):
    send_mail(subject, recipient, 'confirm_email.html', name=name, token=token)

