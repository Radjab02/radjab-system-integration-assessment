package com.ecommerce.integration.repository;

import com.ecommerce.integration.model.SyncState;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Repository;

import java.time.LocalDateTime;
import java.util.Map;
import java.util.Optional;
import java.util.concurrent.ConcurrentHashMap;

/**
 * In-memory repository for tracking sync state
 * In production, this would use a database or distributed cache
 */
@Repository
@Slf4j
public class SyncStateRepository {
    
    private final Map<String, SyncState> syncStates = new ConcurrentHashMap<>();
    
    public Optional<SyncState> findBySourceType(String sourceType) {
        return Optional.ofNullable(syncStates.get(sourceType));
    }
    
    public SyncState save(SyncState syncState) {
        syncState.setUpdatedAt(LocalDateTime.now());
        
        if (syncState.getCreatedAt() == null) {
            syncState.setCreatedAt(LocalDateTime.now());
        }
        
        syncStates.put(syncState.getSourceType(), syncState);
        log.debug("Saved sync state for {}: {}", syncState.getSourceType(), syncState);
        
        return syncState;
    }
    
    public void updateLastSyncTime(String sourceType, LocalDateTime syncTime, long recordCount) {
        SyncState state = syncStates.get(sourceType);
        
        if (state == null) {
            state = SyncState.builder()
                    .sourceType(sourceType)
                    .initialSyncCompleted(true)
                    .totalRecordsSynced(recordCount)
                    .lastSyncRecordCount(recordCount)
                    .build();
        } else {
            state.setTotalRecordsSynced(state.getTotalRecordsSynced() + recordCount);
            state.setLastSyncRecordCount(recordCount);
            state.setInitialSyncCompleted(true);
        }
        
        state.setLastSyncTime(syncTime);
        save(state);
    }
    
    public boolean isInitialSyncCompleted(String sourceType) {
        return findBySourceType(sourceType)
                .map(SyncState::isInitialSyncCompleted)
                .orElse(false);
    }
    
    public Optional<LocalDateTime> getLastSyncTime(String sourceType) {
        return findBySourceType(sourceType)
                .map(SyncState::getLastSyncTime);
    }
}
