from flask import Blueprint, request, jsonify
from extensions import db
from models.model import User
from auth.utils import generate_jwt, check_password, hash_password
from datetime import datetime

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    full_name = data.get('full_name')
    qualification = data.get('qualification')
    dob_str  = data.get('dob')

    dob = datetime.strptime(dob_str, '%Y-%m-%d').date()

    # Check if the user already exists
    if User.query.filter_by(email=email).first():
        return jsonify({'message': 'User already exists'}), 409

    # Hash the password
    hashed_password = hash_password(password)

    # Create a new user
    new_user = User(
        email=email,
        password=hashed_password,
        full_name=full_name,
        qualification=qualification,
        dob=dob
    )
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'User registered successfully'}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    # Find the user by email
    user = User.query.filter_by(email=email).first()

    # Check if the user exists and password is correct
    if not user or not check_password(password, user.password):
        return jsonify({'message': 'Invalid email or password'}), 401

    # Generate JWT token
    token = generate_jwt(user.id)

    return jsonify({'token': token}), 200
