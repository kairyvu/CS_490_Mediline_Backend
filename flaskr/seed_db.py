from datetime import timedelta
import random
from faker import Faker
from flaskr.models import User, Patient, Doctor, Pharmacy, SuperUser, Post, Comment, Report, PatientReport, RatingSurvey, Invoice, Notification, MedicalRecord, Prescription, PrescriptionMedication, Medication, Inventory, ExerciseBank, PatientExercise, Chat, Message, Appointment, AppointmentDetail
import contextlib
from sqlalchemy import MetaData
from flaskr.struct import AccountType, ReportType, PaymentStatus, AppointmentStatus, ExerciseStatus, PrescriptionStatus
from collections import defaultdict
from flaskr.extensions import db
from sqlalchemy import text


faker = Faker('en_US')
users = defaultdict(list)
user_relationship = defaultdict(tuple)

def delete_old_data():
    meta = MetaData()

    engine = db.engine
    with contextlib.closing(engine.connect()) as con:
        trans = con.begin()
        meta.reflect(bind=engine)
        for table in reversed(meta.sorted_tables):
            con.execute(table.delete())
        trans.commit()

def seed_users():
    uniq_user = set()
    username = faker.user_name()
    while username in uniq_user:
        username = faker.user_name()
    uniq_user.add(username)
    user = User(
        username=username,
        password=faker.password(),
        account_type=AccountType.SuperUser
    )
    db.session.add(user)
    db.session.flush()
    users["users"].append(user.user_id)
    super_user = SuperUser(user_id=user.user_id)
    db.session.add(super_user)

    for _ in range(200):
        username = faker.user_name()
        while username in uniq_user:
            username = faker.user_name()
        uniq_user.add(username)
        user = User(
            username=username,
            password=faker.password(),
            account_type=faker.random_element([AccountType.Doctor, AccountType.Pharmacy])
        )
        db.session.add(user)
        db.session.flush()
        users["users"].append(user.user_id)
        
        uniq_email = set()
        email = faker.email()
        while email in uniq_email:
            email = faker.email()
        uniq_email.add(email)
        if user.account_type == AccountType.Doctor:
            doctor = Doctor(
                user_id=user.user_id,
                first_name=faker.first_name(),
                last_name=faker.last_name(),
                email=email,
                phone=faker.basic_phone_number(),
                specialization=faker.job(),
                bio=faker.text(max_nb_chars=300),
                fee=faker.random_number(digits=3, fix_len=False),
                profile_picture=faker.image_url(),
                dob=faker.date_of_birth(minimum_age=30, maximum_age=50),
                license_id=faker.uuid4()
            )
            db.session.add(doctor)
            users["doctors"].append(user.user_id)
        else:
            pharmacy = Pharmacy(
                user_id=user.user_id,
                pharmacy_name=faker.company(),
                phone=faker.basic_phone_number(),
                email=faker.email(),
                hours=faker.time_delta(),
                zipcode=faker.zipcode()
            )
            db.session.add(pharmacy)
            users["pharmacies"].append(user.user_id)
    
    for _ in range(500):
        username = faker.user_name()
        while username in uniq_user:
            username = faker.user_name()
        uniq_user.add(username)
        user = User(
            username=username,
            password=faker.password(),
            account_type=AccountType.Patient
        )
        db.session.add(user)
        db.session.flush()
        users["users"].append(user.user_id)
        users["patients"].append(user.user_id)

        doctor_id=faker.random_element(tuple(users["doctors"])) if users["doctors"] else None
        pharmacy_id=faker.random_element(tuple(users["pharmacies"])) if users["pharmacies"] else None
        user_relationship[user.user_id] = (doctor_id, pharmacy_id)
        
        email = faker.email()
        while email in uniq_email:
            email = faker.email()
        uniq_email.add(email)
        patient = Patient(
            user_id=user.user_id,
            first_name=faker.first_name(),
            last_name=faker.last_name(),
            email=email,
            phone=faker.basic_phone_number(),
            dob=faker.date_of_birth(minimum_age=18, maximum_age=65),
            doctor_id=doctor_id,
            pharmacy_id=pharmacy_id,
        )
        db.session.add(patient)
        db.session.flush()
    
    db.session.commit()
    print("Users done")

def seed_posts(n=1000):
    for _ in range(n):
        created_at = faker.date_time_this_year()
        updated_at = created_at + timedelta(minutes=random.randint(0, 300))
        post = Post(
            user_id=faker.random_element(tuple(users["users"])),
            title=faker.sentence(),
            content=faker.text(max_nb_chars=500),
            created_at=faker.date_time_this_year(),
            updated_at=updated_at,
        )
        db.session.add(post)
        db.session.flush()
        users["posts"].append(post.post_id)

        for _ in range(faker.random_int(min=0, max=5)):
            created_at = faker.date_time_this_year()
            updated_at = created_at + timedelta(minutes=random.randint(0, 300))
            comment = Comment(
                post_id=post.post_id,
                user_id=faker.random_element(tuple(users["users"])),
                content=faker.text(max_nb_chars=200),
                created_at=created_at,
                updated_at=updated_at,
            )
            db.session.add(comment)
            db.session.flush()
    
    db.session.commit()
    print("Posts done")

def seed_reports(n=1000):
    for _ in range(n):
        report = Report(
            type=faker.random_element([ReportType.DAILY, ReportType.WEEKLY, ReportType.MONTHLY]),
            created_at=faker.date_time_this_year(),
        )
        db.session.add(report)
        db.session.flush()
        users["reports"].append(report.report_id)
        patient_id=faker.random_element(tuple(users["patients"]))
        doctor_id=user_relationship[patient_id][0]

        for _ in range(faker.random_int(min=0, max=5)):
            patient_report = PatientReport(
                report_id=report.report_id,
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
    for _ in range(n):
        medication = Medication(
            name=faker.text(max_nb_chars=50),
            description=faker.text(max_nb_chars=200),
        )
        db.session.add(medication)
        db.session.flush()
        users["medications"].append(medication.medication_id)

        for _ in range(faker.random_int(min=0, max=10)):
            inventory = Inventory(
                medication_id=medication.medication_id,
                quantity=faker.random_int(min=1, max=10),
                pharmacy_id=faker.random_element(tuple(users["pharmacies"])),
            )
            db.session.add(inventory)
            db.session.flush()
    
    db.session.commit()
    print("Medications done")

def seed_medical_records(n=400):
    for _ in range(n):
        medical_record = MedicalRecord(
            patient_id=faker.unique.random_element(tuple(users["patients"])),
            description=faker.text(max_nb_chars=200),
            created_at=faker.date_time_this_year(),
        )
        db.session.add(medical_record)
        db.session.flush()
    
    db.session.commit()
    print("Medical records done")

def seed_prescriptions(n=400):
    for _ in range(n):
        prescription = Prescription(
            patient_id=faker.random_element(tuple(users["patients"])),
            doctor_id=faker.random_element(tuple(users["doctors"])),
            amount=faker.random_number(digits=3, fix_len=False),
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

def seed_exercises(n=100):
    for _ in range(n):
        exercise = ExerciseBank(
            type_of_exercise=faker.unique.word(),
            description=faker.text(max_nb_chars=200),
        )
        db.session.add(exercise)
        db.session.flush()
        users["exercises"].append(exercise.exercise_id)

        for _ in range(faker.random_int(min=0, max=10)):
            patient_id = faker.random_element(tuple(users["patients"]))
            doctor_id = user_relationship[patient_id][0]
            if not doctor_id:
                continue
            patient_exercise = PatientExercise(
                exercise_id=exercise.exercise_id,
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
            treatment=faker.word(),
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
    seed_users()
    seed_posts()
    seed_reports()
    seed_medications()
    seed_medical_records()
    seed_prescriptions()
    seed_ratings()
    seed_invoices()
    seed_notifications()
    seed_exercises()
    seed_appointments()
    seed_messages()

if __name__ == "__main__":

    with db.session.begin_nested():
        seed_all()
        print("All data seeded")