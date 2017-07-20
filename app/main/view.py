import traceback
from flask import render_template, flash, redirect, url_for, request, jsonify, current_app, abort, session
from . import main
from .form import PartyForm, PostForm
from ..lib import party, tools, users, post
from flask_login import current_user, login_required
from ..wrap import confirmed_required


@main.route('/')
def index():
    party_list = party.get_parties(limit=10)
    session['from_endpoint'] = 'index'
    return render_template('index.html', party_info_list=party_list, top_title='All Parties')


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
                flash('Create party successfully', category='info')
                return redirect(url_for('main.index'))
        else:
            form_error = form.errors.items()[0]
            warn_msg = form_error[1][0]
            flash(warn_msg, category='warn')
    return render_template('party.html', form=form, top_title='Create Party', back_url=url_for('main.index'))


@main.route('/party_detail/<party_id>')
@login_required
@confirmed_required
def party_detail(party_id):
    party_obj = party.get_party_by_id(party_id=party_id)
    if not party_obj:
        abort(404)
    participators = [p.name for p in party.get_participators(party_obj.party_id)]
    party_detail_info = tools.obj2dic(party_obj)
    party_detail_info.update(dict(host=party_obj.host.name,
                                  create_time=party_obj.local_create_time,
                                  joined=current_user.has_joined(party_obj),
                                  participators=participators))
    from_endpoint = session.get('from_endpoint', 'index')

    if from_endpoint == 'created_party':
        back_url = url_for('main.get_parties', _type='created')
    elif from_endpoint == 'joined_party':
        back_url = url_for('main.get_parties', _type='joined')
    else:
        back_url = url_for('main.index')

    return render_template('party_detail.html', party=party_detail_info, back_url=back_url, top_title='Party Detail')


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


@main.route('/_get_party_guys')
@login_required
@confirmed_required
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


@main.route('/my_zone')
@login_required
@confirmed_required
def my_zone():
    return render_template('my_zone.html',
                           joined_c=users.get_joined_parties(current_user.user_id, get_count=True),
                           created_c=users.get_created_parties(current_user.user_id, get_count=True),
                           blog_c=users.get_current_user_post(get_count=True),
                           top_title='My Zone')


@main.route('/user_info')
@login_required
@confirmed_required
def user_info():
    return render_template('user_info.html', top_title='Profile')


@main.route('/edit_profile/<item>')
@login_required
@confirmed_required
def edit_profile(item):
    if item not in ('name', 'gender', 'city', 'slogan'):
        abort(404)
    return render_template('edit_profile.html', item=item,
                           value=getattr(current_user, item), top_title=item.capitalize())


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
        top_title = 'Created Parties'
        session['from_endpoint'] = 'created_party'
    elif _type == 'joined':
        party_list = users.get_joined_parties(current_user.user_id)
        render_temp = 'party_joined.html'
        top_title = 'Joined Parties'
        session['from_endpoint'] = 'created_party'
    else:
        return redirect(url_for('main.index'))
    return render_template(render_temp, party_list=party_list, top_title=top_title)


@main.route('/_del_party', methods=['POST'])
@login_required
@confirmed_required
def ajax_delete_party():
    result = {'status': -1, 'msg': 'failed', 'data': ''}
    party_id = request.form.get('party_id')
    if party_id:
        try:
            party.delete_party(party_id)
        except:
            current_app.logger.error(traceback.format_exc())
        else:
            result['status'] = 0
            result['msg'] = 'success'
    return jsonify(result)


@main.route('/write_post', methods=['GET', 'POST'])
@login_required
@confirmed_required
def write_post():
    form = PostForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            try:
                p_obj = post.write_blog(title=form.title.data,
                                        content=form.body.data,
                                        author=current_user._get_current_object())
            except:
                flash('Create post failed.', category='warn')
                current_app.logger.error(traceback.format_exc())
            else:
                flash('Create post successfully', category='info')
                return redirect(url_for('main.all_posts'))
        else:
            form_error = form.errors.items()[0]
            warn_msg = form_error[1][0]
            flash(warn_msg, category='warn')
    return render_template('add_post.html', form=form, top_title='Write post', back_url=url_for('main.all_posts'))


@main.route('/edit_post/<post_id>', methods=['GET', 'POST'])
@login_required
@confirmed_required
def edit_post(post_id):
    my_post = post.get_post_by_id(post_id)
    if not my_post:
        abort(404)

    form = PostForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            try:
                post.update_post(post_id=post_id,
                                 title=form.title.data,
                                 body=form.body.data)
            except:
                flash('update post failed', category='warn')
                current_app.logger.error(traceback.format_exc())
            else:
                flash('update post successfully', category='info')
                return redirect(url_for('main.my_posts'))
        else:
            form_error = form.errors.items()[0]
            warn_msg = form_error[1][0]
            flash(warn_msg, category='warn')
    else:
        form.title.data = my_post.title
        form.body.data = my_post.body
    return render_template('add_post.html', form=form, top_title='Edit post', back_url=url_for('main.my_posts'))


@main.route('/all_posts')
def all_posts():
    posts = post.get_posts()
    session['from_endpoint'] = 'main.all_posts'
    return render_template('all_posts.html', posts=posts, top_title='All Posts')


@main.route('/my_posts')
@login_required
@confirmed_required
def my_posts():
    posts = users.get_current_user_post()
    session['from_endpoint'] = 'main.my_posts'
    return render_template('my_posts.html', posts=posts, top_title='My posts')


@main.route('/post_detail/<post_id>')
@login_required
@confirmed_required
def post_detail(post_id):
    post_obj = post.get_post_by_id(post_id)
    if not post_obj:
        abort(404)
    back_endpoint = session.get('from_endpoint', 'main.all_posts')
    return render_template('post_detail.html',
                           post=post_obj,
                           top_title='Post Detail',
                           back_endpoint=back_endpoint)


@main.route('/_del_post', methods=['POST'])
@login_required
@confirmed_required
def ajax_delete_post():
    result = {'status': -1, 'msg': 'failed', 'data': ''}
    post_id = request.form.get('post_id')
    if post_id:
        try:
            post.del_post(post_id)
        except:
            current_app.logger.error(traceback.format_exc())
        else:
            result['status'] = 0
            result['msg'] = 'success'
    return jsonify(result)
