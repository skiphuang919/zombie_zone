from .. import db
from ..model import User
from tools import get_db_unique_id


def add_user(open_id=None, name=None, email=None, gender=None, city=None, slogan=None):
    user = User(user_id=get_db_unique_id(),
                open_id=open_id,
                name=name,
                email=email,
                gender=gender,
                city=city,
                slogan=slogan)
    db.session.add(user)
    db.session.commit()


def is_email_exist(email):
    user = User.query.filter_by(email=email).first()
    return True if user else False


def is_name_exist(name):
    user = User.query.filter_by(name=name).first()
    return True if user else False
