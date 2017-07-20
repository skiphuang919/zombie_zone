from .. import db
from tools import get_db_unique_id, current_utc_time
from ..model import Posts


def write_blog(title, content, author):
    new_post = Posts(post_id=get_db_unique_id(),
                     title=title,
                     body=content,
                     author=author)
    db.session.add(new_post)
    db.session.commit()


def get_post_by_id(post_id):
    return Posts.query.get(post_id)


def get_posts(limit=None, offset=None):
    sql = Posts.query.order_by(Posts.timestamp.desc())

    if limit is not None:
        sql = sql.limit(limit)

    if offset is not None:
        sql = sql.offset(offset)

    return sql.all()


def update_post(post_id, title=None, body=None):
    post_obj = get_post_by_id(post_id)
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
    post = get_post_by_id(post_id)
    if post:
        db.session.delete(post)
        db.session.commit()