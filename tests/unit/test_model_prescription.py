from datetime import datetime
from flaskr.models import PrescriptionMedication 
from flaskr.struct import PrescriptionStatus

def test_prescription(rx1):
    assert rx1.patient_id != rx1.doctor_id
    assert rx1.status == PrescriptionStatus.UNPAID
    assert isinstance(rx1.to_dict(), dict)
    
def test_rx_med(rx1, med1):
    rx_med = PrescriptionMedication(
        prescription_medication_id=1,
        prescription_id=1,
        medication_id=1,
        dosage=2,
        medical_instructions='',
        taken_date=datetime.now(),
        duration=3
    )
    rx_med.prescription = rx1
    rx_med.medication = med1

    assert isinstance(rx_med.to_dict(), dict)
    
def test_inventory(inv1, pharm1, med1):
    _, p, _ = pharm1
    inv1.pharmacy = p
    inv1.medication = med1

    assert inv1.pharmacy.user_id == p.user_id
    assert inv1.medication.medication_id == med1.medication_id

    assert isinstance(inv1.to_dict(), dict)