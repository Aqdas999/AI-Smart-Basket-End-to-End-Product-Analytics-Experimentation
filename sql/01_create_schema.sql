-- =====================================================================
-- 01_create_schema.sql
-- Smart Basket Product Analytics — raw layer (PostgreSQL 13+)
--
-- The raw layer mirrors the Olist CSV files one-to-one. Columns keep the
-- source names (including Olist's "lenght" typo) so loads never need
-- column mapping. Cleaning happens in 03_analytics_model.sql, not here.
--
-- Run:  psql -d olist -f sql/01_create_schema.sql
-- =====================================================================

DROP SCHEMA IF EXISTS raw CASCADE;
CREATE SCHEMA raw;

CREATE TABLE raw.customers (
    customer_id              TEXT PRIMARY KEY,   -- one per order (!)
    customer_unique_id       TEXT NOT NULL,      -- the real person
    customer_zip_code_prefix TEXT,
    customer_city            TEXT,
    customer_state           CHAR(2)
);

CREATE TABLE raw.orders (
    order_id                      TEXT PRIMARY KEY,
    customer_id                   TEXT NOT NULL,
    order_status                  TEXT NOT NULL,
    order_purchase_timestamp      TIMESTAMP NOT NULL,
    order_approved_at             TIMESTAMP,
    order_delivered_carrier_date  TIMESTAMP,
    order_delivered_customer_date TIMESTAMP,
    order_estimated_delivery_date TIMESTAMP
);

CREATE TABLE raw.order_items (
    order_id            TEXT    NOT NULL,
    order_item_id       INT     NOT NULL,        -- line number within the order
    product_id          TEXT    NOT NULL,
    seller_id           TEXT    NOT NULL,
    shipping_limit_date TIMESTAMP,
    price               NUMERIC(10,2) NOT NULL,
    freight_value       NUMERIC(10,2) NOT NULL,
    PRIMARY KEY (order_id, order_item_id)
);

CREATE TABLE raw.order_payments (
    order_id             TEXT NOT NULL,
    payment_sequential   INT  NOT NULL,
    payment_type         TEXT,
    payment_installments INT,
    payment_value        NUMERIC(10,2),
    PRIMARY KEY (order_id, payment_sequential)
);

-- review_id is NOT unique in the source (the same review can cover
-- several orders) and an order can have several reviews, so there is
-- deliberately no primary key here.
CREATE TABLE raw.order_reviews (
    review_id               TEXT NOT NULL,
    order_id                TEXT NOT NULL,
    review_score            INT,
    review_comment_title    TEXT,
    review_comment_message  TEXT,
    review_creation_date    TIMESTAMP,
    review_answer_timestamp TIMESTAMP
);

CREATE TABLE raw.products (
    product_id                 TEXT PRIMARY KEY,
    product_category_name      TEXT,
    product_name_lenght        INT,
    product_description_lenght INT,
    product_photos_qty         INT,
    product_weight_g           INT,
    product_length_cm          INT,
    product_height_cm          INT,
    product_width_cm           INT
);

CREATE TABLE raw.sellers (
    seller_id              TEXT PRIMARY KEY,
    seller_zip_code_prefix TEXT,
    seller_city            TEXT,
    seller_state           CHAR(2)
);

CREATE TABLE raw.category_translation (
    product_category_name         TEXT PRIMARY KEY,
    product_category_name_english TEXT
);

-- Geolocation is not used by the analysis (it has ~1M rows with many
-- duplicate points per zip prefix) and is intentionally not loaded.
