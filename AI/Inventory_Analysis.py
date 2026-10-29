from pathlib import Path
import sqlite3
import pandas as pd
import joblib

# Locate inventory.db and the saved model relative to this file.
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR.parent / "database" / "inventory.db"
MODEL_PATH = BASE_DIR / "demand_model.pkl"

# Load the trained model and the feature column order it was trained on.
saved = joblib.load(MODEL_PATH)
model = saved["model"]
feature_columns = saved["feature_columns"]

# Load current inventory rows, joined with Product for Category.
conn = sqlite3.connect(DB_PATH)
df = pd.read_sql_query(
    """
    SELECT
        i.id,
        i.date,
        i.Store_id,
        i.Product_id,
        i.price,
        i.Discount,
        i.Holiday_Promotion,
        i.Inventory_level,
        i.Weather_Condition,
        i.Seasonality,
        p.Category
    FROM Inventory i
    LEFT JOIN Product p ON i.Product_id = p.Product_id
    """,
    conn,
)
conn.close()

# Rebuild the same feature set used during training (one-hot encoding).
numeric_features = ["price", "Discount", "Holiday_Promotion", "Inventory_level"]
categorical_features = ["Weather_Condition", "Seasonality", "Category"]

X = pd.get_dummies(
    df[numeric_features + categorical_features],
    columns=categorical_features,
    drop_first=True,
)

# Align columns to match training exactly (adds any missing dummy columns as 0,
# drops any extra ones, and puts them in the same order the model expects).
X = X.reindex(columns=feature_columns, fill_value=0)

# Predict demand for every row using the trained model.
df["Predicted_Demand"] = model.predict(X)

# Compare predicted demand against current stock to flag reorder needs.
# If predicted demand exceeds what's currently in stock, a reorder is suggested.
df["Reorder_Suggested"] = df["Predicted_Demand"] > df["Inventory_level"]
df["Suggested_Reorder_Qty"] = (df["Predicted_Demand"] - df["Inventory_level"]).clip(lower=0).round().astype(int)

# Build a clean results table with just the relevant columns.
results = df[[
    "date", "Store_id", "Product_id", "Inventory_level",
    "Predicted_Demand", "Reorder_Suggested", "Suggested_Reorder_Qty"
]]

# Show a quick preview of flagged reorders.
flagged = results[results["Reorder_Suggested"]]
print(f"Total rows analyzed: {len(results)}")
print(f"Rows flagged for reorder: {len(flagged)}")
print(flagged.head(10))

# Save the full results to a CSV for inspection or later use by the backend.
OUTPUT_PATH = BASE_DIR / "reorder_suggestions.csv"
results.to_csv(OUTPUT_PATH, index=False)
print(f"Results saved to {OUTPUT_PATH}")