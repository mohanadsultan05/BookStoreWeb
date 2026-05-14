from flask import Blueprint, request, jsonify
from database import db
from models.book import Book
from models.user import Author
from models.genre import Genre
from middleware.auth_middleware import token_required, admin_required, author_required

books_bp = Blueprint('books', __name__)


@books_bp.route('', methods=['GET'])
def get_books():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 12, type=int)
    search = request.args.get('search', '').strip()
    genre_id = request.args.get('genre_id', type=int)
    author_id = request.args.get('author_id', type=int)
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)

    query = Book.query

    if search:
        matching_author_ids = [
            a.id for a in Author.query.filter(Author.author_name.ilike(f'%{search}%')).all()
        ]
        matching_genre_ids = [
            g.id for g in Genre.query.filter(Genre.genre_name.ilike(f'%{search}%')).all()
        ]
        query = query.filter(
            db.or_(
                Book.title.ilike(f'%{search}%'),
                Book.description.ilike(f'%{search}%'),
                Book.author_id.in_(matching_author_ids),
                Book.genre_id.in_(matching_genre_ids)
            )
        )

    if genre_id:
        query = query.filter_by(genre_id=genre_id)
    if author_id:
        query = query.filter_by(author_id=author_id)
    if min_price is not None:
        query = query.filter(Book.price >= min_price)
    if max_price is not None:
        query = query.filter(Book.price <= max_price)

    pagination = query.order_by(Book.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return jsonify({
        'books': [b.to_dict() for b in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page,
        'per_page': per_page
    }), 200


@books_bp.route('/<int:book_id>', methods=['GET'])
def get_book(book_id):
    book = Book.query.get_or_404(book_id)
    return jsonify({'book': book.to_dict()}), 200


@books_bp.route('', methods=['POST'])
@author_required
def create_book(current_user):
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    if not data.get('title') or data.get('price') is None:
        return jsonify({'error': 'title and price are required'}), 400

    if data.get('isbn') and Book.query.filter_by(isbn=data['isbn']).first():
        return jsonify({'error': 'ISBN already exists'}), 409

    # Resolve author_id from Author table
    if current_user.role == 'admin':
        # Admin can specify any author_id (authors.id)
        author_id = data.get('author_id')
    else:
        author_record = Author.query.filter_by(user_id=current_user.id).first()
        if not author_record:
            return jsonify({'error': 'Author profile not found'}), 404
        author_id = author_record.id

    # Resolve admin_id from Administrator table
    admin_id = None
    if current_user.role == 'admin' and current_user.admin_profile:
        admin_id = current_user.admin_profile.id

    book = Book(
        title=data['title'],
        description=data.get('description', ''),
        isbn=data.get('isbn'),
        price=data['price'],
        stock_quantity=data.get('stock_quantity', 0),
        image_url=data.get('image_url', ''),
        author_id=author_id,
        genre_id=data.get('genre_id'),
        admin_id=admin_id
    )
    db.session.add(book)
    db.session.commit()
    return jsonify({'message': 'Book created', 'book': book.to_dict()}), 201


@books_bp.route('/<int:book_id>', methods=['PUT'])
@author_required
def update_book(current_user, book_id):
    book = Book.query.get_or_404(book_id)

    if current_user.role == 'author':
        author_record = Author.query.filter_by(user_id=current_user.id).first()
        if not author_record or book.author_id != author_record.id:
            return jsonify({'error': 'Not authorized to edit this book'}), 403

    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    for field in ('title', 'description', 'isbn', 'price', 'stock_quantity', 'image_url', 'genre_id'):
        if field in data:
            setattr(book, field, data[field])

    db.session.commit()
    return jsonify({'message': 'Book updated', 'book': book.to_dict()}), 200


@books_bp.route('/<int:book_id>', methods=['DELETE'])
@author_required
def delete_book(current_user, book_id):
    book = Book.query.get_or_404(book_id)

    if current_user.role == 'author':
        author_record = Author.query.filter_by(user_id=current_user.id).first()
        if not author_record or book.author_id != author_record.id:
            return jsonify({'error': 'Not authorized to delete this book'}), 403

    db.session.delete(book)
    db.session.commit()
    return jsonify({'message': 'Book deleted'}), 200
