
import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_KEY = 'secret_key'
    APP_ID = 'appid'
    APP_SECRET = 'app_secret'
    DEBUG = True

    CACHE_TYPE = 'redis'
    CACHE_REDIS_HOST = '127.0.0.1'
    CACHE_REDIS_PORT = 6379
    CACHE_REDIS_DB = ''
    CACHE_REDIS_PASSWORD = ''

    BROKER_URL = 'amqp://localhost:5672//'
    CELERY_RESULT_BACKEND = ''
    CELERY_TASK_SERIALIZER = 'json'

    ZOMBIE_ZONE_ADMIN = os.getenv('ADMIN', '')

    MAIL_SERVER = 'smtp.163.com'
    MAIL_PORT = 465
    MAIL_USE_SSL = True

    MAIL_USERNAME = os.getenv('MAIL_USERNAME', '')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD', '')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER', '')

    HTTP_GRAVATAR_URL = 'http://www.gravatar.com/avatar'
    HTTPS_GRAVATAR_URL = 'https://secure.gravatar.com/avatar'

    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')

    CONFIRM_MAIL_SUBJECT = '[Zombie Zone]'

    POSTS_PER_PAGE = 10
    COMMENTS_PER_PAGE = 10

    @staticmethod
    def init_app(app):
        pass
