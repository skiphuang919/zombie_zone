from app import create_app, celery
from config import Config

app = create_app(Config)

