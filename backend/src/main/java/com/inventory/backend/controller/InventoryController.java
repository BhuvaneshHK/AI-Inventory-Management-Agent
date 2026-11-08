package com.inventory.backend.controller;

import com.inventory.backend.model.InventoryItem;
import com.inventory.backend.repository.InventoryRepository;
import org.springframework.web.bind.annotation.CrossOrigin;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

@RestController
@RequestMapping("/api/inventory")
@CrossOrigin(origins = "*")
public class InventoryController {

    private final InventoryRepository repository;

    public InventoryController(InventoryRepository repository) {
        this.repository = repository;
    }

    @GetMapping
    public List<InventoryItem> getInventory(
            @RequestParam(name = "storeId", required = false) String storeId) {
        return repository.findLatestSnapshot(storeId);
    }
}
