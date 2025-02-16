from functools import wraps
from flask import request, jsonify
import jwt
from config import Config
from models.model import User

# Token Required Decorator
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Check if token is present in Authorization header
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]
        
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        
        try:
            # Decode the token using the secret key
            data = jwt.decode(token, Config.SECRET_KEY, algorithms=["HS256"])
            current_user = User.query.filter_by(id=data['user_id']).first()
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token!'}), 401
        
        # Pass the user to the endpoint
        return f(current_user, *args, **kwargs)
    
    return decorated

# Admin Required Decorator
def admin_required(f):
    @wraps(f)
    def decorated(current_user, *args, **kwargs):
        # Check if the current user is admin
        if not current_user.is_admin:
            return jsonify({'message': 'Admin access required!'}), 403
        
        # Allow access if user is admin
        return f(current_user, *args, **kwargs)
    
    return decorated
