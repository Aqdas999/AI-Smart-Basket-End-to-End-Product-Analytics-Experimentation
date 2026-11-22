-- =====================================================================
-- 02_load_data.sql
-- Loads the Olist CSVs into the raw schema with psql's client-side \copy,
-- so it works without superuser rights or server file access.
--
-- Run from the repository root (paths are relative to it):
--   psql -d olist -f sql/02_load_data.sql
-- =====================================================================

\echo 'Loading raw tables...'

\copy raw.customers            FROM 'data/raw/olist_customers_dataset.csv'          WITH (FORMAT csv, HEADER true)
\copy raw.orders               FROM 'data/raw/olist_orders_dataset.csv'             WITH (FORMAT csv, HEADER true)
\copy raw.order_items          FROM 'data/raw/olist_order_items_dataset.csv'        WITH (FORMAT csv, HEADER true)
\copy raw.order_payments       FROM 'data/raw/olist_order_payments_dataset.csv'     WITH (FORMAT csv, HEADER true)
\copy raw.order_reviews        FROM 'data/raw/olist_order_reviews_dataset.csv'      WITH (FORMAT csv, HEADER true)
\copy raw.products             FROM 'data/raw/olist_products_dataset.csv'           WITH (FORMAT csv, HEADER true)
\copy raw.sellers              FROM 'data/raw/olist_sellers_dataset.csv'            WITH (FORMAT csv, HEADER true)
\copy raw.category_translation FROM 'data/raw/product_category_name_translation.csv' WITH (FORMAT csv, HEADER true)

-- Two categories exist in products but are missing from the translation file.
INSERT INTO raw.category_translation VALUES
    ('pc_gamer', 'pc_gamer'),
    ('portateis_cozinha_e_preparadores_de_alimentos', 'portable_kitchen_and_food_preparers')
ON CONFLICT DO NOTHING;

ANALYZE;

\echo 'Row counts:'
SELECT 'customers' AS table_name, COUNT(*) AS row_count FROM raw.customers
UNION ALL SELECT 'orders',         COUNT(*) FROM raw.orders
UNION ALL SELECT 'order_items',    COUNT(*) FROM raw.order_items
UNION ALL SELECT 'order_payments', COUNT(*) FROM raw.order_payments
UNION ALL SELECT 'order_reviews',  COUNT(*) FROM raw.order_reviews
UNION ALL SELECT 'products',       COUNT(*) FROM raw.products
UNION ALL SELECT 'sellers',        COUNT(*) FROM raw.sellers;
