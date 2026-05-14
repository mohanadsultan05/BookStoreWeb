from flask import Blueprint, request, jsonify
from database import db
from models.genre import Genre
from middleware.auth_middleware import admin_required

genres_bp = Blueprint('genres', __name__)


@genres_bp.route('', methods=['GET'])
def get_genres():
    genres = Genre.query.order_by(Genre.genre_name).all()
    return jsonify({'genres': [g.to_dict() for g in genres]}), 200


@genres_bp.route('/<int:genre_id>', methods=['GET'])
def get_genre(genre_id):
    genre = Genre.query.get_or_404(genre_id)
    return jsonify({'genre': genre.to_dict()}), 200


@genres_bp.route('', methods=['POST'])
@admin_required
def create_genre(current_user):
    data = request.get_json()
    if not data or not data.get('genre_name'):
        return jsonify({'error': 'genre_name is required'}), 400

    if Genre.query.filter_by(genre_name=data['genre_name']).first():
        return jsonify({'error': 'Genre already exists'}), 409

    genre = Genre(genre_name=data['genre_name'])
    db.session.add(genre)
    db.session.commit()
    return jsonify({'message': 'Genre created', 'genre': genre.to_dict()}), 201


@genres_bp.route('/<int:genre_id>', methods=['PUT'])
@admin_required
def update_genre(current_user, genre_id):
    genre = Genre.query.get_or_404(genre_id)
    data = request.get_json()
    if not data or not data.get('genre_name'):
        return jsonify({'error': 'genre_name is required'}), 400
    genre.genre_name = data['genre_name']
    db.session.commit()
    return jsonify({'message': 'Genre updated', 'genre': genre.to_dict()}), 200


@genres_bp.route('/<int:genre_id>', methods=['DELETE'])
@admin_required
def delete_genre(current_user, genre_id):
    genre = Genre.query.get_or_404(genre_id)
    db.session.delete(genre)
    db.session.commit()
    return jsonify({'message': 'Genre deleted'}), 200
