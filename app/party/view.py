import traceback
from flask import render_template, flash, redirect, url_for, request, jsonify, current_app, abort, session
from . import party_blueprint
from .form import PartyForm
from ..lib import party, tools, users
from flask_login import current_user
from ..wrap import permission_required
from ..model import Permission


@party_blueprint.route('/')
@permission_required(Permission.CONFIRMED)
def party_list():
    all_party_list = party.get_parties()
    session['from_endpoint'] = 'party_list'
    return render_template('party/party_list.html', party_info_list=all_party_list, top_title='All Parties')


@party_blueprint.route('/add_party', methods=['GET', 'POST'])
@permission_required(Permission.CONFIRMED)
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
                current_app.logger.error(traceback.format_exc())
                flash('Create party failed.', category='warn')
            else:
                flash('Create party successfully', category='info')
                return redirect(url_for('party.party_list'))
        else:
            warn_msg = form.get_one_err_msg()
            flash(warn_msg, category='warn')
    return render_template('party/party.html', form=form,
                           top_title='Create Party', back_url=url_for('party.party_list'))


@party_blueprint.route('/party_detail/<party_id>')
@permission_required(Permission.CONFIRMED)
def party_detail(party_id):
    party_obj = party.get_party_by_id(party_id=party_id)
    if not party_obj:
        abort(404)
    participators = [p.name for p in party.get_participators(party_obj.party_id)]
    party_detail_info = tools.obj2dic(party_obj)
    party_detail_info.update(dict(host=party_obj.host.name,
                                  joined=current_user.has_joined(party_obj),
                                  participators=participators))
    from_endpoint = session.get('from_endpoint', 'party_list')

    if from_endpoint == 'created_party':
        back_url = url_for('party.get_parties', _type='created')
    elif from_endpoint == 'joined_party':
        back_url = url_for('party.get_parties', _type='joined')
    else:
        back_url = url_for('party.party_list')

    return render_template('party/party_detail.html', party=party_detail_info,
                           back_url=back_url, top_title='Party Detail')


@party_blueprint.route('/_join_or_quit')
@permission_required(Permission.CONFIRMED)
def ajax_join_or_quit():
    result = {'status': -1, 'msg': 'failed', 'data': ''}
    party_id = request.args.get('party_id')
    action_type = request.args.get('action_type')
    if party_id and (action_type in ('join', 'quit')):
        party_obj = party.get_party_by_id(party_id)
        if not party_obj:
            abort(404)
        try:
            if action_type == 'join':
                if party_obj.is_full:
                    result['msg'] = 'Participators is full'
                    return jsonify(result)
                if party_obj.host_id == current_user.user_id:
                    result['msg'] = "Host needn't join"
                    return jsonify(result)
                current_user.join(party_obj)
            else:
                current_user.quit(party_obj)
            participators = [p.name for p in party.get_participators(party_id)]
            result['status'] = 0
            result['msg'] = 'success'
            result['data'] = {'joined_count': len(participators),
                              'participators': ', '.join(participators)}
        except:
            current_app.logger.error(traceback.format_exc())
    return jsonify(result)


@party_blueprint.route('/_get_party_guys')
@permission_required(Permission.CONFIRMED)
def ajax_get_party_guys():
    result = {'status': -1, 'msg': 'failed', 'data': ''}
    party_id = request.args.get('party_id')
    if party_id:
        try:
            party_obj = party.get_party_by_id(party_id=party_id)
            if party_obj:
                if not current_user.has_joined(party_obj) and party_obj.host_id != current_user.user_id:
                    result['status'] = 1
                    result['msg'] = 'Access failed for passerby'
                else:
                    participators = party.get_participators(party_id)
                    result['status'] = 0
                    result['msg'] = 'success'
                    result['data'] = [tools.obj2dic(p) for p in participators]
            else:
                current_app.logger.debug('party not exist.')
        except:
            current_app.logger.error(traceback.format_exc())
    return jsonify(result)


@party_blueprint.route('/get_parties/<_type>')
@permission_required(Permission.CONFIRMED)
def get_parties(_type):
    if _type == 'created':
        c_party_list = users.get_created_parties(current_user.user_id)
        session['from_endpoint'] = 'created_party'
        return render_template('party/party_created.html', party_list=c_party_list, top_title='Created Parties')
    elif _type == 'joined':
        j_party_list = users.get_joined_parties(current_user.user_id)
        session['from_endpoint'] = 'created_party'
        return render_template('party/party_joined.html', party_list=j_party_list, top_title='Joined Parties')
    else:
        return redirect(url_for('party.party_list'))


@party_blueprint.route('/_del_party', methods=['POST'])
@permission_required(Permission.CONFIRMED)
def ajax_delete_party():
    result = {'status': -1, 'msg': 'failed', 'data': ''}
    party_id = request.form.get('party_id')
    try:
        party.delete_party(party_id)
    except:
        current_app.logger.error(traceback.format_exc())
    else:
        result['status'] = 0
        result['msg'] = 'success'
    return jsonify(result)
