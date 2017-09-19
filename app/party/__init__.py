from flask import Blueprint

party_blueprint = Blueprint('party', __name__)

from . import view