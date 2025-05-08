from flaskr.models import Medication, Inventory

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
