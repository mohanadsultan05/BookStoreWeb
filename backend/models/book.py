from datetime import datetime
from database import db


class Book(db.Model):
    __tablename__ = 'books'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    isbn = db.Column(db.String(50), unique=True)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    stock_quantity = db.Column(db.Integer, default=0)
    rating = db.Column(db.Numeric(3, 2), default=0.0)
    image_url = db.Column(db.String(255))
    author_id = db.Column(db.Integer, db.ForeignKey('authors.id', ondelete='SET NULL'), nullable=True)
    genre_id = db.Column(db.Integer, db.ForeignKey('genres.id', ondelete='SET NULL'), nullable=True)
    admin_id = db.Column(db.Integer, db.ForeignKey('administrators.id', ondelete='SET NULL'), nullable=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    order_items = db.relationship('OrderItem', backref='book', lazy=True)
    cart_items = db.relationship('CartItem', backref='book', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'isbn': self.isbn,
            'price': float(self.price) if self.price is not None else 0,
            'stock_quantity': self.stock_quantity,
            'rating': float(self.rating) if self.rating is not None else 0,
            'image_url': self.image_url,
            'author_id': self.author_id,
            'author_name': self.author.author_name if self.author else None,
            'genre_id': self.genre_id,
            'genre_name': self.genre.genre_name if self.genre else None,
            'admin_id': self.admin_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
