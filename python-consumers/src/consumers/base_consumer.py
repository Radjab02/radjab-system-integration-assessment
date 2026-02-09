"""
Base consumer class with common Kafka consumer functionality
"""
import logging
import json
from typing import Dict, Any, Optional, Callable
from confluent_kafka import Consumer, KafkaError, KafkaException

from src.config import settings
from src.services.idempotency_service import IdempotencyService

logger = logging.getLogger(__name__)


class BaseConsumer:
    """
    Base class for Kafka consumers
    Provides common functionality for consuming messages
    """
    
    def __init__(
        self,
        topic: str,
        idempotency_service: IdempotencyService,
        consumer_config: Optional[Dict[str, Any]] = None
    ):
        self.topic = topic
        self.idempotency_service = idempotency_service
        
        # Use default config or override
        self.config = consumer_config or settings.KAFKA_CONSUMER_CONFIG.copy()
        
        # Create consumer
        self.consumer = Consumer(self.config)
        self.consumer.subscribe([self.topic])
        
        self.running = False
        self.messages_processed = 0
        self.messages_skipped = 0
        self.errors_count = 0
        
        logger.info(
            f"Consumer initialized for topic '{self.topic}' "
            f"with group '{self.config.get('group.id')}'"
        )
    
    def consume(
        self,
        process_callback: Callable[[Dict[str, Any]], bool],
        poll_timeout: float = 1.0
    ) -> None:
        """
        Start consuming messages
        
        Args:
            process_callback: Function to process each message
                             Should return True if successful, False otherwise
            poll_timeout: Timeout for polling messages in seconds
        """
        self.running = True
        
        logger.info(f"Starting consumer for topic '{self.topic}'...")
        
        try:
            while self.running:
                msg = self.consumer.poll(timeout=poll_timeout) # ← Async, non-blocking
                
                if msg is None:
                    continue # No message available, continue loop
                
                if msg.error():
                    self._handle_error(msg.error())
                    continue
                
                # Process message
                success = self._process_message(msg, process_callback)
                
                # Commit offset only if processing was successful
                if success:
                    self.consumer.commit(message=msg)
                    self.messages_processed += 1
                else:
                    self.errors_count += 1
                    logger.error(
                        f"Failed to process message from topic '{self.topic}'. "
                        f"Offset NOT committed."
                    )
                    
        except KeyboardInterrupt:
            logger.info("Consumer interrupted by user")
        except KafkaException as e:
            logger.error(f"Kafka exception: {e}", exc_info=True)
        finally:
            self.stop()
    
    def _process_message(
        self,
        msg,
        process_callback: Callable[[Dict[str, Any]], bool]
    ) -> bool:
        """
        Process a single Kafka message
        
        Args:
            msg: Kafka message
            process_callback: Function to process the message
            
        Returns:
            True if processing was successful, False otherwise
        """
        try:
            # Parse JSON message
            message_data = json.loads(msg.value().decode('utf-8'))
            
            message_id = message_data.get('messageId', 'unknown')
            event_type = message_data.get('eventType', 'unknown')
            
            logger.debug(
                f"Received message: id={message_id}, "
                f"type={event_type}, "
                f"partition={msg.partition()}, "
                f"offset={msg.offset()}"
            )
            
            # Check for duplicates (idempotency)
            if self.idempotency_service.is_processed(message_id):
                logger.warning(
                    f"Skipping duplicate message: {message_id} "
                    f"(already processed)"
                )
                self.messages_skipped += 1
                return True  # Return True to commit offset
            
            # Check for duplicate content (hash-based)
            payload = message_data.get('payload', [])
            payload_hash = self.idempotency_service.get_payload_hash(payload)
            
            if self.idempotency_service.is_duplicate_content(payload_hash):
                logger.warning(
                    f"Skipping message with duplicate content: {message_id}"
                )
                self.messages_skipped += 1
                # Still mark as processed to avoid reprocessing
                self.idempotency_service.mark_processed(
                    message_id,
                    event_type,
                    len(payload),
                    payload_hash
                )
                return True
            
            # Process the message
            success = process_callback(message_data)
            
            if success:
                # Mark as processed for idempotency
                record_count = len(payload)
                self.idempotency_service.mark_processed(
                    message_id,
                    event_type,
                    record_count,
                    payload_hash
                )
                
                logger.info(
                    f"Successfully processed message: {message_id} "
                    f"({record_count} records)"
                )
            
            return success
            
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in message: {e}")
            return False
        except Exception as e:
            logger.error(f"Error processing message: {e}", exc_info=True)
            return False
    
    def _handle_error(self, error: KafkaError) -> None:
        """Handle Kafka errors"""
        if error.code() == KafkaError._PARTITION_EOF:
            logger.debug(
                f"Reached end of partition for topic '{self.topic}'"
            )
        else:
            logger.error(f"Kafka error: {error}")
            self.errors_count += 1
    
    def stop(self) -> None:
        """Stop consuming and close consumer"""
        self.running = False
        
        if self.consumer:
            self.consumer.close()
            logger.info(
                f"Consumer stopped for topic '{self.topic}'. "
                f"Messages processed: {self.messages_processed}, "
                f"Messages skipped: {self.messages_skipped}, "
                f"Errors: {self.errors_count}"
            )
    
    def get_stats(self) -> Dict[str, Any]:
        """Get consumer statistics"""
        return {
            'topic': self.topic,
            'messages_processed': self.messages_processed,
            'messages_skipped': self.messages_skipped,
            'errors_count': self.errors_count,
            'is_running': self.running
        }
