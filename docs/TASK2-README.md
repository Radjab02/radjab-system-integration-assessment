# Task 2: Java Producers - Complete

## Overview

This implementation provides a **production-ready Java/Spring Boot producer** system that:
- Fetches data from Mock CRM and Inventory APIs
- Implements **hybrid sync strategy**: Initial full sync + incremental updates
- Publishes to Kafka topics with proper metadata
- Includes comprehensive retry logic and error handling
- Supports both scheduled and manual triggering
- Modular design for easy extension to new data sources

## Architecture

### Hybrid Sync Strategy

```
First Run (Initial Sync):
┌─────────────┐
│  Mock APIs  │
└──────┬──────┘
       │ Fetch ALL data
       ▼
┌─────────────────┐     ┌──────────────┐
│ Java Producers  │────▶│    Kafka     │
│ (Full Sync)     │     │ Topics       │
└─────────────────┘     └──────────────┘
       │
       └─▶ Mark: Initial sync complete

Subsequent Runs (Incremental Sync):
┌─────────────┐
│  Mock APIs  │
└──────┬──────┘
       │ Fetch ONLY changed data (since last sync)
       ▼
┌─────────────────┐     ┌──────────────┐
│ Java Producers  │────▶│    Kafka     │
│ (Incremental)   │     │ Topics       │
└─────────────────┘     └──────────────┘
       │
       └─▶ Update: Last sync time
```

### Key Components

1. **MockApiClient** - Fetches data from REST APIs with retry logic
2. **CustomerProducerService** - Manages customer data synchronization
3. **InventoryProducerService** - Manages product data synchronization
4. **KafkaProducerService** - Publishes messages to Kafka with metadata
5. **SyncStateRepository** - Tracks sync state (in-memory)
6. **ProducerController** - REST endpoints for manual triggering

## Technology Stack

- **Java 21**
- **Spring Boot 3.4.1**
- **Spring Kafka** - Kafka integration
- **Spring Retry** - Retry logic with exponential backoff
- **Spring WebFlux** - RestClient for API calls
- **Lombok** - Reduce boilerplate code

## Configuration

### application.yml

```yaml
kafka:
  bootstrap-servers: localhost:9093
  topics:
    customer-data: customer_data
    inventory-data: inventory_data

api:
  mock-apis:
    base-url: http://localhost:8081
    retry:
      max-attempts: 3
      backoff-delay: 1000  # 1 second
      backoff-multiplier: 2.0  # Exponential backoff

scheduling:
  customer-sync:
    initial-delay: 10000   # 10 seconds after startup
    fixed-delay: 60000     # Every 60 seconds
  inventory-sync:
    initial-delay: 15000   # 15 seconds after startup
    fixed-delay: 60000     # Every 60 seconds
```

## Kafka Message Format

Each message sent to Kafka includes metadata for traceability:

```json
{
  "messageId": "uuid-here",
  "source": "java-producers",
  "eventType": "CUSTOMER" or "INVENTORY",
  "timestamp": "2024-02-07T10:30:00Z",
  "payload": [
    {
      "id": "CUST001",
      "name": "John Doe",
      ...
    }
  ],
  "metadata": {
    "producerVersion": "1.0.0",
    "isFullSync": true,
    "isIncrementalSync": false,
    "recordCount": 5,
    "syncType": "INITIAL_FULL" or "INCREMENTAL"
  }
}
```

## Features

### 1. Hybrid Sync Strategy ✅

**Initial Full Sync:**
- Triggered on first run
- Fetches ALL existing data
- Marks initial sync as complete
- Records sync time and count

**Incremental Sync:**
- Triggered on subsequent runs
- Fetches ONLY data changed since last sync
- Updates sync time and count
- Efficient use of API resources

### 2. Retry Logic ✅

**Spring Retry Configuration:**
```java
@Retryable(
    retryFor = {RestClientException.class},
    maxAttempts = 3,
    backoff = @Backoff(
        delay = 1000,
        multiplier = 2.0
    )
)
```

**Behavior:**
- Attempt 1: Immediate
- Attempt 2: After 1 second
- Attempt 3: After 2 seconds (1 × 2.0)
- After 3 failures: Exception thrown

### 3. Scheduled Execution ✅

- **Customer Sync**: Starts 10s after boot, runs every 60s
- **Inventory Sync**: Starts 15s after boot, runs every 60s
- Configurable via `application.yml`

### 4. Manual Triggering ✅

REST endpoints for on-demand sync:

```bash
# Trigger full customer sync
POST http://localhost:8082/api/sync/customers/full

# Trigger incremental customer sync
POST http://localhost:8082/api/sync/customers/incremental

# Trigger full inventory sync
POST http://localhost:8082/api/sync/inventory/full

# Trigger incremental inventory sync
POST http://localhost:8082/api/sync/inventory/incremental

# Get sync status
GET http://localhost:8082/api/sync/status
```

### 5. Comprehensive Logging ✅

```
2024-02-07 10:30:00 [pool-1] INFO  CustomerProducerService - === Starting scheduled customer sync ===
2024-02-07 10:30:00 [pool-1] INFO  CustomerProducerService - Initial sync not completed. Performing full sync...
2024-02-07 10:30:00 [pool-1] INFO  CustomerProducerService - Starting FULL sync for customers
2024-02-07 10:30:01 [pool-1] INFO  MockApiClient - Fetching all customers (full sync)
2024-02-07 10:30:01 [pool-1] DEBUG MockApiClient - Fetched page 0 with 5 customers
2024-02-07 10:30:01 [pool-1] INFO  MockApiClient - Successfully fetched 5 customers
2024-02-07 10:30:01 [pool-1] INFO  CustomerProducerService - Fetched 5 customers. Publishing to Kafka...
2024-02-07 10:30:01 [pool-1] INFO  KafkaProducerService - Successfully sent customer message: key=uuid, partition=0, offset=0
2024-02-07 10:30:01 [pool-1] INFO  CustomerProducerService - Full sync completed successfully. Synced 5 customers
```

### 6. Modular Design ✅

Easy to add new producers:

```java
@Service
@RequiredArgsConstructor
@Slf4j
public class OrderProducerService {
    
    private final MockApiClient apiClient;
    private final KafkaProducerService kafkaProducerService;
    private final SyncStateRepository syncStateRepository;
    
    @Scheduled(...)
    public void scheduledSync() {
        // Same pattern as Customer/Inventory producers
    }
}
```

## Running the Application

### Option 1: Using Docker Compose (Recommended)

```bash
# From project root
docker-compose up -d

# Check logs
docker-compose logs -f java-producers

# Verify it's working
curl http://localhost:8082/actuator/health
```

### Option 2: Local Development

1. **Start dependencies:**
```bash
# Kafka and Mock APIs must be running
docker-compose up -d kafka zookeeper mock-apis
```

2. **Run the application:**
```bash
cd java-producers
./gradlew bootRun
```

## Testing

### 1. Check Sync Status

```bash
curl http://localhost:8082/api/sync/status
```

Response:
```json
{
  "customer": {
    "initialSyncCompleted": true,
    "lastSyncTime": "2024-02-07T10:30:00",
    "totalRecordsSynced": 10,
    "lastSyncRecordCount": 5
  },
  "inventory": {
    "initialSyncCompleted": true,
    "lastSyncTime": "2024-02-07T10:30:15",
    "totalRecordsSynced": 14,
    "lastSyncRecordCount": 7
  }
}
```

### 2. Trigger Manual Sync

```bash
# Full sync
curl -X POST http://localhost:8082/api/sync/customers/full

# Incremental sync
curl -X POST http://localhost:8082/api/sync/customers/incremental
```

### 3. Verify Kafka Messages

Using Kafka UI (http://localhost:8090):
1. Navigate to Topics
2. Select `customer_data` or `inventory_data`
3. View messages
4. Verify metadata and payload

Or using kafka-console-consumer:
```bash
docker exec -it kafka kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic customer_data \
  --from-beginning
```

## Project Structure

```
java-producers/
├── src/
│   └── main/
│       ├── java/com/ecommerce/integration/
│       │   ├── client/
│       │   │   └── MockApiClient.java          # API client with retry
│       │   ├── config/
│       │   │   ├── ApplicationConfig.java      # Retry & Scheduling
│       │   │   └── KafkaProducerConfig.java    # Kafka setup
│       │   ├── controller/
│       │   │   └── ProducerController.java     # REST endpoints
│       │   ├── model/
│       │   │   ├── Customer.java
│       │   │   ├── Product.java
│       │   │   ├── ApiResponse.java
│       │   │   ├── KafkaMessage.java           # Message wrapper
│       │   │   └── SyncState.java
│       │   ├── producer/
│       │   │   ├── CustomerProducerService.java
│       │   │   └── InventoryProducerService.java
│       │   ├── repository/
│       │   │   └── SyncStateRepository.java    # Sync state tracking
│       │   ├── service/
│       │   │   └── KafkaProducerService.java   # Kafka publishing
│       │   └── JavaProducersApplication.java
│       └── resources/
│           └── application.yml
├── build.gradle
├── settings.gradle
└── Dockerfile
```

## Key Design Decisions

### 1. Why Hybrid Sync?

**Problem**: Full sync on every run is wasteful.  
**Solution**: Initial full sync + incremental updates.  
**Benefit**: Efficient use of API resources, faster sync times.

### 2. Why In-Memory Sync State?

**Current**: Simple concurrent hash map.  
**Production**: Would use Redis or database for persistence.  
**Benefit**: Easy to test, no external dependencies for demo.

### 3. Why RestClient over RestTemplate?

**RestClient**: Modern (Spring 6.1+), fluent API, better error handling.  
**RestTemplate**: Legacy, more verbose.  
**Benefit**: Cleaner code, better maintainability.

### 4. Why Separate Producer Services?

**Modularity**: Each data source is independent.  
**Scalability**: Can scale different producers independently.  
**Maintainability**: Easy to add/modify single source.

### 5. Why Kafka Message Wrapper?

**Traceability**: Track message origin, timestamp, version.  
**Debugging**: Easier to troubleshoot issues.  
**Monitoring**: Metadata enables better metrics.

## Performance Considerations

### Current Configuration
- **Batch Size**: 16KB
- **Linger**: 10ms
- **Compression**: Snappy
- **Idempotence**: Enabled

### Expected Throughput
- **Full Sync**: 5-10 seconds for 100 records
- **Incremental Sync**: <1 second for 0-10 records
- **API Retry**: Max 7 seconds (1s + 2s + 4s)

### Scaling Recommendations
For 10,000+ records/hour:
1. Increase batch size
2. Adjust linger time
3. Use multiple partitions
4. Implement producer pooling

## Error Handling

### API Call Failures
1. **Retry**: Up to 3 attempts with exponential backoff
2. **Log**: Detailed error information
3. **Fail**: Throw exception after max retries

### Kafka Publishing Failures
1. **Retry**: Built-in Kafka retries (3 attempts)
2. **Idempotence**: Prevents duplicates
3. **Callback**: Log success/failure

### Sync State Corruption
- Thread-safe concurrent hash map
- Atomic updates
- Fallback to default values

## Future Enhancements

- [ ] Persistent sync state (Redis/Database)
- [ ] Dead letter queue for failed messages
- [ ] Metrics and monitoring (Prometheus)
- [ ] Circuit breaker pattern
- [ ] Webhook support for real-time sync
- [ ] Multi-threading for large datasets
- [ ] Delta sync optimization

## Troubleshooting

### Producer Won't Start

**Check Kafka connection:**
```bash
docker-compose logs kafka
telnet localhost 9093
```

### No Messages in Kafka

**Check producer logs:**
```bash
docker-compose logs -f java-producers | grep "Successfully sent"
```

### Retry Exhausted

**Verify Mock APIs are running:**
```bash
curl http://localhost:8081/api/customers
```

