from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from database import db
from models.user import User, Customer, Administrator, Author
from middleware.auth_middleware import token_required

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    for field in ('full_name', 'email', 'password', 'role'):
        if not data.get(field):
            return jsonify({'error': f'{field} is required'}), 400

    role = data['role'].lower()
    if role not in ('customer', 'admin', 'author'):
        return jsonify({'error': 'Role must be customer, admin, or author'}), 400

    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already registered'}), 409

    user = User(full_name=data['full_name'], email=data['email'], role=role)
    user.set_password(data['password'])
    db.session.add(user)
    db.session.flush()

    if role == 'customer':
        db.session.add(Customer(
            user_id=user.id,
            full_name=data['full_name'],
            address=data.get('address', ''),
            phone=data.get('phone', '')
        ))
    elif role == 'admin':
        db.session.add(Administrator(
            user_id=user.id,
            full_name=data['full_name'],
            admin_role=data.get('admin_role', 'Administrator')
        ))
    elif role == 'author':
        db.session.add(Author(
            user_id=user.id,
            author_name=data['full_name'],
            biography=data.get('biography', '')
        ))

    db.session.commit()
    token = create_access_token(identity=user.id)
    return jsonify({
        'message': 'Registration successful',
        'token': token,
        'user': user.to_dict()
    }), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    email = data.get('email', '').strip()
    password = data.get('password', '')
    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({'error': 'Invalid email or password'}), 401

    token = create_access_token(identity=user.id)
    user_data = user.to_dict()

    if user.role == 'customer' and user.customer_profile:
        user_data['profile'] = user.customer_profile.to_dict()
    elif user.role == 'author' and user.author_profile:
        user_data['profile'] = user.author_profile.to_dict()
    elif user.role == 'admin' and user.admin_profile:
        user_data['profile'] = user.admin_profile.to_dict()

    return jsonify({'message': 'Login successful', 'token': token, 'user': user_data}), 200


@auth_bp.route('/profile', methods=['GET'])
@token_required
def get_profile(current_user):
    user_data = current_user.to_dict()
    if current_user.role == 'customer' and current_user.customer_profile:
        user_data['profile'] = current_user.customer_profile.to_dict()
    elif current_user.role == 'author' and current_user.author_profile:
        user_data['profile'] = current_user.author_profile.to_dict()
    elif current_user.role == 'admin' and current_user.admin_profile:
        user_data['profile'] = current_user.admin_profile.to_dict()
    return jsonify({'user': user_data}), 200


@auth_bp.route('/profile', methods=['PUT'])
@token_required
def update_profile(current_user):
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    if data.get('full_name'):
        current_user.full_name = data['full_name']

    if current_user.role == 'customer' and current_user.customer_profile:
        p = current_user.customer_profile
        if 'address' in data:
            p.address = data['address']
        if 'phone' in data:
            p.phone = data['phone']
        if 'payment_info' in data:
            p.payment_info = data['payment_info']

    elif current_user.role == 'author' and current_user.author_profile:
        p = current_user.author_profile
        if 'biography' in data:
            p.biography = data['biography']
        if 'author_name' in data:
            p.author_name = data['author_name']

    db.session.commit()
    return jsonify({'message': 'Profile updated', 'user': current_user.to_dict()}), 200
