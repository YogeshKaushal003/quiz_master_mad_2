from flask import Blueprint, jsonify
from auth.auth_middleware import token_required, admin_required

protected_bp = Blueprint('protected', __name__)

# Test route for general user access
@protected_bp.route('/user', methods=['GET'])
@token_required
def user_dashboard(current_user):
    return jsonify({'message': f'Welcome {current_user.full_name}, you are authenticated!'})

# Test route for admin-only access
@protected_bp.route('/admin', methods=['GET'])
@token_required
@admin_required
def admin_dashboard(current_user):
    return jsonify({'message': f'Welcome {current_user.full_name}, you are an admin!'})
