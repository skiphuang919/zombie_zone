from flask import render_template, flash, redirect, url_for, request, jsonify
from . import main
from .form import PartyForm
from ..lib import party, tools
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
    party_list = party.get_parties(limit=10)
    party_info_list = [{'party': party_obj, 'joined_count': len(party_obj.participators)}
                       for party_obj in party_list]
    return render_template('index.html', party_info_list=party_info_list)


@main.route('/add_party', methods=['GET', 'POST'])
@login_required
@confirmed_required
def add_party():
    form = PartyForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            try:
                party.add_party(subject=form.subject.data,
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
    party_obj = party.get_party_by_id(party_id=party_id)
    if not party_obj:
        flash('Party not exist.', category='warn')
        return redirect(url_for('main.index'))

    participators = ', '.join([p.name for p in party_obj.participators])
    return render_template('party_detail.html', party=party_obj,
                           joined_count=len(party_obj.participators), joined=current_user.has_joined(party_obj),
                           participators=participators)


@main.route('/_join_or_quit')
@login_required
@confirmed_required
def ajax_join_or_quit():
    result = {'status': -1, 'msg': 'failed', 'data': ''}
    party_id = request.args.get('party_id')
    action_type = request.args.get('action_type')
    if party_id and (action_type in ('join', 'quit')):
        party_obj = party.get_party_by_id(party_id)
        if party_obj:
            try:
                if action_type == 'join':
                    if party_obj.is_full:
                        result['msg'] = 'participators is full'
                        return jsonify(result)
                    current_user.join(party_obj)
                else:
                    current_user.quit(party_obj)
                participators = [p.name for p in party_obj.participators]
                result['status'] = 0
                result['msg'] = 'success'
                result['data'] = {'joined_count': len(participators),
                                  'participators': ', '.join(participators)}
            except Exception as ex:
                print str(ex)
    return jsonify(result)


@main.route('/_get_parties')
@login_required
def ajax_get_parties():
    result = {'status': -1, 'msg': 'failed', 'data': ''}
    _type = request.args.get('_type')
    if _type in ('all', 'created', 'joined'):
        try:
            party_list = party.get_parties(_type=_type)
            if party_list:
                result['data'] = [tools.obj2dic(p) for p in party_list]
            result['status'] = 0
            result['msg'] = 'success'
        except Exception as ex:
            print str(ex)
    return jsonify(result)


@main.route('/party_guys/<party_id>')
@login_required
@confirmed_required
def party_guys(party_id):
    party_obj = party.get_party_by_id(party_id=party_id)
    if not current_user.has_joined(party_obj):
        flash('Access failed for passerby.', category='message')
        return redirect(url_for('main.party_detail', party_id=party_id))
    return render_template('participators.html', participators=party_obj.participators, party_id=party_id)



