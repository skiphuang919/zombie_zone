from .. import db
from tools import get_db_unique_id
from ..model import Posts


def write_blog(content, author):
    new_post = Posts(post_id=get_db_unique_id(),
                     body=content,
                     author=author)
    db.session.add(new_post)
    db.session.commit()


def get_post_by_id(post_id):
    return Posts.query.get(post_id)
