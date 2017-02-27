from datetime import datetime
from . import db
from flask import current_app
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.String(64), nullable=False, unique=True, index=True)
    open_id = db.Column(db.String(64), index=True)
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

    def generate_confirm_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.user_id})

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        db.session.commit()
        return True

