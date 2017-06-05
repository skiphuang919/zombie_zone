from .. import db
from ..model import Parties
from tools import get_db_unique_id, get_calculated_datetime, current_utc_time
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


def get_party_by_id(party_id):
    return Parties.query.filter_by(party_id=party_id).first()


def get_parties(_type='all', available=False, limit=None, offset=None):
    res = None

    # get all the parties
    if _type == 'all':
        res = Parties.query
        if available:
            dead_line = get_calculated_datetime(current_utc_time(), hours=1)
            res = res.filter(Parties.party_time > dead_line)
            res.order_by(Parties.create_time.desc())

    # get parties current user ever created
    if _type == 'created':
        res = current_user.created_parties.order_by(Parties.create_time.desc())

    # get parties current user ever joined
    if _type == 'joined':
        res = current_user.joined_parties.all()

    if res is not None:
        if limit is not None:
            res = res.limit(limit)
        if offset is not None:
            res = res.offset(offset)
        return res.all()
    return []
