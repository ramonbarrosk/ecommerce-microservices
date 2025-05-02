CREATE TABLE IF NOT EXISTS category (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS product (
    id_product SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    price DECIMAL(10,2) NOT NULL,
    category_id INTEGER NOT NULL REFERENCES category(id),
    CONSTRAINT unique_product_name UNIQUE(name)
);


CREATE TABLE IF NOT EXISTS customers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password BYTEA NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Inserindo categorias apenas se não existirem
INSERT INTO category (name)
VALUES 
    ('Electronics'),
    ('Books'),
    ('Clothing'),
    ('Toys'),
    ('Home & Kitchen')
ON CONFLICT (name) DO NOTHING;

-- Inserindo produtos apenas se não existirem
INSERT INTO product (name, description, price, category_id)
SELECT 'Smartphone X1', 'Latest smartphone with 128GB storage', 699.99, c.id
FROM category c WHERE c.name = 'Electronics'
AND NOT EXISTS (
    SELECT 1 FROM product p WHERE p.name = 'Smartphone X1'
);

INSERT INTO product (name, description, price, category_id)
SELECT 'Laptop Pro 15', 'High-performance laptop for professionals', 1299.99, c.id
FROM category c WHERE c.name = 'Electronics'
AND NOT EXISTS (
    SELECT 1 FROM product p WHERE p.name = 'Laptop Pro 15'
);

INSERT INTO product (name, description, price, category_id)
SELECT 'Wireless Headphones', 'Noise-cancelling Bluetooth headphones', 199.99, c.id
FROM category c WHERE c.name = 'Electronics'
AND NOT EXISTS (
    SELECT 1 FROM product p WHERE p.name = 'Wireless Headphones'
);

INSERT INTO product (name, description, price, category_id)
SELECT 'The Great Gatsby', 'Classic novel by F. Scott Fitzgerald', 14.99, c.id
FROM category c WHERE c.name = 'Books'
AND NOT EXISTS (
    SELECT 1 FROM product p WHERE p.name = 'The Great Gatsby'
);

INSERT INTO product (name, description, price, category_id)
SELECT 'Jeans Slim Fit', 'Comfortable slim fit jeans', 49.99, c.id
FROM category c WHERE c.name = 'Clothing'
AND NOT EXISTS (
    SELECT 1 FROM product p WHERE p.name = 'Jeans Slim Fit'
);

INSERT INTO product (name, description, price, category_id)
SELECT 'Action Figure - Superhero', 'Collectible superhero toy', 24.99, c.id
FROM category c WHERE c.name = 'Toys'
AND NOT EXISTS (
    SELECT 1 FROM product p WHERE p.name = 'Action Figure - Superhero'
);

INSERT INTO product (name, description, price, category_id)
SELECT 'Non-stick Frying Pan', 'Durable non-stick frying pan 28cm', 34.90, c.id
FROM category c WHERE c.name = 'Home & Kitchen'
AND NOT EXISTS (
    SELECT 1 FROM product p WHERE p.name = 'Non-stick Frying Pan'
);
