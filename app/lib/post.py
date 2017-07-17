from .. import db
from tools import get_db_unique_id
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
    sql = Posts.query

    if limit is not None:
        sql = sql.limit(limit)

    if offset is not None:
        sql = sql.offset(offset)

    return sql.all()
