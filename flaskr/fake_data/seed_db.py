from datetime import timedelta
import random
import contextlib
from collections import defaultdict
from faker import Faker
from sqlalchemy import MetaData
from sqlalchemy import text
from flaskr.fake_data.deepseek_integration import generate_cities_for_countries, generate_addresses_for_cities, generate_doctor_profiles, generate_exercises, generate_medications, generate_social_media_posts
from flaskr.models import User, Patient, Doctor, Pharmacy, SuperUser, Post, Comment, Report, PatientReport, RatingSurvey, Invoice, Notification, MedicalRecord, Prescription, PrescriptionMedication, Medication, Inventory, ExerciseBank, PatientExercise, Chat, Message, Appointment, AppointmentDetail, Address, City, Country
from flaskr.struct import AccountType, ReportType, PaymentStatus, AppointmentStatus, ExerciseStatus, PrescriptionStatus, Gender
from flaskr.extensions import db

faker = Faker('en_US')
users = defaultdict(list)
user_relationship = defaultdict(tuple)
uniq_user = set()
uniq_email = set()

def delete_old_data():
    meta = MetaData()

    engine = db.engine
    with contextlib.closing(engine.connect()) as con:
        trans = con.begin()
        meta.reflect(bind=engine)
        for table in reversed(meta.sorted_tables):
            con.execute(table.delete())
        trans.commit()

def generate_email() -> str:
    email = faker.email()
    while email in uniq_email:
        email = faker.email()
    uniq_email.add(email)
    return email

def generate_user(account_type: AccountType) -> User:
    username = generate_email()
    while username in uniq_user:
        username = generate_email()
    uniq_user.add(username)
    user = User(
        username=username,
        password=faker.password(),
        account_type=account_type,
        address_id=faker.random_element(tuple(users["addresses"])) if users["addresses"] else None
    )
    db.session.add(user)
    db.session.flush()
    users["users"].append(user.user_id)
    return user

def generate_pharmacy(user: User):
    pharmacy = Pharmacy(
        user_id=user.user_id,
        pharmacy_name=faker.company(),
        phone=faker.basic_phone_number(),
        email=user.username,
        hours=faker.time_delta(),
    )
    db.session.add(pharmacy)
    users["pharmacies"].append(user.user_id)

def generate_doctor(user: User, doctor_profile: dict):
    doctor = Doctor(
        user_id=user.user_id,
        first_name=doctor_profile["first_name"],
        last_name=doctor_profile["last_name"],
        gender=doctor_profile["gender"],
        email=user.username,
        phone=faker.basic_phone_number(),
        specialization=doctor_profile["specialization"],
        bio=doctor_profile["bio"],
        fee=faker.random_number(digits=3, fix_len=False),
        profile_picture=faker.image_url(),
        dob=faker.date_of_birth(minimum_age=30, maximum_age=50),
        license_id=faker.uuid4()
    )
    db.session.add(doctor)
    users["doctors"].append(user.user_id)

def generate_patient(user: User, doctor_id=None, pharmacy_id=None):
    patient = Patient(
        user_id=user.user_id,
        first_name=faker.first_name(),
        last_name=faker.last_name(),
        gender=faker.random_element([Gender.MALE, Gender.FEMALE]),
        email=user.username,
        phone=faker.basic_phone_number(),
        dob=faker.date_of_birth(minimum_age=18, maximum_age=65),
        doctor_id=doctor_id,
        pharmacy_id=pharmacy_id,
    )
    db.session.add(patient)
    db.session.flush()

def seed_addresses():
    countries = [
        "United States", "Canada", "China", "United Kingdom",
    ]
    for country in countries:
        ctr = Country(country=country)
        db.session.add(ctr)

    country_map = {
        c.country: c.country_id
        for c in Country.query.all()
    }
    cities = generate_cities_for_countries(countries, min_count=5, max_count=10)
    for country, city_list in cities.items():
        country_id = country_map[country]
        address_list = generate_addresses_for_cities(country=country, cities=city_list)
        for city in city_list:
            ct = City(city=city, country_id=country_id)
            db.session.add(ct)
            db.session.flush()
            
            city_id = ct.city_id
            for address in address_list[city]:
                address = Address(
                    address1=address["address1"],
                    address2=address["address2"],
                    state=address["state"],
                    zipcode=address["zipcode"],
                    city_id=city_id
                )
                db.session.add(address)
                db.session.flush()
                users["addresses"].append(address.address_id)
    
    db.session.commit()
    print("Addresses done")

def seed_users(pharmacy_count=10, doctor_count=20, patient_count=500):
    user = generate_user(AccountType.SUPERUSER)
    super_user = SuperUser(user_id=user.user_id)
    db.session.add(super_user)
    doctor_profile = generate_doctor_profiles(doctor_count)

    for _ in range(pharmacy_count):
        user = generate_user(AccountType.PHARMACY)
        generate_pharmacy(user)
    for i in range(doctor_count):
        user = generate_user(AccountType.DOCTOR)
        generate_doctor(user, doctor_profile[i])
    for _ in range(patient_count):
        user = generate_user(AccountType.PATIENT)   
        users["users"].append(user.user_id)
        users["patients"].append(user.user_id)

        doctor_id=faker.random_element(tuple(users["doctors"])) if users["doctors"] else None
        pharmacy_id=faker.random_element(tuple(users["pharmacies"])) if users["pharmacies"] else None
        user_relationship[user.user_id] = (doctor_id, pharmacy_id)

        generate_patient(user, doctor_id, pharmacy_id)
    
    db.session.commit()
    print("Users done")

def seed_posts(n=50):
    posts = generate_social_media_posts(n)
    for post in posts:
        created_at = faker.date_time_this_year()
        updated_at = created_at + timedelta(minutes=random.randint(0, 300))
        post = Post(
            user_id=faker.random_element(tuple(users["users"])),
            title=post["title"],
            content=post["content"],
            created_at=created_at,
            updated_at=updated_at,
        )
        db.session.add(post)
        db.session.flush()
        users["posts"].append(post.post_id)

        for _ in range(faker.random_int(min=0, max=5)):
            comment_created_at = created_at + timedelta(minutes=random.randint(0, 300))
            comment_updated_at = comment_created_at + timedelta(minutes=random.randint(0, 10))
            comment = Comment(
                post_id=post.post_id,
                user_id=faker.random_element(tuple(users["users"])),
                content=faker.text(max_nb_chars=200),
                created_at=comment_created_at,
                updated_at=comment_updated_at,
            )
            db.session.add(comment)
            db.session.flush()
    
    db.session.commit()
    print("Posts done")

def seed_reports(n=300):
    for _, member in ReportType.__members__.items():
        report = Report(
            type=member,
        )
        db.session.add(report)
        db.session.flush()
        users["reports"].append(report.report_id)

    for _ in range(n):
        patient_id=faker.random_element(tuple(users["patients"]))
        doctor_id=user_relationship[patient_id][0]

        for _ in range(faker.random_int(min=0, max=5)):
            patient_report = PatientReport(
                report_id=faker.random_element(tuple(users["reports"])),
                patient_id=patient_id,
                doctor_id=doctor_id,
                height=faker.random_number(digits=3, fix_len=False),
                weight=faker.random_number(digits=3, fix_len=False),
                calories_intake=faker.random_number(digits=3, fix_len=False),
                hours_of_exercise=faker.random_number(digits=3, fix_len=False),
                hours_of_sleep=faker.random_number(digits=2, fix_len=False),
            )
            db.session.add(patient_report)
            db.session.flush()
            users["patient_reports"].append(patient_report.patient_report_id)
    
    db.session.commit()
    print("Reports done")

def seed_medications(n=200):
    medications = generate_medications()
    for med in medications:
        medication = Medication(
            name=med["medication_name"],
            description=med["medication_description"],
        )
        db.session.add(medication)
        db.session.flush()
        users["medications"].append(medication.medication_id)

        for pharmacy_id in users["pharmacies"]:
            inventory = Inventory(
                medication_id=medication.medication_id,
                quantity=faker.random_int(min=1000, max=100000),
                pharmacy_id=pharmacy_id,
                expiration_date=faker.date_time_between(start_date=faker.date_time_this_year(), end_date=faker.date_time_this_year() + timedelta(days=365*2))
            )
            db.session.add(inventory)
            db.session.flush()
    
    db.session.commit()
    print("Medications done")

def seed_medical_records():
    for appointment_id in users["appointments"]:
        medical_record = MedicalRecord(
            appointment_id=appointment_id,
            description=faker.text(max_nb_chars=200),
            created_at=faker.date_time_this_year(),
        )
        db.session.add(medical_record)
    db.session.commit()
    print("Medical records done")

def seed_prescriptions(n=400):
    for _ in range(n):
        prescription = Prescription(
            patient_id=faker.random_element(tuple(users["patients"])),
            doctor_id=faker.random_element(tuple(users["doctors"])),
            amount=faker.random_number(digits=3, fix_len=False),
            pharmacy_id=faker.random_element(tuple(users["pharmacies"])),
            status=faker.random_element([PrescriptionStatus.PAID, PrescriptionStatus.UNPAID]),
            created_at=faker.date_time_this_year(),
        )
        db.session.add(prescription)
        db.session.flush()
        users["prescriptions"].append(prescription.prescription_id)

        for _ in range(faker.random_int(min=0, max=10)):
            prescription_medication = PrescriptionMedication(
                prescription_id=prescription.prescription_id,
                medication_id=faker.random_element(tuple(users["medications"])),
                dosage=faker.random_int(min=1, max=10),
                medical_instructions=faker.text(max_nb_chars=200),
                taken_date=faker.date_time_this_year(),
                duration=random.randint(1, 30),
            )
            db.session.add(prescription_medication)
            db.session.flush()
    
    db.session.commit()
    print("Prescriptions done")

def seed_ratings(n=1000):
    for _ in range(n):
        rating_survey = RatingSurvey(
            patient_id=faker.random_element(tuple(users["patients"])),
            doctor_id=faker.random_element(tuple(users["doctors"])),
            comment=faker.text(max_nb_chars=200),
            stars=faker.random_int(min=1, max=5),
        )
        db.session.add(rating_survey)
        db.session.flush()
        users["rating_surveys"].append(rating_survey.survey_id)
    
    db.session.commit()
    print("Ratings done")

def seed_invoices(n=500):
    for _ in range(n):
        invoice = Invoice(
            patient_id=faker.random_element(tuple(users["patients"])),
            doctor_id=faker.random_element(tuple(users["doctors"])),
            status=faker.random_element([PaymentStatus.PAID, PaymentStatus.PENDING]),
            pay_date=faker.date_time_this_year(),
            created_at=faker.date_time_this_year(),
        )
        db.session.add(invoice)
        db.session.flush()

    db.session.commit()
    print("Invoices done")

def seed_notifications(n=1000):
    for _ in range(n):
        notification = Notification(
            user_id=faker.random_element(tuple(users["users"])),
            notification_content=faker.text(max_nb_chars=200),
            created_at=faker.date_time_this_year(),
        )
        db.session.add(notification)
        db.session.flush()

    db.session.commit()
    print("Notifications done")

def seed_exercises():
    exercises = generate_exercises()
    for exercise in exercises:
        exercise = ExerciseBank(
            type_of_exercise=exercise["type_of_exercise"],
            description=exercise["description"],
        )
        db.session.add(exercise)
        db.session.flush()
        users["exercises"].append(exercise.exercise_id)
    
    for patient_id in users["patients"]:
        doctor_id = user_relationship[patient_id][0]
        if not doctor_id:
            continue
        for _ in range(faker.random_int(min=0, max=10)):
            patient_exercise = PatientExercise(
                exercise_id=faker.random_element(tuple(users["exercises"])),
                patient_id=patient_id,
                doctor_id=doctor_id,
                reps=faker.random_int(min=1, max=20),
                status=faker.random_element([
                    ExerciseStatus.IN_PROGRESS,
                    ExerciseStatus.COMPLETED]),
                created_at=faker.date_time_this_year(),
            )
            db.session.add(patient_exercise)
            db.session.flush()
            users["patient_exercises"].append(patient_exercise.patient_exercise_id)
    
    db.session.commit()
    print("Exercises done")

def seed_appointments(n=300):
    treatments = ("Consultation", "Examination", "Diagnosis", "Prescription", "Referral", "Vaccination", "Counseling", "Screening", "Imaging", "Therapy")
    for _ in range(n):
        patient_id = faker.random_element(tuple(users["patients"]))
        doctor_id = user_relationship[patient_id][0]
        created_at = faker.date_time_this_year()
        appointment = Appointment(
            doctor_id=doctor_id,
            patient_id=patient_id,
            created_at=created_at,
            updated_at=created_at + timedelta(minutes=random.randint(0, 300)),
        )
        db.session.add(appointment)
        db.session.flush()
        users["appointments"].append(appointment.appointment_id)

        start_date = faker.date_time_this_year()
        status = faker.random_element([
            AppointmentStatus.PENDING,
            AppointmentStatus.CONFIRMED,
            AppointmentStatus.CANCELLED,
            AppointmentStatus.COMPLETED
        ])

        end_date = (
            start_date + timedelta(minutes=random.randint(0, 300))
            if status == AppointmentStatus.COMPLETED else None
        )
        appointment_detail = AppointmentDetail(
            appointment_details_id=appointment.appointment_id,
            treatment=faker.random_element(treatments),
            start_date=start_date,
            end_date=end_date,
            status=status,
        )
        db.session.add(appointment_detail)
        db.session.flush()
    
    db.session.commit()
    print("Appointments done")


def seed_messages(n=300):
    for _ in range(n):
        start_date=faker.date_time_this_year()
        end_date=start_date + timedelta(minutes=random.randint(0, 300))

        chat = Chat(
            appointment_id=faker.unique.random_element(tuple(users["appointments"])),
            start_date=start_date,
            end_date=end_date,
        )
        db.session.add(chat)
        db.session.flush()
        users["chats"].append(chat.chat_id)


        patient_id = faker.random_element(tuple(users["patients"]))
        doctor_id = user_relationship[patient_id][0]
        for _ in range(faker.random_int(min=0, max=10)):
            message = Message(
                chat_id=chat.chat_id,
                user_id=faker.random_element([patient_id, doctor_id]),
                message_content=faker.text(max_nb_chars=200),
                time=start_date + (end_date - start_date) * random.random()
            )
            db.session.add(message)
            db.session.flush()
    
    db.session.commit()
    print("Messages done")

def seed_all():
    delete_old_data()
    for table_name in db.metadata.tables.keys():
        sql = text(f"ALTER TABLE {table_name} AUTO_INCREMENT = 1;")
        db.session.execute(sql)
    db.session.commit()
    faker.unique.clear()
    seed_addresses()
    seed_users()
    seed_posts()
    seed_reports()
    seed_medications()
    seed_prescriptions()
    seed_ratings()
    seed_invoices()
    seed_notifications()
    seed_exercises()
    seed_appointments()
    seed_messages()
    seed_medical_records()

if __name__ == "__main__":

    with db.session.begin_nested():
        seed_all()
        print("All data seeded")