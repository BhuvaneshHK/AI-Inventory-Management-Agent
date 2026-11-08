package com.inventory.backend.controller;

import com.inventory.backend.model.ReorderSuggestion;
import com.inventory.backend.service.AiServiceClient;
import org.springframework.web.bind.annotation.CrossOrigin;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

@RestController
@RequestMapping("/api/reorder-suggestions")
@CrossOrigin(origins = "*")
public class ReorderController {

    private final AiServiceClient aiServiceClient;

    public ReorderController(AiServiceClient aiServiceClient) {
        this.aiServiceClient = aiServiceClient;
    }

    @GetMapping
    public List<ReorderSuggestion> getSuggestions(
            @RequestParam(name = "storeId", required = false) String storeId,
            @RequestParam(name = "onlyFlagged", defaultValue = "false") boolean onlyFlagged) {
        return aiServiceClient.getReorderSuggestions(storeId, onlyFlagged);
    }
}
