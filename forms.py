from wtforms import fields, Form, validators
from nflpbp_models import *



# class CheckValueExists(object):
#     def __call__(self, form, field):
#         if RegisteredUsers.select(fn.Count(RegisteredUsers.email)).where(RegisteredUsers.email==field.data).scalar() > 0:
#             raise validators.ValidationError('User Already Exists')





class RegisterForm(Form):
    email = fields.StringField('Email', [validators.InputRequired(), validators.Email()])
    password = fields.PasswordField('Password', [validators.Length(min=6, max=16), validators.EqualTo('confirm', 'Passwords do not match')])
    confirm = fields.PasswordField('Re-type Password')
    image_upload = fields.FileField('Image File')

    def validate_email(form, field):
        if RegisteredUsers.select(fn.Count(RegisteredUsers.email)).where(RegisteredUsers.email==field.data).scalar() > 0:
            raise validators.ValidationError('User Already Exists')