"""
Unit tests for IdempotencyService
Tests deduplication logic with various scenarios
"""
import pytest
from datetime import datetime, timedelta
import time

from src.services.idempotency_service import IdempotencyService


class TestIdempotencyService:
    """Test suite for IdempotencyService"""
    
    @pytest.fixture
    def service(self):
        """Create fresh IdempotencyService for each test"""
        return IdempotencyService()
    
    # ==================== SUCCESS CASES ====================
    
    def test_is_processed_returns_false_for_new_message(self, service):
        """Test that new messages are not marked as processed"""
        # When
        result = service.is_processed("new-message-123")
        
        # Then
        assert result is False
    
    def test_mark_processed_stores_message(self, service):
        """Test that mark_processed stores the message"""
        # When
        service.mark_processed("msg-123", "CUSTOMER", 5, "hash123")
        
        # Then
        assert service.is_processed("msg-123") is True
    
    def test_is_processed_returns_true_for_existing_message(self, service):
        """Test that processed messages return True"""
        # Given
        service.mark_processed("msg-123", "CUSTOMER", 5, "hash123")
        
        # When
        result = service.is_processed("msg-123")
        
        # Then
        assert result is True
    
    def test_get_payload_hash_is_consistent(self, service):
        """Test that same payload produces same hash"""
        # Given
        payload1 = {"id": "1", "name": "John", "email": "john@example.com"}
        payload2 = {"id": "1", "name": "John", "email": "john@example.com"}
        
        # When
        hash1 = service.get_payload_hash(payload1)
        hash2 = service.get_payload_hash(payload2)
        
        # Then
        assert hash1 == hash2
        assert len(hash1) == 64  # SHA-256 produces 64 hex characters
    
    def test_get_payload_hash_different_for_different_data(self, service):
        """Test that different payloads produce different hashes"""
        # Given
        payload1 = {"id": "1", "name": "John"}
        payload2 = {"id": "2", "name": "Jane"}
        
        # When
        hash1 = service.get_payload_hash(payload1)
        hash2 = service.get_payload_hash(payload2)
        
        # Then
        assert hash1 != hash2
    
    def test_is_duplicate_content_detects_duplicate(self, service):
        """Test that duplicate content is detected"""
        # Given
        payload = {"id": "1", "name": "Test"}
        payload_hash = service.get_payload_hash(payload)
        service.mark_processed("msg-1", "CUSTOMER", 1, payload_hash)
        
        # When
        result = service.is_duplicate_content(payload_hash)
        
        # Then
        assert result is True
    
    def test_is_duplicate_content_returns_false_for_new_content(self, service):
        """Test that new content is not marked as duplicate"""
        # Given
        payload_hash = service.get_payload_hash({"id": "1", "name": "New"})
        
        # When
        result = service.is_duplicate_content(payload_hash)
        
        # Then
        assert result is False
    
    # ==================== EDGE CASES ====================
    
    def test_handles_empty_payload(self, service):
        """Test handling of empty payload"""
        # Given
        empty_payload = {}
        
        # When
        hash_value = service.get_payload_hash(empty_payload)
        
        # Then
        assert hash_value is not None
        assert len(hash_value) == 64
    
    def test_handles_nested_payload(self, service):
        """Test handling of nested data structures"""
        # Given
        nested_payload = {
            "customer": {
                "id": "1",
                "name": "John",
                "addresses": [
                    {"street": "123 Main St", "city": "NYC"},
                    {"street": "456 Oak Ave", "city": "LA"}
                ]
            },
            "metadata": {"timestamp": "2024-02-08"}
        }
        
        # When
        hash_value = service.get_payload_hash(nested_payload)
        
        # Then
        assert hash_value is not None
        assert len(hash_value) == 64
    
    def test_handles_list_payload(self, service):
        """Test handling of list payloads"""
        # Given
        list_payload = [
            {"id": "1", "name": "John"},
            {"id": "2", "name": "Jane"}
        ]
        
        # When
        hash_value = service.get_payload_hash(list_payload)
        
        # Then
        assert hash_value is not None
    
    def test_hash_order_independent(self, service):
        """Test that hash is consistent regardless of key order"""
        # Given
        payload1 = {"name": "John", "id": "1", "email": "john@example.com"}
        payload2 = {"id": "1", "email": "john@example.com", "name": "John"}
        
        # When
        hash1 = service.get_payload_hash(payload1)
        hash2 = service.get_payload_hash(payload2)
        
        # Then
        assert hash1 == hash2  # Should be same despite different key order
    
    # ==================== CACHE MANAGEMENT ====================
    
    def test_cache_size_limit_evicts_oldest(self, service):
        """Test that cache respects max size and evicts oldest entries"""
        # Given
        service._max_size = 3
        
        # When - Add 4 entries
        service.mark_processed("msg-1", "CUSTOMER", 1, "hash1")
        service.mark_processed("msg-2", "CUSTOMER", 1, "hash2")
        service.mark_processed("msg-3", "CUSTOMER", 1, "hash3")
        service.mark_processed("msg-4", "CUSTOMER", 1, "hash4")
        
        # Then - First entry should be evicted
        assert service.is_processed("msg-1") is False
        assert service.is_processed("msg-2") is True
        assert service.is_processed("msg-3") is True
        assert service.is_processed("msg-4") is True
    
    def test_cleanup_expired_removes_old_entries(self, service):
        """Test that expired entries are removed"""
        # Given
        service._ttl_seconds = 0  # Immediate expiration
        service.mark_processed("msg-old", "CUSTOMER", 1, "hash123")
        
        # When
        time.sleep(0.1)  # Small delay to ensure expiration
        service._cleanup_expired()
        
        # Then
        assert service.is_processed("msg-old") is False
    
    def test_cleanup_preserves_valid_entries(self, service):
        """Test that cleanup only removes expired entries"""
        # Given
        service._ttl_seconds = 3600  # 1 hour
        service.mark_processed("msg-valid", "CUSTOMER", 1, "hash123")
        
        # When
        service._cleanup_expired()
        
        # Then
        assert service.is_processed("msg-valid") is True
    
    def test_clear_removes_all_entries(self, service):
        """Test that clear() removes all entries"""
        # Given
        service.mark_processed("msg-1", "CUSTOMER", 1, "hash1")
        service.mark_processed("msg-2", "CUSTOMER", 1, "hash2")
        service.mark_processed("msg-3", "CUSTOMER", 1, "hash3")
        
        # When
        service.clear()
        
        # Then
        assert service.is_processed("msg-1") is False
        assert service.is_processed("msg-2") is False
        assert service.is_processed("msg-3") is False
    
    # ==================== STATISTICS ====================
    
    def test_get_stats_returns_correct_metrics(self, service):
        """Test that get_stats returns accurate statistics"""
        # Given
        service.mark_processed("msg-1", "CUSTOMER", 1, "hash1")
        service.mark_processed("msg-2", "INVENTORY", 1, "hash2")
        
        # When
        stats = service.get_stats()
        
        # Then
        assert stats['total_entries'] == 2
        assert stats['max_size'] == service._max_size
        assert stats['ttl_seconds'] == service._ttl_seconds
        assert 0 <= stats['utilization_percent'] <= 100
    
    def test_get_stats_calculates_utilization_correctly(self, service):
        """Test utilization percentage calculation"""
        # Given
        service._max_size = 10
        service.mark_processed("msg-1", "CUSTOMER", 1, "hash1")
        service.mark_processed("msg-2", "CUSTOMER", 1, "hash2")
        service.mark_processed("msg-3", "CUSTOMER", 1, "hash3")
        
        # When
        stats = service.get_stats()
        
        # Then
        assert stats['total_entries'] == 3
        assert stats['utilization_percent'] == 30.0  # 3/10 * 100
    
    # ==================== CONCURRENT SCENARIOS ====================
    
    def test_multiple_messages_same_content_different_ids(self, service):
        """Test handling multiple messages with same content but different IDs"""
        # Given
        payload = {"id": "1", "name": "Test"}
        payload_hash = service.get_payload_hash(payload)
        
        # When
        service.mark_processed("msg-1", "CUSTOMER", 1, payload_hash)
        service.mark_processed("msg-2", "CUSTOMER", 1, payload_hash)
        
        # Then
        assert service.is_processed("msg-1") is True
        assert service.is_processed("msg-2") is True
        assert service.is_duplicate_content(payload_hash) is True
    
    def test_same_id_different_event_types(self, service):
        """Test that same ID can be used for different event types"""
        # When
        service.mark_processed("msg-123", "CUSTOMER", 5, "hash1")
        service.mark_processed("msg-123", "INVENTORY", 3, "hash2")
        
        # Then
        # Should still detect as duplicate (message ID is the key)
        assert service.is_processed("msg-123") is True
    
    # ==================== SPECIAL CHARACTERS AND ENCODING ====================
    
    def test_handles_special_characters_in_payload(self, service):
        """Test handling of special characters"""
        # Given
        special_payload = {
            "name": "José García",
            "description": "Special chars: @#$%^&*()",
            "unicode": "🎉🎊"
        }
        
        # When
        hash_value = service.get_payload_hash(special_payload)
        
        # Then
        assert hash_value is not None
        assert len(hash_value) == 64
    
    def test_handles_datetime_objects_in_payload(self, service):
        """Test handling of datetime objects (converted to string)"""
        # Given
        payload_with_datetime = {
            "id": "1",
            "timestamp": datetime.now()
        }
        
        # When
        hash_value = service.get_payload_hash(payload_with_datetime)
        
        # Then
        assert hash_value is not None
    
    # ==================== STRESS TESTS ====================
    
    def test_handles_large_number_of_entries(self, service):
        """Test handling large number of cache entries"""
        # Given
        service._max_size = 1000
        
        # When - Add 500 entries
        for i in range(500):
            service.mark_processed(f"msg-{i}", "CUSTOMER", 1, f"hash{i}")
        
        # Then
        stats = service.get_stats()
        assert stats['total_entries'] == 500
        assert service.is_processed("msg-0") is True
        assert service.is_processed("msg-499") is True
    
    def test_handles_very_large_payload(self, service):
        """Test handling of very large payloads"""
        # Given
        large_payload = {
            "customers": [{"id": f"CUST{i}", "name": f"Customer {i}"} for i in range(1000)]
        }
        
        # When
        hash_value = service.get_payload_hash(large_payload)
        
        # Then
        assert hash_value is not None
        assert len(hash_value) == 64
