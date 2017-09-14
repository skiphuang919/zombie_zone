import random
import hashlib
from flask import session, current_app, request
from captcha.image import ImageCaptcha
from flask_wtf import FlaskForm

LOW_LETTERS = 'abcdefghjkmnpqrstuvwxyz'
UPPER_LETTERS = 'ABCDEFGHJKLMNPQRSTUVWXYZ'
NUMBERS = '1234567890'

HTTP_GRAVATAR_URL = 'http://www.gravatar.com/avatar'
HTTPS_GRAVATAR_URL = 'https://secure.gravatar.com/avatar'


class Captcha(object):
    def __init__(self):
        self.char_pool = ''.join((LOW_LETTERS, NUMBERS, UPPER_LETTERS))

    def generate_captcha_stream(self):
        try:
            captcha_code = ''.join(random.sample(self.char_pool, 4))
            image = ImageCaptcha()
            data = image.generate(captcha_code)
            captcha = data.getvalue().encode('base64')
        except Exception as ex:
            captcha = None
            current_app.logger.error('generate_captcha exception: {}'.format(ex))
        else:
            session['captcha_code'] = captcha_code
        return captcha

    @staticmethod
    def validate(code):
        if code:
            return True if session.get('captcha_code', '').lower() == str(code).lower() else False
        else:
            return False


class ZombieForm(FlaskForm):

    def __init__(self, *args, **kwargs):
        super(ZombieForm, self).__init__(*args, **kwargs)

    def get_one_err_msg(self):
        error_msg = ''
        if self.errors:
            try:
                error_msg = self.errors.values()[0][0]
            except Exception as ex:
                current_app.logger.error('get_one_err_msg exception: {}'.format(ex))
        return error_msg


class Gravatar(object):
    def __init__(self, email, size=100):
        self.email = email.lower()
        self.size = size
        self.email_hash = hashlib.md5(self.email.encode('utf-8')).hexdigest()

    def avatar_url(self):
        url = HTTPS_GRAVATAR_URL if request.is_secure else HTTP_GRAVATAR_URL
        return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(
            url=url, hash=self.email_hash, size=self.size, default='identicon', rating='g')



