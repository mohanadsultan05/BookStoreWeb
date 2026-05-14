from flask import Blueprint, request, jsonify
from database import db
from models.user import User, Customer, Administrator, Author
from models.book import Book
from models.order import Order, OrderItem
from models.payment import Payment
from models.genre import Genre
from middleware.auth_middleware import admin_required

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/dashboard', methods=['GET'])
@admin_required
def dashboard(current_user):
    total_users = User.query.count()
    total_customers = User.query.filter_by(role='customer').count()
    total_authors = User.query.filter_by(role='author').count()
    total_books = Book.query.count()
    total_orders = Order.query.count()
    total_genres = Genre.query.count()
    pending_orders = Order.query.filter_by(order_status='Pending').count()
    completed_orders = Order.query.filter_by(order_status='Completed').count()
    processing_orders = Order.query.filter_by(order_status='Processing').count()

    total_revenue = db.session.query(
        db.func.sum(Payment.amount)
    ).filter_by(payment_status='Paid').scalar() or 0

    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(5).all()
    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    low_stock = Book.query.filter(Book.stock_quantity <= 5).order_by(Book.stock_quantity).limit(5).all()

    return jsonify({
        'stats': {
            'total_users': total_users,
            'total_customers': total_customers,
            'total_authors': total_authors,
            'total_books': total_books,
            'total_orders': total_orders,
            'total_genres': total_genres,
            'pending_orders': pending_orders,
            'processing_orders': processing_orders,
            'completed_orders': completed_orders,
            'total_revenue': float(total_revenue)
        },
        'recent_orders': [o.to_dict() for o in recent_orders],
        'recent_users': [u.to_dict() for u in recent_users],
        'low_stock_books': [b.to_dict() for b in low_stock]
    }), 200


@admin_bp.route('/users', methods=['GET'])
@admin_required
def get_users(current_user):
    role = request.args.get('role')
    query = User.query
    if role:
        query = query.filter_by(role=role)
    users = query.order_by(User.created_at.desc()).all()
    result = []
    for u in users:
        data = u.to_dict()
        if u.role == 'customer' and u.customer_profile:
            data['profile'] = u.customer_profile.to_dict()
        elif u.role == 'author' and u.author_profile:
            data['profile'] = u.author_profile.to_dict()
        result.append(data)
    return jsonify({'users': result}), 200


@admin_bp.route('/users/<int:user_id>', methods=['DELETE'])
@admin_required
def delete_user(current_user, user_id):
    if user_id == current_user.id:
        return jsonify({'error': 'Cannot delete yourself'}), 400
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'User deleted'}), 200


@admin_bp.route('/books', methods=['GET'])
@admin_required
def get_all_books(current_user):
    books = Book.query.order_by(Book.created_at.desc()).all()
    return jsonify({'books': [b.to_dict() for b in books]}), 200


@admin_bp.route('/books/<int:book_id>/stock', methods=['PUT'])
@admin_required
def update_stock(current_user, book_id):
    book = Book.query.get_or_404(book_id)
    data = request.get_json()
    if 'stock_quantity' not in data:
        return jsonify({'error': 'stock_quantity is required'}), 400
    book.stock_quantity = max(0, int(data['stock_quantity']))
    db.session.commit()
    return jsonify({'message': 'Stock updated', 'book': book.to_dict()}), 200


@admin_bp.route('/orders', methods=['GET'])
@admin_required
def get_all_orders(current_user):
    status = request.args.get('status')
    query = Order.query
    if status:
        query = query.filter_by(order_status=status)
    orders = query.order_by(Order.created_at.desc()).all()
    return jsonify({'orders': [o.to_dict() for o in orders]}), 200


@admin_bp.route('/payments', methods=['GET'])
@admin_required
def get_all_payments(current_user):
    payments = Payment.query.order_by(Payment.payment_date.desc()).all()
    return jsonify({'payments': [p.to_dict() for p in payments]}), 200


@admin_bp.route('/reports', methods=['GET'])
@admin_required
def get_reports(current_user):
    # Sales per genre
    genre_sales = db.session.query(
        Genre.genre_name,
        db.func.coalesce(db.func.sum(OrderItem.quantity), 0).label('units'),
        db.func.coalesce(db.func.sum(OrderItem.unit_price * OrderItem.quantity), 0).label('revenue')
    ).outerjoin(Book, Book.genre_id == Genre.id).outerjoin(
        OrderItem, OrderItem.book_id == Book.id
    ).group_by(Genre.genre_name).all()

    # Top selling books
    top_books = db.session.query(
        Book.id, Book.title,
        db.func.sum(OrderItem.quantity).label('units')
    ).join(OrderItem, OrderItem.book_id == Book.id).group_by(
        Book.id, Book.title
    ).order_by(db.desc('units')).limit(10).all()

    return jsonify({
        'genre_sales': [
            {'genre': r.genre_name, 'units': int(r.units), 'revenue': float(r.revenue)}
            for r in genre_sales
        ],
        'top_books': [
            {'id': r.id, 'title': r.title, 'units_sold': int(r.units)}
            for r in top_books
        ]
    }), 200
