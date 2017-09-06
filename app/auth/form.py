# -*- coding: utf-8 -*-
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField
from wtforms.validators import DataRequired, Length, Email


class RegisterForm(FlaskForm):
    name = StringField(u'Name', validators=[DataRequired(message=u'Name is required.'),
                                            Length(max=16, message=u'Subject out of limitation 16')])
    email = StringField(u'E-mail', validators=[DataRequired(message=u'E-mail is required'),
                                               Email(message=u'Invalid E-mail.')])
    submit = SubmitField(u'Submit')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(message=u'Missing email'), Length(1, 64),
                                             Email()])
    password = PasswordField('Password', validators=[DataRequired(message=u'Missing password')])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Log In')



