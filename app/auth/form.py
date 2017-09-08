# -*- coding: utf-8 -*-
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, ValidationError
from wtforms.validators import DataRequired, Length, Email, EqualTo
from ..lib import users
from ..lib.tools import Captcha


class RegisterForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(message='Name is required.'),
                                           Length(max=16, message='Subject out of limitation 16')])
    email = StringField('E-mail', validators=[DataRequired(message='E-mail is required'),
                                              Email(message='Invalid E-mail.')])
    password = PasswordField('Password', validators=[DataRequired(message='password is required'),
                                                     EqualTo('password2', message='Password mismatch.'),
                                                     Length(min=6, message='password too short')])
    password2 = PasswordField('Confirm', validators=[DataRequired(message='confirm password is required')])
    captcha = StringField('Captcha', validators=[DataRequired(message='Invalid captcha.')])
    submit = SubmitField('Register')

    def validate_name(self, field):
        if users.is_email_exist(field.data):
            raise ValidationError('Name already exist.')

    def validate_email(self, field):
        if users.is_email_exist(field.data):
            raise ValidationError('Email already exist.')

    def validate_captcha(self, field):
        cap = Captcha()
        if not cap.validate(field.data):
            raise ValidationError('Invalid captcha.')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(message='Missing email'),
                                             Email(message='Invalid E-mail.')])
    password = PasswordField('Password', validators=[DataRequired(message='Missing password')])
    captcha = StringField('Captcha', validators=[DataRequired(message='Invalid captcha.')])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Log In')

    def validate_captcha(self, field):
        cap = Captcha()
        if not cap.validate(field.data):
            raise ValidationError('Invalid captcha.')



