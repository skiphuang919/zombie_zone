from datetime import datetime
from .. import db
from flask import current_app
from ..model import Users, Participate, Parties
from tools import get_db_unique_id
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer


def register_user(open_id=None, reg_info=None):
    """
    :param open_id: user openid; str
    :param reg_info: user info; dict
    :return:
    """
    _commit = False
    user = get_user(open_id=open_id)
    if not user:
        user = Users(user_id=get_db_unique_id(),
                     open_id=open_id)
        _commit = True
    if reg_info:
        for k, v in reg_info.items():
            if hasattr(Users, k):
                setattr(user, k, v)
                _commit = True
    if _commit:
        user.update_time = datetime.utcnow()
        db.session.add(user)
        db.session.commit()
    return user


def update_user_profile(user_id, profile_dic):
    if user_id and profile_dic:
        user = get_user(user_id=user_id)
        if user:
            _commit = False
            for k, v in profile_dic.items():
                if hasattr(Users, k):
                    setattr(user, k, v)
                    _commit = True
            if _commit:
                user.update_time = datetime.utcnow()
                db.session.add(user)
                db.session.commit()


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


def get_joined_parties(user_id, limit=None, offset=None, get_count=False):
    sql = Participate.query.filter_by(participator_id=user_id)

    if get_count:
        return sql.count()
    else:
        sql = sql.order_by(Participate.join_time.desc())

        if limit is not None:
            sql = sql.limit(limit)

        if offset is not None:
            sql = sql.offset(offset)

        return [p.joined_party for p in sql.all()]


def get_created_parties(user_id, limit=None, offset=None, get_count=False):
    sql = Parties.query.filter_by(host_id=user_id)

    if get_count:
        return sql.count()
    else:
        sql = sql.order_by(Parties.create_time.desc())

        if limit is not None:
            sql = sql.limit(limit)

        if offset is not None:
            sql = sql.offset(offset)

        return sql.all()
