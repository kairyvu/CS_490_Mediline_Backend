from flaskr.models.payment import Invoice

def get_invoices_by_user(user_id, sort_by='created_at', order='desc'):
    if not hasattr(Invoice, sort_by):
        raise ValueError(f"Invalid sort field: {sort_by}")
    
    column = getattr(Invoice, sort_by)
    if order == 'desc':
        column = column.desc()
    invoices = Invoice.query.filter_by(patient_id=user_id).order_by(column).all()
    return [invoice.to_dict() for invoice in invoices]