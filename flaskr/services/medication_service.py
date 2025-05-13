from flaskr.extensions import db
from flaskr.models import Medication, Inventory

def all_meds(sort_by='medication_id', order='asc'):
    if not hasattr(Medication, sort_by):
        raise ValueError(f"Invalid sort field: {sort_by}")
    column = getattr(Medication, sort_by)
    if order.lower() == 'desc':
        column = column.desc()
    elif order.lower() == 'asc':
        column = column.asc()
    else:
        raise ValueError(f"Invalid order: {order}")
    meds = db.paginate(
        db.select(Medication)
        .order_by(column), error_out=False)
    return [med.to_dict() for med in meds]

def medication_info(medication_id):
    medication = Medication.query.filter_by(medication_id=medication_id).first()
    if not medication:
        return None

    inventories = Inventory.query.filter_by(medication_id=medication_id).all()

    inventory_data = []
    for inventory in inventories:
        inventory_data.append({
            "inventory_id": inventory.inventory_id,
            "pharmacy_id": inventory.pharmacy_id,
            "quantity": inventory.quantity,
            "expiration_date": inventory.expiration_date.strftime("%Y-%m-%d")
        })

    return {
        "medication_id": medication.medication_id,
        "name": medication.name,
        "description": medication.description,
        "inventories": inventory_data
    }
