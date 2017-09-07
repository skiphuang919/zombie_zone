import uuid
import traceback
import pytz
import bleach
import random
from captcha.image import ImageCaptcha
from markdown import markdown
from flask import current_app
from datetime import datetime, timedelta
from bs4 import BeautifulSoup as Bs


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
            res[k] = v
    except:
        current_app.logger.warning(traceback.format_exc())
    return res


def markdown_to_safe_html(md):
    """
    convert the markdown to the safe html
    :param md: str markdown txt
    :return: str html
    """
    allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                    'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                    'h1', 'h2', 'h3', 'p']

    # convert markdown to html
    origin_html = markdown(md, output_format='html')

    # remove the tag not in allowed_tags list
    filtered_html = bleach.clean(origin_html, tags=allowed_tags, strip=True)

    # convert URL-like strings in an HTML fragment to links
    res = bleach.linkify(filtered_html)

    return res


def prettify(html):
    soup = Bs(html, 'html.parser')
    return soup.prettify()


def generate_captcha():
    """
    generate captcha
    :return: (code, data)
    """
    _letter_cases = 'abcdefghjkmnpqrstuvwxy"'
    _upper_cases = 'ABCDEFGHJKLMNPQRSTUVWXY'
    _numbers = '1234567890'

    try:
        char_pool = ''.join((_letter_cases, _upper_cases, _numbers))
        captcha_code = ''.join(random.sample(char_pool, 4))
        image = ImageCaptcha()
        data = image.generate(captcha_code)
        image.write(captcha_code, 'out.png')
        return captcha_code, data
    except Exception as ex:
        current_app.logger.error('generate_captcha: {}'.format(ex))


if __name__ == '__main__':
    generate_captcha()
