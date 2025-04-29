from datetime import datetime, timedelta, timezone
import jwt

from flask import current_app, jsonify
from flaskr.models import User
from flaskr.extensions import db

def user_id_credentials(username, password):
    user: User = User.authenticate(username=username, password=password)

    if user:
        token = jwt.encode({
            'sub': user.username,
            'iat': str(datetime.now(tz=timezone.utc)),
            'exp': str(datetime.now(tz=timezone.utc) + timedelta(minutes=30)),
            'user_id': user.user_id,
            'account_type': user.account_type.value
        }, current_app.config['SECRET_KEY'])
        return {'token': token}
    return None