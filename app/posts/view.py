import traceback
from flask import render_template, flash, redirect, url_for, request, jsonify, current_app, abort, session
from . import posts_blueprint
from .form import PostForm, CommentForm
from ..lib import users, post
from ..wrap import permission_required
from app.model import Permission
from ..lib.utils import Captcha


@posts_blueprint.route('/write_post', methods=['GET', 'POST'])
@permission_required(Permission.CONFIRMED)
def write_post():
    form = PostForm()
    if form.is_submitted():
        if form.validate_on_submit():
            try:
                post.write_blog(title=form.title.data,
                                content=form.body.data)
            except:
                current_app.logger.error(traceback.format_exc())
            else:
                flash('Create post successfully', category='info')
                return redirect(url_for('posts.my_posts'))

        warn_msg = form.get_one_err_msg() or 'Create post failed.'
        flash(warn_msg, category='warn')

    return render_template('posts/add_post.html', form=form,
                           top_title='Write post', back_url=url_for('main.index'))


@posts_blueprint.route('/edit_post/<post_id>', methods=['GET', 'POST'])
@permission_required(Permission.CONFIRMED)
def edit_post(post_id):
    my_post = post.get_post_by_id(post_id)

    form = PostForm()
    if form.is_submitted():
        if form.validate_on_submit():
            try:
                post.update_post(post_id=post_id,
                                 title=form.title.data,
                                 body=form.body.data)
            except:
                current_app.logger.error(traceback.format_exc())
            else:
                flash('update post successfully', category='info')
                return redirect(url_for('posts.my_posts'))

        warn_msg = form.get_one_err_msg() or 'update post failed'
        flash(warn_msg, category='warn')
    else:
        form.title.data = my_post.title
        form.body.data = my_post.body
    return render_template('posts/add_post.html', form=form, top_title='Edit post', back_url=url_for('posts.my_posts'))


@posts_blueprint.route('/my_posts')
@permission_required(Permission.CONFIRMED)
def my_posts():
    c_posts = users.get_current_user_post()
    session['from_endpoint'] = 'posts.my_posts'
    return render_template('posts/my_posts.html', posts=c_posts, top_title='My posts')


@posts_blueprint.route('/post_detail/<post_id>', methods=['GET', 'POST'])
def post_detail(post_id):
    post_obj = post.get_post_by_id(post_id)
    back_endpoint = session.get('from_endpoint', 'main.index')

    comment_form = CommentForm()
    if comment_form.is_submitted():
        if comment_form.validate_on_submit():
            try:
                post.add_comment(post_id=post_id,
                                 content=comment_form.body.data)
            except:
                current_app.logger.error(traceback.format_exc())
            else:
                flash('comment successfully', category='info')
                return redirect(url_for('posts.post_detail', post_id=post_id))
        warn_msg = comment_form.get_one_err_msg() or 'commit comment failed.'
        flash(warn_msg, category='warn')

    captcha = Captcha()
    captcha_stm = captcha.generate_captcha_stream()
    return render_template('posts/post_detail.html',
                           post=post_obj,
                           form=comment_form,
                           top_title='Post Detail',
                           captcha_stm=captcha_stm,
                           back_endpoint=back_endpoint)


@posts_blueprint.route('/_del_post', methods=['POST'])
@permission_required(Permission.CONFIRMED)
def ajax_delete_post():
    result = {'status': -1, 'msg': 'failed', 'data': ''}
    post_id = request.form.get('post_id')
    try:
        post.del_post(post_id)
    except:
        current_app.logger.error(traceback.format_exc())
    else:
        result['status'] = 0
        result['msg'] = 'success'
    return jsonify(result)
