from tasks import task
from flask import current_app


def send_confirm_mail(recipient, mail_info):
    task.send_mail.apply_async(args=[current_app.config.get('CONFIRM_MAIL_SUBJECT'),
                                     recipient,
                                     'mail/confirm_email.html',
                                     mail_info],)


def send_reset_pwd_mail(recipient, mail_info):
    task.send_mail.apply_async(args=[current_app.config.get('CONFIRM_MAIL_SUBJECT'),
                                     recipient,
                                     'mail/reset_password_mail.html',
                                     mail_info],)

