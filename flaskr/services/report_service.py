from flaskr.models import PatientReport
from flaskr.extensions import db

def get_patient_report_result(user_id, sort_by='created_at', order='asc'):
    if not hasattr(PatientReport, sort_by):
        raise ValueError(f"Invalid sort field: {sort_by}")

    column = getattr(PatientReport, sort_by)
    if order == 'desc':
        column = column.desc()
    reports = PatientReport.query.filter_by(patient_id=user_id).order_by(column).all()
    return [report.to_dict() for report in reports]

def add_patient_report(report_id, patient_id, doctor_id, height=None, weight=None,
                       calories_intake=None, hours_of_exercise=None, hours_of_sleep=None):
    new_report = PatientReport(
        report_id=report_id,
        patient_id=patient_id,
        doctor_id=doctor_id,
        height=height,
        weight=weight,
        calories_intake=calories_intake,
        hours_of_exercise=hours_of_exercise,
        hours_of_sleep=hours_of_sleep
    )
    db.session.add(new_report)
    db.session.commit()