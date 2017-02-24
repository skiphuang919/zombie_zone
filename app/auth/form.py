# -*- coding: utf-8 -*-
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, Email


class UserForm(FlaskForm):
    name = StringField(u'Nick Name', validators=[DataRequired(message=u'nick name is required.'),
                                                 Length(max=32, message=u'nick name out of limitation 32')])
    email = StringField(u'E-mail', validators=[DataRequired(message=u'E-mail is required'),
                                               Email(message=u'Invalid E-mail.')])
    gender = SelectField(u'Gender', choices=[('1', u'Male'), ('0', u'Female')])
    city = SelectField(u'City', choices=[('1', u'Jixi'), ('0', u'Shanghai')])
    slogan = TextAreaField(u'Slogan', validators=[Length(max=128, message=u'slogan out of limitation 128')])
    submit = SubmitField(u'Submit')




