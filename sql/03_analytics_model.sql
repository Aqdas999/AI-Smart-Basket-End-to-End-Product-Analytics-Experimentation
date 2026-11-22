-- =====================================================================
-- 03_analytics_model.sql
-- Builds the analytics layer: clean, correctly-grained tables.
--
--   analytics.fct_order_items   one row per order line
--   analytics.fct_orders        one row per order          <- main fact table
--   analytics.dim_customers     one row per real customer (customer_unique_id)
--
-- Key design rule: every child table (items, payments, reviews) is
-- aggregated to ORDER grain *before* it is joined. Joining items to
-- payments directly multiplies rows (an order with 2 items and 2 payments
-- becomes 4 rows) and overstates revenue — the bug in the original
-- version of this project.
--
-- Run:  psql -d olist -f sql/03_analytics_model.sql
-- =====================================================================

DROP SCHEMA IF EXISTS analytics CASCADE;
CREATE SCHEMA analytics;

-- ---------------------------------------------------------------------
-- Order lines, with English category names
-- ---------------------------------------------------------------------
CREATE TABLE analytics.fct_order_items AS
SELECT
    i.order_id,
    i.order_item_id,
    i.product_id,
    i.seller_id,
    COALESCE(t.product_category_name_english, 'unknown') AS category,
    i.price,
    i.freight_value
FROM raw.order_items i
LEFT JOIN raw.products p             ON p.product_id = i.product_id
LEFT JOIN raw.category_translation t ON t.product_category_name = p.product_category_name;

ALTER TABLE analytics.fct_order_items ADD PRIMARY KEY (order_id, order_item_id);

-- ---------------------------------------------------------------------
-- Order fact table
-- ---------------------------------------------------------------------
CREATE TABLE analytics.fct_orders AS
WITH items AS (                        -- items -> order grain
    SELECT
        order_id,
        COUNT(*)                    AS items_count,
        COUNT(DISTINCT product_id)  AS distinct_products,
        COUNT(DISTINCT category)    AS distinct_categories,
        COUNT(DISTINCT seller_id)   AS distinct_sellers,
        SUM(price)                  AS item_revenue,
        SUM(freight_value)          AS freight_revenue
    FROM analytics.fct_order_items
    GROUP BY order_id
),
main_category AS (                     -- category of the most expensive line
    SELECT DISTINCT ON (order_id) order_id, category AS primary_category
    FROM analytics.fct_order_items
    ORDER BY order_id, price DESC, order_item_id
),
payments AS (                          -- payments -> order grain
    SELECT
        order_id,
        SUM(payment_value)          AS payment_value,
        MAX(payment_installments)   AS max_installments,
        COUNT(*)                    AS payment_count
    FROM raw.order_payments
    GROUP BY order_id
),
main_payment AS (                      -- payment type carrying the most value
    SELECT DISTINCT ON (order_id) order_id, payment_type AS primary_payment_type
    FROM raw.order_payments
    ORDER BY order_id, payment_value DESC, payment_sequential
),
reviews AS (                           -- latest review per order
    SELECT DISTINCT ON (order_id) order_id, review_score
    FROM raw.order_reviews
    ORDER BY order_id, review_answer_timestamp DESC NULLS LAST, review_creation_date DESC
)
SELECT
    o.order_id,
    c.customer_unique_id,
    c.customer_state,
    o.order_status,
    o.order_purchase_timestamp                                   AS purchased_at,
    DATE_TRUNC('month', o.order_purchase_timestamp)::DATE        AS purchase_month,
    (o.order_status = 'delivered')                               AS is_delivered,
    (o.order_status IN ('canceled', 'unavailable'))              AS is_canceled,
    i.items_count,
    i.distinct_products,
    i.distinct_categories,
    i.distinct_sellers,
    (i.distinct_products > 1)                                    AS is_multi_product,
    mc.primary_category,
    i.item_revenue,
    i.freight_revenue,
    i.item_revenue + i.freight_revenue                           AS gmv,
    p.payment_value,
    mp.primary_payment_type,
    p.max_installments,
    r.review_score,
    CASE WHEN o.order_delivered_customer_date IS NOT NULL
         THEN EXTRACT(EPOCH FROM o.order_delivered_customer_date
                              - o.order_purchase_timestamp) / 86400.0 END
                                                                 AS delivery_days,
    CASE WHEN o.order_delivered_customer_date IS NOT NULL
         THEN o.order_delivered_customer_date::DATE
              > o.order_estimated_delivery_date::DATE END        AS is_late,
    -- order sequence per REAL customer, computed once per order (not per line)
    ROW_NUMBER() OVER (PARTITION BY c.customer_unique_id
                       ORDER BY o.order_purchase_timestamp, o.order_id)
                                                                 AS customer_order_number
FROM raw.orders o
JOIN raw.customers c        ON c.customer_id = o.customer_id
JOIN items i                ON i.order_id = o.order_id      -- drops 775 orders with no items
LEFT JOIN main_category mc  ON mc.order_id = o.order_id
LEFT JOIN payments p        ON p.order_id = o.order_id
LEFT JOIN main_payment mp   ON mp.order_id = o.order_id
LEFT JOIN reviews r         ON r.order_id = o.order_id;

ALTER TABLE analytics.fct_orders ADD PRIMARY KEY (order_id);
ALTER TABLE analytics.fct_orders ADD COLUMN is_repeat_order BOOLEAN;
UPDATE analytics.fct_orders SET is_repeat_order = customer_order_number > 1;
CREATE INDEX ON analytics.fct_orders (customer_unique_id);
CREATE INDEX ON analytics.fct_orders (purchase_month);

-- ---------------------------------------------------------------------
-- Customer dimension (valid = not canceled/unavailable)
-- ---------------------------------------------------------------------
CREATE TABLE analytics.dim_customers AS
SELECT
    customer_unique_id,
    MIN(purchased_at)                                AS first_order_at,
    DATE_TRUNC('month', MIN(purchased_at))::DATE     AS cohort_month,
    MAX(purchased_at)                                AS last_order_at,
    COUNT(*)                                         AS valid_orders,
    SUM(gmv)                                         AS lifetime_gmv,
    AVG(review_score)                                AS avg_review_score,
    (COUNT(*) > 1)                                   AS is_repeat_customer
FROM analytics.fct_orders
WHERE NOT is_canceled
GROUP BY customer_unique_id;

ALTER TABLE analytics.dim_customers ADD PRIMARY KEY (customer_unique_id);

ANALYZE;

SELECT 'fct_order_items' AS table_name, COUNT(*) AS row_count FROM analytics.fct_order_items
UNION ALL SELECT 'fct_orders',    COUNT(*) FROM analytics.fct_orders
UNION ALL SELECT 'dim_customers', COUNT(*) FROM analytics.dim_customers;
