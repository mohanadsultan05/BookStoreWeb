"""
Seed the database with sample data.
Usage (from the backend/ directory):
    python database/seed.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from database import db
from models.user import User, Customer, Administrator, Author
from models.genre import Genre
from models.book import Book
from models.order import Order, OrderItem
from models.payment import Payment
from models.cart import CartItem


def seed():
    app = create_app()
    with app.app_context():
        # Clear all tables safely
        db.session.execute(db.text('SET FOREIGN_KEY_CHECKS=0'))
        for table in reversed(db.metadata.sorted_tables):
            db.session.execute(table.delete())
        db.session.execute(db.text('SET FOREIGN_KEY_CHECKS=1'))
        db.session.commit()

        # ── Genres ───────────────────────────────────────────────────────────
        genre_names = [
            'Programming', 'Database', 'Science Fiction', 'Business',
            'History', 'Fiction', 'Mystery', 'Romance', 'Self-Help', 'Biography'
        ]
        genres = [Genre(genre_name=n) for n in genre_names]
        db.session.add_all(genres)
        db.session.flush()
        gmap = {g.genre_name: g.id for g in genres}

        # ── Admin ─────────────────────────────────────────────────────────────
        admin_user = User(full_name='Admin User', email='admin@bookstore.com', role='admin')
        admin_user.set_password('Admin@123')
        db.session.add(admin_user)
        db.session.flush()
        admin_profile = Administrator(user_id=admin_user.id, admin_role='System Administrator')
        db.session.add(admin_profile)
        db.session.flush()

        # ── Authors ───────────────────────────────────────────────────────────
        authors_data = [
            ('Sarah Author', 'sarah@example.com', 'Sarah Author', 'Technology book writer and software engineer.'),
            ('James Patterson', 'james@author.com', 'James Patterson', 'Bestselling thriller and mystery novelist.'),
            ('J.K. Rowling', 'jkr@author.com', 'J.K. Rowling', 'Author of the Harry Potter fantasy series.'),
            ('Yuval Noah Harari', 'harari@author.com', 'Yuval Noah Harari', 'Historian, philosopher, and author of Sapiens.'),
        ]
        author_records = []
        for full_name, email, author_name, bio in authors_data:
            u = User(full_name=full_name, email=email, role='author')
            u.set_password('Author@123')
            db.session.add(u)
            db.session.flush()
            a = Author(user_id=u.id, author_name=author_name, biography=bio)
            db.session.add(a)
            db.session.flush()
            author_records.append(a)

        # ── Customers ─────────────────────────────────────────────────────────
        customers_data = [
            ('John Customer', 'john@example.com', 'Istanbul, Turkey', '+90 555 123 4567'),
            ('Alice Johnson', 'alice@customer.com', '123 Main St, Springfield', '555-0101'),
            ('Bob Smith', 'bob@customer.com', '456 Oak Ave, Shelbyville', '555-0102'),
        ]
        customer_records = []
        for full_name, email, address, phone in customers_data:
            u = User(full_name=full_name, email=email, role='customer')
            u.set_password('Customer@123')
            db.session.add(u)
            db.session.flush()
            c = Customer(user_id=u.id, address=address, phone=phone)
            db.session.add(c)
            db.session.flush()
            customer_records.append(c)

        # ── Books ─────────────────────────────────────────────────────────────
        books_data = [
            ('Flask Web Development', 'Learn Flask framework step by step for modern web apps.', '9781234567890', 29.99, 50, 4.8, author_records[0].id, gmap['Programming']),
            ('Mastering SQL', 'Advanced SQL and database design concepts with real examples.', '9789876543210', 24.99, 30, 4.5, author_records[0].id, gmap['Database']),
            ('Along Came a Spider', 'A gripping detective thriller featuring Alex Cross.', '9780316769174', 14.99, 45, 4.3, author_records[1].id, gmap['Mystery']),
            ('Kiss the Girls', 'Alex Cross hunts a kidnapper in this page-turning thriller.', '9780316969956', 13.99, 40, 4.2, author_records[1].id, gmap['Mystery']),
            ("Harry Potter and the Philosopher's Stone", 'A young boy discovers he is a wizard and is accepted into Hogwarts.', '9780439708180', 12.99, 100, 4.9, author_records[2].id, gmap['Fiction']),
            ('Harry Potter and the Chamber of Secrets', 'Harry returns to Hogwarts for his second year full of new mysteries.', '9780439064873', 12.99, 90, 4.8, author_records[2].id, gmap['Fiction']),
            ('Sapiens', 'A Brief History of Humankind from ancient foragers to modern humans.', '9780062316097', 18.99, 80, 4.8, author_records[3].id, gmap['History']),
            ('Homo Deus', 'A Brief History of Tomorrow — exploring where humanity is heading.', '9780062464316', 17.99, 70, 4.5, author_records[3].id, gmap['Biography']),
            ('21 Lessons for the 21st Century', 'Navigating the present in a rapidly changing world.', '9780525512172', 16.99, 65, 4.4, author_records[3].id, gmap['Self-Help']),
            ('Python Crash Course', 'A hands-on, project-based introduction to programming with Python.', '9781593279288', 31.99, 60, 4.7, author_records[0].id, gmap['Programming']),
        ]

        book_objects = []
        for title, desc, isbn, price, stock, rating, author_id, genre_id in books_data:
            b = Book(
                title=title,
                description=desc,
                isbn=isbn,
                price=price,
                stock_quantity=stock,
                rating=rating,
                image_url=f'https://via.placeholder.com/200x300/4a90d9/ffffff?text={title[:12].replace(" ", "+")}',
                author_id=author_id,
                genre_id=genre_id,
                admin_id=admin_profile.id
            )
            db.session.add(b)
            book_objects.append(b)
        db.session.flush()

        # ── Sample completed order for John ───────────────────────────────────
        order1 = Order(customer_id=customer_records[0].id, total_amount=44.98, order_status='Completed')
        db.session.add(order1)
        db.session.flush()
        db.session.add(OrderItem(order_id=order1.id, book_id=book_objects[0].id, quantity=1, unit_price=29.99))
        db.session.add(OrderItem(order_id=order1.id, book_id=book_objects[1].id, quantity=1, unit_price=14.99))
        db.session.add(Payment(order_id=order1.id, payment_method='Credit Card', payment_status='Paid', amount=44.98))

        # ── Sample pending order for Alice ────────────────────────────────────
        order2 = Order(customer_id=customer_records[1].id, total_amount=25.98, order_status='Pending')
        db.session.add(order2)
        db.session.flush()
        db.session.add(OrderItem(order_id=order2.id, book_id=book_objects[4].id, quantity=2, unit_price=12.99))

        db.session.commit()

        print("Database seeded successfully!")
        print("\nLogin credentials:")
        print("  Admin:    admin@bookstore.com  / Admin@123")
        print("  Author:   sarah@example.com    / Author@123")
        print("  Author:   james@author.com     / Author@123")
        print("  Customer: john@example.com     / Customer@123")
        print("  Customer: alice@customer.com   / Customer@123")


if __name__ == '__main__':
    seed()
