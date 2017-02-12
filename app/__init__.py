from flask import Flask
from flask_cache import Cache


cache = Cache()


def create_app(config):
    app = Flask(__name__)
    app.config.from_object(config)
    config.init_app(app)

    cache.init_app(app)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    return app
