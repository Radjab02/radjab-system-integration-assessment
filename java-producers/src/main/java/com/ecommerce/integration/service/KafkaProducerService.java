package com.ecommerce.integration.service;

import com.ecommerce.integration.model.KafkaMessage;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.kafka.support.SendResult;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.UUID;
import java.util.concurrent.CompletableFuture;

/**
 * Service for publishing messages to Kafka topics
 */
@Service
@RequiredArgsConstructor
@Slf4j
public class KafkaProducerService {
    
    private final KafkaTemplate<String, Object> kafkaTemplate;
    
    @Value("${kafka.topics.customer-data}")
    private String customerTopic;
    
    @Value("${kafka.topics.inventory-data}")
    private String inventoryTopic;
    
    @Value("${spring.application.name}")
    private String applicationName;
    
    /**
     * Send message to customer data topic
     */
    public <T> CompletableFuture<SendResult<String, Object>> sendCustomerData(
            T payload, String syncType, boolean isFullSync, int recordCount) {
        
        KafkaMessage<T> message = buildKafkaMessage(
                payload, 
                "CUSTOMER", 
                syncType, 
                isFullSync, 
                recordCount
        );
        
        String key = UUID.randomUUID().toString();
        
        log.debug("Sending customer message to topic {}: key={}, syncType={}", 
                customerTopic, key, syncType);
        
        CompletableFuture<SendResult<String, Object>> future = 
                kafkaTemplate.send(customerTopic, key, message);
        
        future.whenComplete((result, ex) -> {
            if (ex == null) {
                log.info("Successfully sent customer message: key={}, partition={}, offset={}", 
                        key, result.getRecordMetadata().partition(), 
                        result.getRecordMetadata().offset());
            } else {
                log.error("Failed to send customer message: key={}, error={}", 
                        key, ex.getMessage(), ex);
            }
        });
        
        return future;
    }
    
    /**
     * Send message to inventory data topic
     */
    public <T> CompletableFuture<SendResult<String, Object>> sendInventoryData(
            T payload, String syncType, boolean isFullSync, int recordCount) {
        
        KafkaMessage<T> message = buildKafkaMessage(
                payload, 
                "INVENTORY", 
                syncType, 
                isFullSync, 
                recordCount
        );
        
        String key = UUID.randomUUID().toString();
        
        log.debug("Sending inventory message to topic {}: key={}, syncType={}", 
                inventoryTopic, key, syncType);
        
        CompletableFuture<SendResult<String, Object>> future = 
                kafkaTemplate.send(inventoryTopic, key, message);
        
        future.whenComplete((result, ex) -> {
            if (ex == null) {
                log.info("Successfully sent inventory message: key={}, partition={}, offset={}", 
                        key, result.getRecordMetadata().partition(), 
                        result.getRecordMetadata().offset());
            } else {
                log.error("Failed to send inventory message: key={}, error={}", 
                        key, ex.getMessage(), ex);
            }
        });
        
        return future;
    }
    
    /**
     * Build Kafka message with metadata
     */
    private <T> KafkaMessage<T> buildKafkaMessage(
            T payload, String eventType, String syncType, boolean isFullSync, int recordCount) {
        
        return KafkaMessage.<T>builder()
                .messageId(UUID.randomUUID().toString())
                .source(applicationName)
                .eventType(eventType)
                .timestamp(LocalDateTime.now())
                .payload(payload)
                .metadata(KafkaMessage.MessageMetadata.builder()
                        .producerVersion("1.0.0")
                        .isFullSync(isFullSync)
                        .isIncrementalSync(!isFullSync)
                        .recordCount(recordCount)
                        .syncType(syncType)
                        .build())
                .build();
    }
}
