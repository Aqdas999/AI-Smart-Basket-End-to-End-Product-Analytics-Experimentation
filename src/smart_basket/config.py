"""Project paths and analysis constants shared by every notebook and script."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = ROOT / "data" / "raw"
PROCESSED_DIR = ROOT / "data" / "processed"
REPORTS_DIR = ROOT / "reports"
IMAGES_DIR = ROOT / "images"
DASHBOARD_DIR = ROOT / "dashboard"

RAW_FILES = {
    "customers": "olist_customers_dataset.csv",
    "orders": "olist_orders_dataset.csv",
    "order_items": "olist_order_items_dataset.csv",
    "order_payments": "olist_order_payments_dataset.csv",
    "order_reviews": "olist_order_reviews_dataset.csv",
    "products": "olist_products_dataset.csv",
    "sellers": "olist_sellers_dataset.csv",
    "category_translation": "product_category_name_translation.csv",
}

# Olist data is sparse before Jan 2017 and after Aug 2018 (partial months,
# orders not yet delivered), so trend metrics use this complete window.
ANALYSIS_START = "2017-01-01"
ANALYSIS_END = "2018-08-31"

# Two Portuguese category names that are missing from the translation file.
MISSING_TRANSLATIONS = {
    "pc_gamer": "pc_gamer",
    "portateis_cozinha_e_preparadores_de_alimentos": "portable_kitchen_and_food_preparers",
}

RANDOM_SEED = 42
