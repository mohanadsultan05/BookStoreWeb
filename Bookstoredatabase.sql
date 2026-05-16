CREATE DATABASE IF NOT EXISTS bookstore;
USE bookstore;

-- ==========================================
-- USERS TABLE
-- ==========================================
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('customer', 'author', 'admin') NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ==========================================
-- CUSTOMERS TABLE
-- ==========================================
CREATE TABLE customers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT UNIQUE NOT NULL,
	full_name VARCHAR(100) NOT NULL,
    address VARCHAR(255),
    phone VARCHAR(20),
    payment_info VARCHAR(255),

    CONSTRAINT fk_customer_user
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE
);

-- ==========================================
-- ADMINISTRATORS TABLE
-- ==========================================
CREATE TABLE administrators (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT UNIQUE NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    admin_role VARCHAR(50),
    

    CONSTRAINT fk_admin_user
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE
        
        
);

-- ==========================================
-- AUTHORS TABLE
-- ==========================================
CREATE TABLE authors (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT UNIQUE,
    author_name VARCHAR(100) NOT NULL,
    biography TEXT,

    CONSTRAINT fk_author_user
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE SET NULL
);

-- ==========================================
-- GENRES TABLE
-- ==========================================
CREATE TABLE genres (
    id INT AUTO_INCREMENT PRIMARY KEY,
    genre_name VARCHAR(100) UNIQUE NOT NULL
);

-- ==========================================
-- BOOKS TABLE
-- ==========================================
CREATE TABLE books (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    isbn VARCHAR(50) UNIQUE,
    price DECIMAL(10,2) NOT NULL CHECK (price >= 0),
    stock_quantity INT DEFAULT 0 CHECK (stock_quantity >= 0),
    rating DECIMAL(3,2) DEFAULT 0,
    image_url VARCHAR(255),

    author_id INT,
    genre_id INT,
    admin_id INT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_book_author
        FOREIGN KEY (author_id)
        REFERENCES authors(id)
        ON DELETE SET NULL,

    CONSTRAINT fk_book_genre
        FOREIGN KEY (genre_id)
        REFERENCES genres(id)
        ON DELETE SET NULL,

    CONSTRAINT fk_book_admin
        FOREIGN KEY (admin_id)
        REFERENCES administrators(id)
        ON DELETE SET NULL
);

-- ==========================================
-- ORDERS TABLE
-- ==========================================
CREATE TABLE orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT NOT NULL,
    total_amount DECIMAL(10,2) NOT NULL,

    order_status ENUM('Pending', 'Processing', 'Completed')
        DEFAULT 'Pending',

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_order_customer
        FOREIGN KEY (customer_id)
        REFERENCES customers(id)
        ON DELETE CASCADE
);

-- ==========================================
-- ORDER ITEMS TABLE
-- ==========================================
CREATE TABLE order_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    book_id INT NOT NULL,
    quantity INT NOT NULL CHECK (quantity > 0),
    unit_price DECIMAL(10,2) NOT NULL,

    CONSTRAINT fk_orderitem_order
        FOREIGN KEY (order_id)
        REFERENCES orders(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_orderitem_book
        FOREIGN KEY (book_id)
        REFERENCES books(id)
        ON DELETE CASCADE
);

-- ==========================================
-- PAYMENTS TABLE
-- ==========================================
CREATE TABLE payments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT UNIQUE NOT NULL,

    payment_method ENUM('Credit Card', 'PayPal', 'Cash')
        NOT NULL,

    payment_status ENUM('Pending', 'Paid', 'Failed')
        DEFAULT 'Pending',

    amount DECIMAL(10,2) NOT NULL,
    payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_payment_order
        FOREIGN KEY (order_id)
        REFERENCES orders(id)
        ON DELETE CASCADE
);

-- ==========================================
-- CART ITEMS TABLE
-- ==========================================
CREATE TABLE cart_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT NOT NULL,
    book_id INT NOT NULL,
    quantity INT DEFAULT 1 CHECK (quantity > 0),

    CONSTRAINT fk_cart_customer
        FOREIGN KEY (customer_id)
        REFERENCES customers(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_cart_book
        FOREIGN KEY (book_id)
        REFERENCES books(id)
        ON DELETE CASCADE
);

-- ==========================================
-- TRIGGER: UPDATE ORDER STATUS AFTER PAYMENT
-- ==========================================
DELIMITER $$

CREATE TRIGGER trg_update_order_status
AFTER INSERT ON payments
FOR EACH ROW
BEGIN
    IF NEW.payment_status = 'Paid' THEN
        UPDATE orders
        SET order_status = 'Completed'
        WHERE id = NEW.order_id;
    END IF;
END$$

DELIMITER ;

-- ==========================================
-- SAMPLE GENRES
-- ==========================================
INSERT INTO genres (genre_name)
VALUES
('Programming'),
('Database'),
('Science Fiction'),
('Business'),
('History');

-- ==========================================
-- SAMPLE USERS
-- ==========================================
INSERT INTO users (full_name, email, password_hash, role)
VALUES
('Admin User', 'admin@bookstore.com', 'hashed_password', 'admin'),
('John Customer', 'john@example.com', 'hashed_password', 'customer'),
('Sarah Author', 'sarah@example.com', 'hashed_password', 'author');

-- ==========================================
-- SAMPLE AUTHOR
-- ==========================================
INSERT INTO authors (user_id, author_name, biography)
VALUES
(3, 'Sarah Author', 'Technology book writer');

-- ==========================================
-- SAMPLE CUSTOMER
-- ==========================================
INSERT INTO customers (user_id, full_name, address, phone)
VALUES
(2, 'Yusuf Ahmed','Istanbul, Turkey', '+90 555 123 4567');

-- ==========================================
-- SAMPLE ADMIN
-- ==========================================
INSERT INTO administrators (
    user_id,
    full_name,
    admin_role
)
VALUES
(1,  'John Michel','System Administrator');

-- ==========================================
-- SAMPLE BOOKS
-- ==========================================
INSERT INTO books (
    title,
    description,
    isbn,
    price,
    stock_quantity,
    rating,
    author_id,
    genre_id,
    admin_id
)
VALUES
(
    'Flask Web Development',
    'Learn Flask framework step by step',
    '9781234567890',
    29.99,
    50,
    4.8,
    1,
    1,
    1
),
(
    'Mastering SQL',
    'Advanced SQL database concepts',
    '9789876543210',
    24.99,
    30,
    4.5,
    1,
    2,
    1
);

-- ==========================================
-- VIEW: BOOK DETAILS
-- ==========================================
CREATE VIEW view_book_details AS
SELECT
    b.id,
    b.title,
    b.price,
    b.rating,
    a.author_name,
    g.genre_name
FROM books b
LEFT JOIN authors a ON b.author_id = a.id
LEFT JOIN genres g ON b.genre_id = g.id;
