package com.inventory.backend.service;

import com.inventory.backend.model.ReorderSuggestion;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestClientException;
import org.springframework.web.client.RestTemplate;
import org.springframework.web.server.ResponseStatusException;
import org.springframework.web.util.UriComponentsBuilder;

import java.util.Arrays;
import java.util.List;

@Service
public class AiServiceClient {

    private final RestTemplate restTemplate;
    private final String baseUrl;

    public AiServiceClient(RestTemplate restTemplate, @Value("${ai.service.url}") String baseUrl) {
        this.restTemplate = restTemplate;
        this.baseUrl = baseUrl;
    }

    public List<ReorderSuggestion> getReorderSuggestions(String storeId, boolean onlyFlagged) {
        UriComponentsBuilder uri = UriComponentsBuilder
                .fromUriString(baseUrl + "/reorder-suggestions")
                .queryParam("only_flagged", onlyFlagged);

        if (storeId != null && !storeId.isBlank()) {
            uri.queryParam("store_id", storeId);
        }

        try {
            ReorderSuggestion[] response = restTemplate.getForObject(uri.toUriString(), ReorderSuggestion[].class);
            return response == null ? List.of() : Arrays.asList(response);
        } catch (RestClientException e) {
            throw new ResponseStatusException(HttpStatus.BAD_GATEWAY, "AI service is unavailable", e);
        }
    }
}
