
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

    MAIL_SERVER = 'smtp.163.com'
    MAIL_PORT = 25
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER')

    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')

    @staticmethod
    def init_app(app):
        pass
