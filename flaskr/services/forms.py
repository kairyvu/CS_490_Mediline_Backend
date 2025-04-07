"""\
    Used in `register.py`; ORM-like models for form data used in validation
"""
from wtforms import Form, StringField, PasswordField, EmailField, validators

class UserRegistrationForm(Form):
    _phone_num_regexp = "^(\+\d{1,2}\s?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}$"
    username        =   StringField('Username', [
                            validators.Length(min=4, max=25),
                            validators.InputRequired()
                        ])
    password        =   PasswordField('Password', [
                            validators.Length(min=8),
                            validators.InputRequired()
                        ])
    account_type    =   StringField('Password', [
                            validators.AnyOf(['patient', 'doctor', 'pharmacy']),
                            validators.InputRequired()
                        ])
    email           =   EmailField('Email', [
                            validators.Email(),
                            validators.InputRequired()
                        ])
    phone           =   StringField('Phone Number', [
                            validators.Regexp(_phone_num_regexp),
                            validators.InputRequired()
                        ]) 

class PtRegForm(UserRegistrationForm):
    first_name      =   StringField('First Name', [
                            validators.InputRequired()
                        ])
    last_name       =   StringField('Last Name', [
                            validators.InputRequired()
                        ])
    dob             =   StringField('Date of Birth', [
                            validators.InputRequired()
                            #TODO: Include date validator
                        ])

class DrRegForm(PtRegForm):
    specialization  =   StringField('Specialization', [
                            validators.InputRequired()
                        ])
    fee             =   StringField('Fee', [
                            validators.InputRequired()
                        ])
    license_id      =   StringField('License ID', [
                            validators.InputRequired()
                        ])

class PharmRegForm(UserRegistrationForm):
    pharmacy_name   =   StringField('Pharmacy Name', [
                            validators.InputRequired()
                        ])
    hours           =   StringField('Hours', [
                            validators.InputRequired()
                        ])
    zipcode         =   StringField('Zip Code', [
                            validators.InputRequired()
                        ])