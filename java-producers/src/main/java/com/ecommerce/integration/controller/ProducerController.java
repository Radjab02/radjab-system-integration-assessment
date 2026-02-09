package com.ecommerce.integration.controller;

import com.ecommerce.integration.producer.CustomerProducerService;
import com.ecommerce.integration.producer.InventoryProducerService;
import com.ecommerce.integration.repository.SyncStateRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

/**
 * REST controller for manually triggering sync operations
 * Useful for testing and on-demand synchronization
 */
@RestController
@RequestMapping("/api/sync")
@RequiredArgsConstructor
@Slf4j
public class ProducerController {
    
    private final CustomerProducerService customerProducerService;
    private final InventoryProducerService inventoryProducerService;
    private final SyncStateRepository syncStateRepository;
    
    /**
     * Trigger full customer sync
     */
    @PostMapping("/customers/full")
    public ResponseEntity<Map<String, String>> triggerCustomerFullSync() {
        log.info("REST: Triggering full customer sync");
        
        try {
            customerProducerService.triggerFullSync();
            return ResponseEntity.ok(Map.of(
                    "status", "SUCCESS",
                    "message", "Full customer sync triggered successfully"
            ));
        } catch (Exception e) {
            log.error("Error triggering customer full sync", e);
            return ResponseEntity.internalServerError().body(Map.of(
                    "status", "ERROR",
                    "message", "Failed to trigger sync: " + e.getMessage()
            ));
        }
    }
    
    /**
     * Trigger incremental customer sync
     */
    @PostMapping("/customers/incremental")
    public ResponseEntity<Map<String, String>> triggerCustomerIncrementalSync() {
        log.info("REST: Triggering incremental customer sync");
        
        try {
            customerProducerService.triggerIncrementalSync();
            return ResponseEntity.ok(Map.of(
                    "status", "SUCCESS",
                    "message", "Incremental customer sync triggered successfully"
            ));
        } catch (Exception e) {
            log.error("Error triggering customer incremental sync", e);
            return ResponseEntity.internalServerError().body(Map.of(
                    "status", "ERROR",
                    "message", "Failed to trigger sync: " + e.getMessage()
            ));
        }
    }
    
    /**
     * Trigger full inventory sync
     */
    @PostMapping("/inventory/full")
    public ResponseEntity<Map<String, String>> triggerInventoryFullSync() {
        log.info("REST: Triggering full inventory sync");
        
        try {
            inventoryProducerService.triggerFullSync();
            return ResponseEntity.ok(Map.of(
                    "status", "SUCCESS",
                    "message", "Full inventory sync triggered successfully"
            ));
        } catch (Exception e) {
            log.error("Error triggering inventory full sync", e);
            return ResponseEntity.internalServerError().body(Map.of(
                    "status", "ERROR",
                    "message", "Failed to trigger sync: " + e.getMessage()
            ));
        }
    }
    
    /**
     * Trigger incremental inventory sync
     */
    @PostMapping("/inventory/incremental")
    public ResponseEntity<Map<String, String>> triggerInventoryIncrementalSync() {
        log.info("REST: Triggering incremental inventory sync");
        
        try {
            inventoryProducerService.triggerIncrementalSync();
            return ResponseEntity.ok(Map.of(
                    "status", "SUCCESS",
                    "message", "Incremental inventory sync triggered successfully"
            ));
        } catch (Exception e) {
            log.error("Error triggering inventory incremental sync", e);
            return ResponseEntity.internalServerError().body(Map.of(
                    "status", "ERROR",
                    "message", "Failed to trigger sync: " + e.getMessage()
            ));
        }
    }
    
    /**
     * Get sync status for all sources
     */
    @GetMapping("/status")
    public ResponseEntity<Map<String, Object>> getSyncStatus() {
        log.info("REST: Getting sync status");
        
        var customerState = syncStateRepository.findBySourceType("CUSTOMER").orElse(null);
        var productState = syncStateRepository.findBySourceType("PRODUCT").orElse(null);
        
        return ResponseEntity.ok(Map.of(
                "customer", customerState != null ? Map.of(
                        "initialSyncCompleted", customerState.isInitialSyncCompleted(),
                        "lastSyncTime", customerState.getLastSyncTime(),
                        "totalRecordsSynced", customerState.getTotalRecordsSynced(),
                        "lastSyncRecordCount", customerState.getLastSyncRecordCount()
                ) : Map.of("status", "NOT_STARTED"),
                "inventory", productState != null ? Map.of(
                        "initialSyncCompleted", productState.isInitialSyncCompleted(),
                        "lastSyncTime", productState.getLastSyncTime(),
                        "totalRecordsSynced", productState.getTotalRecordsSynced(),
                        "lastSyncRecordCount", productState.getLastSyncRecordCount()
                ) : Map.of("status", "NOT_STARTED")
        ));
    }
}
