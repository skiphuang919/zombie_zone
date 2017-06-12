from functools import wraps
from flask_login import current_user
from flask import flash, redirect, url_for


def confirmed_required(func):
    @wraps(func)
    def inner(*args, **kwargs):
        if not current_user.confirmed:
            flash('You have not confirmed your email.', category='message')
            return redirect(url_for('main.index'))
        return func(*args, **kwargs)
    return inner
