import traceback
from . import user_blueprint
from flask import render_template, abort, request, current_app, jsonify, flash, redirect, url_for
from flask_login import current_user
from ..wrap import permission_required
from ..lib import users
from .form import ChangePwdForm
from app.model import Permission


@user_blueprint.route('/my_zone')
@permission_required(Permission.LOGIN)
def my_zone():
    return render_template('user/my_zone.html',
                           joined_c=users.get_joined_parties(current_user.user_id, get_count=True),
                           created_c=users.get_created_parties(current_user.user_id, get_count=True),
                           blog_c=users.get_current_user_post(get_count=True),
                           top_title='My Zone')


@user_blueprint.route('/user_info')
@permission_required(Permission.CONFIRMED)
def user_info():
    return render_template('user/user_info.html', top_title='Profile')


@user_blueprint.route('/edit_profile/<item>')
@permission_required(Permission.CONFIRMED)
def edit_profile(item):
    if item not in ('name', 'gender', 'city', 'slogan'):
        abort(404)
    return render_template('user/edit_profile.html', item=item,
                           value=getattr(current_user, item) or '', top_title=item.capitalize())


@user_blueprint.route('/_update_profile')
@permission_required(Permission.CONFIRMED)
def ajax_update_profile():
    result = {'status': -1, 'msg': 'failed', 'data': ''}
    item = request.args.get('item')
    value = request.args.get('value')
    if item in ('name', 'gender', 'city', 'slogan') and value:
        try:
            users.update_user_profile(user_id=current_user.user_id,
                                      profile_dic={item: value})
            result['status'] = 0
            result['msg'] = 'success'
        except:
            current_app.logger.error(traceback.format_exc())
    return jsonify(result)


@user_blueprint.route('/update_password', methods=['GET', 'POST'])
@permission_required(Permission.CONFIRMED)
def update_password():
    form = ChangePwdForm()
    if form.is_submitted():
        if form.validate_on_submit():
            try:
                users.change_pwd(form.new_password.data)
            except Exception as ex:
                current_app.logger.error('change_password failed: {}'.format(ex))
                warn_msg = 'update password failed.'
            else:
                flash('update password successfully.', category='info')
                return redirect(url_for('main.index'))
        else:
            warn_msg = form.get_one_err_msg()
        flash(warn_msg, category='warn')
    return render_template('user/update_pwd.html', form=form)


@user_blueprint.route('/admin_zone')
@permission_required(Permission.ADMINISTRATOR)
def admin_zone():
    return render_template('user/admin_zone.html', top_title='Admin Zone')


@user_blueprint.route('/user_list')
@permission_required(Permission.ADMINISTRATOR)
def user_list():
    page = request.args.get('page', 1, type=int)
    users_pagination = users.get_paginate_users(page_num=page)
    return render_template('user/user_list.html', pagination=users_pagination, top_title='All users')


