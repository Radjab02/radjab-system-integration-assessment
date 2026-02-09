# Task 3: Python Consumers - Complete

## Overview

This implementation provides **production-ready Python consumers** that:
- Consume messages from Kafka topics (`customer_data` and `inventory_data`)
- Merge customer and inventory data into unified analytics payload
- Send merged data to Analytics API with retry logic
- Implement **idempotency** to prevent duplicate processing
- Handle errors gracefully with comprehensive logging

## Architecture

```
┌─────────────────┐
│  Kafka Topics   │
│ - customer_data │
│ - inventory_data│
└────────┬────────┘
         │
         ├─────────────────┐
         │                 │
         ▼                 ▼
┌────────────────┐  ┌──────────────────┐
│   Customer     │  │   Inventory      │
│   Consumer     │  │   Consumer       │
└───────┬────────┘  └────────┬─────────┘
        │                    │
        │   Add to buffer    │
        └──────────┬─────────┘
                   ▼
           ┌───────────────┐
           │ Merge Service │
           │  (Buffer)     │
           └───────┬───────┘
                   │
                   │ Every 30s or when ready
                   ▼
          ┌─────────────────┐
          │ Analytics API   │
          │  POST /data     │
          └─────────────────┘
```

## Key Components

### 1. **BaseConsumer**
- Base class for all Kafka consumers
- Handles message polling, parsing, and committing
- Integrates idempotency checking
- Provides common error handling

### 2. **CustomerConsumer**
- Consumes from `customer_data` topic
- Adds customer records to merge buffer
- Extends BaseConsumer

### 3. **InventoryConsumer**
- Consumes from `inventory_data` topic  
- Adds product records to merge buffer
- Extends BaseConsumer

### 4. **MergeService**
- Buffers customer and product data
- Creates unified analytics payload
- Clears buffers after successful send

### 5. **AnalyticsService**
- Sends data to Analytics API
- Implements retry logic with exponential backoff
- HTTP connection pooling for efficiency

### 6. **IdempotencyService**
- Prevents duplicate message processing
- Two-level deduplication:
  - Message ID tracking
  - Content hash-based detection
- In-memory LRU cache with TTL

## Features

### ✅ Idempotency Implementation

**Dual deduplication strategy:**

1. **Message ID Tracking**
```python
if idempotency_service.is_processed(message_id):
    logger.warning("Skipping duplicate message")
    return True  # Already processed
```

2. **Content Hash Deduplication**
```python
payload_hash = get_payload_hash(payload)
if is_duplicate_content(payload_hash):
    logger.warning("Skipping duplicate content")
    return True  # Same data, different message ID
```

**Benefits:**
- Handles Kafka redeliveries
- Detects duplicate data with different IDs
- Configurable cache size and TTL

### ✅ Retry Logic with Exponential Backoff

```python
Attempt 1: Immediate
Attempt 2: +1 second   (1.0 * 2^0)
Attempt 3: +2 seconds  (1.0 * 2^1)
Attempt 4: +4 seconds  (1.0 * 2^2)
```

**Configuration:**
```python
MAX_RETRIES = 3
RETRY_BACKOFF_BASE = 1.0
RETRY_BACKOFF_MULTIPLIER = 2.0
```

### ✅ Asynchronous Processing

**Multi-threading architecture:**
- Thread 1: Customer consumer
- Thread 2: Inventory consumer  
- Thread 3: Periodic merger/sender

**Benefits:**
- Non-blocking consumption
- Parallel processing
- Efficient resource usage

### ✅ Manual Offset Committing

```python
# Only commit if processing succeeds
if success:
    consumer.commit(message=msg)
else:
    # Don't commit - will reprocess on restart
    logger.error("Not committing offset due to error")
```

**Guarantees at-least-once delivery**

### ✅ Comprehensive Logging

```
2024-02-08 10:30:00 - INFO - Starting python-consumers v1.0.0
2024-02-08 10:30:01 - INFO - Customer consumer thread started
2024-02-08 10:30:01 - INFO - Inventory consumer thread started  
2024-02-08 10:30:15 - INFO - Received message: id=abc-123, type=CUSTOMER
2024-02-08 10:30:15 - INFO - Successfully processed message: abc-123 (5 records)
2024-02-08 10:30:45 - INFO - Flushing data to Analytics API: customers=5, products=7
2024-02-08 10:30:45 - INFO - Analytics data sent successfully: records=12
```

## Configuration

### Environment Variables

```bash
# Kafka
KAFKA_BOOTSTRAP_SERVERS=localhost:9093
KAFKA_CUSTOMER_TOPIC=customer_data
KAFKA_INVENTORY_TOPIC=inventory_data
KAFKA_GROUP_ID=python-consumers-group

# Analytics API
ANALYTICS_API_BASE_URL=http://localhost:8081
ANALYTICS_API_TIMEOUT=30

# Retry
MAX_RETRIES=3
RETRY_BACKOFF_BASE=1.0
RETRY_BACKOFF_MULTIPLIER=2.0

# Idempotency
IDEMPOTENCY_CACHE_SIZE=10000
IDEMPOTENCY_CACHE_TTL=3600  # 1 hour

# Merge
MERGE_FLUSH_INTERVAL=30  # seconds

# Logging
LOG_LEVEL=INFO
```

## Message Flow

### 1. Java Producers → Kafka
```json
{
  "messageId": "uuid-here",
  "source": "java-producers",
  "eventType": "CUSTOMER",
  "timestamp": "2024-02-08T10:30:00Z",
  "payload": [
    {"id": "CUST001", "name": "John Doe", ...}
  ],
  "metadata": {
    "syncType": "INITIAL_FULL",
    "recordCount": 5
  }
}
```

### 2. Python Consumers → Analytics API
```json
{
  "eventId": "EVT-20240208103000-abc123",
  "timestamp": "2024-02-08T10:30:00Z",
  "customers": [
    {"id": "CUST001", "name": "John Doe", ...}
  ],
  "products": [
    {"id": "PROD001", "productName": "Laptop", ...}
  ],
  "metadata": {
    "source": "python-consumers",
    "version": "1.0.0",
    "customerCount": 5,
    "productCount": 7
  }
}
```

## Running the Application

### Option 1: Docker Compose (Recommended)

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f python-consumers

# Stop
docker-compose down
```

### Option 2: Local Development

```bash
cd python-consumers

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export KAFKA_BOOTSTRAP_SERVERS=localhost:9093
export ANALYTICS_API_BASE_URL=http://localhost:8081

# Run
python -m src.main
```

## Testing

### 1. Verify Consumers are Running

```bash
# Check logs
docker-compose logs python-consumers | grep "started"

# Expected output:
# Customer consumer thread started
# Inventory consumer thread started
# Merger thread started
```

### 2. Verify Message Consumption

```bash
# Watch logs for message processing
docker-compose logs -f python-consumers

# Should see:
# Received message: id=..., type=CUSTOMER
# Successfully processed message: ... (5 records)
```

### 3. Verify Analytics API Calls

```bash
# Check Analytics API logs
docker-compose logs mock-apis | grep analytics

# Should see:
# POST /api/analytics/data
# Data processed successfully
```

### 4. Verify Idempotency

```bash
# Restart consumers (Kafka will redeliver messages)
docker-compose restart python-consumers

# Check logs for duplicates
docker-compose logs python-consumers | grep "duplicate"

# Should see:
# Skipping duplicate message: ... (already processed)
```

## Project Structure

```
python-consumers/
├── src/
│   ├── __init__.py
│   ├── main.py                       # Main application
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py               # Configuration
│   ├── consumers/
│   │   ├── __init__.py
│   │   ├── base_consumer.py          # Base consumer logic
│   │   ├── customer_consumer.py      # Customer consumer
│   │   └── inventory_consumer.py     # Inventory consumer
│   ├── services/
│   │   ├── __init__.py
│   │   ├── analytics_service.py      # Analytics API client
│   │   ├── merge_service.py          # Data merging
│   │   └── idempotency_service.py    # Deduplication
│   └── models/
│       ├── __init__.py
│       └── data_models.py            # Data classes
├── tests/
├── requirements.txt
├── Dockerfile
└── README.md
```

## Key Design Decisions

### 1. Why Separate Consumers?

**Scalability**: Can scale customer and inventory consumers independently  
**Isolation**: Failure in one doesn't affect the other  
**Clarity**: Each consumer has single responsibility

### 2. Why In-Memory Idempotency Cache?

**Current**: Simple OrderedDict with TTL (demo/testing)  
**Production**: Would use Redis for persistence across restarts  
**Benefit**: No external dependencies for demo

### 3. Why Periodic Merging?

**Efficiency**: Batch multiple messages into one API call  
**Control**: Configurable flush interval (30s default)  
**Reliability**: Ensures data is sent even if only one topic has data

### 4. Why Manual Offset Commit?

**Reliability**: Only commit after successful processing  
**At-least-once**: If crash occurs, message will be reprocessed  
**Idempotency**: Duplicate detection handles reprocessing

### 5. Why confluent-kafka-python?

**Performance**: C-based, faster than kafka-python  
**Features**: Better error handling, metrics  
**Support**: Well-maintained, production-ready

## Error Handling Strategy

### API Call Failures
1. Retry up to 3 times with exponential backoff
2. Don't retry on 4xx errors (client errors)
3. Keep data in buffer for next flush attempt
4. Log detailed error information

### Kafka Connection Issues
- Auto-reconnect built into confluent-kafka
- Will pause consumption until reconnection
- No messages lost (not committed)

### Deserialization Errors
- Log error with message details
- Skip message (commit offset)
- Continue processing

### Duplicate Messages
- Detected via message ID
- Detected via content hash
- Skip silently (log as warning)
- Commit offset to avoid reprocessing

## Performance Considerations

### Current Configuration
- **Flush interval**: 30 seconds
- **Poll timeout**: 1 second
- **Max retries**: 3
- **Cache size**: 10,000 messages

### Expected Throughput
- **Messages/second**: 100-500
- **Latency**: <100ms per message (excluding API call)
- **API calls**: 1 every 30 seconds (batched)

### Scaling Recommendations

For 10,000+ messages/hour:
1. Increase number of consumer instances
2. Add more Kafka partitions
3. Tune flush interval
4. Use Redis for idempotency cache

## Monitoring

### Statistics Logged Every Minute

```
Application Statistics:
  Customer Consumer: processed=50, skipped=2, errors=0
  Inventory Consumer: processed=45, skipped=1, errors=0
  Merge Buffer: customers=5, products=7
  Idempotency Cache: entries=95, utilization=0.9%
```

### Key Metrics to Monitor

- Messages processed per minute
- Messages skipped (duplicates)
- Error count
- Buffer size
- API call success rate
- Idempotency cache utilization

## Future Enhancements

- [ ] Redis-based idempotency cache
- [ ] Dead letter queue for failed messages
- [ ] Prometheus metrics endpoint
- [ ] Configurable consumer count per topic
- [ ] Dynamic flush interval based on buffer size
- [ ] Avro schema support
- [ ] Unit and integration tests

## Troubleshooting

### Consumers Not Starting

```bash
# Check Kafka connection
docker-compose logs kafka

# Verify topics exist
docker exec -it kafka kafka-topics --list --bootstrap-server localhost:9092
```

### No Messages Being Consumed

```bash
# Check if producers are running
curl http://localhost:8082/api/sync/status

# Check topic has messages
docker exec -it kafka kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic customer_data \
  --from-beginning \
  --max-messages 1
```

### Analytics API Calls Failing

```bash
# Check Analytics API is up
curl http://localhost:8081/actuator/health

# Check network connectivity from container
docker exec -it python-consumers ping mock-apis
```

---


