from flask import render_template, session, request
from . import main
from ..lib import post


@main.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    posts_pagination = post.get_paginate_posts(page_num=page)
    posts = posts_pagination.items
    session['from_endpoint'] = 'main.index'
    return render_template('index.html', posts=posts, pagination=posts_pagination, top_title='All Posts')
