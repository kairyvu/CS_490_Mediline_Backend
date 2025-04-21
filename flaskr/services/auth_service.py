from flaskr.models import User
from flaskr.extensions import db

def user_id_credentials(username, password):
    user = User.query.filter_by(username=username, password=password).first()
    if user:
        return {
            "user_id": user.user_id,
            "account_type": user.account_type.value,
        }
    return None