from datetime import datetime
from . import db, login_manager
from flask_login import UserMixin
from flask import current_app
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer


party_guy_table = db.Table('party_guy_table',
                           db.Column('user_id', db.String(64), db.ForeignKey('users.user_id')),
                           db.Column('party_id', db.String(64), db.ForeignKey('parties.party_id')))


class Users(db.Model, UserMixin):
    __tablename__ = 'users'
    user_id = db.Column(db.String(64), unique=True, index=True, primary_key=True)
    open_id = db.Column(db.String(64), index=True, unique=True, nullable=False)
    name = db.Column(db.String(64))
    email = db.Column(db.String(128), unique=True, index=True)
    cellphone = db.Column(db.String(16), unique=True, index=True)
    gender = db.Column(db.Integer)
    city = db.Column(db.String(32))
    slogan = db.Column(db.String(512))
    head_img_url = db.Column(db.String(512))
    confirmed = db.Column(db.Boolean, default=False)
    add_time = db.Column(db.DateTime, default=datetime.utcnow())
    update_time = db.Column(db.DateTime)
    created_parties = db.relationship('Parties',
                                      backref='host',
                                      lazy='dynamic')
    joined_parties = db.relationship('Parties',
                                     secondary=party_guy_table,
                                     backref=db.backref('joined_users', lazy='dynamic'),
                                     lazy='dynamic')

    def __init__(self, *args, **kwargs):
        super(Users, self).__init__(*args, **kwargs)
        pass

    def get_id(self):
        """
        overwrite the method inherit from UserMixin
        return `open_id` attr instead of default `id`
        """
        return self.open_id

    def generate_confirm_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.user_id})

    def has_joined(self, party):
        return True if self.joined_parties.filter_by(party_id=party.party_id).first() \
            else False

    def join(self, party):
        if not self.has_joined(party):
            self.joined_parties.append(party)
            db.session.commit()

    def quit(self, party):
        if self.has_joined(party):
            self.joined_parties.remove(party)
            db.session.commit()


@login_manager.user_loader
def load_user(user_id):
    return Users.query.filter_by(open_id=user_id).first()


class Parties(db.Model):
    __tablename__ = 'parties'
    party_id = db.Column(db.String(64), unique=True, index=True, primary_key=True)
    subject = db.Column(db.String(128), nullable=False)
    party_time = db.Column(db.DateTime)
    address = db.Column(db.String(128), nullable=False)
    host_id = db.Column(db.String(64), db.ForeignKey('users.user_id'))
    required_count = db.Column(db.Integer, nullable=False)
    note = db.Column(db.String(512))
    status = db.Column(db.Integer, default=0)
    create_time = db.Column(db.DateTime, default=datetime.utcnow())

    def __init__(self, *args, **kwargs):
        super(Parties, self).__init__(*args, **kwargs)
        pass

    @property
    def participators(self):
        return self.joined_users.all()

    @property
    def is_full(self):
        return False if len(self.participators) < self.required_count else True




