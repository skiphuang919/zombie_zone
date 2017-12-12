from datetime import datetime
from . import db, login_manager
from flask_login import UserMixin
from flask import current_app
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from werkzeug.security import generate_password_hash, check_password_hash
from .lib import tools
from .lib.utils import Gravatar


class Permission(object):
    LOGIN = 0x01
    CONFIRMED = 0x02
    ADMINISTRATOR = 0x40


class Participate(db.Model):
    __tablename__ = 'participate'
    participator_id = db.Column(db.String(64), db.ForeignKey('users.user_id'), primary_key=True)
    joined_party_id = db.Column(db.String(64), db.ForeignKey('parties.party_id'), primary_key=True)
    join_time = db.Column(db.DateTime, default=datetime.utcnow)


class Users(db.Model, UserMixin):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True)
    open_id = db.Column(db.String(64), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    name = db.Column(db.String(64), unique=True, index=True)
    email = db.Column(db.String(128), unique=True, index=True)
    cellphone = db.Column(db.String(16), unique=True, index=True)
    gender = db.Column(db.Integer, default=1)
    city = db.Column(db.String(32))
    slogan = db.Column(db.String(512))
    head_img_url = db.Column(db.String(512))
    confirmed = db.Column(db.Boolean, default=False)
    add_time = db.Column(db.DateTime, default=datetime.utcnow)
    timestamp = db.Column(db.DateTime)

    created_parties = db.relationship('Parties',
                                      backref='host',
                                      lazy='dynamic')

    # more that one foreign key between two table, use `foreign_keys` to
    # qualify each relationship by instructing which foreign key column should be considered
    joined_parties = db.relationship('Participate',
                                     foreign_keys=[Participate.participator_id],
                                     backref=db.backref('participator', lazy='joined'),
                                     lazy='dynamic',
                                     cascade='all, delete-orphan')

    posts = db.relationship('Posts', backref='author', lazy='dynamic')

    def __init__(self, **kwargs):
        super(Users, self).__init__(**kwargs)

        if self.email is not None and self.head_img_url is None:
            gravatar = Gravatar(self.email)
            self.head_img_url = gravatar.avatar_url()
            db.session.add(self)
            db.session.commit()

    @property
    def is_administrator(self):
        return True if self.email == current_app.config['ZOMBIE_ZONE_ADMIN'] else False

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

    def verify_confirm_token(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False

        if data.get('confirm') != self.user_id:
            return False

        self.confirmed = True
        db.session.add(self)
        db.session.commit()
        return True

    def generate_reset_pwd_token(self, expiration=300):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'reset_pwd': self.user_id})

    def reset_pwd(self, token, new_pwd):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False

        if data.get('reset_pwd') != self.user_id:
            return False

        self.password = new_pwd
        db.session.add(self)
        db.session.commit()
        return True

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
    party_id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(128), nullable=False)
    party_time = db.Column(db.DateTime)
    address = db.Column(db.String(128), nullable=False)
    host_id = db.Column(db.String(64), db.ForeignKey('users.user_id'))
    required_count = db.Column(db.Integer, nullable=False)
    note = db.Column(db.String(512))
    status = db.Column(db.Integer, default=0)
    create_time = db.Column(db.DateTime, default=datetime.utcnow)

    participators = db.relationship('Participate',
                                    foreign_keys=[Participate.joined_party_id],
                                    backref=db.backref('joined_party', lazy='joined'),
                                    lazy='dynamic',
                                    cascade='all, delete-orphan')

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


class Posts(db.Model):
    __tablename__ = 'posts'
    post_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(512))
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    author_id = db.Column(db.String(64), db.ForeignKey('users.user_id'))

    @staticmethod
    def on_changed_body(target, value, old_value, initiator):
        """
        the call back func if event listening
        :param target: the object instance receiving the event
        :param value: the value being set
        :param old_value: the previous value being replaced.
        :param initiator: An instance of attributes.Event representing the initiation of the event.
        :return:
        """
        target.body_html = tools.markdown_to_safe_html(md=value)

# register set event listening
db.event.listen(Posts.body, 'set', Posts.on_changed_body)


