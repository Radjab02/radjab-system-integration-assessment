"""
Inventory data consumer
Consumes inventory data from Kafka and adds to merge buffer
"""
import logging
from typing import Dict, Any

from src.consumers.base_consumer import BaseConsumer
from src.services.idempotency_service import IdempotencyService
from src.services.merge_service import MergeService
from src.config import settings

logger = logging.getLogger(__name__)


class InventoryConsumer(BaseConsumer):
    """
    Consumer for inventory/product data from Kafka
    """
    
    def __init__(
        self,
        idempotency_service: IdempotencyService,
        merge_service: MergeService
    ):
        super().__init__(
            topic=settings.KAFKA_INVENTORY_TOPIC,
            idempotency_service=idempotency_service
        )
        self.merge_service = merge_service
        
        logger.info("Inventory consumer initialized")
    
    def start(self) -> None:
        """Start consuming inventory data"""
        logger.info("Starting inventory consumer...")
        self.consume(process_callback=self._process_inventory_message)
    
    def _process_inventory_message(self, message_data: Dict[str, Any]) -> bool:
        """
        Process an inventory message
        
        Args:
            message_data: Parsed Kafka message
            
        Returns:
            True if processing was successful
        """
        try:
            message_id = message_data.get('messageId')
            payload = message_data.get('payload', [])
            metadata = message_data.get('metadata', {})
            sync_type = metadata.get('syncType', 'UNKNOWN')
            
            logger.info(
                f"Processing inventory message: "
                f"id={message_id}, "
                f"syncType={sync_type}, "
                f"records={len(payload)}"
            )
            
            # Add to merge buffer
            if payload:
                self.merge_service.add_inventory_data(payload)
                logger.debug(
                    f"Added {len(payload)} products to merge buffer"
                )
            
            return True
            
        except Exception as e:
            logger.error(f"Error processing inventory message: {e}", exc_info=True)
            return False
