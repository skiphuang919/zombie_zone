from functools import wraps
from flask_login import current_user, login_required
from flask import flash, redirect, url_for, abort
from app.model import Permission


def permission_required(permission):
    if permission == Permission.LOGIN:
        return login_required

    def decorator(func):
        @wraps(func)
        def inner(*args, **kwargs):
            if permission == Permission.CONFIRMED:
                if not current_user.is_authenticated:
                    flash('Please login to access this page.', category='message')
                    return redirect(url_for('auth.login'))
                if not current_user.confirmed:
                    flash('You have not confirmed your email.', category='message')
                    return redirect(url_for('main.index'))
            elif permission == Permission.ADMINISTRATOR:
                if current_user.is_anonymous or not current_user.is_administrator:
                    abort(403)
            return func(*args, **kwargs)
        return inner
    return decorator
