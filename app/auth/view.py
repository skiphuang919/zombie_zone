import traceback
from flask import redirect, url_for, current_app, render_template, flash, request
from . import auth
from .form import RegisterForm, LoginForm
from ..lib import users
from ..email import send_confirm_mail
from flask_login import login_user, current_user, login_required, logout_user


@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            if users.is_email_exist(form.email.data):
                warn_msg = 'Email already exist.'
            elif users.is_name_exist(form.name.data):
                warn_msg = 'Name already exist.'
            else:
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
            form_error = form.errors.items()[0]
            warn_msg = form_error[1][0]
        flash(warn_msg, category='warn')
    return render_template('auth/register.html', form=form, top_title='Register')


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            user = users.get_user(email=form.email.data)
            if user is not None and user.verify_password(form.password.data):
                login_user(user, form.remember_me.data)
                return redirect(request.args.get('next') or url_for('main.index'))
            else:
                warn_msg = 'invalid email or password'
        else:
            form_error = form.errors.items()[0]
            warn_msg = form_error[1][0]
        flash(warn_msg, category='warn')
    return render_template('auth/login.html', form=form, top_title='Login')


@auth.route('/logout')
@login_required
def logout():
    try:
        logout_user()
    except:
        current_app.logger.error(traceback.format_exc())
    else:
        flash('You have been logged out.', category='info')
        return redirect(url_for('main.index'))


@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('main.index'))

    if current_user.confirm_token(token):
        return render_template('auth/success.html',
                               success_title='Success',
                               success_detail='Your email address has been confirmed successfully.')
    else:
        return render_template('auth/warn.html',
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
