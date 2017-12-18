# -*- coding: utf-8 -*-
from wtforms import StringField, SubmitField, ValidationError, TextAreaField
from wtforms.validators import DataRequired, Length
from flask_pagedown.fields import PageDownField
from ..lib.utils import ZombieForm, Captcha


class PostForm(ZombieForm):
    title = StringField('Title', validators=[DataRequired(message='Subject is required.'),
                                              Length(max=32, message='Subject out of limitation 32')])
    body = PageDownField('Settle down, and write it down.')
    submit = SubmitField('Submit')


class CommentForm(ZombieForm):
    body = TextAreaField('Comment', validators=[DataRequired(message='Nothing to commit.')])
    captcha = StringField('Captcha', validators=[DataRequired(message='Invalid captcha.')])
    submit = SubmitField('Submit')

    def validate_captcha(self, field):
        cap = Captcha()
        if not cap.validate(field.data):
            raise ValidationError('Invalid captcha.')
