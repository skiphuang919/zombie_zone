from .. import db
from tools import current_utc_time
from ..model import Posts
from flask import current_app, abort
from flask_login import current_user


def write_blog(title, content, author):
    try:
        new_post = Posts(title=title,
                         body=content,
                         author=author)
        db.session.add(new_post)
        db.session.commit()
    except:
        db.session.rollback()
        raise
    else:
        return new_post


def get_post_by_id(post_id):
    return Posts.query.get_or_404(post_id)


def get_paginate_posts(page_num):
    return Posts.query.order_by(Posts.timestamp.desc()).\
        paginate(page=page_num, per_page=current_app.config['POSTS_PER_PAGE'], error_out=False)


def update_post(post_id, title=None, body=None):
    post_obj = Posts.query.get_or_404(post_id)

    if post_obj.author_id != current_user.user_id:
        abort(403)

    if post_obj:
        _commit = False
        if title is not None:
            post_obj.title = title
            _commit = True
        if body is not None:
            post_obj.body = body
            _commit = True
        if _commit:
            post_obj.timestamp = current_utc_time()
            db.session.add(post_obj)
            db.session.commit()
    return post_obj


def del_post(post_id):
    my_post = Posts.query.get_or_404(post_id)
    if str(my_post.author_id) != str(current_user.user_id):
        abort(403)
    db.session.delete(my_post)
    db.session.commit()
