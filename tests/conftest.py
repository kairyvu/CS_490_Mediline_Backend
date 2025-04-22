from datetime import datetime, timedelta
import pytest
from flaskr import create_app
from flaskr.extensions import db
from flaskr.struct import AccountType, AppointmentStatus
from flaskr.models import Country, City, Address
from flaskr.models import User, Patient, Doctor, Pharmacy
from flaskr.models import Appointment, AppointmentDetail
from flaskr.models import Chat, Message

## Unit test fixtures
@pytest.fixture(scope='module')
def app():
    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///tests.db"
    })

    with app.app_context():
        yield app

@pytest.fixture
def database_session(app):
    db.create_all()
    yield db
    db.drop_all()

## Integration test fixtures
@pytest.fixture
def client(app, database_session):
    yield app.test_client(), database_session

### MODELS FIXTURES
@pytest.fixture(scope='module')
def addr1(request):
    country: Country = Country(country_id=1, country='US')
    city: City = City(city_id=1, city='NYC', country_id=1)
    address: Address = Address(
        address_id=1,
        address1='123 North St',
        address2='Apt 2',
        city_id=1,
        state='New York',
        zipcode='11223'
    )
    yield address, city, country

@pytest.fixture(scope='module')
def addr2(request):
    country: Country = Country(country_id=1, country='US')
    city: City = City(city_id=1, city='NYC', country_id=1)
    address: Address = Address(
        address_id=2,
        address1='777 20th Ave',
        city_id=1,
        state='New York',
        zipcode='33882'
    )
    yield address, city, country

@pytest.fixture(scope='module')
def addr3(request):
    country: Country = Country(country_id=1, country='US')
    city: City = City(city_id=2, city='Albany', country_id=1)
    address: Address = Address(
        address_id=3,
        address1='28 11 Blvd',
        city_id=2,
        state='New York',
        zipcode='33221'
    )
    yield address, city, country

@pytest.fixture(scope='module')
def addr4(request):
    country: Country = Country(country_id=1, country='US')
    city: City = City(city_id=3, city='Newark', country_id=1)
    address: Address = Address(
        address_id=4,
        address1='38 88 St',
        city_id=3,
        state='New Jersey',
        zipcode='07030'
    )
    yield address, city, country

@pytest.fixture(scope='module')
def pt1(request, addr1):
    _dob = datetime.fromisoformat('2000-01-01')
    addr, _, _ = addr1
    u1 = User(
        user_id=1,
        username='user1',
        password='password1',
        account_type=AccountType.Patient,
        address_id=addr.address_id
    )
    pt = Patient(
        user_id=1,
        first_name='John',
        last_name='Smith',
        dob=_dob,
        phone='9992223333',
        email='email@email.com',
    )
    yield u1, pt

@pytest.fixture(scope='module')
def dr1(request, addr2):
    _dob = datetime.fromisoformat('2000-01-01')
    addr, _, _ = addr2
    u2 = User(
        user_id=2,
        username='doct1',
        password='password1',
        account_type=AccountType.Doctor,
        address_id=addr.address_id
    )
    dr = Doctor(
        user_id=2,
        first_name='Jack',
        last_name='Daniels',
        dob=_dob,
        phone='2228381991',
        email='maile@example.com',
        bio='Blah Blah Blah',
        specialization='Neurology',
        license_id='9f82hslc-982j',
        fee=200.00
    )
    yield u2, dr

@pytest.fixture(scope='module')
def pharm1(request, addr3):
    addr, _, _ = addr3
    u3 = User(
        user_id=3,
        username='pharm',
        password='password1',
        account_type=AccountType.Pharmacy,
        address_id=addr.address_id
    )
    pharm = Pharmacy(
        user_id=3,
        pharmacy_name='Walgreens',
        phone='281-288-3949',
        email='walgreens.pharm@gmail.com',
        hours='10am-5pm'
    )
    yield u3, pharm

@pytest.fixture(scope='module')
def appt1(request, pt1, dr1):
    _up, _p = pt1
    _ud, _d = dr1
    appt = Appointment(
        appointment_id=1,
        doctor_id=_d.user_id,
        patient_id=_p.user_id,
    )
    _start = datetime.fromisoformat('2000-01-01T12:00:00')
    _end = datetime.fromisoformat('2000-05-01T12:00:00')
    appt_dt = AppointmentDetail(
        appointment_details_id=appt.appointment_id,
        treatment='Hyperglycoma',
        start_date=_start,
        end_date=_end,
        status=AppointmentStatus.PENDING
    )
    yield pt1, dr1, appt, appt_dt

@pytest.fixture(scope='module')
def msg1(request):
    _curr_time = datetime.now().isoformat()
    _time = datetime.fromisoformat('2001-01-01T12:00:00')
    _m = Message(
        message_id=1,
        chat_id=1,
        user_id=1,
        message_content='lakjsoijosdj',
        time=_curr_time
    )
    yield _m

@pytest.fixture(scope='module')
def chat1(request, appt1, msg1):
    # A chat involves a list of messages and an appointment
    # A message involves a user id, message, and timestamp
    pt, dr, appt, appt_dt = appt1
    _chat = Chat(
        chat_id=1,
        appointment_id=appt.appointment_id,
        start_date=msg1.time
    )
    _chat.messages = [
        Message(
            message_id=1,
            chat_id=1,
            user_id=1,
            message_content='lakjsoijosdj',
            time=datetime.now().isoformat()
        ),
        Message(
            message_id=2,
            chat_id=1,
            user_id=1,
            message_content='lakjsoijosdj',
            time=(datetime.now().isoformat() + timedelta(0, 30))
        )
    ]

@pytest.fixture(scope='session')
def pt_reg_form1(request):
    yield {
        'username': 'username', 
        'password': 'apoliknsdbvpoiahnwepn',
        'account_type': 'patient',
        'address1': '123 St St',
        'city': 'NYC',
        'state': 'New York',
        'zipcode': '01122',
        'country': 'US',
        'first_name': 'John',
        'last_name': 'Smith', 
        'phone': '1112223333',
        'email': 'email@email.com',
        'dob': '2000-01-01'
    }