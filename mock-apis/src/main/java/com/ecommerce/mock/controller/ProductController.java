package com.ecommerce.mock.controller;

import com.ecommerce.mock.model.DTOs.PagedProductResponse;
import com.ecommerce.mock.model.DTOs.ProductResponse;
import com.ecommerce.mock.service.ProductService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.media.Content;
import io.swagger.v3.oas.annotations.media.Schema;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/products")
@RequiredArgsConstructor
@Slf4j
@Tag(name = "Inventory", description = "Product inventory operations")
public class ProductController {

    private final ProductService productService;

    @GetMapping
    @Operation(
        summary = "Retrieve all products with inventory",
        description = "Fetch product stock data from Inventory system with optional filtering"
    )
    @ApiResponse(
        responseCode = "200",
        description = "Successful response",
        content = @Content(schema = @Schema(implementation = PagedProductResponse.class))
    )
    public ResponseEntity<PagedProductResponse> getProducts(
            @Parameter(description = "Page number") 
            @RequestParam(defaultValue = "0") int page,
            
            @Parameter(description = "Page size") 
            @RequestParam(defaultValue = "100") int size,
            
            @Parameter(description = "Filter by stock availability") 
            @RequestParam(required = false) Boolean inStock) {
        
        log.info("GET /api/products - page: {}, size: {}, inStock: {}", page, size, inStock);
        
        List<ProductResponse> products = productService.getAllProducts(page, size, inStock);
        long total = productService.getTotalProducts();
        
        PagedProductResponse response = PagedProductResponse.builder()
                .data(products)
                .page(page)
                .size(size)
                .total(total)
                .build();
        
        return ResponseEntity.ok(response);
    }
}
