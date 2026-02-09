package com.ecommerce.mock.controller;

import com.ecommerce.mock.model.DTOs.*;
import com.ecommerce.mock.service.CustomerService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.media.Content;
import io.swagger.v3.oas.annotations.media.Schema;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/customers")
@RequiredArgsConstructor
@Slf4j
@Tag(name = "CRM", description = "Customer Relationship Management operations")
public class CustomerController {

    private final CustomerService customerService;

    @GetMapping
    @Operation(
        summary = "Retrieve all customers",
        description = "Fetch customer data from CRM system with pagination support"
    )
    @ApiResponse(
        responseCode = "200",
        description = "Successful response",
        content = @Content(schema = @Schema(implementation = PagedCustomerResponse.class))
    )
    public ResponseEntity<PagedCustomerResponse> getCustomers(
            @Parameter(description = "Page number") 
            @RequestParam(defaultValue = "0") int page,
            
            @Parameter(description = "Page size") 
            @RequestParam(defaultValue = "100") int size) {
        
        log.info("GET /api/customers - page: {}, size: {}", page, size);
        
        List<CustomerResponse> customers = customerService.getAllCustomers(page, size);
        long total = customerService.getTotalCustomers();
        
        PagedCustomerResponse response = PagedCustomerResponse.builder()
                .data(customers)
                .page(page)
                .size(size)
                .total(total)
                .build();
        
        return ResponseEntity.ok(response);
    }

    @PostMapping
    @Operation(
        summary = "Create a new customer",
        description = "Add a new customer to the CRM system"
    )
    @ApiResponse(
        responseCode = "201",
        description = "Customer created successfully",
        content = @Content(schema = @Schema(implementation = CustomerResponse.class))
    )
    @ApiResponse(
        responseCode = "400",
        description = "Invalid input",
        content = @Content(schema = @Schema(implementation = ErrorResponse.class))
    )
    public ResponseEntity<CustomerResponse> createCustomer(
            @Valid @RequestBody CustomerRequest request) {
        
        log.info("POST /api/customers - email: {}", request.getEmail());
        
        CustomerResponse customer = customerService.createCustomer(request);
        
        return ResponseEntity.status(HttpStatus.CREATED).body(customer);
    }
}
