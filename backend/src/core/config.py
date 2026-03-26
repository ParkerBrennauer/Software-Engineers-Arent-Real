"""Centralized configuration for data file paths."""
from pathlib import Path

# Base data directory
DATA_DIR = Path(__file__).resolve().parent.parent / "data"

# Individual file paths
USERS_FILE = DATA_DIR / "users.json"
ITEMS_FILE = DATA_DIR / "items.json"
ORDERS_FILE = DATA_DIR / "orders.json"
RESTAURANTS_FILE = DATA_DIR / "restaurants.json"
REVIEWS_FILE = DATA_DIR / "reviews.json"
REPORTS_FILE = DATA_DIR / "reports.json"
DELIVERY_FILE = DATA_DIR / "delivery.json"
CUSTOMERS_FILE = DATA_DIR / "customers.json"
