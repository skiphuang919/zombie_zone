from flask import render_template
from flask_mail import Message
from .. import celery, mail


@celery.task
def send_mail(subject, recipient, template, mail_info):
    msg = Message(subject=subject, recipients=[recipient])
    msg.html = render_template(template, **mail_info)
    mail.send(msg)
