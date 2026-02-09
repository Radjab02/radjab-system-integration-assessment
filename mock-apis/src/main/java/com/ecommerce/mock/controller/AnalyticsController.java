package com.ecommerce.mock.controller;

import com.ecommerce.mock.model.DTOs.AnalyticsDataRequest;
import com.ecommerce.mock.model.DTOs.AnalyticsDataResponse;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.media.Content;
import io.swagger.v3.oas.annotations.media.Schema;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/analytics")
@Slf4j
@Tag(name = "Analytics", description = "Analytics data ingestion")
public class AnalyticsController {

    @PostMapping("/data")
    @Operation(
        summary = "Ingest analytics data",
        description = "Accept merged customer and inventory data for analytics processing"
    )
    @ApiResponse(
        responseCode = "200",
        description = "Data ingested successfully",
        content = @Content(schema = @Schema(implementation = AnalyticsDataResponse.class))
    )
    public ResponseEntity<AnalyticsDataResponse> ingestData(
            @Valid @RequestBody AnalyticsDataRequest request) {
        
        log.info("POST /api/analytics/data - eventId: {}, customers: {}, products: {}", 
                request.getEventId(),
                request.getCustomers() != null ? request.getCustomers().size() : 0,
                request.getProducts() != null ? request.getProducts().size() : 0);
        
        // Simulate processing
        int totalRecords = 0;
        if (request.getCustomers() != null) {
            totalRecords += request.getCustomers().size();
        }
        if (request.getProducts() != null) {
            totalRecords += request.getProducts().size();
        }
        
        log.info("Analytics data processed - Total records: {}", totalRecords);
        
        AnalyticsDataResponse response = AnalyticsDataResponse.builder()
                .status("SUCCESS")
                .message("Data processed successfully")
                .recordsProcessed(totalRecords)
                .build();
        
        return ResponseEntity.ok(response);
    }
}
