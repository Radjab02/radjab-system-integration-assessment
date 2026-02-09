"""
Merge service for combining customer and inventory data
"""
import logging
from typing import List, Dict, Any
from datetime import datetime
import uuid

from src.config import settings

logger = logging.getLogger(__name__)


class MergeService:
    """
    Service for merging customer and inventory data
    Collects data from both topics and creates analytics payload
    """
    
    def __init__(self):
        self.customer_buffer: List[Dict[str, Any]] = []
        self.inventory_buffer: List[Dict[str, Any]] = []
        
        logger.info("Merge service initialized")
    
    def add_customer_data(self, customers: List[Dict[str, Any]]) -> None:
        """
        Add customer data to buffer
        
        Args:
            customers: List of customer records
        """
        self.customer_buffer.extend(customers)
        logger.debug(
            f"Added {len(customers)} customers to buffer. "
            f"Total customers: {len(self.customer_buffer)}"
        )
    
    def add_inventory_data(self, products: List[Dict[str, Any]]) -> None:
        """
        Add inventory data to buffer
        
        Args:
            products: List of product records
        """
        self.inventory_buffer.extend(products)
        logger.debug(
            f"Added {len(products)} products to buffer. "
            f"Total products: {len(self.inventory_buffer)}"
        )
    
    def has_data(self) -> bool:
        """
        Check if there's any data to merge
        
        Returns:
            True if there's customer or inventory data
        """
        return len(self.customer_buffer) > 0 or len(self.inventory_buffer) > 0
    
    def create_analytics_payload(self) -> Dict[str, Any]:
        """
        Create analytics payload from buffered data
        
        Returns:
            Analytics payload ready to send to API
        """
        event_id = f"EVT-{datetime.now().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:8]}"
        
        # Format timestamp without microseconds to match Spring Boot
        timestamp = datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')

        payload = {
            'eventId': event_id,
            'timestamp': timestamp,
            'customers': self.customer_buffer.copy(),
            'products': self.inventory_buffer.copy(),
            'metadata': {
                'source': settings.APP_NAME,
                'version': settings.APP_VERSION,
                'customerCount': len(self.customer_buffer),
                'productCount': len(self.inventory_buffer),
                'mergedAt': datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')
            }
        }

        logger.info(
            f"Created analytics payload: eventId={event_id}, "
            f"customers={len(self.customer_buffer)}, "
            f"products={len(self.inventory_buffer)}"
        )

        return payload

    def clear_buffers(self) -> None:
        """Clear both customer and inventory buffers after successful send"""
        customer_count = len(self.customer_buffer)
        product_count = len(self.inventory_buffer)

        self.customer_buffer.clear()
        self.inventory_buffer.clear()

        logger.debug(
            f"Cleared buffers: {customer_count} customers, {product_count} products"
        )

    def get_buffer_stats(self) -> Dict[str, int]:
        """
        Get statistics about buffered data

        Returns:
            Dictionary with buffer statistics
        """
        return {
            'customer_count': len(self.customer_buffer),
            'product_count': len(self.inventory_buffer),
            'total_records': len(self.customer_buffer) + len(self.inventory_buffer)
        }