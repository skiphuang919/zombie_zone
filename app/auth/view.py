import traceback
from flask import redirect, url_for, session, jsonify, \
    current_app, render_template, flash, request
from ..lib.wc_lib import WeChat
from . import auth
from .form import RegisterForm
from ..lib import users
from ..email import send_confirm_mail
from flask_login import login_user, current_user, login_required, logout_user


@auth.before_app_request
def before_request():
    """
    login the user by open id if it exist
    otherwise redirect to wechat oauth url
    """
    print session
    if current_user.is_anonymous and request.endpoint not in \
            ['auth.wc_oauth2', 'auth.confirm', 'static', 'auth.logout']:
        openid = session.get('openid')
        if openid is None:
            # get the openid process
            session['redirect_url_endpoint'] = request.endpoint
            we_chat = WeChat(current_app.config.get('APP_ID'), current_app.config.get('APP_SECRET'))
            oauth2_url = we_chat.get_oauth2_url(redirect_url=url_for('auth.wc_oauth2', _external=True))
            return redirect(oauth2_url)
        else:
            # login the user only if it has registered before
            user = users.get_user(open_id=openid)
            if user and user.cellphone and user.email:
                login_user(user)


@auth.route('/wc_oauth2', methods=['GET', 'POST'])
def wc_oauth2():
    """
    to be call back by wechat oauth with code
    then get open id by the code
    """
    code = request.args.get('code')
    if code is not None:
        try:
            we_chat = WeChat(current_app.config.get('APP_ID'), current_app.config.get('APP_SECRET'))
            token_info = we_chat.get_web_access_token_by_code(code)
            openid = token_info.get('openid')
            if openid:
                # get user info by openid
                access_token = we_chat.get_access_token()
                user_info = we_chat.get_wc_user_info(openid, access_token)

                user = users.update_user(open_id=openid,
                                         name=user_info.get('nickname', 'Curry'),
                                         gender=user_info.get('sex', 1),
                                         city=user_info.get('city', 'Shanghai'),
                                         head_img_url=user_info.get('headimgurl', '/static/img/head_test.jpeg'))
                session['openid'] = openid

                # login the user only if the user has registered, even got the openid
                if user.cellphone and user.email:
                    login_user(user)

                url_endpoint = session.get('redirect_url_endpoint', 'main.index')
                return redirect(url_for(url_endpoint))
        except:
            print traceback.format_exc()
    return jsonify({'msg': 'Authorization failed, please try again.'})


@auth.route('/register', methods=['GET', 'POST'])
def register():
    if not current_user.is_anonymous:
        flash('You have registered before.', category='message')
        return redirect(url_for('main.index'))
    form = RegisterForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            if users.is_email_exist(form.email.data):
                warn_msg = 'Email already exist.'
            elif users.is_cellphone_exist(form.cellphone.data):
                warn_msg = 'Cellphone already exist.'
            else:
                try:
                    open_id = session.get('openid')
                    new_user = users.update_user(open_id=open_id,
                                                 email=form.email.data,
                                                 cellphone=form.cellphone.data,
                                                 slogan=form.slogan.data)
                    token = new_user.generate_confirm_token()
                    send_confirm_mail(recipient=new_user.email,
                                      mail_info=dict(name=new_user.name,
                                                     confirm_url=url_for('auth.confirm', token=token, _external=True)))
                except:
                    warn_msg = 'Register failed.'
                else:
                    flash('A confirmation email has been sent to your mailbox.', category='message')
                    return redirect(url_for('main.index'))
        else:
            form_error = form.errors.items()[0]
            warn_msg = form_error[1][0]
        flash(warn_msg, category='warn')
    return render_template('register.html', form=form)


@auth.route('/confirm/<token>')
def confirm(token):
    if users.confirm(token):
        return render_template('success.html',
                               success_title='Success',
                               success_detail='Your email address has been confirmed successfully.')
    else:
        return render_template('warn.html',
                               warn_title='Failed',
                               warn_detail='The confirmation link is invalid or has expired.')


@auth.route('/resend_confirm')
@login_required
def resend_confirmation():
    try:
        token = current_user.generate_confirm_token()
        send_confirm_mail(recipient=current_user.email,
                          mail_info=dict(name=current_user.name,
                                         confirm_url=url_for('auth.confirm', token=token, _external=True)))
    except:
        return jsonify({'msg': 'resend confirmation email failed.'})
    else:
        flash('A new confirmation email has been sent to you by email.', category='message')
        return redirect(url_for('main.index'))


@auth.route('/logout')
@login_required
def logout():
    try:
        if 'openid' in session:
            session.pop('openid')
        logout_user()
    except:
        return jsonify({'msg': 'logout failed'})
    else:
        return jsonify({'msg': 'logout success'})
