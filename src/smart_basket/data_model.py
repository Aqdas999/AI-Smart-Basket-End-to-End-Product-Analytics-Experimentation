"""Builds the analytics tables from the raw Olist CSVs with pandas.

This is the Python twin of ``sql/03_analytics_model.sql``; both produce the
same three tables at the same grain:

* ``order_items`` – one row per order line
* ``orders``      – one row per order (main fact table)
* ``customers``   – one row per real customer (``customer_unique_id``)

The rule that fixes the original project's revenue bug: aggregate each child
table (items, payments, reviews) to order grain *before* joining.
"""

from __future__ import annotations

import pandas as pd

from . import config

_DATE_COLS = {
    "orders": [
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date",
    ],
    "order_reviews": ["review_creation_date", "review_answer_timestamp"],
}


def load_raw(raw_dir=config.RAW_DIR) -> dict[str, pd.DataFrame]:
    """Read every raw CSV into a dict of DataFrames (geolocation is skipped)."""
    missing = [f for f in config.RAW_FILES.values() if not (raw_dir / f).exists()]
    if missing:
        raise FileNotFoundError(
            f"Missing raw files in {raw_dir}: {missing}. "
            "Run `python scripts/download_data.py` first (see data/README.md)."
        )
    raw = {}
    for name, filename in config.RAW_FILES.items():
        raw[name] = pd.read_csv(
            raw_dir / filename,
            parse_dates=_DATE_COLS.get(name, []),
            encoding="utf-8-sig",  # the translation file starts with a BOM
            dtype={"customer_zip_code_prefix": str, "seller_zip_code_prefix": str},
        )
    return raw


def build_order_items(raw: dict[str, pd.DataFrame]) -> pd.DataFrame:
    translation = raw["category_translation"].set_index("product_category_name")[
        "product_category_name_english"
    ].to_dict()
    translation.update(config.MISSING_TRANSLATIONS)

    items = raw["order_items"].merge(
        raw["products"][["product_id", "product_category_name"]], on="product_id", how="left"
    )
    items["category"] = items["product_category_name"].map(translation).fillna("unknown")
    return items[
        ["order_id", "order_item_id", "product_id", "seller_id", "category", "price", "freight_value"]
    ]


def build_orders(raw: dict[str, pd.DataFrame], order_items: pd.DataFrame) -> pd.DataFrame:
    # items -> order grain
    items = order_items.groupby("order_id").agg(
        items_count=("order_item_id", "size"),
        distinct_products=("product_id", "nunique"),
        distinct_categories=("category", "nunique"),
        distinct_sellers=("seller_id", "nunique"),
        item_revenue=("price", "sum"),
        freight_revenue=("freight_value", "sum"),
    )
    primary_category = (
        order_items.sort_values(["order_id", "price", "order_item_id"], ascending=[True, False, True])
        .drop_duplicates("order_id")
        .set_index("order_id")["category"]
        .rename("primary_category")
    )

    # payments -> order grain
    pay = raw["order_payments"]
    payments = pay.groupby("order_id").agg(
        payment_value=("payment_value", "sum"),
        max_installments=("payment_installments", "max"),
        payment_count=("payment_sequential", "size"),
    )
    primary_payment = (
        pay.sort_values(["order_id", "payment_value", "payment_sequential"], ascending=[True, False, True])
        .drop_duplicates("order_id")
        .set_index("order_id")["payment_type"]
        .rename("primary_payment_type")
    )

    # latest review per order
    reviews = (
        raw["order_reviews"]
        .sort_values(["order_id", "review_answer_timestamp", "review_creation_date"], na_position="first")
        .drop_duplicates("order_id", keep="last")
        .set_index("order_id")["review_score"]
    )

    o = raw["orders"].merge(
        raw["customers"][["customer_id", "customer_unique_id", "customer_state"]],
        on="customer_id",
        how="inner",
    )
    o = o.join(items, on="order_id", how="inner")  # drops orders with no items
    o = o.join(primary_category, on="order_id").join(payments, on="order_id")
    o = o.join(primary_payment, on="order_id").join(reviews, on="order_id")

    delivered = o["order_delivered_customer_date"]
    orders = pd.DataFrame(
        {
            "order_id": o["order_id"],
            "customer_unique_id": o["customer_unique_id"],
            "customer_state": o["customer_state"],
            "order_status": o["order_status"],
            "purchased_at": o["order_purchase_timestamp"],
            "purchase_month": o["order_purchase_timestamp"].dt.to_period("M").dt.to_timestamp(),
            "is_delivered": o["order_status"].eq("delivered"),
            "is_canceled": o["order_status"].isin(["canceled", "unavailable"]),
            "items_count": o["items_count"],
            "distinct_products": o["distinct_products"],
            "distinct_categories": o["distinct_categories"],
            "distinct_sellers": o["distinct_sellers"],
            "is_multi_product": o["distinct_products"] > 1,
            "primary_category": o["primary_category"],
            "item_revenue": o["item_revenue"],
            "freight_revenue": o["freight_revenue"],
            "gmv": o["item_revenue"] + o["freight_revenue"],
            "payment_value": o["payment_value"],
            "primary_payment_type": o["primary_payment_type"],
            "max_installments": o["max_installments"],
            "review_score": o["review_score"],
            "delivery_days": (delivered - o["order_purchase_timestamp"]).dt.total_seconds() / 86400,
            "is_late": (delivered.dt.normalize() > o["order_estimated_delivery_date"].dt.normalize()).where(
                delivered.notna()
            ),
        }
    )
    orders = orders.sort_values(["customer_unique_id", "purchased_at", "order_id"])
    orders["customer_order_number"] = orders.groupby("customer_unique_id").cumcount() + 1
    orders["is_repeat_order"] = orders["customer_order_number"] > 1
    return orders.sort_values("purchased_at").reset_index(drop=True)


def build_customers(orders: pd.DataFrame) -> pd.DataFrame:
    valid = orders[~orders["is_canceled"]]
    c = valid.groupby("customer_unique_id").agg(
        first_order_at=("purchased_at", "min"),
        last_order_at=("purchased_at", "max"),
        valid_orders=("order_id", "size"),
        lifetime_gmv=("gmv", "sum"),
        avg_review_score=("review_score", "mean"),
    )
    c["cohort_month"] = c["first_order_at"].dt.to_period("M").dt.to_timestamp()
    c["is_repeat_customer"] = c["valid_orders"] > 1
    return c.reset_index()


def build_all(raw_dir=config.RAW_DIR, save: bool = True) -> dict[str, pd.DataFrame]:
    """Build all analytics tables; optionally cache them to data/processed/."""
    raw = load_raw(raw_dir)
    order_items = build_order_items(raw)
    orders = build_orders(raw, order_items)
    customers = build_customers(orders)
    tables = {"order_items": order_items, "orders": orders, "customers": customers}
    if save:
        config.PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
        for name, df in tables.items():
            df.to_csv(config.PROCESSED_DIR / f"{name}.csv", index=False)
    return tables


def load_tables() -> dict[str, pd.DataFrame]:
    """Load cached analytics tables, building them first if needed."""
    paths = {n: config.PROCESSED_DIR / f"{n}.csv" for n in ("order_items", "orders", "customers")}
    if not all(p.exists() for p in paths.values()):
        return build_all()
    dates = {
        "orders": ["purchased_at", "purchase_month"],
        "customers": ["first_order_at", "last_order_at", "cohort_month"],
        "order_items": [],
    }
    return {n: pd.read_csv(p, parse_dates=dates[n]) for n, p in paths.items()}
