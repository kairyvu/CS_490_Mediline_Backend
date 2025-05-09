from datetime import datetime, timedelta
import pytest
from flaskr import create_app
from flaskr.extensions import db
from flaskr.struct import AccountType, AppointmentStatus, ExerciseStatus, Gender, PrescriptionStatus
from flaskr.models import Country, City, Address
from flaskr.models import User, Patient, Doctor, Pharmacy
from flaskr.models import Appointment, AppointmentDetail
from flaskr.models import Chat, Message
from flaskr.models import ExerciseBank, PatientExercise
from flaskr.models import MedicalRecord, Medication, PrescriptionMedication, Prescription, Inventory

## Unit test fixtures
@pytest.fixture(scope='session')
def app():
    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///tests.db",
        "FLASK_ENV": "testing"
    })

    with app.app_context():
        yield app

@pytest.fixture
def database_session(app):
    yield db
    db.drop_all()

## Integration test fixtures
@pytest.fixture
def client(app, database_session):
    database_session.create_all()
    yield app.test_client(), database_session
    database_session.session.rollback()
    database_session.drop_all()

### MODELS FIXTURES
@pytest.fixture(scope='module')
def addr1(request):
    country: Country = Country(country_id=1, country='US')
    city: City = City(city_id=1, city='NYC', country_id=1)
    address: Address = Address(
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
    u1 = User('user1', 'password1', AccountType.PATIENT, addr.address_id)
    u1.address = addr
    pt = Patient(
        first_name='John',
        last_name='Smith',
        dob=_dob,
        phone='9992223333',
        email='email@email.com',
        gender=Gender.MALE,
        user=u1
    )
    yield u1, pt, addr1

@pytest.fixture(scope='module')
def dr1(request, addr2):
    _dob = datetime.fromisoformat('2000-01-01')
    addr, _, _ = addr2
    u2 = User('doct1', 'password1', AccountType.DOCTOR, addr.address_id)
    u2.address = addr
    dr = Doctor(
        first_name='Jack',
        last_name='Daniels',
        dob=_dob,
        phone='2228381991',
        email='maile@example.com',
        bio='Blah Blah Blah',
        specialization='Neurology',
        license_id='9f82hslc-982j',
        fee=200.00,
        gender=Gender.FEMALE,
        user=u2
    )
    yield u2, dr, addr2

@pytest.fixture(scope='module')
def pharm1(request, addr3):
    addr, _, _ = addr3
    u3 = User('pharm', 'password1', AccountType.PHARMACY, addr.address_id)
    u3.address = addr
    pharm = Pharmacy(
        pharmacy_name='Walgreens',
        phone='281-288-3949',
        email='walgreens.pharm@gmail.com',
        hours='10am-5pm',
        user=u3
    )
    yield u3, pharm, addr3

@pytest.fixture(scope='module')
def appt1(request, pt1, dr1):
    _up, _p, _addr1 = pt1
    _ud, _d, _addr2 = dr1
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
        start_date=datetime.now()
    )
    _chat.messages = [
        Message(
            message_id=1,
            chat_id=1,
            user_id=1,
            message_content='lakjsoijosdj',
            time=datetime.now()
        ),
        Message(
            message_id=2,
            chat_id=1,
            user_id=1,
            message_content='lakjsoijosdj',
            time=(datetime.now() + timedelta(0, 30))
        )
    ]
    _chat.appointment = appt
    yield _chat, appt

@pytest.fixture(scope='module')
def ex1(request):
    _ex = ExerciseBank(
        exercise_id=1,
        type_of_exercise='Callisthenic',
        description='Push-ups'
    )
    yield _ex

@pytest.fixture(scope='module')
def ex2(request):
    _ex = ExerciseBank(
        exercise_id=2,
        type_of_exercise='Cardio',
        description='Pull-ups'
    )
    yield _ex

@pytest.fixture(scope='module')
def ex3(request):
    _ex = ExerciseBank(
        exercise_id=3,
        type_of_exercise='HIT',
        description='Boxing'
    )
    yield _ex

@pytest.fixture(scope='module')
def pt_ex1(request, ex1, pt1, dr1):
    u1, u1_pt, _ = pt1
    u2, u2_dr, _ = dr1
    _pt_ex = PatientExercise(
        patient_exercise_id=1,
        exercise_id=ex1.exercise_id,
        patient_id=u1.user_id,
        doctor_id=u2.user_id,
        reps='3-5',
        status=ExerciseStatus.IN_PROGRESS,
    )
    _pt_ex.exercise = ex1
    _pt_ex.patient = u1_pt
    _pt_ex.doctor = u2_dr
    yield _pt_ex, pt1, dr1, ex1 

@pytest.fixture(scope='module')
def pt_ex2(request, ex2, pt1, dr1):
    u1, u1_pt, _ = pt1
    u2, u2_dr, _ = dr1
    _pt_ex = PatientExercise(
        patient_exercise_id=2,
        exercise_id=ex2.exercise_id,
        patient_id=u1.user_id,
        doctor_id=u2.user_id,
        reps='4-10',
        status=ExerciseStatus.IN_PROGRESS,
    )
    _pt_ex.exercise = ex2
    _pt_ex.patient = u1_pt
    _pt_ex.doctor = u2_dr
    yield _pt_ex, pt1, dr1, ex2 

@pytest.fixture(scope='module')
def pt_ex3(request, ex3, pt1, dr1):
    u1, u1_pt, _ = pt1
    u2, u2_dr, _ = dr1
    _pt_ex = PatientExercise(
        patient_exercise_id=3,
        exercise_id=ex3.exercise_id,
        patient_id=u1.user_id,
        doctor_id=u2.user_id,
        reps='30min',
        status=ExerciseStatus.IN_PROGRESS,
    )
    _pt_ex.exercise = ex3
    _pt_ex.patient = u1_pt
    _pt_ex.doctor = u2_dr
    yield _pt_ex, pt1, dr1, ex3 

@pytest.fixture(scope='module')
def record1(request):
    yield MedicalRecord(
        medical_record_id=1,
        appointment_id=1,
        description="",
        created_at=datetime.now()
    )

@pytest.fixture(scope='module')
def rx1(request):
    yield Prescription(
        prescription_id=1,
        patient_id=1,
        doctor_id=2,
        pharmacy_id=3,
        amount=300.00,
        status=PrescriptionStatus.UNPAID,
        created_at=datetime.now()
    )
    
@pytest.fixture(scope='module')
def med1(request):
    yield Medication(
        medication_id=1,
        name='med1',
        description='desc1'
    )

@pytest.fixture(scope='module')
def med2(request):
    yield Medication(
        medication_id=1,
        name='med2',
        description='desc2'
    )

@pytest.fixture(scope='module')
def inv1(request):
    yield Inventory(
        inventory_id=1,
        pharmacy_id=1,
        medication_id=1,
        quantity=10,
        expiration_date=datetime.now()
    )

@pytest.fixture(scope='session')
def pt_reg_form1(request):
    yield {
        'username': 'email@email.com',
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
        'dob': '2000-01-01',
        'gender': 'FEMALE',
    }

@pytest.fixture(scope='session')
def dr_reg_form1(request):
    yield {
        'username': 'email1@email.com',
        'password': 'apoliknsdbvpoiahnwepn',
        'account_type': 'doctor',
        'address1': '888 St St',
        'city': 'NYC',
        'state': 'New York',
        'zipcode': '01122',
        'country': 'US',
        'first_name': 'Alex',
        'last_name': 'Smith', 
        'phone': '1112223383',
        'email': 'email1@email.com',
        'dob': '2000-01-01',
        'gender': 'MALE',
        'specialization': 'Orthology',
        'license_id': '8873j0sk10',
        'fee': '200.00'
    }
   
   