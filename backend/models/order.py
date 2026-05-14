from database import db


class Order(db.Model):
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id', ondelete='CASCADE'), nullable=False)
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)
    order_status = db.Column(
        db.Enum('Pending', 'Processing', 'Completed'),
        nullable=False,
        default='Pending'
    )
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    items = db.relationship('OrderItem', backref='order', lazy=True, cascade='all, delete-orphan')
    payment = db.relationship('Payment', backref='order', uselist=False, cascade='all, delete-orphan')

    def to_dict(self):
        customer_name = None
        if self.customer and self.customer.user:
            customer_name = self.customer.user.full_name
        return {
            'id': self.id,
            'customer_id': self.customer_id,
            'customer_name': customer_name,
            'total_amount': float(self.total_amount) if self.total_amount is not None else 0,
            'order_status': self.order_status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'items': [item.to_dict() for item in self.items],
            'payment': self.payment.to_dict() if self.payment else None
        }


class OrderItem(db.Model):
    __tablename__ = 'order_items'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id', ondelete='CASCADE'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id', ondelete='CASCADE'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Numeric(10, 2), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'order_id': self.order_id,
            'book_id': self.book_id,
            'book_title': self.book.title if self.book else None,
            'book_image': self.book.image_url if self.book else None,
            'quantity': self.quantity,
            'unit_price': float(self.unit_price) if self.unit_price is not None else 0
        }
