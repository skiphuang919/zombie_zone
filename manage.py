from flask_script import Manager
from app import create_app
from config import Config

app = create_app(Config)
manager = Manager(app)

if __name__ == '__main__':
    manager.run()
