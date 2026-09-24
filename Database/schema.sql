
--Defines the database structure for the AI Inventory Management System

-- Creating a table for Product
CREATE TABLE Product(
    Product_id TEXT PRIMARY KEY,
    Category TEXT
);

-- Creating a table for Store
CREATE TABLE Store(
    Store_id TEXT PRIMARY KEY,
    Region TEXT
);

-- Creating a table for Inventory
CREATE TABLE Inventory(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT,
    Store_id TEXT,
    Product_id TEXT,
    Inventory_level INTEGER,
    Units_Sold INTEGER,
    Units_Ordered INTEGER,
    Demand_Forecast REAL,
    price REAL,
    Discount REAL,
    Weather_Condition TEXT,
    Holiday_Promotion INTEGER,
    Competitor_Price REAL,
    Seasonality TEXT,
    FOREIGN KEY (Store_id) REFERENCES Store(Store_id),
    FOREIGN KEY (Product_id) REFERENCES Product(Product_id)

);