import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your_secret_key_here')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///quiz_master_v2.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_ALGORITHM = 'HS256'
    JWT_EXPIRATION_DELTA = 3600  # Token validity in seconds
