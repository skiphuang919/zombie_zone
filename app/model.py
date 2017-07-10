from datetime import datetime
from . import db, login_manager
from flask_login import UserMixin
from flask import current_app
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from werkzeug.security import generate_password_hash, check_password_hash
from .lib import tools

class Participate(db.Model):
    __tablename__ = 'participate'
    participator_id = db.Column(db.String(64), db.ForeignKey('users.user_id'), primary_key=True)
    joined_party_id = db.Column(db.String(64), db.ForeignKey('parties.party_id'), primary_key=True)
    join_time = db.Column(db.DateTime, default=datetime.utcnow())


class Users(db.Model, UserMixin):
    __tablename__ = 'users'
    user_id = db.Column(db.String(64), unique=True, index=True, primary_key=True)
    open_id = db.Column(db.String(64), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
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

    joined_parties = db.relationship('Participate',
                                     foreign_keys=[Participate.participator_id],
                                     backref=db.backref('participator', lazy='joined'),
                                     lazy='dynamic',
                                     cascade='all, delete-orphan')

    def __init__(self, *args, **kwargs):
        super(Users, self).__init__(*args, **kwargs)
        pass

    @property
    def password(self):
        raise AttributeError('Unreadable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        """
        overwrite the method inherit from UserMixin
        return `user_id` attr instead of default `id`
        """
        return self.user_id

    def generate_confirm_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.user_id})

    def has_joined(self, party):
        return self.joined_parties.filter_by(joined_party_id=party.party_id).first() is not None

    def join(self, party):
        if self.has_joined(party) is False:
            participate = Participate(participator=self, joined_party=party)
            db.session.add(participate)
            db.session.commit()

    def quit(self, party):
        participate = self.joined_parties.filter_by(joined_party_id=party.party_id).first()
        if participate:
            db.session.delete(participate)
            db.session.commit()


@login_manager.user_loader
def load_user(user_id):
    return Users.query.filter_by(user_id=user_id).first()


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

    participators = db.relationship('Participate',
                                    foreign_keys=[Participate.joined_party_id],
                                    backref=db.backref('joined_party', lazy='joined'),
                                    lazy='dynamic',
                                    cascade='all, delete-orphan')

    def __init__(self, *args, **kwargs):
        super(Parties, self).__init__(*args, **kwargs)
        pass

    @property
    def participant_count(self):
        return self.participators.count()

    @participant_count.setter
    def participant_count(self, v):
        raise AttributeError('Read only attribute')

    @property
    def is_full(self):
        return self.participant_count >= self.required_count

    @is_full.setter
    def is_full(self, v):
        raise AttributeError('Read only attribute')

    @property
    def local_create_time(self):
        return tools.utc2local(self.create_time)

    @local_create_time.setter
    def local_create_time(self, v):
        raise AttributeError('Read only attribute')


