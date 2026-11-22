-- =====================================================================
-- 04_data_validation.sql
-- Data-quality and reconciliation checks for the analytics layer.
-- Every check returns one row: check name, observed value, expected
-- value and PASS/FAIL. Any FAIL means the model must not be used.
--
-- Run:  psql -d olist -f sql/04_data_validation.sql
-- =====================================================================

WITH checks AS (

    -- 1. Grain: exactly one row per order in the fact table
    SELECT 1 AS id, 'fct_orders has one row per order' AS check_name,
           (SELECT COUNT(*) - COUNT(DISTINCT order_id) FROM analytics.fct_orders)::NUMERIC AS observed,
           0::NUMERIC AS expected

    -- 2. Completeness: every raw order with items reaches the fact table
    UNION ALL
    SELECT 2, 'raw orders with items missing from fct_orders',
           (SELECT COUNT(DISTINCT i.order_id) FROM raw.order_items i
             LEFT JOIN analytics.fct_orders f USING (order_id)
             WHERE f.order_id IS NULL), 0

    -- 3. Reconciliation: item revenue equals the raw items table
    UNION ALL
    SELECT 3, 'item revenue difference vs raw.order_items',
           (SELECT SUM(item_revenue) FROM analytics.fct_orders)
         - (SELECT SUM(price) FROM raw.order_items), 0

    -- 4. Reconciliation: payments equal the raw payments table
    --    (for orders that have items)
    UNION ALL
    SELECT 4, 'payment difference vs raw.order_payments',
           (SELECT SUM(payment_value) FROM analytics.fct_orders)
         - (SELECT SUM(p.payment_value) FROM raw.order_payments p
             WHERE EXISTS (SELECT 1 FROM raw.order_items i WHERE i.order_id = p.order_id)), 0

    -- 5. Payments ~ price + freight (vouchers/interest cause small gaps)
    UNION ALL
    SELECT 5, '% orders where |payment - gmv| > 1 BRL',
           (SELECT ROUND(100.0 * AVG((ABS(payment_value - gmv) > 1)::INT), 2)
              FROM analytics.fct_orders WHERE payment_value IS NOT NULL), 5   -- tolerance: under 5%

    -- 6. Repeat flag is consistent with the order sequence
    UNION ALL
    SELECT 6, 'orders where is_repeat_order disagrees with order number',
           (SELECT COUNT(*) FROM analytics.fct_orders
             WHERE is_repeat_order <> (customer_order_number > 1)), 0

    -- 7. Each customer has exactly one first order
    UNION ALL
    SELECT 7, 'customers without exactly one first order',
           (SELECT COUNT(*) FROM (
               SELECT customer_unique_id FROM analytics.fct_orders
               GROUP BY customer_unique_id
               HAVING SUM((customer_order_number = 1)::INT) <> 1) x), 0

    -- 8. No negative money
    UNION ALL
    SELECT 8, 'orders with negative revenue',
           (SELECT COUNT(*) FROM analytics.fct_orders WHERE item_revenue < 0 OR freight_revenue < 0), 0

    -- 9. Delivery cannot happen before purchase
    UNION ALL
    SELECT 9, 'orders delivered before purchase',
           (SELECT COUNT(*) FROM analytics.fct_orders WHERE delivery_days < 0), 0

    -- 10. Review scores in range
    UNION ALL
    SELECT 10, 'review scores outside 1-5',
           (SELECT COUNT(*) FROM analytics.fct_orders WHERE review_score NOT BETWEEN 1 AND 5), 0

    -- 11. Customer dimension reconciles with valid orders
    UNION ALL
    SELECT 11, 'dim_customers order count difference vs valid fct_orders',
           (SELECT SUM(valid_orders) FROM analytics.dim_customers)
         - (SELECT COUNT(*) FROM analytics.fct_orders WHERE NOT is_canceled), 0

    -- 12. Category coverage (unknown = product without a category in source)
    UNION ALL
    SELECT 12, '% order lines with unknown category',
           (SELECT ROUND(100.0 * AVG((category = 'unknown')::INT), 2)
              FROM analytics.fct_order_items), 2                               -- tolerance: under 2%
)
SELECT id, check_name, observed, expected,
       CASE
           WHEN id IN (5, 12) THEN CASE WHEN observed <= expected THEN 'PASS' ELSE 'FAIL' END
           ELSE CASE WHEN observed = expected THEN 'PASS' ELSE 'FAIL' END
       END AS status
FROM checks
ORDER BY id;

-- ---------------------------------------------------------------------
-- Informational profile (not pass/fail)
-- ---------------------------------------------------------------------
SELECT order_status, COUNT(*) AS orders,
       ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS pct
FROM analytics.fct_orders
GROUP BY order_status
ORDER BY orders DESC;

SELECT
    COUNT(*) FILTER (WHERE payment_value IS NULL)   AS orders_without_payment,
    COUNT(*) FILTER (WHERE review_score IS NULL)    AS orders_without_review,
    COUNT(*) FILTER (WHERE delivery_days IS NULL)   AS orders_not_delivered_yet,
    MIN(purchased_at)                               AS first_purchase,
    MAX(purchased_at)                               AS last_purchase
FROM analytics.fct_orders;
