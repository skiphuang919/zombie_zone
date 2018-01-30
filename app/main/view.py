from flask import render_template, session, request
from . import main
from ..lib import post
from .. import cache


@main.before_request
def set_session():
    session['from_url'] = request.url


@main.route('/')
@cache.cached(timeout=300, key_prefix='index_page')
def index():
    posts_pagination = post.get_paginate_posts(page_num=1)
    return render_template('index.html', pagination=posts_pagination, top_title='All Posts')


@main.route('/paginate/<page_num>')
def paginate(page_num):
    posts_pagination = post.get_paginate_posts(page_num=int(page_num))
    return render_template('index.html', pagination=posts_pagination, top_title='All Posts')
