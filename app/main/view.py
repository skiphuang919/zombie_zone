import traceback
from flask import render_template, flash, redirect, url_for, request, jsonify, current_app
from . import main
from .form import PartyForm
from ..lib import party, tools, users
from flask_login import current_user, login_required
from ..wrap import confirmed_required


@main.route('/')
def index():
    party_list = party.get_parties(limit=10)
    return render_template('index.html', party_info_list=party_list)


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
                current_app.logger.error(traceback.format_exc())
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
    participators = [p.name for p in party.get_participators(party_obj.party_id)]
    party_detail_info = tools.obj2dic(party_obj)
    party_detail_info.update(dict(host=party_obj.host.name,
                                  create_time=tools.utc2local(party_obj.create_time),
                                  joined=current_user.has_joined(party_obj),
                                  participators=participators))
    return render_template('party_detail.html', party=party_detail_info)


@main.route('/_join_or_quit')
@login_required
@confirmed_required
def ajax_join_or_quit():
    result = {'status': -1, 'msg': 'internal error', 'data': ''}
    party_id = request.args.get('party_id')
    action_type = request.args.get('action_type')
    if party_id and (action_type in ('join', 'quit')):
        party_obj = party.get_party_by_id(party_id)
        if party_obj:
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


@main.route('/_get_parties')
@login_required
def ajax_get_parties():
    result = {'status': -1, 'msg': 'failed', 'data': ''}
    _type = request.args.get('_type')
    if _type in ('all', 'created', 'joined'):
        try:
            if _type == 'all':
                party_list = party.get_parties()
            elif _type == 'joined':
                party_list = users.get_joined_parties(current_user.user_id)
            else:
                party_list = users.get_created_parties(current_user.user_id)
            if party_list:
                result['data'] = [tools.obj2dic(p) for p in party_list]
            result['status'] = 0
            result['msg'] = 'success'
        except:
            current_app.logger.error(traceback.format_exc())
    return jsonify(result)


@main.route('/party_guys/<party_id>')
@login_required
@confirmed_required
def party_guys(party_id):
    party_obj = party.get_party_by_id(party_id=party_id)
    if not current_user.has_joined(party_obj) and party_obj.host_id != current_user.user_id:
        flash('Access failed for passerby.', category='message')
        return redirect(url_for('main.party_detail', party_id=party_id))
    return render_template('participators.html', participators=party.get_participators(party_id), party_id=party_id)


@main.route('/my_zone')
@login_required
@confirmed_required
def my_zone():
    return render_template('my_zone.html',
                           joined_c=users.get_joined_parties(current_user.user_id, get_count=True),
                           created_c=users.get_created_parties(current_user.user_id, get_count=True))


@main.route('/user_info')
@login_required
@confirmed_required
def user_info():
    return render_template('user_info.html')


@main.route('/edit_profile/<item>')
@login_required
@confirmed_required
def edit_profile(item):
    if item not in ('name', 'gender', 'city', 'slogan'):
        flash('invalid item', category='message')
        return redirect(url_for('main.user_info'))
    return render_template('edit_profile.html', item=item, value=getattr(current_user, item))


@main.route('/_update_profile')
@login_required
@confirmed_required
def ajax_update_profile():
    result = {'status': -1, 'msg': 'failed', 'data': ''}
    item = request.args.get('item')
    value = request.args.get('value')
    current_app.logger.error(request.args)
    if item in ('name', 'gender', 'city', 'slogan') and value:
        try:
            users.update_user_profile(user_id=current_user.user_id,
                                      profile_dic={item: value})
            result['status'] = 0
            result['msg'] = 'success'
        except:
            current_app.logger.error(traceback.format_exc())
    return jsonify(result)


@main.route('/get_parties/<_type>')
@login_required
@confirmed_required
def get_parties(_type):
    if _type == 'created':
        party_list = users.get_created_parties(current_user.user_id)
        render_temp = 'party_created.html'
    elif _type == 'joined':
        party_list = users.get_joined_parties(current_user.user_id)
        render_temp = 'party_joined.html'
    else:
        return redirect(url_for('main.index'))
    return render_template(render_temp, party_list=party_list)



