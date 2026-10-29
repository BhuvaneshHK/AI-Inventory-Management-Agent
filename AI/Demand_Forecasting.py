
from pathlib import Path
import sqlite3

import joblib
import numpy as np
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_absolute_error
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

# Define file paths
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR.parent / "database" / "inventory.db"
MODEL_PATH = BASE_DIR / "demand_model.pkl"

if not DB_PATH.exists():
    raise FileNotFoundError(f"Database not found: {DB_PATH}")

# Load inventory data and join product categories
query = """
    SELECT
        i.price,
        i.Discount,
        i.Holiday_Promotion,
        i.Inventory_level,
        i.Weather_Condition,
        i.Seasonality,
        i.Units_Sold,
        p.Category
    FROM Inventory AS i
    LEFT JOIN Product AS p
        ON i.Product_id = p.Product_id
"""

with sqlite3.connect(DB_PATH) as conn:
    df = pd.read_sql_query(query, conn)

if df.empty:
    raise ValueError("No inventory records were found in the database.")

print(f"Loaded {len(df)} inventory records.")

# Define numeric features, categorical features, and target
numeric_features = [
    "price",
    "Discount",
    "Holiday_Promotion",
    "Inventory_level",
]

categorical_features = [
    "Weather_Condition",
    "Seasonality",
    "Category",
]

feature_columns = numeric_features + categorical_features
target_column = "Units_Sold"

# Convert numeric columns to valid numeric values
for column in numeric_features + [target_column]:
    df[column] = pd.to_numeric(df[column], errors="coerce")

# Remove rows with missing or infinite target values
df = df.dropna(subset=[target_column]).copy()
df = df[np.isfinite(df[target_column])].copy()

if df.empty:
    raise ValueError("No valid Units_Sold values are available.")

# Prepare input features and target values
X = df[feature_columns].copy()
y = df[target_column].copy()

# Replace infinite feature values with missing values
X[numeric_features] = X[numeric_features].replace(
    [np.inf, -np.inf], np.nan
)

# Split data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
)

print(f"Training records: {len(X_train)}")
print(f"Testing records: {len(X_test)}")

# Fill missing numeric values with medians
numeric_pipeline = Pipeline([
    ("imputer", SimpleImputer(strategy="median")),
])

# Fill missing categorical values and encode text columns
categorical_pipeline = Pipeline([
    ("imputer", SimpleImputer(strategy="most_frequent")),
    ("encoder", OneHotEncoder(handle_unknown="ignore")),
])

# Apply the appropriate preprocessing to each feature type
preprocessor = ColumnTransformer([
    ("numeric", numeric_pipeline, numeric_features),
    ("categorical", categorical_pipeline, categorical_features),
])

# Create a Random Forest regression pipeline
model = Pipeline([
    ("preprocessor", preprocessor),
    (
        "regressor",
        RandomForestRegressor(
            n_estimators=300,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=-1,
        ),
    ),
])

# Train the model using historical inventory data
print("\nTraining demand forecasting model...")
model.fit(X_train, y_train)
print("Training completed.")

# Predict units sold for the test dataset
predictions = model.predict(X_test)

# Calculate the model's mean absolute error
mae = mean_absolute_error(y_test, predictions)

# Calculate baseline error by predicting average training sales
baseline_predictions = np.full(len(y_test), y_train.mean())
baseline_mae = mean_absolute_error(y_test, baseline_predictions)

# Display model performance
print("\nModel Evaluation")
print(f"Model MAE: {mae:.2f}")
print(f"Baseline MAE: {baseline_mae:.2f}")

if baseline_mae > 0:
    improvement = (
        (baseline_mae - mae) / baseline_mae
    ) * 100
    print(f"Baseline MAE reduction: {improvement:.2f}%")

if mae < baseline_mae:
    print("Result: Model outperforms the baseline.")
elif mae == baseline_mae:
    print("Result: Model matches the baseline.")
else:
    print("Result: Model does not outperform the baseline.")

# Save the trained model and preprocessing pipeline
joblib.dump(model, MODEL_PATH)
print(f"\nModel saved to {MODEL_PATH}")
