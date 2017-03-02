from flask import render_template, flash, current_app, session
from . import main
from .form import OrderForm
from ..lib import user


@main.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')


@main.route('/order', methods=['GET', 'POST'])
def order():
    form = OrderForm()
    if form.is_submitted():
        if form.validate():
            # DO SOMETHING HERE
            return render_template('success.html')
        else:
            form_error = form.errors.items()[0]
            f_error = form_error[1][0]
            flash(f_error)
    return render_template('order.html', form=form)