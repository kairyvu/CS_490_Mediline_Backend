"""\
    Used in `register.py`; ORM-like models for form data used in validation
"""
from wtforms import Form, Field, ValidationError, DecimalField, TelField, DateField, StringField, PasswordField, EmailField, validators, BooleanField

def length(min=-1, max=-1):
    message = f'Must be between {min} and {max} characters long.'
    def _length(form: dict[str, str], field: Field):
        l = field.data and len(field.data) or 0
        if l < min or max != -1 and l > max:
            raise ValidationError(message)
    return _length

def length_no_max(min=-1):
    message = f'Must be at least {min} characters long.'
    def _length(form: dict[str, str], field: Field):
        l = field.data and len(field.data) or 0
        if l < min:
            raise ValidationError(message)
    return _length

class AddressForm(Form):
    address1        =   StringField('Address 1', [
                            validators.InputRequired()
                        ])
    address2        =   StringField('Address 2', [ ])
    city            =   StringField('City', [
                            validators.InputRequired()
                        ])
    state           =   StringField('State', [
                            validators.InputRequired()
                        ])
    country         =   StringField('Country', [
                            validators.InputRequired()
                        ])
    zipcode         =   StringField('Zipcode', [
                            validators.InputRequired()
                        ])


class UserRegistrationForm(AddressForm):
    _phone_num_regexp = "^(\+\d{1,2}\s?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}$"
    username        =   StringField('Username', [
                            length(4, 80),
                            validators.InputRequired()
                        ])
    password        =   PasswordField('Password', [
                            length_no_max(8),
                            validators.InputRequired()
                        ])
    account_type    =   StringField('Account Type', [
                            validators.AnyOf(
                                ['patient', 'doctor', 'pharmacy'], 
                                message='Invalid account type'
                            ),
                            validators.InputRequired()
                        ])
    email           =   EmailField('Email', [
                            validators.Email(),
                            validators.InputRequired()
                        ])
    phone           =   TelField('Phone Number', [
                            validators.Regexp(
                                _phone_num_regexp, 
                                message='Invalid phone number'),
                            validators.InputRequired()
                        ]) 


class PtRegForm(UserRegistrationForm):
    first_name      =   StringField('First Name', [
                            validators.InputRequired()
                        ])
    last_name       =   StringField('Last Name', [
                            validators.InputRequired()
                        ])
    dob             =   DateField('Date of Birth', [
                            validators.InputRequired()
                        ])
    gender          =   StringField('Gender', [
                            validators.InputRequired()
                        ])

class DrRegForm(PtRegForm):
    specialization  =   StringField('Specialization', [
                            validators.InputRequired()
                        ])
    fee             =   DecimalField('Fee', [
                            validators.InputRequired()
                        ])
    license_id      =   StringField('License ID', [
                            validators.InputRequired()
                        ])
    accepting_patients  =   BooleanField('Accepting Patients', [ ])

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
