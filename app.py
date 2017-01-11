from flask import Flask, redirect, url_for, request, session
from flask_script import Manager
from config import Config
from lib.wc_lib import WeChat

app = Flask(__name__)
app.config.from_object(Config)
manager = Manager(app)


@app.before_request
def before_request():
    if request.endpoint != 'sc_oauth2':
        if session.get('openid') is None:
            session['redirect_url_endpoint'] = request.endpoint
            we_chat = WeChat(app.config.get('APP_ID'), app.config.get('APP_SECRET'))
            oauth2_url = we_chat.get_oauth2_url(redirect_url=url_for('wc_oauth2', _external=True))
            return redirect(oauth2_url)


@app.route('/oauth2', methods=['GET', 'POST'])
def wc_oauth2():
    code = request.args.get('code', None)
    result = {'msg': 'Authorization failed, please try again.'}
    if code is not None:
        we_chat = WeChat(app.config.get('APP_ID'), app.config.get('APP_SECRET'))
        token_info = we_chat.get_web_access_token_by_code(code)
        openid = token_info.get('openid', None)
        if openid:
            session['openid'] = openid
            url_endpoint = session.get('redirect_url_endpoint', 'index')
            return redirect(url_for(url_endpoint))
    return result


@app.route('/', methods=['GET', 'POST'])
def index():
    pass


if __name__ == '__main__':
    manager.run()
