package com.ecommerce.integration.producer;

import com.ecommerce.integration.client.MockApiClient;
import com.ecommerce.integration.model.Customer;
import com.ecommerce.integration.repository.SyncStateRepository;
import com.ecommerce.integration.service.KafkaProducerService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.List;

/**
 * Producer service for Customer data
 * Implements hybrid sync: initial full sync + incremental updates
 */
@Service
@RequiredArgsConstructor
@Slf4j
public class CustomerProducerService {
    
    private static final String SOURCE_TYPE = "CUSTOMER";
    
    private final MockApiClient apiClient;
    private final KafkaProducerService kafkaProducerService;
    private final SyncStateRepository syncStateRepository;
    
    /**
     * Scheduled sync job
     * Runs initial full sync on first execution, then incremental sync
     */
    @Scheduled(
        initialDelayString = "${scheduling.customer-sync.initial-delay}",
        fixedDelayString = "${scheduling.customer-sync.fixed-delay}"
    )
    public void scheduledSync() {
        log.info("=== Starting scheduled customer sync ===");
        
        try {
            if (!syncStateRepository.isInitialSyncCompleted(SOURCE_TYPE)) {
                log.info("Initial sync not completed. Performing full sync...");
                performFullSync();
            } else {
                log.info("Initial sync completed. Performing incremental sync...");
                performIncrementalSync();
            }
        } catch (Exception e) {
            log.error("Error during scheduled customer sync", e);
        }
        
        log.info("=== Completed scheduled customer sync ===");
    }
    
    /**
     * Perform full sync - fetch all customers
     */
    public void performFullSync() {
        log.info("Starting FULL sync for customers");
        LocalDateTime syncStartTime = LocalDateTime.now();
        
        try {
            // Fetch all customers from API
            List<Customer> customers = apiClient.fetchAllCustomers();
            
            if (customers.isEmpty()) {
                log.warn("No customers found during full sync");
                return;
            }
            
            log.info("Fetched {} customers. Publishing to Kafka...", customers.size());
            
            // Publish to Kafka
            kafkaProducerService.sendCustomerData(
                    customers,
                    "INITIAL_FULL",
                    true,
                    customers.size()
            );
            
            // Update sync state
            syncStateRepository.updateLastSyncTime(SOURCE_TYPE, syncStartTime, customers.size());
            
            log.info("Full sync completed successfully. Synced {} customers", customers.size());
            
        } catch (Exception e) {
            log.error("Full sync failed for customers", e);
            throw new RuntimeException("Full sync failed", e);
        }
    }
    
    /**
     * Perform incremental sync - fetch only updated customers
     */
    public void performIncrementalSync() {
        log.info("Starting INCREMENTAL sync for customers");
        LocalDateTime syncStartTime = LocalDateTime.now();
        
        try {
            // Get last sync time
            LocalDateTime lastSyncTime = syncStateRepository.getLastSyncTime(SOURCE_TYPE)
                    .orElse(LocalDateTime.now().minusMinutes(5)); // Default to 5 minutes ago
            
            log.info("Fetching customers updated since: {}", lastSyncTime);
            
            // Fetch only updated customers
            List<Customer> updatedCustomers = apiClient.fetchCustomersSince(lastSyncTime);
            
            if (updatedCustomers.isEmpty()) {
                log.info("No updated customers found since {}", lastSyncTime);
                // Still update sync time even if no changes
                syncStateRepository.updateLastSyncTime(SOURCE_TYPE, syncStartTime, 0);
                return;
            }
            
            log.info("Found {} updated customers. Publishing to Kafka...", updatedCustomers.size());
            
            // Publish to Kafka
            kafkaProducerService.sendCustomerData(
                    updatedCustomers,
                    "INCREMENTAL",
                    false,
                    updatedCustomers.size()
            );
            
            // Update sync state
            syncStateRepository.updateLastSyncTime(SOURCE_TYPE, syncStartTime, updatedCustomers.size());
            
            log.info("Incremental sync completed successfully. Synced {} customers", 
                    updatedCustomers.size());
            
        } catch (Exception e) {
            log.error("Incremental sync failed for customers", e);
            throw new RuntimeException("Incremental sync failed", e);
        }
    }
    
    /**
     * Manually trigger full sync (via REST endpoint)
     */
    public void triggerFullSync() {
        log.info("Manual full sync triggered for customers");
        performFullSync();
    }
    
    /**
     * Manually trigger incremental sync (via REST endpoint)
     */
    public void triggerIncrementalSync() {
        log.info("Manual incremental sync triggered for customers");
        performIncrementalSync();
    }
}
