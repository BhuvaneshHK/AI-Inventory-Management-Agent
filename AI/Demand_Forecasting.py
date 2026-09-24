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
MODEL_PATH = BASE_DIR / 'demand_model.pkl'

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

# Inspect the target distribution before splitting and training.
print(df["Units_Sold"].describe())
print(df.corr(numeric_only=True)["Units_Sold"].sort_values(ascending=False))

# Keep numeric inputs as-is and one-hot encode text columns for LinearRegression.
numeric_features = ["price", "Discount", "Holiday_Promotion", "Inventory_level"]
categorical_features = ["Weather_Condition", "Seasonality", "Category"]

X = pd.get_dummies(
    df[numeric_features + categorical_features],
    columns=categorical_features,
    drop_first=True,
)
Y = df["Units_Sold"]

# Hold out 20% of rows so MAE is measured on unseen data.
X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.2, random_state=42)

# Fit a linear model that maps the selected features to Units_Sold.
model = LinearRegression()
model.fit(X_train, Y_train)

# Generate test-set predictions and report average absolute error.
predictions = model.predict(X_test)
mae = mean_absolute_error(Y_test, predictions)
print(f"Mean Absolute Error: {mae: .2f}")

# Save the model and dummy column names so later predictions use the same feature layout.
joblib.dump({"model": model, "feature_columns": X.columns.tolist()}, MODEL_PATH)
print(f"Model saved to {MODEL_PATH}")
print(f"Training features: {X.columns.tolist()}")
