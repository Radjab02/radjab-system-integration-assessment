"""
Configuration settings for Python consumers
"""
import os
from typing import Dict

# Kafka Configuration
KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9093')
KAFKA_CUSTOMER_TOPIC = os.getenv('KAFKA_CUSTOMER_TOPIC', 'customer_data')
KAFKA_INVENTORY_TOPIC = os.getenv('KAFKA_INVENTORY_TOPIC', 'inventory_data')
KAFKA_GROUP_ID = os.getenv('KAFKA_GROUP_ID', 'python-consumers-group')

# Kafka Consumer Configuration
KAFKA_CONSUMER_CONFIG: Dict[str, any] = {
    'bootstrap.servers': KAFKA_BOOTSTRAP_SERVERS,
    'group.id': KAFKA_GROUP_ID,
    'auto.offset.reset': 'earliest',  # Start from beginning if no offset
    'enable.auto.commit': False,  # Manual commit for better control
    'max.poll.interval.ms': 300000,  # 5 minutes
    'session.timeout.ms': 30000,  # 30 seconds
}

# Analytics API Configuration
ANALYTICS_API_BASE_URL = os.getenv('ANALYTICS_API_BASE_URL', 'http://localhost:8081')
ANALYTICS_API_ENDPOINT = '/api/analytics/data'
ANALYTICS_API_TIMEOUT = int(os.getenv('ANALYTICS_API_TIMEOUT', '30'))

# Retry Configuration
MAX_RETRIES = int(os.getenv('MAX_RETRIES', '3'))
RETRY_BACKOFF_BASE = float(os.getenv('RETRY_BACKOFF_BASE', '1.0'))  # seconds
RETRY_BACKOFF_MULTIPLIER = float(os.getenv('RETRY_BACKOFF_MULTIPLIER', '2.0'))

# Idempotency Configuration
IDEMPOTENCY_CACHE_SIZE = int(os.getenv('IDEMPOTENCY_CACHE_SIZE', '10000'))
IDEMPOTENCY_CACHE_TTL = int(os.getenv('IDEMPOTENCY_CACHE_TTL', '3600'))  # 1 hour

# Merge Configuration
MERGE_BATCH_SIZE = int(os.getenv('MERGE_BATCH_SIZE', '100'))
MERGE_FLUSH_INTERVAL = int(os.getenv('MERGE_FLUSH_INTERVAL', '30'))  # seconds

# Logging
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FORMAT = os.getenv('LOG_FORMAT', 'json')  # 'json' or 'text'

# Application
APP_NAME = 'python-consumers'
APP_VERSION = '1.0.0'
