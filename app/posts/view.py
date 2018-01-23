import traceback
from flask import render_template, flash, redirect, url_for, request, \
    jsonify, current_app, session
from flask_login import current_user
from . import posts_blueprint
from .form import PostForm, CommentForm
from ..lib import users, post
from ..wrap import permission_required
from app.model import Permission
from ..lib.utils import Captcha
from .. import cache


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
            if current_user.is_anonymous:
                flash('Login first', category='message')
                return redirect(url_for('posts.post_detail', post_id=post_id))

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

    comment_form.captcha.data = ''
    captcha = Captcha()
    captcha_stm = captcha.generate_captcha_stream()
    return render_template('posts/post_detail.html',
                           post=post_obj,
                           cmt_count=post_obj.comments.count(),
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
    finally:
        # expire the index cache
        cache.delete('index')
    return jsonify(result)


@posts_blueprint.route('/_set_post_status', methods=['POST'])
@permission_required(Permission.CONFIRMED)
def ajax_set_post_status():
    result = {'status': -1, 'msg': 'failed', 'data': ''}
    post_id = request.form.get('post_id')
    des_status = request.form.get('des_status')
    try:
        post.update_post(post_id, status=int(des_status))
    except:
        current_app.logger.error(traceback.format_exc())
    else:
        result['status'] = 0
        result['msg'] = 'success'
    finally:
        # expire the index cache
        cache.delete('index')
    return jsonify(result)


@posts_blueprint.route('/_get_post_cmt')
def get_post_cmt():
    result = {'status': -1, 'msg': 'failed', 'data': ''}
    post_id = request.args.get('post_id')
    page = request.args.get('page', 1)
    try:
        page = int(page)
        cmt_pagination = post.get_paginate_cmt(post_id=post_id, page_num=page)

        paginate_info = dict()
        paginate_info['has_prev'] = cmt_pagination.has_prev
        paginate_info['has_next'] = cmt_pagination.has_next
        paginate_info['prev_num'] = cmt_pagination.prev_num
        paginate_info['next_num'] = cmt_pagination.next_num
        paginate_info['pages'] = cmt_pagination.pages
        paginate_info['total'] = cmt_pagination.total

        cmt_list = [{'comment_id': item.comment_id,
                     'status': item.disabled,
                     'author': item.author.name,
                     'body_html': item.body_html,
                     'head_img_url': item.author.head_img_url,
                     'timestamp': item.timestamp} for item in cmt_pagination.items]
        result['data'] = {
            'paginate_info': paginate_info,
            'cmt_list': cmt_list
        }
    except:
        current_app.logger.error(traceback.format_exc())
    else:
        result['status'] = 0
        result['msg'] = 'success'
    return jsonify(result)


@posts_blueprint.route('/_modify_comment_status')
@permission_required(Permission.ADMINISTRATOR)
def modify_comment_status():
    result = {'status': -1, 'msg': 'failed', 'data': ''}
    comment_id = request.args.get('comment_id')
    status = request.args.get('status')

    if not comment_id:
        result['msg'] = 'missing comment_id'
        return result
    if status not in ('disabled', 'enabled'):
        result['msg'] = 'invalid status'
        return result

    try:
        comment_obj = post.update_comment_status(comment_id, status)
    except:
        current_app.logger.error(traceback.format_exc())
    else:
        result['status'] = 0
        result['msg'] = 'success'
        result['data'] = {'status': comment_obj.disabled}
    return jsonify(result)


@posts_blueprint.route('/_search_by_title')
@cache.cached(timeout=300)
def search_by_title():
    result = {'status': -1, 'msg': 'failed', 'data': ''}
    title_key = request.args.get('title_key')
    if not title_key:
        result['msg'] = 'missing title_key value'
        return result

    try:
        result['data'] = [{'title': item[1], 'url': url_for('posts.post_detail', post_id=item[0])}
                          for item in post.search_title(title_key)]
        result['msg'] = 'success'
        result['status'] = 0
    except:
        current_app.logger.error(traceback.format_exc())
    return jsonify(result)

