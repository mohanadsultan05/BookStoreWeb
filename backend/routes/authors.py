from flask import Blueprint, request, jsonify
from database import db
from models.user import Author, User
from models.book import Book
from models.order import OrderItem
from middleware.auth_middleware import token_required, admin_required

authors_bp = Blueprint('authors', __name__)


@authors_bp.route('', methods=['GET'])
def get_authors():
    authors = Author.query.all()
    result = []
    for a in authors:
        data = a.to_dict()
        data['book_count'] = Book.query.filter_by(author_id=a.id).count()
        result.append(data)
    return jsonify({'authors': result}), 200


@authors_bp.route('/<int:author_id>', methods=['GET'])
def get_author(author_id):
    author = Author.query.get_or_404(author_id)
    data = author.to_dict()
    data['books'] = [b.to_dict() for b in Book.query.filter_by(author_id=author_id).all()]
    return jsonify({'author': data}), 200


@authors_bp.route('/<int:author_id>/books', methods=['GET'])
def get_author_books(author_id):
    Author.query.get_or_404(author_id)
    books = Book.query.filter_by(author_id=author_id).all()
    return jsonify({'books': [b.to_dict() for b in books]}), 200


@authors_bp.route('/me/stats', methods=['GET'])
@token_required
def get_my_stats(current_user):
    if current_user.role not in ('author', 'admin'):
        return jsonify({'error': 'Author or admin access required'}), 403

    author_record = Author.query.filter_by(user_id=current_user.id).first()
    if not author_record:
        return jsonify({'error': 'Author profile not found'}), 404

    return _build_stats(author_record)


@authors_bp.route('/<int:author_id>/stats', methods=['GET'])
@token_required
def get_author_stats(current_user, author_id):
    if current_user.role == 'author':
        my_record = Author.query.filter_by(user_id=current_user.id).first()
        if not my_record or my_record.id != author_id:
            return jsonify({'error': 'Not authorized'}), 403

    author = Author.query.get_or_404(author_id)
    return _build_stats(author)


def _build_stats(author):
    books = Book.query.filter_by(author_id=author.id).all()
    total_sales = 0
    total_revenue = 0.0
    book_stats = []

    for book in books:
        items = OrderItem.query.filter_by(book_id=book.id).all()
        qty_sold = sum(i.quantity for i in items)
        revenue = sum(float(i.unit_price) * i.quantity for i in items)
        total_sales += qty_sold
        total_revenue += revenue
        book_stats.append({
            'book': book.to_dict(),
            'units_sold': qty_sold,
            'revenue': round(revenue, 2)
        })

    return jsonify({
        'author': author.to_dict(),
        'total_books': len(books),
        'total_units_sold': total_sales,
        'total_revenue': round(total_revenue, 2),
        'book_stats': book_stats
    }), 200
