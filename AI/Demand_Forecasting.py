from pathlib import Path
import sqlite3
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error
import joblib

# Locate inventory.db relative to this file so the script can run from any working directory.
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR.parent / "database" / "inventory.db"
MODEL_PATH = BASE_DIR / "demand_model.pkl"

# Load inventory rows and join Product so Category is available as a feature.
conn = sqlite3.connect(DB_PATH)
df = pd.read_sql_query(
    """
    SELECT
        i.price,
        i.Discount,
        i.Holiday_Promotion,
        i.Inventory_level,
        i.Weather_Condition,
        i.Seasonality,
        i.Units_Sold,
        p.Category
    FROM Inventory i
    LEFT JOIN Product p ON i.Product_id = p.Product_id
    """,
    conn,
)
conn.close()

# NOTE: Demand_Forecast is deliberately excluded. It correlates ~0.997 with Units_Sold,
# meaning it's essentially a near-copy of the target rather than a genuine input signal.
# Including it would make this a "correct an existing forecast" model, not a real
# demand-forecasting model built from operational data.
numeric_features = ["price", "Discount", "Holiday_Promotion", "Inventory_level"]
categorical_features = ["Weather_Condition", "Seasonality", "Category"]

# One-hot encode text columns so LinearRegression can use them.
X = pd.get_dummies(
    df[numeric_features + categorical_features],
    columns=categorical_features,
    drop_first=True,
)
Y = df["Units_Sold"]

# Hold out 20% of rows so MAE is measured on unseen data.
X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.2, random_state=42)

# Fit a linear model mapping the selected features to Units_Sold.
model = LinearRegression()
model.fit(X_train, Y_train)

# Generate test-set predictions and report error against a naive baseline.
predictions = model.predict(X_test)
mae = mean_absolute_error(Y_test, predictions)
baseline_mae = mean_absolute_error(Y_test, [Y_train.mean()] * len(Y_test))

print(f"Mean Absolute Error: {mae:.2f}")
print(f"Baseline MAE (predicting the average every time): {baseline_mae:.2f}")

# Save the model and feature column order so future predictions use the same layout.
joblib.dump({"model": model, "feature_columns": X.columns.tolist()}, MODEL_PATH)
print(f"Model saved to {MODEL_PATH}")