from pathlib import Path
import sqlite3
import pandas as pd
import joblib

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR.parent / "database" / "inventory.db"
MODEL_PATH = BASE_DIR / "demand_model.pkl"
OUTPUT_PATH = BASE_DIR / "reorder_suggestions.csv"

# Flag a reorder when current stock covers fewer than this many days of predicted demand.
COVER_THRESHOLD_DAYS = 2.0
# When reordering, bring stock up to this many days of predicted demand.
TARGET_COVER_DAYS = 3.0

# Must match the feature lists used in Demand_Forecasting.py.
NUMERIC_FEATURES = ["price", "Discount", "Holiday_Promotion", "Inventory_level"]
CATEGORICAL_FEATURES = ["Weather_Condition", "Seasonality", "Category"]


def load_latest_inventory():
    """Load only the most recent row for each store/product pair (the current stock snapshot)."""
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(
        """
        SELECT
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
        JOIN (
            SELECT Store_id, Product_id, MAX(date) AS max_date
            FROM Inventory
            GROUP BY Store_id, Product_id
        ) latest
            ON i.Store_id = latest.Store_id
            AND i.Product_id = latest.Product_id
            AND i.date = latest.max_date
        LEFT JOIN Product p ON i.Product_id = p.Product_id
        """,
        conn,
    )
    conn.close()
    return df


def generate_reorder_suggestions():
    """Predict demand for the current snapshot and return reorder suggestions."""
    saved = joblib.load(MODEL_PATH)
    model = saved["model"]
    feature_columns = saved["feature_columns"]

    df = load_latest_inventory()

    # Encode without drop_first, then reindex to the training columns so the layout always matches.
    X = pd.get_dummies(
        df[NUMERIC_FEATURES + CATEGORICAL_FEATURES],
        columns=CATEGORICAL_FEATURES,
    )
    X = X.reindex(columns=feature_columns, fill_value=0)

    df["Predicted_Demand"] = model.predict(X).clip(min=0).round(1)
    df["Days_Of_Cover"] = (df["Inventory_level"] / df["Predicted_Demand"].clip(lower=1)).round(2)
    df["Reorder_Suggested"] = df["Days_Of_Cover"] < COVER_THRESHOLD_DAYS
    df["Suggested_Reorder_Qty"] = (
        (TARGET_COVER_DAYS * df["Predicted_Demand"] - df["Inventory_level"])
        .clip(lower=0)
        .round()
        .astype(int)
    )

    return df[[
        "date", "Store_id", "Product_id", "Category", "Inventory_level",
        "Predicted_Demand", "Days_Of_Cover", "Reorder_Suggested", "Suggested_Reorder_Qty",
    ]]


if __name__ == "__main__":
    results = generate_reorder_suggestions()
    flagged = results[results["Reorder_Suggested"]]

    print(f"Store/product pairs analyzed: {len(results)}")
    print(f"Flagged for reorder: {len(flagged)}")
    print(results["Days_Of_Cover"].describe())
    print(flagged.head(10))

    results.to_csv(OUTPUT_PATH, index=False)
    print(f"Results saved to {OUTPUT_PATH}")