import os
from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from config import config
from database import db


def create_app(config_name=None):
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'default')

    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Initialize extensions
    db.init_app(app)
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    JWTManager(app)

    # Register blueprints
    from routes.auth import auth_bp
    from routes.books import books_bp
    from routes.genres import genres_bp
    from routes.authors import authors_bp
    from routes.orders import orders_bp
    from routes.payments import payments_bp
    from routes.cart import cart_bp
    from routes.admin import admin_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(books_bp, url_prefix='/api/books')
    app.register_blueprint(genres_bp, url_prefix='/api/genres')
    app.register_blueprint(authors_bp, url_prefix='/api/authors')
    app.register_blueprint(orders_bp, url_prefix='/api/orders')
    app.register_blueprint(payments_bp, url_prefix='/api/payments')
    app.register_blueprint(cart_bp, url_prefix='/api/cart')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')

    # Health check
    @app.route('/api/health')
    def health():
        return jsonify({'status': 'ok', 'message': 'Bookstore API is running'}), 200

    # Error handlers
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({'error': 'Resource not found'}), 404

    @app.errorhandler(405)
    def method_not_allowed(e):
        return jsonify({'error': 'Method not allowed'}), 405

    @app.errorhandler(500)
    def internal_error(e):
        return jsonify({'error': 'Internal server error'}), 500

    # Create all tables
    with app.app_context():
        db.create_all()

    return app


if __name__ == '__main__':
    app = create_app()
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
