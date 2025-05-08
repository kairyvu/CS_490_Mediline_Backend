import os
from datetime import datetime, timedelta, timezone

from flask import current_app, jsonify
from flask_jwt_extended import create_access_token
from flaskr.models import User
from flaskr.extensions import db

def user_id_credentials(username, password):
    user: User = User.authenticate(username=username, password=password)

    if user:
        token = create_access_token(
            identity=user,
            fresh=timedelta(minutes=10),
            expires_delta=False \
                if (current_app.config['FLASK_ENV'] == 'development')
                else timedelta(minutes=30),
            additional_claims={
                'acct_type': user.account_type.name
            }
        )
        return {'token': token}
    return None