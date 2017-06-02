from .. import db
from ..model import Parties
from tools import get_db_unique_id, get_calculated_datetime, current_time
from flask_login import current_user


def add_party(subject=None, party_time=None, address=None, host_id=None,
              required_count=None, note=None):
    party = Parties(party_id=get_db_unique_id(),
                    subject=subject,
                    party_time=party_time,
                    address=address,
                    host_id=host_id,
                    required_count=required_count,
                    note=note)
    db.session.add(party)
    db.session.commit()
    return party


def get_all_parties(available=False):
    sql = Parties.query
    if available:
        dead_line = get_calculated_datetime(current_time(), hours=1)
        sql = sql.filter(Parties.party_time > dead_line)
    return sql.order_by(Parties.create_time.desc()).all()


def get_party_by_id(party_id):
    return Parties.query.filter_by(party_id=party_id).first()


def get_parties(_type='all', available=False):
    # get all the parties
    if _type == 'all':
        sql = Parties.query
        if available:
            dead_line = get_calculated_datetime(current_time(), hours=1)
            sql = sql.filter(Parties.party_time > dead_line)
        return sql.order_by(Parties.create_time.desc()).all()

    # get parties current user ever created
    if _type == 'created':
        current_user.created_parties.all()

    # get parties current user ever joined
    if _type == 'joined':
        current_user.joined_parties.all()
