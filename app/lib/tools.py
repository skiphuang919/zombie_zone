import uuid
import traceback
import pytz
from flask import current_app
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
    origin_dt = datetime.strptime(origin_dt, "%Y-%m-%d %H:%M:%S") if \
        not isinstance(origin_dt, datetime) else origin_dt
    result_dt = origin_dt + timedelta(days=days if days is not None else 0,
                                      hours=hours if hours is not None else 0,
                                      seconds=seconds if seconds is not None else 0)
    return result_dt


def current_utc_time():
    """
    get the utc datetime
    :return: datetime obj
    """
    return datetime.utcnow()


def utc2local(utc_dt, timezone='Asia/Shanghai', res_type='str'):
    """
    convert utc datetime obj or str to local time base on timezone
    :param utc_dt: utc datetime
    :param timezone: local timezone
    :param res_type: return type str or obj
    :return: local datetime obj
    """
    utc_dt = datetime.strptime(utc_dt, "%Y-%m-%d %H:%M:%S") if \
        not isinstance(utc_dt, datetime) else utc_dt
    local_tz = pytz.timezone(timezone)
    local_dt = utc_dt.replace(tzinfo=pytz.utc).astimezone(local_tz)
    return local_tz.normalize(local_dt).strftime("%Y-%m-%d %H:%M:%S") if \
        res_type == 'str' else local_tz.normalize(local_dt)


def obj2dic(obj):
    """
    convert the obj to dict
    :param obj:
    :return: dict
    """
    res = {}
    try:
        if not obj:
            return res
        for k, v in vars(obj).items():
            if k.startswith('_'):
                continue
            if isinstance(v, date):
                v = v.strftime("%Y-%m-%d %H:%M:%S")
            res[k] = v
    except:
        current_app.logger.warning(traceback.format_exc())
    return res


