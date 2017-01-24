# -*- coding: utf-8 -*-
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, Email


class OrderForm(FlaskForm):
    contacts = StringField(u'contacts', validators=[DataRequired(), ])
    tel = StringField(u'tel', validators=[DataRequired(), Length(max=11)])
    store_name = StringField(u'store name')
    store_addr = StringField(u'store addr', validators=[Length(max=64)])
    device_id = StringField(u'device id', validators=[DataRequired(), Length(max=64)])
    accident_desc = TextAreaField(u'accident desc', validators=[Length(max=128)])
    submit = SubmitField(u'submit')


