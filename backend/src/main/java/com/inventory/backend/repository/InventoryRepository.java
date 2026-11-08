package com.inventory.backend.repository;

import com.inventory.backend.model.InventoryItem;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.jdbc.core.RowMapper;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public class InventoryRepository {

    // Most recent row for each store/product pair, joined with Product for the category.
    private static final String LATEST_SNAPSHOT_SQL = """
            SELECT i.date, i.Store_id, i.Product_id, p.Category,
                   i.Inventory_level, i.Units_Sold, i.price, i.Discount
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
            """;

    // Converts one database row into one InventoryItem object.
    private static final RowMapper<InventoryItem> ROW_MAPPER = (rs, rowNum) -> new InventoryItem(
            rs.getString("date"),
            rs.getString("Store_id"),
            rs.getString("Product_id"),
            rs.getString("Category"),
            rs.getInt("Inventory_level"),
            rs.getInt("Units_Sold"),
            rs.getDouble("price"),
            rs.getDouble("Discount"));

    private final JdbcTemplate jdbcTemplate;

    public InventoryRepository(JdbcTemplate jdbcTemplate) {
        this.jdbcTemplate = jdbcTemplate;
    }

    public List<InventoryItem> findLatestSnapshot(String storeId) {
        if (storeId == null || storeId.isBlank()) {
            return jdbcTemplate.query(
                    LATEST_SNAPSHOT_SQL + " ORDER BY i.Store_id, i.Product_id", ROW_MAPPER);
        }
        return jdbcTemplate.query(
                LATEST_SNAPSHOT_SQL + " WHERE i.Store_id = ? ORDER BY i.Product_id", ROW_MAPPER, storeId);
    }
}
