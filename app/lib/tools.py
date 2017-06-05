import uuid
from datetime import date, datetime, timedelta


def get_db_unique_id():
    """
    generate 'unique' id for db
    :return: str
    """
    return str(uuid.uuid4())


def get_calculated_datetime(origin_dt, days=None, hours=None, seconds=None):
    """
    calculate a day before base on origin_dt
    if origin_dt is not datetime obj, convert it.
    :param origin_dt: datetime obj or datetime str
    :param days: int or float
    :param hours: int or float
    :param seconds: int or float
    :return: datetime obj or None
    """
    try:
        origin_dt = datetime.strptime(origin_dt, "%Y-%m-%d %H:%M:%S") if \
            not isinstance(origin_dt, datetime) else origin_dt
        result_dt = origin_dt + timedelta(days=days if days is not None else 0,
                                          hours=hours if hours is not None else 0,
                                          seconds=seconds if seconds is not None else 0)
    except Exception as ex:
        print str(ex)
        result_dt = ''
    return result_dt


def current_utc_time():
    """
    get the utc datetime
    :return: datetime obj
    """
    return datetime.utcnow()


def obj2dic(obj):
    """
    convert the obj to dict
    :param obj:
    :return: dict
    """
    res = {}
    try:
        for k, v in vars(obj).items():
            if k.startswith('_'):
                continue
            if isinstance(v, date):
                v = v.strftime("%Y-%m-%d %H:%M:%S")
            res[k] = v
    except Exception as ex:
        print ex
    return res


