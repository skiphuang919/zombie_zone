from flask import Flask
from flask_cache import Cache
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config
from celery import Celery


cache = Cache()
mail = Mail()
db = SQLAlchemy()

login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.register'
login_manager.login_message = u'Please register and confirm email to access this page.'

celery = Celery(__name__, broker=Config.CELERY_BROKER_URL)


def create_app(config_name=None):
    app = Flask(__name__)

    if config_name is not None:
        app.config.from_object(config_name)
        config_name.init_app(app)

    cache.init_app(app)

    mail.init_app(app)

    db.init_app(app)

    login_manager.init_app(app)

    celery.conf.update(app.config)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    return app
