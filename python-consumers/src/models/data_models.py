"""
Data models for Kafka messages and API payloads
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime


@dataclass
class Customer:
    """Customer data model"""
    id: str
    name: str
    email: str
    phone: Optional[str] = None
    address: Optional[str] = None
    created_date: Optional[str] = None
    status: Optional[str] = None


@dataclass
class Product:
    """Product/Inventory data model"""
    id: str
    product_name: str
    sku: str
    stock_quantity: int
    price: Optional[float] = None
    category: Optional[str] = None
    last_updated: Optional[str] = None


@dataclass
class MessageMetadata:
    """Kafka message metadata"""
    producer_version: str
    is_full_sync: bool
    is_incremental_sync: bool
    record_count: int
    sync_type: str


@dataclass
class KafkaMessage:
    """Kafka message wrapper"""
    message_id: str
    source: str
    event_type: str
    timestamp: str
    payload: List[Dict[str, Any]]
    metadata: MessageMetadata


@dataclass
class AnalyticsPayload:
    """Payload sent to Analytics API"""
    event_id: str
    timestamp: str
    customers: List[Dict[str, Any]] = field(default_factory=list)
    products: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ProcessedMessage:
    """Tracking processed messages for idempotency"""
    message_id: str
    event_type: str
    processed_at: datetime
    record_count: int
    hash_value: str
