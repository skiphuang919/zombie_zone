from .. import db
from ..model import Parties
from tools import get_db_unique_id


def add_party(subject=None, party_time=None, address=None, host_id=None,
              required_count=None, note=None):
    party = Parties(party_id=get_db_unique_id(),
                    subject=subject,
                    party_time=party_time,
                    address=address,
                    host=host_id,
                    required_count=required_count,
                    note=note)
    db.session.add(party)
    db.session.commit()
    return party


def get_all_parties():
    return Parties.query.order_by(Parties.create_time.desc()).all()


def get_party_by_id(party_id):
    return Parties.query.filter_by(party_id=party_id).first()


def get_parties_by_host(host_id):
    return Parties.query.filter_by(host=host_id).all()
