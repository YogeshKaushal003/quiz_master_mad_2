import jwt
from flask import current_app
from flask_bcrypt import Bcrypt
from datetime import datetime, timedelta

bcrypt = Bcrypt()

def hash_password(password):
    return bcrypt.generate_password_hash(password).decode('utf-8')

def check_password(password, hashed):
    return bcrypt.check_password_hash(hashed, password)

def generate_jwt(user_id):
    expiration = datetime.utcnow() + timedelta(seconds=current_app.config['JWT_EXPIRATION_DELTA'])
    token = jwt.encode({
        'user_id': user_id,
        'exp': expiration
    }, current_app.config['SECRET_KEY'], algorithm=current_app.config['JWT_ALGORITHM'])
    return token
