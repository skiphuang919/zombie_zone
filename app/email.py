from flask import render_template
from flask_mail import Message
from tasks import task


def send_mail(subject, recipient, template, **kwargs):
    msg = Message(subject=subject, recipients=[recipient])
    msg.html = render_template(template, **kwargs)
    task.send_mail.delay(msg)


def send_confirm_mail(subject, recipient, name, token):
    send_mail(subject, recipient, 'confirm_email.html', name=name, token=token)

