from database import db


class Genre(db.Model):
    __tablename__ = 'genres'

    id = db.Column(db.Integer, primary_key=True)
    genre_name = db.Column(db.String(100), unique=True, nullable=False)

    books = db.relationship('Book', backref='genre', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'genre_name': self.genre_name
        }
