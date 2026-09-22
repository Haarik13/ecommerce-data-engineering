CREATE SCHEMA IF NOT EXISTS ecommerce;

CREATE TABLE IF NOT EXISTS ecommerce.dim_customer (
    customer_key SERIAL PRIMARY KEY,
    customer_id VARCHAR(50) NOT NULL UNIQUE,
    customer_unique_id VARCHAR(50),
    customer_zip_code_prefix INTEGER,
    customer_city VARCHAR(100),
    customer_state VARCHAR(10)
);

CREATE TABLE IF NOT EXISTS ecommerce.dim_product (
    product_key SERIAL PRIMARY KEY,
    product_id VARCHAR(50) NOT NULL UNIQUE,
    product_category VARCHAR(100),
    product_name_length INTEGER,
    product_description_length INTEGER,
    product_photos_qty INTEGER,
    product_weight_g INTEGER,
    product_length_cm NUMERIC(10, 2),
    product_height_cm NUMERIC(10, 2),
    product_width_cm NUMERIC(10, 2)
);

CREATE TABLE IF NOT EXISTS ecommerce.dim_seller (
    seller_key SERIAL PRIMARY KEY,
    seller_id VARCHAR(50) NOT NULL UNIQUE,
    seller_zip_code_prefix INTEGER,
    seller_city VARCHAR(100),
    seller_state VARCHAR(10)
);

CREATE TABLE IF NOT EXISTS ecommerce.dim_date (
    date_key INTEGER PRIMARY KEY,
    date DATE NOT NULL UNIQUE,
    year INTEGER NOT NULL,
    quarter INTEGER NOT NULL,
    month INTEGER NOT NULL,
    month_name VARCHAR(20) NOT NULL,
    day INTEGER NOT NULL,
    day_of_week INTEGER NOT NULL,
    day_name VARCHAR(20) NOT NULL
);

CREATE TABLE IF NOT EXISTS ecommerce.fact_order_items (
    order_item_key BIGSERIAL PRIMARY KEY,
    order_id VARCHAR(50) NOT NULL,
    order_item_id INTEGER NOT NULL,

    customer_key INTEGER,
    product_key INTEGER,
    seller_key INTEGER,
    order_date_key INTEGER,

    price NUMERIC(12, 2),
    freight_value NUMERIC(12, 2),
    item_total_value NUMERIC(12, 2),

    delivery_days INTEGER,
    is_late_delivery BOOLEAN,

    CONSTRAINT fk_customer
        FOREIGN KEY (customer_key)
        REFERENCES ecommerce.dim_customer(customer_key),

    CONSTRAINT fk_product
        FOREIGN KEY (product_key)
        REFERENCES ecommerce.dim_product(product_key),

    CONSTRAINT fk_seller
        FOREIGN KEY (seller_key)
        REFERENCES ecommerce.dim_seller(seller_key),

    CONSTRAINT fk_order_date
        FOREIGN KEY (order_date_key)
        REFERENCES ecommerce.dim_date(date_key),

    CONSTRAINT unique_order_item
        UNIQUE (order_id, order_item_id)
);
