import traceback
from flask import render_template, flash, redirect, url_for, request, jsonify, current_app, abort, session
from . import posts
from .form import PostForm
from ..lib import users, post
from flask_login import current_user, login_required
from ..wrap import confirmed_required


@posts.route('/write_post', methods=['GET', 'POST'])
@login_required
@confirmed_required
def write_post():
    form = PostForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            try:
                post.write_blog(title=form.title.data,
                                content=form.body.data,
                                author=current_user._get_current_object())
            except:
                flash('Create post failed.', category='warn')
                current_app.logger.error(traceback.format_exc())
            else:
                flash('Create post successfully', category='info')
                return redirect(url_for('posts.all_posts'))
        else:
            warn_msg = form.get_one_err_msg()
            flash(warn_msg, category='warn')
    return render_template('posts/add_post.html', form=form,
                           top_title='Write post', back_url=url_for('posts.all_posts'))


@posts.route('/edit_post/<post_id>', methods=['GET', 'POST'])
@login_required
@confirmed_required
def edit_post(post_id):
    my_post = post.get_post_by_id(post_id)
    if not my_post:
        abort(404)

    form = PostForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            try:
                post.update_post(post_id=post_id,
                                 title=form.title.data,
                                 body=form.body.data)
            except:
                flash('update post failed', category='warn')
                current_app.logger.error(traceback.format_exc())
            else:
                flash('update post successfully', category='info')
                return redirect(url_for('posts.my_posts'))
        else:
            warn_msg = form.get_one_err_msg()
            flash(warn_msg, category='warn')
    else:
        form.title.data = my_post.title
        form.body.data = my_post.body
    return render_template('posts/add_post.html', form=form, top_title='Edit post', back_url=url_for('posts.my_posts'))


@posts.route('/all_posts')
def all_posts():
    a_posts = post.get_posts()
    session['from_endpoint'] = 'posts.all_posts'
    return render_template('posts/all_posts.html', posts=a_posts, top_title='All Posts')


@posts.route('/my_posts')
@login_required
@confirmed_required
def my_posts():
    c_posts = users.get_current_user_post()
    session['from_endpoint'] = 'posts.my_posts'
    return render_template('posts/my_posts.html', posts=c_posts, top_title='My posts')


@posts.route('/post_detail/<post_id>')
@login_required
@confirmed_required
def post_detail(post_id):
    post_obj = post.get_post_by_id(post_id)
    if not post_obj:
        abort(404)
    back_endpoint = session.get('from_endpoint', 'posts.all_posts')
    return render_template('posts/post_detail.html',
                           post=post_obj,
                           top_title='Post Detail',
                           back_endpoint=back_endpoint)


@posts.route('/_del_post', methods=['POST'])
@login_required
@confirmed_required
def ajax_delete_post():
    result = {'status': -1, 'msg': 'failed', 'data': ''}
    post_id = request.form.get('post_id')
    if post_id:
        try:
            post.del_post(post_id)
        except:
            current_app.logger.error(traceback.format_exc())
        else:
            result['status'] = 0
            result['msg'] = 'success'
    return jsonify(result)
