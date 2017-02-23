from flask import redirect, url_for, request, session, jsonify, current_app, render_template
from ..lib.wc_lib import WeChat
from . import auth
from .form import UserForm


#@auth.before_app_request
def before_request():
    if request.endpoint != 'auth.wc_oauth2':
        if session.get('openid') is None:
            session['redirect_url_endpoint'] = request.endpoint
            we_chat = WeChat(current_app.config.get('APP_ID'), current_app.config.get('APP_SECRET'))
            oauth2_url = we_chat.get_oauth2_url(redirect_url=url_for('auth.wc_oauth2', _external=True))
            return redirect(oauth2_url)


@auth.route('/wc_oauth2', methods=['GET', 'POST'])
def wc_oauth2():
    code = request.args.get('code', None)
    if code is not None:
        we_chat = WeChat(current_app.config.get('APP_ID'), current_app.config.get('APP_SECRET'))
        token_info = we_chat.get_web_access_token_by_code(code)
        openid = token_info.get('openid', None)
        if openid:
            session['openid'] = openid
            url_endpoint = session.get('redirect_url_endpoint', 'index')
            return redirect(url_for(url_endpoint))
    return jsonify({'msg': 'Authorization failed, please try again.'})


@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = UserForm()
    return render_template('register.html', form=form)
