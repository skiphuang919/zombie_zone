# -*- coding: utf-8 -*-
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, Email


class UserForm(FlaskForm):
    name = StringField(u'nick name', validators=[DataRequired(message=u'nick name is required.'),
                                                 Length(max=32, message=u'nick name out of limitation 32')])
    email = StringField(u'E-mail', validators=[DataRequired(message=u'E-mail is required'),
                                               Email(message=u'Invalid E-mail.')])
    gender = SelectField(u'gender', choices=[(1, u'male'), (0, u'female')])
    city = StringField(u'city', validators=[Length(max=16, message=u'city out of limitation 16')])
    slogan = TextAreaField(u'slogan', validators=[Length(max=128, message=u'slogan out of limitation 128')])
    submit = SubmitField(u'submit')




