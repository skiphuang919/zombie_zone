from flask import Flask, render_template, redirect, url_for, request
from flask_script import Manager
from flask_bootstrap import Bootstrap
from form import NameForm
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
manager = Manager(app)
bootstrap = Bootstrap(app)


@app.route('/oauth2/', methods=['GET', 'POST'])
def wc_oauth2():
    code = request.args.get('code', None)
    pass


@app.route('/', methods=['GET', 'POST'])
def index():
    form = NameForm()
    return render_template('index.html', name='kevin', form=form)

if __name__ == '__main__':
    manager.run()
