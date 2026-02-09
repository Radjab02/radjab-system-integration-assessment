"""
Main application for Python consumers
Orchestrates customer and inventory consumers
"""
import logging
import sys
import threading
import time
import signal
from typing import Optional

from src.config import settings
from src.consumers.customer_consumer import CustomerConsumer
from src.consumers.inventory_consumer import InventoryConsumer
from src.services.idempotency_service import IdempotencyService
from src.services.merge_service import MergeService
from src.services.analytics_service import AnalyticsService

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger(__name__)


class ConsumerApplication:
    """Main application orchestrating all consumers"""
    
    def __init__(self):
        logger.info("=" * 80)
        logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
        logger.info("=" * 80)
        
        # Initialize services
        self.idempotency_service = IdempotencyService()
        self.merge_service = MergeService()
        self.analytics_service = AnalyticsService()
        
        # Initialize consumers
        self.customer_consumer = CustomerConsumer(
            self.idempotency_service,
            self.merge_service
        )
        self.inventory_consumer = InventoryConsumer(
            self.idempotency_service,
            self.merge_service
        )
        
        # Consumer threads
        self.customer_thread: Optional[threading.Thread] = None
        self.inventory_thread: Optional[threading.Thread] = None
        self.merger_thread: Optional[threading.Thread] = None
        
        self.running = False
        
        # Register signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        logger.info("Application initialized successfully")
    
    def start(self) -> None:
        """Start all consumers and merger"""
        logger.info("Starting consumers...")
        self.running = True
        
        # Check Analytics API health
        if not self.analytics_service.health_check():
            logger.warning(
                "Analytics API health check failed, "
                "but continuing anyway (will retry on send)"
            )
        
        # Start customer consumer in thread
        self.customer_thread = threading.Thread(
            target=self.customer_consumer.start,
            name="CustomerConsumer",
            daemon=True
        )
        self.customer_thread.start()
        logger.info("Customer consumer thread started")
        
        # Start inventory consumer in thread
        self.inventory_thread = threading.Thread(
            target=self.inventory_consumer.start,
            name="InventoryConsumer",
            daemon=True
        )
        self.inventory_thread.start()
        logger.info("Inventory consumer thread started")
        
        # Start merger thread
        self.merger_thread = threading.Thread(
            target=self._run_merger,
            name="Merger",
            daemon=True
        )
        self.merger_thread.start()
        logger.info("Merger thread started")
        
        logger.info("All consumers started successfully")
        
        # Keep main thread alive
        self._wait_for_shutdown()
    
    def _run_merger(self) -> None:
        """
        Periodically check for data and send to Analytics API
        Runs in separate thread
        """
        logger.info("Merger thread started")
        
        while self.running:
            try:
                time.sleep(settings.MERGE_FLUSH_INTERVAL)
                
                if self.merge_service.has_data():
                    self._flush_to_analytics()
                else:
                    logger.debug("No data to merge yet, waiting...")
                    
            except Exception as e:
                logger.error(f"Error in merger thread: {e}", exc_info=True)
        
        logger.info("Merger thread stopped")
    
    def _flush_to_analytics(self) -> None:
        """Flush merged data to Analytics API"""
        try:
            # Get buffer stats
            stats = self.merge_service.get_buffer_stats()
            logger.info(
                f"Flushing data to Analytics API: "
                f"customers={stats['customer_count']}, "
                f"products={stats['product_count']}"
            )
            
            # Create payload
            payload = self.merge_service.create_analytics_payload()
            
            # Send to Analytics API
            success = self.analytics_service.send_analytics_data(payload)
            
            if success:
                # Clear buffers on success
                self.merge_service.clear_buffers()
                logger.info("Successfully flushed data to Analytics API")
            else:
                logger.error(
                    "Failed to send data to Analytics API. "
                    "Data remains in buffer for retry."
                )
                
        except Exception as e:
            logger.error(f"Error flushing to analytics: {e}", exc_info=True)
    
    def _wait_for_shutdown(self) -> None:
        """Wait for shutdown signal"""
        try:
            while self.running:
                time.sleep(1)
                
                # Log stats periodically
                if int(time.time()) % 60 == 0:  # Every minute
                    self._log_stats()
                    
        except KeyboardInterrupt:
            logger.info("Shutdown requested by user")
            self.stop()
    
    def _log_stats(self) -> None:
        """Log application statistics"""
        customer_stats = self.customer_consumer.get_stats()
        inventory_stats = self.inventory_consumer.get_stats()
        buffer_stats = self.merge_service.get_buffer_stats()
        idempotency_stats = self.idempotency_service.get_stats()
        
        logger.info("=" * 80)
        logger.info("Application Statistics:")
        logger.info(
            f"  Customer Consumer: "
            f"processed={customer_stats['messages_processed']}, "
            f"skipped={customer_stats['messages_skipped']}, "
            f"errors={customer_stats['errors_count']}"
        )
        logger.info(
            f"  Inventory Consumer: "
            f"processed={inventory_stats['messages_processed']}, "
            f"skipped={inventory_stats['messages_skipped']}, "
            f"errors={inventory_stats['errors_count']}"
        )
        logger.info(
            f"  Merge Buffer: "
            f"customers={buffer_stats['customer_count']}, "
            f"products={buffer_stats['product_count']}"
        )
        logger.info(
            f"  Idempotency Cache: "
            f"entries={idempotency_stats['total_entries']}, "
            f"utilization={idempotency_stats['utilization_percent']:.1f}%"
        )
        logger.info("=" * 80)
    
    def _signal_handler(self, signum, frame) -> None:
        """Handle shutdown signals"""
        logger.info(f"Received signal {signum}, initiating shutdown...")
        self.stop()
    
    def stop(self) -> None:
        """Stop all consumers and cleanup"""
        logger.info("Stopping application...")
        self.running = False
        
        # Flush any remaining data
        if self.merge_service.has_data():
            logger.info("Flushing remaining data before shutdown...")
            self._flush_to_analytics()
        
        # Stop consumers
        if self.customer_consumer:
            self.customer_consumer.stop()
        if self.inventory_consumer:
            self.inventory_consumer.stop()
        
        # Close services
        if self.analytics_service:
            self.analytics_service.close()
        
        # Final stats
        self._log_stats()
        
        logger.info("Application stopped successfully")
        logger.info("=" * 80)


def main():
    """Main entry point"""
    try:
        app = ConsumerApplication()
        app.start()
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
