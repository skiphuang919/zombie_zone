from datetime import datetime
from .. import db
from flask import current_app
from flask_login import current_user
from ..model import Users, Participate, Parties, Posts
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer


def register_user(email, name, password):

    user = Users(email=email,
                 name=name,
                 password=password,
                 timestamp=datetime.utcnow())
    db.session.add(user)
    db.session.commit()
    return user


def change_pwd(new_pwd):
    current_user.password = new_pwd
    db.session.add(current_user)
    db.session.commit()


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
                user.timestamp = datetime.utcnow()
                db.session.add(user)
                db.session.commit()


def get_user(user_id=None, open_id=None, cellphone=None, email=None, name=None):
    if user_id is not None:
        return Users.query.filter_by(user_id=user_id).first()
    elif open_id is not None:
        return Users.query.filter_by(open_id=open_id).first()
    elif cellphone is not None:
        return Users.query.filter_by(cellphone=cellphone).first()
    elif email is not None:
        return Users.query.filter_by(email=email).first()
    elif name is not None:
        return Users.query.filter_by(name=name).first()
    else:
        return None


def is_email_exist(email):
    user = get_user(email=email)
    return True if user else False


def is_name_exist(name):
    user = get_user(name=name)
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

        return [(p.joined_party, p.join_time)for p in sql.all()]


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


def get_current_user_post(get_count=False):
    if get_count:
        return current_user.posts.count()
    return current_user.posts.order_by(Posts.timestamp.desc()).all()


def get_paginate_users(page_num):
    return Users.query.order_by(Users.timestamp.desc()).\
        paginate(page=page_num, per_page=current_app.config['POSTS_PER_PAGE'], error_out=False)
