from flask import Flask
from flask_cache import Cache
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_pagedown import PageDown
from flask_moment import Moment
from config import Config
from celery import Celery
from lib.tools import prettify


cache = Cache()
mail = Mail()
db = SQLAlchemy()
pagedown = PageDown()
moment = Moment()

login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'
login_manager.login_message = u'Please login to access this page.'

celery = Celery(__name__, broker=Config.CELERY_BROKER_URL)


def create_app(config_name):
    app = Flask(__name__)

    app.config.from_object(config_name)
    config_name.init_app(app)

    # register custom filter `prettify` in app
    app.jinja_env.filters['prettify'] = prettify

    cache.init_app(app)
    mail.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    pagedown.init_app(app)
    celery.conf.update(app.config)
    moment.init_app(app)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .auth import auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    from .user import user_blueprint
    app.register_blueprint(user_blueprint, url_prefix='/user')

    from .posts import posts_blueprint
    app.register_blueprint(posts_blueprint, url_prefix='/posts')

    from .party import party_blueprint
    app.register_blueprint(party_blueprint, url_prefix='/party')

    return app
