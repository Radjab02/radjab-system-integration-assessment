package com.ecommerce.integration.client;

import com.ecommerce.integration.model.ApiResponse;
import com.ecommerce.integration.model.Customer;
import com.ecommerce.integration.model.Product;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.core.ParameterizedTypeReference;
import org.springframework.retry.annotation.Backoff;
import org.springframework.retry.annotation.Retryable;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestClient;
import org.springframework.web.client.RestClientException;

import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.List;

/**
 * Client for interacting with Mock APIs
 * Implements retry logic for resilience
 */
@Component
@Slf4j
public class MockApiClient {
    
    private final RestClient restClient;
    
    @Value("${api.mock-apis.endpoints.customers}")
    private String customersEndpoint;
    
    @Value("${api.mock-apis.endpoints.products}")
    private String productsEndpoint;
    
    public MockApiClient(@Value("${api.mock-apis.base-url}") String baseUrl,
                        @Value("${api.mock-apis.timeout}") int timeout) {
        this.restClient = RestClient.builder()
                .baseUrl(baseUrl)
                .build();
        
        log.info("MockApiClient initialized with base URL: {}", baseUrl);
    }
    
    /**
     * Fetch all customers (full sync)
     */
    @Retryable(
        retryFor = {RestClientException.class},
        maxAttemptsExpression = "${api.mock-apis.retry.max-attempts}",
        backoff = @Backoff(
            delayExpression = "${api.mock-apis.retry.backoff-delay}",
            multiplierExpression = "${api.mock-apis.retry.backoff-multiplier}"
        )
    )
    public List<Customer> fetchAllCustomers() {
        log.info("Fetching all customers (full sync)");
        
        List<Customer> allCustomers = new ArrayList<>();
        int page = 0;
        final int pageSize = 100;
        boolean hasMore = true;
        
        while (hasMore) {
            final int currentPage = page;
            try {
                ApiResponse.CustomerPage response = restClient.get()
                        .uri(uriBuilder -> uriBuilder
                                .path(customersEndpoint)
                                .queryParam("page", currentPage)
                                .queryParam("size", pageSize)
                                .build())
                        .retrieve()
                        .body(new ParameterizedTypeReference<ApiResponse.CustomerPage>() {});
                
                if (response != null && response.getData() != null) {
                    allCustomers.addAll(response.getData());
                    log.debug("Fetched page {} with {} customers", currentPage, response.getData().size());
                    
                    // Check if there are more pages
                    hasMore = (currentPage + 1) * pageSize < response.getTotal();
                    page++;
                } else {
                    hasMore = false;
                }
                
            } catch (Exception e) {
                log.error("Error fetching customers page {}: {}", currentPage, e.getMessage());
                throw new RestClientException("Failed to fetch customers", e);
            }
        }
        
        log.info("Successfully fetched {} customers", allCustomers.size());
        return allCustomers;
    }
    
    /**
     * Fetch customers updated after a specific timestamp (incremental sync)
     */
    @Retryable(
        retryFor = {RestClientException.class},
        maxAttemptsExpression = "${api.mock-apis.retry.max-attempts}",
        backoff = @Backoff(
            delayExpression = "${api.mock-apis.retry.backoff-delay}",
            multiplierExpression = "${api.mock-apis.retry.backoff-multiplier}"
        )
    )
    public List<Customer> fetchCustomersSince(LocalDateTime since) {
        log.info("Fetching customers updated since: {}", since);
        
        // Note: Mock API doesn't support filtering by date yet
        // In production, this would use a query parameter like ?updatedAfter=timestamp
        // For now, we fetch all and filter client-side
        List<Customer> allCustomers = fetchAllCustomers();
        
        List<Customer> updatedCustomers = allCustomers.stream()
                .filter(customer -> customer.getCreatedDate() != null && 
                                   customer.getCreatedDate().isAfter(since))
                .toList();
        
        log.info("Found {} customers updated since {}", updatedCustomers.size(), since);
        return updatedCustomers;
    }
    
    /**
     * Fetch all products (full sync)
     */
    @Retryable(
        retryFor = {RestClientException.class},
        maxAttemptsExpression = "${api.mock-apis.retry.max-attempts}",
        backoff = @Backoff(
            delayExpression = "${api.mock-apis.retry.backoff-delay}",
            multiplierExpression = "${api.mock-apis.retry.backoff-multiplier}"
        )
    )
    public List<Product> fetchAllProducts() {
        log.info("Fetching all products (full sync)");
        
        List<Product> allProducts = new ArrayList<>();
        int page = 0;
        final int pageSize = 100;
        boolean hasMore = true;
        
        while (hasMore) {
            final int currentPage = page;
            try {
                ApiResponse.ProductPage response = restClient.get()
                        .uri(uriBuilder -> uriBuilder
                                .path(productsEndpoint)
                                .queryParam("page", currentPage)
                                .queryParam("size", pageSize)
                                .build())
                        .retrieve()
                        .body(new ParameterizedTypeReference<ApiResponse.ProductPage>() {});
                
                if (response != null && response.getData() != null) {
                    allProducts.addAll(response.getData());
                    log.debug("Fetched page {} with {} products", currentPage, response.getData().size());
                    
                    hasMore = (currentPage + 1) * pageSize < response.getTotal();
                    page++;
                } else {
                    hasMore = false;
                }
                
            } catch (Exception e) {
                log.error("Error fetching products page {}: {}", currentPage, e.getMessage());
                throw new RestClientException("Failed to fetch products", e);
            }
        }
        
        log.info("Successfully fetched {} products", allProducts.size());
        return allProducts;
    }
    
    /**
     * Fetch products updated after a specific timestamp (incremental sync)
     */
    @Retryable(
        retryFor = {RestClientException.class},
        maxAttemptsExpression = "${api.mock-apis.retry.max-attempts}",
        backoff = @Backoff(
            delayExpression = "${api.mock-apis.retry.backoff-delay}",
            multiplierExpression = "${api.mock-apis.retry.backoff-multiplier}"
        )
    )
    public List<Product> fetchProductsSince(LocalDateTime since) {
        log.info("Fetching products updated since: {}", since);
        
        // Note: Mock API doesn't support filtering by date yet
        // In production, this would use a query parameter like ?updatedAfter=timestamp
        // For now, we fetch all and filter client-side
        List<Product> allProducts = fetchAllProducts();
        
        List<Product> updatedProducts = allProducts.stream()
                .filter(product -> product.getLastUpdated() != null && 
                                  product.getLastUpdated().isAfter(since))
                .toList();
        
        log.info("Found {} products updated since {}", updatedProducts.size(), since);
        return updatedProducts;
    }
}
