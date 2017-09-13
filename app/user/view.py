import traceback
from . import user
from flask import render_template, abort, request, current_app, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from ..wrap import confirmed_required
from ..lib import users
from .form import ChangePwdForm


@user.route('/my_zone')
@login_required
@confirmed_required
def my_zone():
    return render_template('user/my_zone.html',
                           joined_c=users.get_joined_parties(current_user.user_id, get_count=True),
                           created_c=users.get_created_parties(current_user.user_id, get_count=True),
                           blog_c=users.get_current_user_post(get_count=True),
                           top_title='My Zone')


@user.route('/user_info')
@login_required
@confirmed_required
def user_info():
    return render_template('user/user_info.html', top_title='Profile')


@user.route('/user_settings')
@login_required
@confirmed_required
def user_settings():
    return render_template('user/user_settings.html', top_title='Settings')


@user.route('/edit_profile/<item>')
@login_required
@confirmed_required
def edit_profile(item):
    if item not in ('name', 'gender', 'city', 'slogan'):
        abort(404)
    return render_template('user/edit_profile.html', item=item,
                           value=getattr(current_user, item) or '', top_title=item.capitalize())


@user.route('/_update_profile')
@login_required
@confirmed_required
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


@user.route('/update_password', methods=['GET', 'POST'])
@login_required
@confirmed_required
def update_password():
    form = ChangePwdForm()
    if request.method == 'POST':
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