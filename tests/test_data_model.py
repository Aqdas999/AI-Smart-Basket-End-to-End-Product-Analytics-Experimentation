"""Data-model tests on a tiny hand-built dataset (no Kaggle download needed)."""

import pandas as pd
import pytest

from smart_basket import data_model as dm


@pytest.fixture
def raw():
    ts = pd.Timestamp
    return {
        "customers": pd.DataFrame(
            {
                "customer_id": ["c1", "c2", "c3"],
                "customer_unique_id": ["alice", "alice", "bob"],  # alice ordered twice
                "customer_zip_code_prefix": ["1", "1", "2"],
                "customer_city": ["x", "x", "y"],
                "customer_state": ["SP", "SP", "RJ"],
            }
        ),
        "orders": pd.DataFrame(
            {
                "order_id": ["o1", "o2", "o3"],
                "customer_id": ["c1", "c2", "c3"],
                "order_status": ["delivered", "delivered", "canceled"],
                "order_purchase_timestamp": [ts("2018-01-01"), ts("2018-02-01"), ts("2018-01-05")],
                "order_approved_at": [ts("2018-01-01")] * 3,
                "order_delivered_carrier_date": [ts("2018-01-02")] * 3,
                "order_delivered_customer_date": [ts("2018-01-05"), ts("2018-02-20"), pd.NaT],
                "order_estimated_delivery_date": [ts("2018-01-10"), ts("2018-02-10"), ts("2018-01-20")],
            }
        ),
        # o1: 2 different products (multi-product); o2: same product twice
        "order_items": pd.DataFrame(
            {
                "order_id": ["o1", "o1", "o2", "o2", "o3"],
                "order_item_id": [1, 2, 1, 2, 1],
                "product_id": ["p1", "p2", "p1", "p1", "p2"],
                "seller_id": ["s1", "s2", "s1", "s1", "s2"],
                "shipping_limit_date": [ts("2018-01-02")] * 5,
                "price": [100.0, 50.0, 100.0, 100.0, 50.0],
                "freight_value": [10.0, 5.0, 10.0, 10.0, 5.0],
            }
        ),
        # o1 paid in two parts -> a naive items x payments join would make 4 rows
        "order_payments": pd.DataFrame(
            {
                "order_id": ["o1", "o1", "o2", "o3"],
                "payment_sequential": [1, 2, 1, 1],
                "payment_type": ["credit_card", "voucher", "boleto", "credit_card"],
                "payment_installments": [3, 1, 1, 1],
                "payment_value": [140.0, 25.0, 220.0, 55.0],
            }
        ),
        "order_reviews": pd.DataFrame(
            {
                "review_id": ["r1", "r2", "r3"],
                "order_id": ["o1", "o1", "o2"],
                "review_score": [2, 5, 1],
                "review_comment_title": [None] * 3,
                "review_comment_message": [None] * 3,
                "review_creation_date": [ts("2018-01-06"), ts("2018-01-08"), ts("2018-02-21")],
                "review_answer_timestamp": [ts("2018-01-07"), ts("2018-01-09"), ts("2018-02-22")],
            }
        ),
        "products": pd.DataFrame({"product_id": ["p1", "p2"], "product_category_name": ["cama_mesa_banho", "pc_gamer"]}),
        "sellers": pd.DataFrame({"seller_id": ["s1", "s2"]}),
        "category_translation": pd.DataFrame(
            {"product_category_name": ["cama_mesa_banho"], "product_category_name_english": ["bed_bath_table"]}
        ),
    }


@pytest.fixture
def tables(raw):
    items = dm.build_order_items(raw)
    orders = dm.build_orders(raw, items)
    return items, orders, dm.build_customers(orders)


def test_one_row_per_order(tables):
    _, orders, _ = tables
    assert orders["order_id"].is_unique
    assert len(orders) == 3


def test_payments_not_multiplied_by_items(raw, tables):
    _, orders, _ = tables
    o1 = orders.set_index("order_id").loc["o1"]
    assert o1["payment_value"] == pytest.approx(165.0)  # 140 + 25, not doubled
    assert orders["payment_value"].sum() == pytest.approx(raw["order_payments"]["payment_value"].sum())
    assert orders["item_revenue"].sum() == pytest.approx(raw["order_items"]["price"].sum())


def test_multi_product_uses_distinct_products(tables):
    _, orders, _ = tables
    o = orders.set_index("order_id")
    assert o.loc["o1", "is_multi_product"]          # p1 + p2
    assert not o.loc["o2", "is_multi_product"]      # p1 twice
    assert o.loc["o2", "items_count"] == 2


def test_repeat_logic_uses_unique_customer(tables):
    _, orders, customers = tables
    o = orders.set_index("order_id")
    assert o.loc["o1", "customer_order_number"] == 1
    assert o.loc["o2", "customer_order_number"] == 2
    assert o.loc["o2", "is_repeat_order"]
    c = customers.set_index("customer_unique_id")
    assert c.loc["alice", "is_repeat_customer"]
    assert "bob" not in c.index  # bob's only order was canceled


def test_latest_review_and_lateness(tables):
    _, orders, _ = tables
    o = orders.set_index("order_id")
    assert o.loc["o1", "review_score"] == 5          # latest answered review wins
    assert not o.loc["o1", "is_late"]
    assert o.loc["o2", "is_late"]                     # delivered 20 Feb, estimated 10 Feb
    assert pd.isna(o.loc["o3", "delivery_days"])


def test_missing_translation_filled(tables):
    items, _, _ = tables
    assert set(items["category"]) == {"bed_bath_table", "pc_gamer"}
