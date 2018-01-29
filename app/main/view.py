from flask import render_template, session, url_for, request
from . import main
from ..lib import post
from .. import cache


@main.route('/')
@cache.cached(timeout=300, key_prefix='index')
def index():
    posts_pagination = post.get_paginate_posts(page_num=1)
    session['from_url'] = request.url
    return render_template('index.html', pagination=posts_pagination, top_title='All Posts')


@main.route('/paginate/<page_num>')
def paginate(page_num):
    posts_pagination = post.get_paginate_posts(page_num=int(page_num))
    session['from_url'] = request.url
    return render_template('index.html', pagination=posts_pagination, top_title='All Posts')
