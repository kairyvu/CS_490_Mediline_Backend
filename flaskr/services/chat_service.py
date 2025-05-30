from datetime import datetime, timezone
from flask import Response
from flaskr.struct import AppointmentStatus
from flaskr.models import User, Chat, Message, Appointment
from flaskr.services import assign_invoice_appoinmtnet, update_appointment
from flaskr.extensions import db

def get_current_chat(appointment_id, requesting_user: User|None=None):
    from flaskr.services import UnauthorizedError
    chat: Chat = Chat.query.filter_by(appointment_id=appointment_id).first()
    if not chat:
        raise ValueError("Chat not found")
    chat_pt = chat.appointment.patient_id
    chat_dr = chat.appointment.doctor_id
    if requesting_user:
        match requesting_user.account_type.name:
            case 'SuperUser':
                pass
            case 'Patient' if requesting_user.user_id == chat_pt:
                pass
            case 'Doctor' if requesting_user.user_id == chat_dr:
                pass
            case _:
                raise UnauthorizedError
    else:
        raise UnauthorizedError
    
    return chat.to_dict()

def add_message(appointment_id, user_id, message_content):
    appointment = Appointment.query.filter_by(appointment_id=appointment_id).first()
    if not appointment:
        return None
    
    chat = Chat.query.filter_by(appointment_id=appointment_id).first()

    if not chat:
        chat = Chat(appointment_id=appointment_id)
        db.session.add(chat)
        db.session.flush()

    message = Message(
        chat_id=chat.chat_id,
        user_id=user_id,
        message_content=message_content,
        time=datetime.now()
    )

    db.session.add(message)
    db.session.commit()

    return {
        "chat_id": chat.chat_id,
        "message_id": message.message_id,
        "user_id": user_id,
        "message": message_content,
        "timestamp": message.time.strftime("%Y-%m-%d %I:%M %p")
    }

def handle_meeting_end(appointment_id):
    appt: Appointment = Appointment.query.filter_by(appointment_id=appointment_id).first()
    appt_dts: dict = appt.appointment_detail.to_dict()
    appt_dr = appt.doctor.user
    dr_id = appt.doctor_id
    pt_id = appt.patient_id
    try:
        update_appointment(
            appointment_id, 
            treatment=appt_dts.get('treatment'),
            start_date=appt_dts.get('start_date', datetime.now(tz=timezone.utc).isoformat()), 
            status=AppointmentStatus.COMPLETED.name,
            end_date=datetime.now(tz=timezone.utc).isoformat(),
            requesting_user=appt_dr
        )
    except Exception as e:
        print(str(e))
    finally:
        try:
            res: Response = assign_invoice_appoinmtnet(dr_id, appointment_id, pt_id, appt_dr)
        except Exception as e:
            print(str(e))
        else:
            return
        

