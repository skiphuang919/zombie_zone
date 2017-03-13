from datetime import datetime
from . import db


class User(db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.String(64), unique=True, index=True, primary_key=True)
    open_id = db.Column(db.String(64), index=True, unique=True)
    name = db.Column(db.String(64), nullable=False, unique=True, index=True)
    email = db.Column(db.String(128), nullable=False, unique=True, index=True)
    gender = db.Column(db.Integer, nullable=False)
    city = db.Column(db.String(32))
    slogan = db.Column(db.String(512))
    confirmed = db.Column(db.Boolean, default=False)
    add_time = db.Column(db.DateTime, default=datetime.utcnow())
    update_time = db.Column(db.DateTime)

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        pass


