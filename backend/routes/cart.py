from flask import Blueprint, request, jsonify
from database import db
from models.cart import CartItem
from models.book import Book
from models.user import Customer
from middleware.auth_middleware import token_required

cart_bp = Blueprint('cart', __name__)


def _get_customer(user):
    customer = Customer.query.filter_by(user_id=user.id).first()
    if not customer:
        return None, (jsonify({'error': 'Customer profile not found'}), 404)
    return customer, None


@cart_bp.route('', methods=['GET'])
@token_required
def get_cart(current_user):
    customer, err = _get_customer(current_user)
    if err:
        return err

    items = CartItem.query.filter_by(customer_id=customer.id).all()
    total = sum(float(i.book.price) * i.quantity for i in items if i.book)
    return jsonify({
        'items': [i.to_dict() for i in items],
        'total': round(total, 2),
        'count': len(items)
    }), 200


@cart_bp.route('/add', methods=['POST'])
@token_required
def add_to_cart(current_user):
    if current_user.role != 'customer':
        return jsonify({'error': 'Only customers can use the cart'}), 403

    customer, err = _get_customer(current_user)
    if err:
        return err

    data = request.get_json()
    if not data or not data.get('book_id'):
        return jsonify({'error': 'book_id is required'}), 400

    book = Book.query.get(data['book_id'])
    if not book:
        return jsonify({'error': 'Book not found'}), 404

    quantity = int(data.get('quantity', 1))
    if quantity < 1:
        return jsonify({'error': 'Quantity must be at least 1'}), 400
    if book.stock_quantity < quantity:
        return jsonify({'error': 'Insufficient stock'}), 400

    existing = CartItem.query.filter_by(customer_id=customer.id, book_id=book.id).first()
    if existing:
        new_qty = existing.quantity + quantity
        if book.stock_quantity < new_qty:
            return jsonify({'error': 'Insufficient stock'}), 400
        existing.quantity = new_qty
    else:
        db.session.add(CartItem(customer_id=customer.id, book_id=book.id, quantity=quantity))

    db.session.commit()
    return jsonify({'message': 'Added to cart'}), 201


@cart_bp.route('/<int:item_id>', methods=['PUT'])
@token_required
def update_cart_item(current_user, item_id):
    customer, err = _get_customer(current_user)
    if err:
        return err

    item = CartItem.query.filter_by(id=item_id, customer_id=customer.id).first_or_404()
    data = request.get_json()
    quantity = int(data.get('quantity', item.quantity))
    if quantity < 1:
        return jsonify({'error': 'Quantity must be at least 1'}), 400
    if item.book and item.book.stock_quantity < quantity:
        return jsonify({'error': 'Insufficient stock'}), 400

    item.quantity = quantity
    db.session.commit()
    return jsonify({'message': 'Cart updated', 'item': item.to_dict()}), 200


@cart_bp.route('/<int:item_id>', methods=['DELETE'])
@token_required
def remove_from_cart(current_user, item_id):
    customer, err = _get_customer(current_user)
    if err:
        return err

    item = CartItem.query.filter_by(id=item_id, customer_id=customer.id).first_or_404()
    db.session.delete(item)
    db.session.commit()
    return jsonify({'message': 'Item removed from cart'}), 200


@cart_bp.route('/clear', methods=['DELETE'])
@token_required
def clear_cart(current_user):
    customer, err = _get_customer(current_user)
    if err:
        return err

    CartItem.query.filter_by(customer_id=customer.id).delete()
    db.session.commit()
    return jsonify({'message': 'Cart cleared'}), 200
