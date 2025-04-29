import time
from datetime import datetime
from celery import shared_task
from flaskr.extensions import db
from flaskr.models import Prescription, PrescriptionMedication
from flaskr.struct import PrescriptionStatus

@shared_task(ignore_result=False)
def my_task(m1: str, m2: str):
    #time.sleep(5)
    print(f'm1 is {m1}')
    #time.sleep(5)
    print(f'm2 is {m2}')
    #time.sleep(5)
    return ' '.join([m1, m2])

@shared_task(ignore_result=False)
def send_rx(pharmacy_id, patient_id, doctor_id, medications):
    # 1) create entry in prescription table
    new_rx = Prescription(
        patient_id=patient_id,
        doctor_id=doctor_id,
        pharmacy_id=pharmacy_id,
        amount=0,
        status=PrescriptionStatus.UNPAID
    )
    db.session.add(new_rx)
    # Flush to get new prescription id
    try:
        db.session.flush()
    except Exception as e:
        raise e
    # 2) for each medication, create entry in rx-med table
    for med in medications:
        new_pt_rx_request = PrescriptionMedication(
            prescription_id=new_rx.prescription_id,
            medication_id=med['medication_id'],
            dosage=med['dosage'],
            medical_instructions=med['instructions'],
            taken_date=datetime.now(),      # what is this supposed to be?
            duration=20
        )
        db.session.add(new_pt_rx_request)
        try:
            db.session.flush()
        except Exception as e:
            raise e
    try:
        db.session.commit()
    except Exception as e:
        raise e
    return new_rx.prescription_id
    