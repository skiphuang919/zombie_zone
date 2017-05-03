from datetime import datetime
from .. import db
from flask import current_app
from ..model import Users
from tools import get_db_unique_id
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer


def update_user(open_id=None, name=None, email=None, cellphone=None,
                gender=None, city=None, slogan=None, head_img_url=None):
    user = get_user(open_id=open_id)
    if not user:
        user = Users(user_id=get_db_unique_id(),
                     open_id=open_id)
    if cellphone is not None:
        user.cellphone = cellphone
    if name is not None:
        user.name = name
    if email is not None:
        user.email = email
    if gender is not None:
        user.gender = gender
    if city is not None:
        user.city = city
    if slogan is not None:
        user.slogan = slogan
    if head_img_url is not None:
        user.head_img_url = head_img_url
    user.update_time = datetime.utcnow()
    db.session.add(user)
    db.session.commit()
    return user


def get_user(user_id=None, open_id=None, cellphone=None, email=None):
    if user_id is not None:
        return Users.query.filter_by(user_id=user_id).first()
    elif open_id is not None:
        return Users.query.filter_by(open_id=open_id).first()
    elif cellphone is not None:
        return Users.query.filter_by(cellphone=cellphone).first()
    elif email is not None:
        return Users.query.filter_by(email=email).first()
    else:
        return None


def is_email_exist(email):
    user = get_user(email=email)
    return True if user else False


def is_cellphone_exist(cellphone):
    user = get_user(cellphone=cellphone)
    return True if user else False


def confirm(token):
    s = Serializer(current_app.config['SECRET_KEY'])
    try:
        data = s.loads(token)
    except:
        return False

    if data.get('confirm') is None:
        return False

    user_obj = get_user(user_id=data.get('confirm'))
    if user_obj is None:
        return False

    if not user_obj.confirmed:
        user_obj.confirmed = True
        db.session.add(user_obj)
        db.session.commit()
    return True

