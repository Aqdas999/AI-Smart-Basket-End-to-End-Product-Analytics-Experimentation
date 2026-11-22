# Metric definitions

Every number in this project follows these definitions. They are implemented once, in `sql/03_analytics_model.sql` and its pandas twin `src/smart_basket/data_model.py`, and every other file reads from those tables.

## Shared rules

| Rule | Definition |
|---|---|
| **Customer** | `customer_unique_id`. Olist's `customer_id` is new on every order and must never be used to count people. |
| **Valid order** | An order with at least one item, whose status is not `canceled` or `unavailable`. |
| **Trend window** | 1 Jan 2017 – 31 Aug 2018. Earlier months have very few orders, and Sep 2018 is incomplete. |
| **Money** | Brazilian reais (R$), nominal. |
| **Grain** | Each metric names its grain. Child tables (items, payments, reviews) are aggregated to order grain **before** any join. |

## Business metrics

| Metric | Formula | Grain | Notes |
|---|---|---|---|
| **GMV** | Σ (item price + freight) over valid orders | order | Reconciles with payments on 99.7% of orders; the gap is installment interest and vouchers. |
| **Orders** | count of valid orders | order | |
| **AOV** | GMV ÷ orders | order | Skewed: mean ≈ R$160, median ≈ R$105. |
| **Items per order** | Σ order lines ÷ orders | order | |
| **Multi-product order rate** | orders with ≥ 2 distinct `product_id` ÷ orders | order | Smart Basket's primary metric. Uses *distinct products*, so 2 units of the same product don't count. |
| **Multi-category order rate** | orders with ≥ 2 distinct categories ÷ orders | order | |
| **Repeat-customer rate** | customers with ≥ 2 valid orders ÷ customers | customer | 3.0%. The original project reported 19% because it flagged rows, not customers. |
| **Customer lifetime GMV** | Σ GMV per customer over the full history | customer | Called "CLV" informally; no margin or discounting is applied. |
| **Cohort retention (month n)** | customers from cohort *c* who order in month *c + n* ÷ cohort size | customer | Cohort = month of first valid order. |
| **Days to 2nd order** | 2nd order timestamp − 1st order timestamp | customer | Same day counts as 0. |
| **GMV concentration** | share of GMV from the top x% of customers (or categories) | customer / category | |

## Experience metrics

| Metric | Formula | Notes |
|---|---|---|
| **Review score** | mean of the latest review (1–5) per order | When an order has several reviews, the most recently answered one is kept. |
| **Late-delivery rate** | delivered orders where delivery date > estimated date ÷ delivered orders | Compared at day level. |
| **Delivery time** | delivered timestamp − purchase timestamp, in days | |
| **Cancellation rate** | orders with status `canceled`/`unavailable` ÷ all orders | Only used as an experiment guardrail (all orders, intent-to-treat). |

## Experiment metrics

Experiment metrics are computed on **all** orders placed during the test (intent-to-treat), including later-canceled ones. Variance is computed at **customer level** with the delta method, because customers are the unit of randomisation.

| Metric | Formula | Role |
|---|---|---|
| **Multi-product order rate** | Σ multi-product orders ÷ Σ orders | Primary |
| **AOV** | Σ GMV ÷ Σ orders | Secondary |
| **GMV per customer** | Σ GMV ÷ customers | Secondary |
| **Items per order** | Σ items ÷ Σ orders | Secondary |
| **Cancellation rate** | Σ canceled orders ÷ Σ orders | Guardrail (+0.3 pp max) |
| **Review score** | Σ review score ÷ Σ reviewed orders | Guardrail (−0.05 max) |
| **Late-delivery rate** | Σ late ÷ Σ delivered orders | Guardrail (+1 pp max) |
| **Widget CTR** | clicks ÷ impressions | Health (treatment only) |
| **Add rate** | recommended items added ÷ clicks | Health (treatment only) |

## Recommender (offline) metric

| Metric | Formula |
|---|---|
| **Hit-rate@k** | share of test cases (a customer bought category A *and* another category B) where B is among the top-k recommendations for A. Train before 5 Mar 2018, test after. |
