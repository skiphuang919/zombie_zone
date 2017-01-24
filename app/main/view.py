from flask import render_template, request
from . import main
from .form import OrderForm


@main.route('/', methods=['GET', 'POST'])
def index():
    form = OrderForm()
    if form.validate_on_submit():
        return 'ok'
    return render_template('index.html', form=form)
