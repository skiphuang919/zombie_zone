from functools import wraps
from flask_login import current_user
from flask import flash, redirect, url_for, abort
from app.model import Permission


def confirmed_required(func):
    @wraps(func)
    def inner(*args, **kwargs):
        if not current_user.confirmed:
            flash('You have not confirmed your email.', category='message')
            return redirect(url_for('main.index'))
        return func(*args, **kwargs)
    return inner


def permission_required(permission):
    def decorator(func):
        @wraps(func)
        def inner(*args, **kwargs):
            if permission == Permission.CONFIRMED:
                if not current_user.confirmed:
                    flash('You have not confirmed your email.', category='message')
                    return redirect(url_for('main.index'))
            elif permission == Permission.ADMINISTRATOR:
                if not current_user.is_administrator():
                    abort(403)
            return func(*args, **kwargs)
        return inner
    return decorator
