from flask import Blueprint, request, jsonify
from database import db
from models.payment import Payment
from models.order import Order
from models.user import Customer
from middleware.auth_middleware import token_required, admin_required

payments_bp = Blueprint('payments', __name__)

VALID_METHODS = ('Credit Card', 'PayPal', 'Cash')


def _get_customer(user):
    return Customer.query.filter_by(user_id=user.id).first()


@payments_bp.route('', methods=['POST'])
@token_required
def make_payment(current_user):
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    order_id = data.get('order_id')
    payment_method = data.get('payment_method')

    if not order_id or not payment_method:
        return jsonify({'error': 'order_id and payment_method are required'}), 400

    if payment_method not in VALID_METHODS:
        return jsonify({'error': f'Payment method must be one of: {", ".join(VALID_METHODS)}'}), 400

    order = Order.query.get(order_id)
    if not order:
        return jsonify({'error': 'Order not found'}), 404

    # Verify ownership
    if current_user.role != 'admin':
        customer = _get_customer(current_user)
        if not customer or order.customer_id != customer.id:
            return jsonify({'error': 'Not authorized'}), 403

    if order.order_status == 'Completed':
        return jsonify({'error': 'Order already completed'}), 400

    if order.payment:
        return jsonify({'error': 'Payment already exists for this order'}), 409

    payment = Payment(
        order_id=order.id,
        payment_method=payment_method,
        payment_status='Paid',
        amount=order.total_amount
    )
    db.session.add(payment)

    # Update order status (mirrors the DB trigger trg_update_order_status)
    order.order_status = 'Completed'
    db.session.commit()

    return jsonify({
        'message': 'Payment successful',
        'payment': payment.to_dict(),
        'order': order.to_dict()
    }), 201


@payments_bp.route('/<int:payment_id>', methods=['GET'])
@token_required
def get_payment(current_user, payment_id):
    payment = Payment.query.get_or_404(payment_id)
    order = Order.query.get(payment.order_id)
    if current_user.role != 'admin':
        customer = _get_customer(current_user)
        if not customer or order.customer_id != customer.id:
            return jsonify({'error': 'Not authorized'}), 403
    return jsonify({'payment': payment.to_dict()}), 200


@payments_bp.route('/order/<int:order_id>', methods=['GET'])
@token_required
def get_order_payment(current_user, order_id):
    order = Order.query.get_or_404(order_id)
    if current_user.role != 'admin':
        customer = _get_customer(current_user)
        if not customer or order.customer_id != customer.id:
            return jsonify({'error': 'Not authorized'}), 403
    return jsonify({'payment': order.payment.to_dict() if order.payment else None}), 200


@payments_bp.route('', methods=['GET'])
@admin_required
def get_all_payments(current_user):
    payments = Payment.query.order_by(Payment.payment_date.desc()).all()
    return jsonify({'payments': [p.to_dict() for p in payments]}), 200
