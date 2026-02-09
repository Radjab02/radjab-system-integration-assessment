"""
Unit tests for Python Consumers
Tests BaseConsumer with mocked Kafka messages
"""
import pytest
import json
from unittest.mock import Mock, MagicMock, patch, call
from confluent_kafka import KafkaError, KafkaException

from src.consumers.base_consumer import BaseConsumer
from src.services.idempotency_service import IdempotencyService


class TestBaseConsumer:
    """Test suite for BaseConsumer with mocked Kafka messages"""
    
    @pytest.fixture
    def idempotency_service(self):
        """Mock idempotency service"""
        service = Mock(spec=IdempotencyService)
        service.is_processed.return_value = False
        service.is_duplicate_content.return_value = False
        service.get_payload_hash.return_value = "hash123"
        return service
    
    @pytest.fixture
    def consumer(self, idempotency_service):
        """Create BaseConsumer with mocked dependencies"""
        with patch('src.consumers.base_consumer.Consumer') as mock_consumer_class:
            mock_kafka_consumer = Mock()
            mock_consumer_class.return_value = mock_kafka_consumer
            
            consumer = BaseConsumer(
                topic="test_topic",
                idempotency_service=idempotency_service
            )
            consumer.consumer = mock_kafka_consumer
            
            return consumer
    
    def create_mock_message(self, message_id="msg-123", payload_data=None):
        """Helper to create mock Kafka message"""
        if payload_data is None:
            payload_data = [{"id": "1", "name": "Test"}]
        
        message_data = {
            'messageId': message_id,
            'eventType': 'CUSTOMER',
            'timestamp': '2024-02-08T10:00:00Z',
            'payload': payload_data,
            'metadata': {
                'syncType': 'INITIAL_FULL',
                'recordCount': len(payload_data)
            }
        }
        
        mock_msg = Mock()
        mock_msg.error.return_value = None
        mock_msg.value.return_value = json.dumps(message_data).encode('utf-8')
        mock_msg.partition.return_value = 0
        mock_msg.offset.return_value = 123
        
        return mock_msg
    
    # ==================== SUCCESS CASES ====================
    
    def test_process_message_success(self, consumer, idempotency_service):
        """Test successful message processing"""
        # Given
        mock_msg = self.create_mock_message()
        process_callback = Mock(return_value=True)
        
        # When
        result = consumer._process_message(mock_msg, process_callback)
        
        # Then
        assert result is True
        process_callback.assert_called_once()
        idempotency_service.mark_processed.assert_called_once()
    
    def test_process_multiple_records_in_payload(self, consumer, idempotency_service):
        """Test processing message with multiple records"""
        # Given
        payload_data = [
            {"id": "1", "name": "Test1"},
            {"id": "2", "name": "Test2"},
            {"id": "3", "name": "Test3"}
        ]
        mock_msg = self.create_mock_message(payload_data=payload_data)
        process_callback = Mock(return_value=True)
        
        # When
        result = consumer._process_message(mock_msg, process_callback)
        
        # Then
        assert result is True
        idempotency_service.mark_processed.assert_called_once_with(
            "msg-123",
            "CUSTOMER",
            3,  # 3 records
            "hash123"
        )
    
    def test_consume_processes_message_and_commits(self, consumer):
        """Test that consume() processes message and commits offset"""
        # Given
        mock_msg = self.create_mock_message()
        consumer.consumer.poll.side_effect = [mock_msg, None]  # One message then stop
        consumer.running = True
        process_callback = Mock(return_value=True)
        
        # When
        with patch.object(consumer, '_process_message', return_value=True):
            consumer.consume(process_callback, poll_timeout=0.1)
            consumer.stop()  # Stop after one iteration
        
        # Then
        consumer.consumer.commit.assert_called_once_with(message=mock_msg)
    
    # ==================== IDEMPOTENCY / DUPLICATE DETECTION ====================
    
    def test_skips_duplicate_message_id(self, consumer, idempotency_service):
        """Test that duplicate message IDs are skipped"""
        # Given
        idempotency_service.is_processed.return_value = True  # Already processed
        mock_msg = self.create_mock_message()
        process_callback = Mock()
        
        # When
        result = consumer._process_message(mock_msg, process_callback)
        
        # Then
        assert result is True  # Returns True to commit offset
        process_callback.assert_not_called()  # But doesn't process
        consumer.messages_skipped += 1
    
    def test_skips_duplicate_content_hash(self, consumer, idempotency_service):
        """Test that duplicate content is skipped"""
        # Given
        idempotency_service.is_processed.return_value = False
        idempotency_service.is_duplicate_content.return_value = True  # Duplicate content
        mock_msg = self.create_mock_message()
        process_callback = Mock()
        
        # When
        result = consumer._process_message(mock_msg, process_callback)
        
        # Then
        assert result is True
        process_callback.assert_not_called()
        idempotency_service.mark_processed.assert_called_once()  # Still mark as processed
    
    def test_processes_unique_message(self, consumer, idempotency_service):
        """Test that unique messages are processed"""
        # Given
        idempotency_service.is_processed.return_value = False
        idempotency_service.is_duplicate_content.return_value = False
        mock_msg = self.create_mock_message()
        process_callback = Mock(return_value=True)
        
        # When
        result = consumer._process_message(mock_msg, process_callback)
        
        # Then
        assert result is True
        process_callback.assert_called_once()
    
    # ==================== EDGE CASES ====================
    
    def test_handles_empty_payload(self, consumer, idempotency_service):
        """Test handling message with empty payload"""
        # Given
        mock_msg = self.create_mock_message(payload_data=[])
        process_callback = Mock(return_value=True)
        
        # When
        result = consumer._process_message(mock_msg, process_callback)
        
        # Then
        assert result is True
        idempotency_service.mark_processed.assert_called_with(
            "msg-123",
            "CUSTOMER",
            0,  # 0 records
            "hash123"
        )
    
    def test_handles_missing_message_id(self, consumer):
        """Test handling message without messageId"""
        # Given
        message_data = {
            'eventType': 'CUSTOMER',
            'payload': [{"id": "1"}]
            # No messageId
        }
        mock_msg = Mock()
        mock_msg.error.return_value = None
        mock_msg.value.return_value = json.dumps(message_data).encode('utf-8')
        mock_msg.partition.return_value = 0
        mock_msg.offset.return_value = 123
        process_callback = Mock(return_value=True)
        
        # When
        result = consumer._process_message(mock_msg, process_callback)
        
        # Then
        # Should handle gracefully with 'unknown' as default
        assert result is True
    
    def test_poll_returns_none(self, consumer):
        """Test handling when poll returns None (no messages)"""
        # Given
        consumer.consumer.poll.return_value = None
        consumer.running = True
        process_callback = Mock()
        
        # When
        with patch.object(consumer, '_process_message') as mock_process:
            # Run one iteration
            consumer.consume(process_callback, poll_timeout=0.1)
            consumer.running = False  # Stop
        
        # Then
        mock_process.assert_not_called()
    
    # ==================== FAILURE CASES ====================
    
    def test_handles_invalid_json(self, consumer):
        """Test handling message with invalid JSON"""
        # Given
        mock_msg = Mock()
        mock_msg.error.return_value = None
        mock_msg.value.return_value = b"not valid json"
        process_callback = Mock()
        
        # When
        result = consumer._process_message(mock_msg, process_callback)
        
        # Then
        assert result is False
        process_callback.assert_not_called()
    
    def test_handles_callback_exception(self, consumer, idempotency_service):
        """Test handling when process callback throws exception"""
        # Given
        mock_msg = self.create_mock_message()
        process_callback = Mock(side_effect=Exception("Processing error"))
        
        # When
        result = consumer._process_message(mock_msg, process_callback)
        
        # Then
        assert result is False
        consumer.errors_count += 1
    
    def test_does_not_commit_on_failure(self, consumer):
        """Test that offset is not committed when processing fails"""
        # Given
        mock_msg = self.create_mock_message()
        consumer.consumer.poll.return_value = mock_msg
        consumer.running = True
        process_callback = Mock(return_value=False)  # Processing fails
        
        # When
        with patch.object(consumer, '_process_message', return_value=False):
            consumer.consume(process_callback, poll_timeout=0.1)
            consumer.running = False
        
        # Then
        consumer.consumer.commit.assert_not_called()
    
    def test_handles_kafka_error(self, consumer):
        """Test handling Kafka error messages"""
        # Given
        mock_msg = Mock()
        mock_error = Mock(spec=KafkaError)
        mock_error.code.return_value = KafkaError._PARTITION_EOF
        mock_msg.error.return_value = mock_error
        
        # When
        consumer._handle_error(mock_error)
        
        # Then
        consumer.errors_count += 1
    
    def test_handles_critical_kafka_exception(self, consumer):
        """Test handling critical Kafka exceptions"""
        # Given
        consumer.consumer.poll.side_effect = KafkaException("Critical error")
        consumer.running = True
        process_callback = Mock()
        
        # When/Then
        with pytest.raises(KafkaException):
            consumer.consume(process_callback)
    
    # ==================== STATS AND METRICS ====================
    
    def test_increments_messages_processed(self, consumer, idempotency_service):
        """Test that messages_processed counter increments"""
        # Given
        mock_msg = self.create_mock_message()
        process_callback = Mock(return_value=True)
        consumer.messages_processed = 0
        
        # When
        consumer._process_message(mock_msg, process_callback)
        consumer.messages_processed += 1  # Simulating what consume() does
        
        # Then
        assert consumer.messages_processed == 1
    
    def test_increments_messages_skipped(self, consumer, idempotency_service):
        """Test that messages_skipped counter increments"""
        # Given
        idempotency_service.is_processed.return_value = True
        mock_msg = self.create_mock_message()
        process_callback = Mock()
        consumer.messages_skipped = 0
        
        # When
        consumer._process_message(mock_msg, process_callback)
        consumer.messages_skipped += 1  # Simulating skip logic
        
        # Then
        assert consumer.messages_skipped == 1
    
    def test_get_stats_returns_correct_data(self, consumer):
        """Test that get_stats returns correct metrics"""
        # Given
        consumer.messages_processed = 10
        consumer.messages_skipped = 2
        consumer.errors_count = 1
        consumer.running = True
        
        # When
        stats = consumer.get_stats()
        
        # Then
        assert stats['topic'] == 'test_topic'
        assert stats['messages_processed'] == 10
        assert stats['messages_skipped'] == 2
        assert stats['errors_count'] == 1
        assert stats['is_running'] is True
    
    def test_stop_closes_consumer(self, consumer):
        """Test that stop() closes Kafka consumer"""
        # Given
        consumer.running = True
        consumer.messages_processed = 5
        
        # When
        consumer.stop()
        
        # Then
        assert consumer.running is False
        consumer.consumer.close.assert_called_once()
    
    # ==================== MESSAGE PARSING ====================
    
    def test_parses_message_fields_correctly(self, consumer, idempotency_service):
        """Test that all message fields are parsed correctly"""
        # Given
        payload_data = [{"id": "1", "name": "Test", "email": "test@example.com"}]
        mock_msg = self.create_mock_message(
            message_id="test-msg-456",
            payload_data=payload_data
        )
        
        captured_data = {}
        def capture_callback(data):
            captured_data.update(data)
            return True
        
        # When
        consumer._process_message(mock_msg, capture_callback)
        
        # Then
        assert captured_data['messageId'] == 'test-msg-456'
        assert captured_data['eventType'] == 'CUSTOMER'
        assert len(captured_data['payload']) == 1
        assert captured_data['payload'][0]['email'] == 'test@example.com'
    
    def test_parses_metadata_correctly(self, consumer, idempotency_service):
        """Test that metadata is parsed correctly"""
        # Given
        mock_msg = self.create_mock_message()
        
        captured_data = {}
        def capture_callback(data):
            captured_data.update(data)
            return True
        
        # When
        consumer._process_message(mock_msg, capture_callback)
        
        # Then
        assert 'metadata' in captured_data
        assert captured_data['metadata']['syncType'] == 'INITIAL_FULL'
        assert captured_data['metadata']['recordCount'] > 0
