"""Load retail_store_inventory.csv into inventory.db (Product, Store, Inventory)."""

from pathlib import Path

import pandas as pd
import sqlite3

# Resolve paths relative to this file so the script can run from any working directory.
BASE_DIR = Path(__file__).resolve().parent
CSV_PATH = BASE_DIR / "retail_store_inventory.csv"
DB_PATH = BASE_DIR / "inventory.db"

# Load the CSV and print a few rows to confirm the columns look right.
df = pd.read_csv(CSV_PATH)
print(df.head())

# Rename CSV headers to match the column names in schema.sql.
df = df.rename(
    columns={
        "Date": "date",
        "Store ID": "Store_id",
        "Product ID": "Product_id",
        "Category": "Category",
        "Region": "Region",
        "Inventory Level": "Inventory_level",
        "Units Sold": "Units_Sold",
        "Units Ordered": "Units_Ordered",
        "Demand Forecast": "Demand_Forecast",
        "Price": "price",
        "Discount": "Discount",
        "Weather Condition": "Weather_Condition",
        "Holiday/Promotion": "Holiday_Promotion",
        "Competitor Pricing": "Competitor_Price",
        "Seasonality": "Seasonality",
    }
)

# Open inventory.db and insert Product, Store, then Inventory rows.
with sqlite3.connect(DB_PATH) as conn:
    # Keep one row per product so each Product_id is unique.
    products_df = df[["Product_id", "Category"]].drop_duplicates(subset=["Product_id"])
    products_df.to_sql("Product", conn, if_exists="append", index=False)

    # Keep one row per store so each Store_id is unique.
    stores_df = df[["Store_id", "Region"]].drop_duplicates(subset=["Store_id"])
    stores_df.to_sql("Store", conn, if_exists="append", index=False)

    # Keep every daily store–product row for the Inventory table.
    inventory_df = df[
        [
            "date",
            "Store_id",
            "Product_id",
            "Inventory_level",
            "Units_Sold",
            "Units_Ordered",
            "Demand_Forecast",
            "price",
            "Discount",
            "Weather_Condition",
            "Holiday_Promotion",
            "Competitor_Price",
            "Seasonality",
        ]
    ]
    inventory_df.to_sql("Inventory", conn, if_exists="append", index=False)

print("Data loaded successfully into inventory.db")
