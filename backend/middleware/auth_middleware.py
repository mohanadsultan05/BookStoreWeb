from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from database import db
from models.user import User


def _get_user_from_token():
    """Verify JWT and return the User object, or raise on failure."""
    verify_jwt_in_request()
    raw_id = get_jwt_identity()
    user = db.session.get(User, int(raw_id))
    return user


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            current_user = _get_user_from_token()
            if not current_user:
                return jsonify({'error': 'User not found'}), 401
            return f(current_user, *args, **kwargs)
        except Exception as e:
            return jsonify({'error': 'Invalid or expired token', 'details': str(e)}), 401
    return decorated


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            current_user = _get_user_from_token()
            if not current_user:
                return jsonify({'error': 'User not found'}), 401
            if current_user.role != 'admin':
                return jsonify({'error': 'Admin access required'}), 403
            return f(current_user, *args, **kwargs)
        except Exception as e:
            return jsonify({'error': 'Invalid or expired token', 'details': str(e)}), 401
    return decorated


def author_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            current_user = _get_user_from_token()
            if not current_user:
                return jsonify({'error': 'User not found'}), 401
            if current_user.role not in ('author', 'admin'):
                return jsonify({'error': 'Author or admin access required'}), 403
            return f(current_user, *args, **kwargs)
        except Exception as e:
            return jsonify({'error': 'Invalid or expired token', 'details': str(e)}), 401
    return decorated


def customer_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            current_user = _get_user_from_token()
            if not current_user:
                return jsonify({'error': 'User not found'}), 401
            if current_user.role != 'customer':
                return jsonify({'error': 'Customer access required'}), 403
            return f(current_user, *args, **kwargs)
        except Exception as e:
            return jsonify({'error': 'Invalid or expired token', 'details': str(e)}), 401
    return decorated
