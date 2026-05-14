from flask import Blueprint, request, jsonify
from database import db
from models.order import Order, OrderItem
from models.cart import CartItem
from models.book import Book
from models.user import Customer
from middleware.auth_middleware import token_required, admin_required

orders_bp = Blueprint('orders', __name__)


def _get_customer(user):
    customer = Customer.query.filter_by(user_id=user.id).first()
    if not customer:
        return None, (jsonify({'error': 'Customer profile not found'}), 404)
    return customer, None


@orders_bp.route('', methods=['GET'])
@token_required
def get_orders(current_user):
    if current_user.role == 'admin':
        orders = Order.query.order_by(Order.created_at.desc()).all()
    else:
        customer, err = _get_customer(current_user)
        if err:
            return err
        orders = Order.query.filter_by(customer_id=customer.id).order_by(Order.created_at.desc()).all()

    return jsonify({'orders': [o.to_dict() for o in orders]}), 200


@orders_bp.route('/<int:order_id>', methods=['GET'])
@token_required
def get_order(current_user, order_id):
    order = Order.query.get_or_404(order_id)
    if current_user.role != 'admin':
        customer, err = _get_customer(current_user)
        if err:
            return err
        if order.customer_id != customer.id:
            return jsonify({'error': 'Not authorized'}), 403
    return jsonify({'order': order.to_dict()}), 200


@orders_bp.route('', methods=['POST'])
@token_required
def create_order(current_user):
    if current_user.role != 'customer':
        return jsonify({'error': 'Only customers can place orders'}), 403

    customer, err = _get_customer(current_user)
    if err:
        return err

    cart_items = CartItem.query.filter_by(customer_id=customer.id).all()
    if not cart_items:
        return jsonify({'error': 'Cart is empty'}), 400

    total = 0.0
    prepared = []

    for ci in cart_items:
        book = Book.query.get(ci.book_id)
        if not book:
            return jsonify({'error': f'Book {ci.book_id} not found'}), 404
        if book.stock_quantity < ci.quantity:
            return jsonify({'error': f'Insufficient stock for "{book.title}"'}), 400
        total += float(book.price) * ci.quantity
        prepared.append({'book': book, 'quantity': ci.quantity, 'price': book.price})

    order = Order(
        customer_id=customer.id,
        total_amount=round(total, 2),
        order_status='Pending'
    )
    db.session.add(order)
    db.session.flush()

    for item in prepared:
        db.session.add(OrderItem(
            order_id=order.id,
            book_id=item['book'].id,
            quantity=item['quantity'],
            unit_price=item['price']
        ))
        item['book'].stock_quantity -= item['quantity']

    for ci in cart_items:
        db.session.delete(ci)

    db.session.commit()
    return jsonify({'message': 'Order placed successfully', 'order': order.to_dict()}), 201


@orders_bp.route('/<int:order_id>/status', methods=['PUT'])
@admin_required
def update_order_status(current_user, order_id):
    order = Order.query.get_or_404(order_id)
    data = request.get_json()
    valid_statuses = ('Pending', 'Processing', 'Completed')
    status = data.get('order_status')
    if status not in valid_statuses:
        return jsonify({'error': f'Status must be one of {valid_statuses}'}), 400
    order.order_status = status
    db.session.commit()
    return jsonify({'message': 'Order status updated', 'order': order.to_dict()}), 200
