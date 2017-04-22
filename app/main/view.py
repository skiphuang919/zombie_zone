from flask import render_template, flash, redirect, url_for, request, jsonify
from . import main
from .form import PartyForm
from ..lib import parties
from flask_login import current_user, login_required
from functools import wraps


def confirmed_required(func):
    @wraps(func)
    def inner(*args, **kwargs):
        if not current_user.confirmed:
            flash('You have not confirmed your email.', category='message')
            return redirect(url_for('main.index'))
        return func(*args, **kwargs)
    return inner


@main.route('/')
def index():
    party_list = parties.get_all_parties()
    party_info_list = [{'party': party, 'joined_count': len(party.participators)}
                       for party in party_list]
    return render_template('index.html', party_info_list=party_info_list)


@main.route('/add_party', methods=['GET', 'POST'])
@login_required
@confirmed_required
def add_party():
    form = PartyForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            try:
                parties.add_party(subject=form.subject.data,
                                  party_time=form.party_time.data,
                                  address=form.address.data,
                                  host_id=current_user.user_id,
                                  required_count=form.required_count.data,
                                  note=form.note.data)
            except:
                flash('Create party failed.', category='warn')
            else:
                flash('Create party success', category='info')
                return redirect(url_for('main.index'))
        else:
            form_error = form.errors.items()[0]
            warn_msg = form_error[1][0]
            flash(warn_msg, category='warn')
    return render_template('party.html', form=form)


@main.route('/party_detail/<party_id>')
@login_required
@confirmed_required
def party_detail(party_id):
    party = parties.get_party_by_id(party_id=party_id)
    if not party:
        flash('Party not exist.', category='warn')
        return redirect(url_for('main.index'))
    return render_template('party_detail.html', party=party,
                           joined_count=len(party.participators), joined=current_user.has_joined(party))


@main.route('/_join_or_quit')
def join_or_quit():
    result = {'status': -1, 'msg': 'failed'}
    party_id = request.args.get('party_id', None)
    action_type = request.args.get('action_type', None)
    if (party_id is None) or (action_type is None) or (action_type not in ('join', 'quit')):
        return jsonify(result)
    party = parties.get_party_by_id(party_id)
    if party:
        try:
            current_user.join(party) if action_type == 'join' \
                else current_user.quit(party)
        except Exception as ex:
            print str(ex)
        else:
            result['status'] = 0
            result['msg'] = 'success'
    return jsonify(result)

