from datetime import datetime
from . import db


party_guy_table = db.Table('party_guy_table',
                           db.Column('user_id', db.String(64), db.ForeignKey('users.user_id')),
                           db.Column('party_id', db.String(64), db.ForeignKey('parties.party_id')))


class Users(db.Model):
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
    parties = db.relationship('Parties',
                              secondary=party_guy_table,
                              backref=db.backref('users', lazy='dynamic'))

    def __init__(self, *args, **kwargs):
        super(Users, self).__init__(*args, **kwargs)
        pass


class Parties(db.Model):
    __tablename__ = 'parties'
    party_id = db.Column(db.String(64), unique=True, index=True, primary_key=True)
    subject = db.Column(db.String(128), nullable=False)
    party_time = db.Column(db.DateTime)
    address = db.Column(db.String(128), nullable=False)
    host = db.Column(db.String(64), nullable=False, index=True)
    required_count = db.Column(db.Integer, nullable=False)
    note = db.Column(db.String(512))
    status = db.Column(db.Integer, default=0)
    create_time = db.Column(db.DateTime, default=datetime.utcnow())

    def __init__(self, *args, **kwargs):
        super(Parties, self).__init__(*args, **kwargs)
        pass

