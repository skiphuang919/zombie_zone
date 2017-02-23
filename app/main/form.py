# -*- coding: utf-8 -*-
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, Regexp, Email


class OrderForm(FlaskForm):
    contacts = StringField(u'contacts', validators=[DataRequired(message=u'Contacts is required.'),
                                                    Length(max=32, message=u'contacts out of limitation 32')])
    tel = StringField(u'tel', validators=[DataRequired(message=u'Phone number is required'),
                                          Length(min=11, max=11, message=u'Invalid phone number.'),
                                          Regexp('^\d{11}$', message=u'Invalid phone number.')])
    store_name = StringField(u'store name', validators=[Length(max=32, message=u'Store name out of limitation 32')])
    store_addr = StringField(u'store addr', validators=[Length(max=64, message=u'Store addr out of limitation 64')])
    device_id = StringField(u'device id', validators=[DataRequired(message=u'Device id is required.'),
                                                      Length(max=32, message=u'Device id out of limitation 32')])
    accident_desc = TextAreaField(u'accident desc',
                                  validators=[Length(max=128, message=u'Accident desc out of limitation 128')])
    submit = SubmitField(u'submit')




