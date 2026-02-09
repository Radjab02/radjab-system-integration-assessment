"""
Idempotency service for deduplication
Prevents processing duplicate messages
"""
import hashlib
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict
from collections import OrderedDict

from src.config import settings

logger = logging.getLogger(__name__)


class IdempotencyService:
    """
    Tracks processed messages to prevent duplicates
    Uses in-memory LRU cache with TTL
    
    In production, this would use Redis or a database
    """
    
    def __init__(self):
        self._cache: OrderedDict[str, Dict] = OrderedDict()
        self._max_size = settings.IDEMPOTENCY_CACHE_SIZE
        self._ttl_seconds = settings.IDEMPOTENCY_CACHE_TTL
        
        logger.info(
            f"Idempotency service initialized: "
            f"max_size={self._max_size}, ttl={self._ttl_seconds}s"
        )
    
    def is_processed(self, message_id: str) -> bool:
        """
        Check if message has already been processed
        
        Args:
            message_id: Unique message identifier
            
        Returns:
            True if message was already processed, False otherwise
        """
        self._cleanup_expired()
        
        if message_id in self._cache:
            entry = self._cache[message_id]
            logger.debug(f"Message {message_id} found in cache (duplicate)")
            return True
        
        return False
    
    def mark_processed(
        self,
        message_id: str,
        event_type: str,
        record_count: int,
        payload_hash: str
    ) -> None:
        """
        Mark a message as processed
        
        Args:
            message_id: Unique message identifier
            event_type: Type of event (CUSTOMER/INVENTORY)
            record_count: Number of records in message
            payload_hash: Hash of payload for content-based deduplication
        """
        # Remove oldest entry if cache is full
        if len(self._cache) >= self._max_size:
            oldest_key = next(iter(self._cache))
            del self._cache[oldest_key]
            logger.debug(f"Cache full, removed oldest entry: {oldest_key}")
        
        # Add to cache
        self._cache[message_id] = {
            'event_type': event_type,
            'record_count': record_count,
            'payload_hash': payload_hash,
            'processed_at': datetime.now(),
            'expires_at': datetime.now() + timedelta(seconds=self._ttl_seconds)
        }
        
        logger.debug(
            f"Marked as processed: {message_id} "
            f"(type={event_type}, records={record_count})"
        )
    
    def get_payload_hash(self, payload: any) -> str:
        """
        Generate hash of payload for content-based deduplication
        
        Args:
            payload: The message payload
            
        Returns:
            SHA-256 hash of the payload
        """
        import json
        
        # Convert to JSON string and hash
        payload_str = json.dumps(payload, sort_keys=True, default=str)
        return hashlib.sha256(payload_str.encode()).hexdigest()
    
    def is_duplicate_content(self, payload_hash: str) -> bool:
        """
        Check if we've seen this exact content before (hash-based deduplication)
        
        Args:
            payload_hash: Hash of the payload
            
        Returns:
            True if content has been seen before
        """
        self._cleanup_expired()
        
        for entry in self._cache.values():
            if entry['payload_hash'] == payload_hash:
                logger.warning(
                    f"Duplicate content detected with hash: {payload_hash[:16]}..."
                )
                return True
        
        return False
    
    def _cleanup_expired(self) -> None:
        """Remove expired entries from cache"""
        now = datetime.now()
        expired_keys = [
            key for key, value in self._cache.items()
            if value['expires_at'] < now
        ]
        
        for key in expired_keys:
            del self._cache[key]
        
        if expired_keys:
            logger.debug(f"Cleaned up {len(expired_keys)} expired entries")
    
    def get_stats(self) -> Dict:
        """Get cache statistics"""
        self._cleanup_expired()
        
        return {
            'total_entries': len(self._cache),
            'max_size': self._max_size,
            'utilization_percent': (len(self._cache) / self._max_size) * 100,
            'ttl_seconds': self._ttl_seconds
        }
    
    def clear(self) -> None:
        """Clear all entries (for testing)"""
        self._cache.clear()
        logger.info("Idempotency cache cleared")
