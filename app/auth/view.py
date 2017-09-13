import traceback
from flask import redirect, url_for, current_app, render_template, flash, request, jsonify
from . import auth
from .form import RegisterForm, LoginForm, ChangePwdForm, PasswordResetRequestForm, PasswordResetForm
from ..lib import users
from ..lib.utils import Captcha
from ..email import send_confirm_mail, send_reset_pwd_mail
from flask_login import login_user, current_user, login_required, logout_user
from ..wrap import confirmed_required


@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            try:
                new_user = users.register_user(email=form.email.data,
                                               name=form.name.data,
                                               password=form.password.data)
                token = new_user.generate_confirm_token()
                send_confirm_mail(recipient=new_user.email,
                                  mail_info=dict(name=new_user.name,
                                                 confirm_url=url_for('auth.confirm', token=token, _external=True)))
            except:
                warn_msg = 'Register failed.'
                current_app.logger.error(traceback.format_exc())
            else:
                flash('A confirmation email has been sent to your mailbox.', category='message')
                return redirect(url_for('auth.login'))
        else:
            warn_msg = form.get_one_err_msg()
        flash(warn_msg, category='warn')
    form.captcha.data = ''

    # generate captcha img stream
    captcha = Captcha()
    captcha_stm = captcha.generate_captcha_stream()
    return render_template('auth/register.html', form=form, captcha_stm=captcha_stm)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            user = users.get_user(email=form.email.data)
            if user is not None and user.verify_password(form.password.data):
                login_user(user, form.remember_me.data)
                return redirect(request.args.get('next') or url_for('main.index'))
        warn_msg = form.get_one_err_msg() or 'invalid email or password'
        flash(warn_msg, category='warn')
    form.captcha.data = ''

    # generate captcha img stream
    captcha = Captcha()
    captcha_stm = captcha.generate_captcha_stream()
    return render_template('auth/login.html', form=form, captcha_stm=captcha_stm)


@auth.route('/logout')
@login_required
def logout():
    try:
        logout_user()
    except:
        current_app.logger.error(traceback.format_exc())
    else:
        flash('You have been logged out.', category='info')
        return redirect(url_for('auth.login'))


@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('main.index'))

    if current_user.verify_confirm_token(token):
        return render_template('success.html',
                               success_title='Success',
                               success_detail='Your email address has been confirmed successfully.')
    else:
        return render_template('warn.html',
                               warn_title='Failed',
                               warn_detail='The confirmation link is invalid or has expired.')


@auth.route('/resend_confirm')
@login_required
def resend_confirm():
    try:
        token = current_user.generate_confirm_token()
        send_confirm_mail(recipient=current_user.email,
                          mail_info=dict(name=current_user.name,
                                         confirm_url=url_for('auth.confirm', token=token, _external=True)))
    except:
        current_app.logger.error(traceback.format_exc())
        flash('resend confirmation email failed.', category='warn')
    else:
        flash('A new confirmation email has been sent to you by email.', category='message')
    return redirect(url_for('main.index'))


@auth.route('/_change_captcha')
def change_captcha():
    result = {'status': -1,
              'data': ''}
    try:
        new_captcha = Captcha()
        captcha_stm = new_captcha.generate_captcha_stream()
        result['data'] = captcha_stm
        result['status'] = 0
    except Exception as ex:
        current_app.logger.error('change_captcha exception: {}'.format(ex))
    return jsonify(result)


@auth.route('/update_password', methods=['GET', 'POST'])
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
    return render_template('auth/update_pwd.html', form=form)


@auth.route('/password_reset_request', methods=['GET', 'POST'])
def password_reset_request():
    form = PasswordResetRequestForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            user = users.get_user(email=form.email.data)
            if user:
                token = user.generate_reset_pwd_token()
                send_reset_pwd_mail(recipient=user.email,
                                    mail_info={'name': user.name,
                                               'reset_pwd_url': url_for('auth.reset_password',
                                                                        token=token,
                                                                        _external=True)})

                flash('An email to reset your password has been sent to you.', category='message')
                return redirect(url_for('auth.login'))
        warn_msg = form.get_one_err_msg() or 'invalid email'
        flash(warn_msg, category='warn')
    return render_template('auth/send_reset_pwd.html', form=form)


@auth.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    form = PasswordResetForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            user = users.get_user(email=form.email.data)
            if user and user.reset_pwd(token, form.password.data):
                flash('Your password has been updated.', category='info')
                return redirect(url_for('auth.login'))
        warn_msg = form.get_one_err_msg() or 'update password failed'
        flash(warn_msg, category='warn')
    return render_template('auth/reset_password.html', form=form)




