from wtforms import SubmitField, PasswordField, ValidationError
from wtforms.validators import DataRequired, Length, EqualTo
from flask_login import current_user
from ..lib.utils import ZombieForm


class ChangePwdForm(ZombieForm):
    old_password = PasswordField('Old Pwd')
    new_password = PasswordField('New pwd', validators=[DataRequired(message='password is required'),
                                                        EqualTo('password2', message='Password mismatch.'),
                                                        Length(min=6, message='password too short')])
    password2 = PasswordField('Confirm', validators=[DataRequired(message='confirm password is required')])
    submit = SubmitField('Submit')

    def validate_old_password(self, field):
        if not current_user.verify_password(field.data):
            raise ValidationError('Password incorrect.')