package com.inventory.backend.model;

public record InventoryItem(
        String date,
        String storeId,
        String productId,
        String category,
        int inventoryLevel,
        int unitsSold,
        double price,
        double discount) {
}
