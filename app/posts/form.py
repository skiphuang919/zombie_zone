# -*- coding: utf-8 -*-
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length
from flask_pagedown.fields import PageDownField
from ..lib.utils import ZombieForm


class PostForm(ZombieForm):
    title = StringField(u'Title', validators=[DataRequired(message=u'Subject is required.'),
                                              Length(max=32, message=u'Subject out of limitation 32')])
    body = PageDownField(u'Settle down, and write it down.')
    submit = SubmitField('Submit')