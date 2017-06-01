from tasks import task
from flask import current_app


def send_confirm_mail(recipient, mail_info):
    task.send_mail.apply_async(args=[current_app.config.get('CONFIRM_MAIL_SUBJECT'),
                                     recipient,
                                     'confirm_email.html',
                                     mail_info],)

