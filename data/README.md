# Data

The raw data is **not stored in this repository** (~120 MB). It's the public
[Brazilian E-Commerce Public Dataset by Olist](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)
on Kaggle (licence: CC BY-NC-SA 4.0): ~100k orders from 2016–2018 across 9 related tables.

## Get it

**Option A: automatic** (needs a free Kaggle account and an API token in `~/.kaggle/kaggle.json`):

```bash
python scripts/download_data.py
```

**Option B: manual.** Download the zip from the Kaggle page above, then unzip all CSVs into `data/raw/`.

Either way, you should end up with:

```text
data/raw/
├── olist_customers_dataset.csv
├── olist_geolocation_dataset.csv        (not used by the analysis)
├── olist_order_items_dataset.csv
├── olist_order_payments_dataset.csv
├── olist_order_reviews_dataset.csv
├── olist_orders_dataset.csv
├── olist_products_dataset.csv
├── olist_sellers_dataset.csv
└── product_category_name_translation.csv
```

## Generated files

`data/processed/` is filled automatically by notebook 01 (or `scripts/run_pipeline.py`)
with the cleaned analytics tables: `orders.csv`, `order_items.csv`, `customers.csv`.
It's git-ignored, so rebuild it any time.

## Data model

| Raw table | Rows | Key | Notes |
|---|---|---|---|
| orders | 99,441 | `order_id` | 775 have no items (never fulfilled) |
| customers | 99,441 | `customer_id` | `customer_id` is **per order**; the person is `customer_unique_id` (96,096) |
| order_items | 112,650 | `order_id` + `order_item_id` | One row per unit/line |
| order_payments | 103,886 | `order_id` + `payment_sequential` | Orders can be split across payments |
| order_reviews | 99,224 | none | Some orders have several reviews; some `review_id`s cover several orders |
| products | 32,951 | `product_id` | 610 products have no category |
| sellers | 3,095 | `seller_id` | |
| category_translation | 71 | `product_category_name` | 2 categories missing (patched in the model) |
