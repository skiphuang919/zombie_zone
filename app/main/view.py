from flask import render_template, session
from . import main
from ..lib import post


@main.route('/')
def index():
    a_posts = post.get_posts()
    session['from_endpoint'] = 'main.index'
    return render_template('posts/all_posts.html', posts=a_posts, top_title='All Posts')