# BookHaven – Online Bookstore System

A full-stack Online Bookstore System built with **Python Flask** (backend) and **HTML/CSS/Bootstrap 5** (frontend).

---

## Architecture

```
4-Tier Architecture:
  1. Frontend Layer    → HTML / CSS / Bootstrap 5 / JavaScript (Fetch API)
  2. Flask API Layer   → Python Flask + JWT + Flask-CORS
  3. Business Logic    → Python Services / SQLAlchemy ORM
  4. Database Layer    → MySQL (bookstore)


---

## Project Structure

```
├── backend/
│   ├── app.py                  # Flask app factory
│   ├── config.py               # Configuration (dev/prod)
│   ├── requirements.txt
│   ├── .env.example
│   ├── models/                 # SQLAlchemy models
│   │   ├── user.py             # User, Customer, Administrator, Author
│   │   ├── book.py
│   │   ├── genre.py
│   │   ├── order.py            # Order, OrderItem
│   │   ├── payment.py
│   │   └── cart.py
│   ├── routes/                 # Flask Blueprints (REST APIs)
│   │   ├── auth.py
│   │   ├── books.py
│   │   ├── genres.py
│   │   ├── authors.py
│   │   ├── orders.py
│   │   ├── payments.py
│   │   ├── cart.py
│   │   └── admin.py
│   ├── middleware/
│   │   └── auth_middleware.py  # JWT decorators
│   ├── utils/
│   │   └── helpers.py
│   └── database/
│       └── seed.py             # Sample data seeder
│
└── frontend/
    ├── index.html              # Home page
    ├── login.html
    ├── register.html
    ├── books.html              # Book catalog with search/filter
    ├── book-detail.html        # Single book page
    ├── cart.html               # Shopping cart + checkout
    ├── orders.html             # Order history
    ├── admin-dashboard.html    # Admin panel (single-page)
    ├── author-dashboard.html   # Author panel (single-page)
    ├── css/style.css
    └── js/
        ├── auth.js             # JWT helpers, login/register
        ├── main.js             # Toasts, utilities, cart badge
        ├── books.js            # Catalog, search, book detail
        ├── cart.js             # Cart, orders
        ├── admin.js            # Admin dashboard
        └── author.js           # Author dashboard
```

---

## Setup & Installation

### Prerequisites

- Python 3.9+
- MySQL Server running locally
- A MySQL database named `bookstore`

---

### Step 1 – Create the Database

**Option A – Use the provided SQL file:**
```sql
-- Run in MySQL Workbench or CLI:
source Bookstoredatabase.sql
```

**Option B – Let SQLAlchemy create tables automatically:**
```bash
# Tables are created when you first run app.py
python app.py
```

---

### Step 2 – Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (macOS/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy and configure environment
copy .env.example .env
```

Edit `.env`:
```
DATABASE_URL=mysql+pymysql://root:YOUR_PASSWORD@localhost/bookstore
SECRET_KEY=your-super-secret-key
JWT_SECRET_KEY=your-jwt-secret-key
FLASK_ENV=development
```

---

### Step 3 – Run the Backend

```bash
# From the backend/ directory
python app.py
```

The API will be available at: **http://localhost:5000**

Health check: http://localhost:5000/api/health

---

### Step 4 – Seed Sample Data

```bash
# From the backend/ directory
python database/seed.py
```

This creates sample genres, users, books, and orders.

---

### Step 5 – Open the Frontend

Open any HTML file in a browser. Recommended: open `frontend/index.html` directly.

> **Note:** Because the frontend uses `fetch()` to call `http://localhost:5000`, you need the backend running. You can also serve frontend files with a simple HTTP server:
>
> ```bash
> cd frontend
> python -m http.server 8080
> # Then visit http://localhost:8080
> ```

---

## Demo Credentials

| Role     | Email                    | Password       |
|----------|--------------------------|----------------|
| Admin    | admin@bookstore.com      | Admin@123      |
| Author   | sarah@example.com        | Author@123     |
| Author   | james@author.com         | Author@123     |
| Customer | john@example.com         | Customer@123   |
| Customer | alice@customer.com       | Customer@123   |

---

## API Reference

### Authentication
| Method | Endpoint             | Description         | Auth |
|--------|----------------------|---------------------|------|
| POST   | /api/auth/register   | Register new user   | No   |
| POST   | /api/auth/login      | Login               | No   |
| GET    | /api/auth/profile    | Get profile         | Yes  |
| PUT    | /api/auth/profile    | Update profile      | Yes  |

### Books
| Method | Endpoint           | Description            | Auth        |
|--------|--------------------|------------------------|-------------|
| GET    | /api/books         | List books (+ filters) | No          |
| GET    | /api/books/:id     | Get book detail        | No          |
| POST   | /api/books         | Create book            | Author/Admin|
| PUT    | /api/books/:id     | Update book            | Author/Admin|
| DELETE | /api/books/:id     | Delete book            | Author/Admin|

### Cart (Customer only)
| Method | Endpoint         | Description       |
|--------|------------------|-------------------|
| GET    | /api/cart        | Get cart          |
| POST   | /api/cart/add    | Add item          |
| PUT    | /api/cart/:id    | Update quantity   |
| DELETE | /api/cart/:id    | Remove item       |
| DELETE | /api/cart/clear  | Clear cart        |

### Orders
| Method | Endpoint                   | Description         | Auth   |
|--------|----------------------------|---------------------|--------|
| GET    | /api/orders                | List orders         | Yes    |
| GET    | /api/orders/:id            | Get order           | Yes    |
| POST   | /api/orders                | Place order         | Customer|
| PUT    | /api/orders/:id/status     | Update status       | Admin  |

### Payments
| Method | Endpoint                   | Description       | Auth     |
|--------|----------------------------|-------------------|----------|
| POST   | /api/payments              | Make payment      | Customer |
| GET    | /api/payments/:id          | Get payment       | Yes      |
| GET    | /api/payments/order/:id    | Payment by order  | Yes      |
| GET    | /api/payments              | All payments      | Admin    |

### Admin
| Method | Endpoint                     | Description       |
|--------|------------------------------|-------------------|
| GET    | /api/admin/dashboard         | Dashboard stats   |
| GET    | /api/admin/users             | All users         |
| DELETE | /api/admin/users/:id         | Delete user       |
| GET    | /api/admin/books             | All books         |
| PUT    | /api/admin/books/:id/stock   | Update stock      |
| GET    | /api/admin/orders            | All orders        |
| GET    | /api/admin/payments          | All payments      |
| GET    | /api/admin/reports           | Reports           |

---

## Features

### Customer
- Browse & search books (by title, author, genre)
- View book details
- Add to cart / update quantities / remove items
- Place orders with payment (Credit Card, PayPal, Cash)
- View order history

### Author
- Add / edit / delete own books
- View sales statistics and revenue
- Update profile & biography

### Admin
- Full dashboard with KPI stats
- Manage all books, users, genres, orders
- Update order status (Pending → Processing → Completed)
- Manage stock quantities
- View payment records
- Sales reports by genre and top books

---

## Tech Stack

| Layer      | Technology                           |
|------------|--------------------------------------|
| Frontend   | HTML5, CSS3, Bootstrap 5, JavaScript |
| Backend    | Python 3, Flask, Flask-JWT-Extended  |
| ORM        | SQLAlchemy (Flask-SQLAlchemy)        |
| Database   | MySQL via PyMySQL                    |
| Auth       | JWT (JSON Web Tokens) + bcrypt       |
| CORS       | Flask-CORS                           |

---

## Database Schema

The database schema is defined in `Bookstoredatabase.sql`. Key tables:

- **users** – base user table (role: customer/author/admin)
- **customers** – customer profile (user_id FK)
- **administrators** – admin profile (user_id FK)
- **authors** – author profile (user_id FK, author_name)
- **genres** – book genres
- **books** – book catalog (author_id→authors, genre_id→genres)
- **orders** – customer orders (customer_id→customers)
- **order_items** – line items per order
- **payments** – payment records (one per order)
- **cart_items** – shopping cart (customer_id→customers)

Two DB triggers are defined in the SQL:
- `trg_update_order_status` – auto-sets order status to Completed when payment is Paid

---

*Software Architecture Final Project – Online Bookstore System*
