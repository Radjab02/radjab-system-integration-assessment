package com.ecommerce.mock.model;

import com.fasterxml.jackson.annotation.JsonFormat;
import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.List;

public class DTOs {

    // Customer DTOs
    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    @Builder
    public static class CustomerRequest {
        @NotBlank(message = "Name is required")
        private String name;

        @Email(message = "Email should be valid")
        @NotBlank(message = "Email is required")
        private String email;

        private String phone;
        private String address;
    }

    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    @Builder
    public static class CustomerResponse {
        private String id;
        private String name;
        private String email;
        private String phone;
        private String address;
        
        @JsonFormat(pattern = "yyyy-MM-dd'T'HH:mm:ss'Z'")
        private LocalDateTime createdDate;
        
        private String status;
    }

    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    @Builder
    public static class PagedCustomerResponse {
        private List<CustomerResponse> data;
        private int page;
        private int size;
        private long total;
    }

    // Product DTOs
    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    @Builder
    public static class ProductResponse {
        private String id;
        private String productName;
        private String sku;
        private Integer stockQuantity;
        private BigDecimal price;
        private String category;
        
        @JsonFormat(pattern = "yyyy-MM-dd'T'HH:mm:ss'Z'")
        private LocalDateTime lastUpdated;
    }

    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    @Builder
    public static class PagedProductResponse {
        private List<ProductResponse> data;
        private int page;
        private int size;
        private long total;
    }

    // Analytics DTOs
    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    @Builder
    public static class AnalyticsDataRequest {
        private String eventId;
        
        @JsonFormat(pattern = "yyyy-MM-dd'T'HH:mm:ss'Z'")
        private LocalDateTime timestamp;
        
        private List<CustomerResponse> customers;
        private List<ProductResponse> products;
        private Object metadata;
    }

    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    @Builder
    public static class AnalyticsDataResponse {
        private String status;
        private String message;
        private Integer recordsProcessed;
    }

    // Error DTO
    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    @Builder
    public static class ErrorResponse {
        @JsonFormat(pattern = "yyyy-MM-dd'T'HH:mm:ss'Z'")
        private LocalDateTime timestamp;
        
        private Integer status;
        private String error;
        private String message;
        private String path;
    }
}
