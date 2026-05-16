from datetime import datetime
from database import db
import bcrypt


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum('customer', 'author', 'admin'), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    # One-to-one reverse relationships (defined here for convenience)
    customer_profile = db.relationship('Customer', backref='user', uselist=False, cascade='all, delete-orphan', foreign_keys='Customer.user_id')
    admin_profile = db.relationship('Administrator', backref='user', uselist=False, cascade='all, delete-orphan', foreign_keys='Administrator.user_id')
    author_profile = db.relationship('Author', backref='user', uselist=False, cascade='all, delete-orphan', foreign_keys='Author.user_id')

    def set_password(self, password):
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def check_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))

    def to_dict(self):
        return {
            'id': self.id,
            'full_name': self.full_name,
            'email': self.email,
            'role': self.role,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Customer(db.Model):
    __tablename__ = 'customers'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), unique=True, nullable=False)
    full_name = db.Column(db.String(100))
    address = db.Column(db.String(255))
    phone = db.Column(db.String(20))
    payment_info = db.Column(db.String(255))

    orders = db.relationship('Order', backref='customer', lazy=True, cascade='all, delete-orphan')
    cart_items = db.relationship('CartItem', backref='customer', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'address': self.address,
            'phone': self.phone,
            'payment_info': self.payment_info
        }


class Administrator(db.Model):
    __tablename__ = 'administrators'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), unique=True, nullable=False)
    full_name = db.Column(db.String(100))
    admin_role = db.Column(db.String(50), default='Administrator')

    managed_books = db.relationship('Book', backref='admin', lazy=True, foreign_keys='Book.admin_id')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'admin_role': self.admin_role
        }


class Author(db.Model):
    __tablename__ = 'authors'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), unique=True, nullable=True)
    author_name = db.Column(db.String(100), nullable=False)
    biography = db.Column(db.Text)

    books = db.relationship('Book', backref='author', lazy=True, foreign_keys='Book.author_id')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'author_name': self.author_name,
            'biography': self.biography
        }
