# -*- coding: utf-8 -*-
from wtforms import StringField, SubmitField, ValidationError
from wtforms.validators import DataRequired, Length
from flask_pagedown.fields import PageDownField
from ..lib.utils import ZombieForm, Captcha


class PostForm(ZombieForm):
    title = StringField(u'Title', validators=[DataRequired(message=u'Subject is required.'),
                                              Length(max=32, message=u'Subject out of limitation 32')])
    body = PageDownField(u'Settle down, and write it down.')
    submit = SubmitField('Submit')


class CommentForm(ZombieForm):
    body = StringField(u'Enter your comment', validators=[DataRequired(message=u'Nothing to commit.')])
    captcha = StringField('Captcha', validators=[DataRequired(message='Invalid captcha.')])
    submit = SubmitField('Submit')

    def validate_captcha(self, field):
        cap = Captcha()
        if not cap.validate(field.data):
            raise ValidationError('Invalid captcha.')
