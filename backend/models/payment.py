from database import db


class Payment(db.Model):
    __tablename__ = 'payments'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id', ondelete='CASCADE'), unique=True, nullable=False)
    payment_method = db.Column(
        db.Enum('Credit Card', 'PayPal', 'Cash'),
        nullable=False
    )
    payment_status = db.Column(
        db.Enum('Pending', 'Paid', 'Failed'),
        nullable=False,
        default='Pending'
    )
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    payment_date = db.Column(db.DateTime, server_default=db.func.now())

    def to_dict(self):
        return {
            'id': self.id,
            'order_id': self.order_id,
            'payment_method': self.payment_method,
            'payment_status': self.payment_status,
            'amount': float(self.amount) if self.amount is not None else 0,
            'payment_date': self.payment_date.isoformat() if self.payment_date else None
        }
