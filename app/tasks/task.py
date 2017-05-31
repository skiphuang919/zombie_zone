from .. import celery, mail


@celery.task
def send_mail(msg):
    mail.send(msg)
