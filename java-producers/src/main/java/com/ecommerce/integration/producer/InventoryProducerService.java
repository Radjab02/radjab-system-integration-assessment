package com.ecommerce.integration.producer;

import com.ecommerce.integration.client.MockApiClient;
import com.ecommerce.integration.model.Product;
import com.ecommerce.integration.repository.SyncStateRepository;
import com.ecommerce.integration.service.KafkaProducerService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.List;

/**
 * Producer service for Inventory/Product data
 * Implements hybrid sync: initial full sync + incremental updates
 */
@Service
@RequiredArgsConstructor
@Slf4j
public class InventoryProducerService {
    
    private static final String SOURCE_TYPE = "PRODUCT";
    
    private final MockApiClient apiClient;
    private final KafkaProducerService kafkaProducerService;
    private final SyncStateRepository syncStateRepository;
    
    /**
     * Scheduled sync job
     * Runs initial full sync on first execution, then incremental sync
     */
    @Scheduled(
        initialDelayString = "${scheduling.inventory-sync.initial-delay}",
        fixedDelayString = "${scheduling.inventory-sync.fixed-delay}"
    )
    public void scheduledSync() {
        log.info("=== Starting scheduled inventory sync ===");
        
        try {
            if (!syncStateRepository.isInitialSyncCompleted(SOURCE_TYPE)) {
                log.info("Initial sync not completed. Performing full sync...");
                performFullSync();
            } else {
                log.info("Initial sync completed. Performing incremental sync...");
                performIncrementalSync();
            }
        } catch (Exception e) {
            log.error("Error during scheduled inventory sync", e);
        }
        
        log.info("=== Completed scheduled inventory sync ===");
    }
    
    /**
     * Perform full sync - fetch all products
     */
    public void performFullSync() {
        log.info("Starting FULL sync for products");
        LocalDateTime syncStartTime = LocalDateTime.now();
        
        try {
            // Fetch all products from API
            List<Product> products = apiClient.fetchAllProducts();
            
            if (products.isEmpty()) {
                log.warn("No products found during full sync");
                return;
            }
            
            log.info("Fetched {} products. Publishing to Kafka...", products.size());
            
            // Publish to Kafka
            kafkaProducerService.sendInventoryData(
                    products,
                    "INITIAL_FULL",
                    true,
                    products.size()
            );
            
            // Update sync state
            syncStateRepository.updateLastSyncTime(SOURCE_TYPE, syncStartTime, products.size());
            
            log.info("Full sync completed successfully. Synced {} products", products.size());
            
        } catch (Exception e) {
            log.error("Full sync failed for products", e);
            throw new RuntimeException("Full sync failed", e);
        }
    }
    
    /**
     * Perform incremental sync - fetch only updated products
     */
    public void performIncrementalSync() {
        log.info("Starting INCREMENTAL sync for products");
        LocalDateTime syncStartTime = LocalDateTime.now();
        
        try {
            // Get last sync time
            LocalDateTime lastSyncTime = syncStateRepository.getLastSyncTime(SOURCE_TYPE)
                    .orElse(LocalDateTime.now().minusMinutes(5)); // Default to 5 minutes ago
            
            log.info("Fetching products updated since: {}", lastSyncTime);
            
            // Fetch only updated products
            List<Product> updatedProducts = apiClient.fetchProductsSince(lastSyncTime);
            
            if (updatedProducts.isEmpty()) {
                log.info("No updated products found since {}", lastSyncTime);
                // Still update sync time even if no changes
                syncStateRepository.updateLastSyncTime(SOURCE_TYPE, syncStartTime, 0);
                return;
            }
            
            log.info("Found {} updated products. Publishing to Kafka...", updatedProducts.size());
            
            // Publish to Kafka
            kafkaProducerService.sendInventoryData(
                    updatedProducts,
                    "INCREMENTAL",
                    false,
                    updatedProducts.size()
            );
            
            // Update sync state
            syncStateRepository.updateLastSyncTime(SOURCE_TYPE, syncStartTime, updatedProducts.size());
            
            log.info("Incremental sync completed successfully. Synced {} products", 
                    updatedProducts.size());
            
        } catch (Exception e) {
            log.error("Incremental sync failed for products", e);
            throw new RuntimeException("Incremental sync failed", e);
        }
    }
    
    /**
     * Manually trigger full sync (via REST endpoint)
     */
    public void triggerFullSync() {
        log.info("Manual full sync triggered for products");
        performFullSync();
    }
    
    /**
     * Manually trigger incremental sync (via REST endpoint)
     */
    public void triggerIncrementalSync() {
        log.info("Manual incremental sync triggered for products");
        performIncrementalSync();
    }
}
