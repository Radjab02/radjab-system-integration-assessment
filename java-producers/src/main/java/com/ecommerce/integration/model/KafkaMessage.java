package com.ecommerce.integration.model;

import com.fasterxml.jackson.annotation.JsonFormat;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

/**
 * Wrapper for Kafka messages with metadata for traceability
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class KafkaMessage<T> {
    
    private String messageId;
    private String source;
    private String eventType;
    
    @JsonFormat(pattern = "yyyy-MM-dd'T'HH:mm:ss'Z'")
    private LocalDateTime timestamp;
    
    private T payload;
    
    private MessageMetadata metadata;
    
    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    @Builder
    public static class MessageMetadata {
        private String producerVersion;
        private boolean isFullSync;
        private boolean isIncrementalSync;
        private Integer recordCount;
        private String syncType; // "INITIAL_FULL" or "INCREMENTAL"
    }
}
