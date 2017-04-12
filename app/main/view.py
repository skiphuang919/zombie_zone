from flask import render_template, flash, redirect, url_for
from . import main
from .form import PartyForm
from ..lib import parties
from flask_login import current_user, login_required


@main.route('/', methods=['GET', 'POST'])
def index():
    party_list = parties.get_all_parties()
    party_info_list = [{'party': party, 'joined_count': len(party.users.all())}
                       for party in party_list]
    return render_template('index.html', party_info_list=party_info_list)


@main.route('/add_party', methods=['GET', 'POST'])
@login_required
def add_party():
    form = PartyForm()
    if form.is_submitted():
        if form.validate():
            if not current_user.confirmed:
                flash('You have not confirmed your email.', category='message')
                return redirect(url_for('main.index'))
            try:
                parties.add_party(subject=form.subject.data,
                                  party_time=form.party_time.data,
                                  address=form.address.data,
                                  host_id=current_user.user_id,
                                  required_count=form.required_count.data,
                                  note=form.note.data)
            except Exception as ex:
                print str(ex)
                flash('Create party failed.', category='warn')
            else:
                flash('Create party success', category='info')
                return redirect(url_for('main.index'))
        else:
            form_error = form.errors.items()[0]
            warn_msg = form_error[1][0]
            flash(warn_msg, category='warn')
    return render_template('party.html', form=form)

