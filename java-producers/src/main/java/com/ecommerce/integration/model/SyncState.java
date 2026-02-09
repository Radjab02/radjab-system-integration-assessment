package com.ecommerce.integration.model;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

/**
 * Tracks the last sync state for each data source
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class SyncState {
    
    private String sourceType; // "CUSTOMER" or "PRODUCT"
    private LocalDateTime lastSyncTime;
    private boolean initialSyncCompleted;
    private long totalRecordsSynced;
    private long lastSyncRecordCount;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;
}
