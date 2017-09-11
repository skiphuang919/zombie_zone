# -*- coding: utf-8 -*-
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, DateField
from wtforms.validators import DataRequired, Length, Regexp
from flask_pagedown.fields import PageDownField
from ..lib.utils import ZombieForm


class PartyForm(ZombieForm):
    subject = StringField(u'Subject', validators=[DataRequired(message=u'Subject is required.'),
                                                  Length(max=32, message=u'Subject out of limitation 32')])
    party_time = DateField(u'Party time', validators=[DataRequired(message=u'Party time is required')])
    address = StringField(u'Address', validators=[DataRequired(message=u'Party Address is required'),
                                                  Length(max=64, message=u'Address out of limitation 64')])
    required_count = StringField(u'Count',
                                 validators=[DataRequired(message=u'Require count is required.'),
                                             Regexp('^\d{1,2}$', message=u'Invalid required count.')])
    note = TextAreaField(u'Note',
                         validators=[Length(max=128, message=u'Accident desc out of limitation 128')])
    submit = SubmitField(u'Submit')


class PostForm(ZombieForm):
    title = StringField(u'Title', validators=[DataRequired(message=u'Subject is required.'),
                                              Length(max=32, message=u'Subject out of limitation 32')])
    body = PageDownField(u'Settle down, and write it down.')
    submit = SubmitField('Submit')

