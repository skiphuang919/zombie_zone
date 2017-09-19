from flask import render_template, session
from . import main
from ..lib import party


@main.route('/')
def index():
    party_list = party.get_parties(limit=10)
    session['from_endpoint'] = 'index'
    return render_template('index.html', party_info_list=party_list, top_title='All Parties')
