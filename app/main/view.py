from flask import render_template, flash
from . import main
from .form import OrderForm


@main.route('/', methods=['GET', 'POST'])
def index():
    form = OrderForm()
    if form.is_submitted():
        if form.validate():
            return 'ok'
        else:
            form_error = form.errors.items()[0]
            f_error = form_error[1][0]
            flash(f_error)
    return render_template('index.html', form=form)
