from flask import Flask
from flask_cache import Cache
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_pagedown import PageDown
from flask_moment import Moment
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

celery = Celery(__name__)


def configure_celery(app, celery_app):
    """
    creates a new Celery object, configures it with the broker from the application config,
    updates the rest of the Celery config from the Flask config and then
    creates a subclass of the task that wraps the task execution in an application context.
    """
    app.config.update({'backend': app.config['CELERY_RESULT_BACKEND'],
                       'broker': app.config['CELERY_BROKER_URL']})
    celery_app.conf.update(app.config)

    task_base = celery.Task

    class ContextTask(task_base):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return task_base.__call__(self, *args, **kwargs)

    celery.Task = ContextTask


def configure_blueprint(app):
    """
    register blueprint to the app
    """
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
    moment.init_app(app)
    configure_celery(app, celery)
    configure_blueprint(app)

    return app
