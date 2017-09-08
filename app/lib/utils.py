import random
from flask import session, current_app
from captcha.image import ImageCaptcha

LOW_LETTERS = 'abcdefghjkmnpqrstuvwxyz'
UPPER_LETTERS = 'ABCDEFGHJKLMNPQRSTUVWXYZ'
NUMBERS = '1234567890'


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
            current_app.logger.info('captcha code: {}'.format(captcha_code))
        return captcha

    @staticmethod
    def validate(code):
        if code:
            return True if session.get('captcha_code', '').lower() == str(code).lower() else False
        else:
            return False



