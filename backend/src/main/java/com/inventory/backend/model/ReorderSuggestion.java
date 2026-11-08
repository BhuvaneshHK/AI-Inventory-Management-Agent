package com.inventory.backend.model;

import com.fasterxml.jackson.annotation.JsonAlias;

// @JsonAlias lets us read the Python service's field names (e.g. "Store_id")
// while still exposing clean camelCase names from our own API.
public record ReorderSuggestion(
        String date,
        @JsonAlias("Store_id") String storeId,
        @JsonAlias("Product_id") String productId,
        @JsonAlias("Category") String category,
        @JsonAlias("Inventory_level") int inventoryLevel,
        @JsonAlias("Predicted_Demand") double predictedDemand,
        @JsonAlias("Days_Of_Cover") double daysOfCover,
        @JsonAlias("Reorder_Suggested") boolean reorderSuggested,
        @JsonAlias("Suggested_Reorder_Qty") int suggestedReorderQty) {
}
