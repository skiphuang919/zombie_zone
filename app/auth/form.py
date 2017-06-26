# -*- coding: utf-8 -*-
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, Regexp


class RegisterForm(FlaskForm):
    cellphone = StringField(u'Cellphone', validators=[DataRequired(message=u'cellphone is required.'),
                                                      Regexp('^\d{11}$', message=u'invalid cellphone')])
    email = StringField(u'E-mail', validators=[DataRequired(message=u'E-mail is required'),
                                               Email(message=u'Invalid E-mail.')])
    slogan = TextAreaField(u'Slogan', validators=[Length(max=100, message=u'slogan out of limitation 100')])
    submit = SubmitField(u'Submit')




