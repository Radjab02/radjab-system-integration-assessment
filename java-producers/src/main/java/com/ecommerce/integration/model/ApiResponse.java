package com.ecommerce.integration.model;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;

/**
 * Response wrappers for API calls
 */
public class ApiResponse {

    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    @Builder
    public static class CustomerPage {
        private List<Customer> data;
        private int page;
        private int size;
        private long total;
    }

    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    @Builder
    public static class ProductPage {
        private List<Product> data;
        private int page;
        private int size;
        private long total;
    }
}
