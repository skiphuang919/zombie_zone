from flask import Flask, request, jsonify, render_template
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


def configure_extension(app):
    """
    config and init extension with flask app instance
    """

    db.init_app(app)

    cache.init_app(app)

    mail.init_app(app)

    login_manager.session_protection = 'strong'
    login_manager.login_view = 'auth.login'
    login_manager.login_message = u'Please login to access this page.'
    login_manager.init_app(app)

    pagedown.init_app(app)

    moment.init_app(app)


def configure_error_handler(app):
    """
    configure the error handler
    """
    @app.errorhandler(403)
    def forbidden_page(e):
        if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
            res = jsonify({'status': -1, 'msg': 'access forbidden', 'data': ''})
            res.status_code = 403
            return res
        return render_template('error/403.html')

    @app.errorhandler(404)
    def not_found_page(e):
        if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
            res = jsonify({'status': -1, 'msg': 'not found', 'data': ''})
            res.status_code = 404
            return res
        return render_template('error/404.html')

    @app.errorhandler(500)
    def internal_error_page(e):
        if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
            res = jsonify({'status': -1, 'msg': 'internal error', 'data': ''})
            res.status_code = 500
            return res
        return render_template('error/500.html')


def create_app(config_name):
    """
    create flask app instance and do the configure
    """

    app = Flask(__name__)

    app.config.from_object(config_name)
    config_name.init_app(app)

    # register custom filter `prettify` in app
    app.jinja_env.filters['prettify'] = prettify

    configure_extension(app)
    configure_celery(app, celery)
    configure_blueprint(app)
    configure_error_handler(app)

    return app
