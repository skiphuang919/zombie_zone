from .. import db
from ..model import Parties, Participate
from tools import get_db_unique_id, get_calculated_datetime, current_utc_time


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


def get_participators(party_id):
    return [p.participator for p in Participate.query.filter_by(joined_party_id=party_id).all()]


def get_parties(available=False, limit=None, offset=None):
    sql = Parties.query
    if available:
        dead_line = get_calculated_datetime(current_utc_time(), hours=1)
        sql = sql.filter(Parties.party_time > dead_line)
    sql = sql.order_by(Parties.create_time.desc())
    if limit is not None:
        sql = sql.limit(limit)

    if offset is not None:
        sql = sql.offset(offset)

    return sql.all()


def delete_party(party_id):
    party = Parties.query.filter_by(party_id=party_id).first()
    if party:
        db.session.delete(party)
        db.session.commit()
