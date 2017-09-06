# -*- coding: utf-8 -*-
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo


class RegisterForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(message='Name is required.'),
                                           Length(max=16, message='Subject out of limitation 16')])
    email = StringField('E-mail', validators=[DataRequired(message='E-mail is required'),
                                              Email(message='Invalid E-mail.')])
    password = PasswordField('Password', validators=[DataRequired(message='password is required'),
                                                     EqualTo('password2', message='Password mismatch.'),
                                                     Length(min=6, message='password too short')])
    password2 = PasswordField('Confirm', validators=[DataRequired(message='confirm password is required')])
    submit = SubmitField('Submit')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(message='Missing email'),
                                             Email(message='Invalid E-mail.')])
    password = PasswordField('Password', validators=[DataRequired(message='Missing password')])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Log In')



