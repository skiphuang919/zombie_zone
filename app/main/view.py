from flask import render_template, flash, redirect, url_for, current_app, session
from . import main
from .form import OrderForm, PartyForm
from ..lib import users


@main.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')


@main.route('/add_party', methods=['GET', 'POST'])
def add_party():
    form = PartyForm()
    if form.is_submitted():
        if form.validate():
            # DO SOMETHING HERE
            return redirect(url_for('main.add_party_success'))
        else:
            form_error = form.errors.items()[0]
            f_error = form_error[1][0]
            flash(f_error)
    return render_template('party.html', form=form)


@main.route('/add_party_success')
def add_party_success():
    return render_template('success.html',
                           success_title='Success',
                           success_detail='You have create a party successfully.')
