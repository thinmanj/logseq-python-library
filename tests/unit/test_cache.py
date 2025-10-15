"""
Unit tests for the caching system.

Tests the various cache backends and high-level cache interfaces.
"""

import pytest
import time
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

from logseq_py.pipeline.cache import (
    CacheEntry,
    MemoryCache,
    SQLiteCache,
    PipelineCache,
    CachedExtractor,
    CachedAnalyzer,
    create_memory_cache,
    create_sqlite_cache,
    cached
)


class TestCacheEntry:
    """Test CacheEntry data class."""
    
    def test_creation(self):
        """Test basic cache entry creation."""
        now = datetime.now()
        entry = CacheEntry(
            key="test_key",
            value="test_value",
            created_at=now
        )
        
        assert entry.key == "test_key"
        assert entry.value == "test_value"
        assert entry.created_at == now
        assert entry.expires_at is None
        assert entry.access_count == 0
        assert entry.last_accessed == now
        assert entry.tags == []
    
    def test_creation_with_optional_fields(self):
        """Test cache entry creation with optional fields."""
        now = datetime.now()
        expires = now + timedelta(hours=1)
        
        entry = CacheEntry(
            key="test_key",
            value="test_value",
            created_at=now,
            expires_at=expires,
            access_count=5,
            tags=["tag1", "tag2"]
        )
        
        assert entry.expires_at == expires
        assert entry.access_count == 5
        assert entry.tags == ["tag1", "tag2"]
    
    def test_is_expired_no_expiration(self):
        """Test is_expired with no expiration set."""
        entry = CacheEntry(
            key="test",
            value="value",
            created_at=datetime.now()
        )
        
        assert not entry.is_expired()
    
    def test_is_expired_future(self):
        """Test is_expired with future expiration."""
        entry = CacheEntry(
            key="test",
            value="value",
            created_at=datetime.now(),
            expires_at=datetime.now() + timedelta(hours=1)
        )
        
        assert not entry.is_expired()
    
    def test_is_expired_past(self):
        """Test is_expired with past expiration."""
        entry = CacheEntry(
            key="test",
            value="value",
            created_at=datetime.now() - timedelta(hours=2),
            expires_at=datetime.now() - timedelta(hours=1)
        )
        
        assert entry.is_expired()
    
    def test_access(self):
        """Test accessing entry updates metadata."""
        entry = CacheEntry(
            key="test",
            value="value",
            created_at=datetime.now()
        )
        
        original_count = entry.access_count
        original_time = entry.last_accessed
        
        # Wait a tiny bit to ensure time difference
        time.sleep(0.001)
        entry.access()
        
        assert entry.access_count == original_count + 1
        assert entry.last_accessed > original_time


class TestMemoryCache:
    """Test MemoryCache backend."""
    
    def test_basic_operations(self):
        """Test basic get/set/delete operations."""
        cache = MemoryCache()
        
        # Initially empty
        assert cache.get("nonexistent") is None
        assert cache.stats()['size'] == 0
        
        # Set and get
        cache.set("key1", "value1")
        entry = cache.get("key1")
        
        assert entry is not None
        assert entry.value == "value1"
        assert entry.access_count == 1
        
        # Delete
        assert cache.delete("key1") is True
        assert cache.get("key1") is None
        assert cache.delete("key1") is False  # Already deleted
    
    def test_ttl_expiration(self):
        """Test TTL-based expiration."""
        cache = MemoryCache()
        
        # Set with very short TTL
        cache.set("key", "value", ttl=0.001)  # 1ms
        
        # Should exist immediately
        assert cache.get("key") is not None
        
        # Wait for expiration
        time.sleep(0.002)
        
        # Should be expired
        assert cache.get("key") is None
    
    def test_lru_eviction(self):
        """Test LRU eviction when at capacity."""
        cache = MemoryCache(max_size=2)
        
        # Fill to capacity
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        assert cache.stats()['size'] == 2
        
        # Access key1 to make it more recently used
        cache.get("key1")
        
        # Add third item, should evict key2 (LRU)
        cache.set("key3", "value3")
        assert cache.stats()['size'] == 2
        assert cache.get("key1") is not None  # Still exists
        assert cache.get("key2") is None      # Evicted
        assert cache.get("key3") is not None  # Newly added
    
    def test_pattern_matching(self):
        """Test pattern matching for keys."""
        cache = MemoryCache()
        
        cache.set("user:1", "user1")
        cache.set("user:2", "user2")
        cache.set("post:1", "post1")
        
        # All keys
        all_keys = cache.keys("*")
        assert len(all_keys) == 3
        
        # Pattern matching
        user_keys = cache.keys("user:*")
        assert len(user_keys) == 2
        assert "user:1" in user_keys
        assert "user:2" in user_keys
    
    def test_clear(self):
        """Test clearing all cache entries."""
        cache = MemoryCache()
        
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        assert cache.stats()['size'] == 2
        
        cleared = cache.clear()
        assert cleared == 2
        assert cache.stats()['size'] == 0
        assert cache.get("key1") is None
    
    def test_stats(self):
        """Test cache statistics."""
        cache = MemoryCache(max_size=100)
        
        stats = cache.stats()
        assert stats['backend'] == 'memory'
        assert stats['max_size'] == 100
        assert stats['size'] == 0
        assert stats['hits'] == 0
        assert stats['misses'] == 0
        assert stats['hit_rate'] == 0
        
        # Add some data and access
        cache.set("key", "value")
        cache.get("key")  # Hit
        cache.get("nonexistent")  # Miss
        
        stats = cache.stats()
        assert stats['size'] == 1
        assert stats['hits'] == 1
        assert stats['misses'] == 1
        assert stats['hit_rate'] == 0.5


class TestSQLiteCache:
    """Test SQLiteCache backend."""
    
    def test_basic_operations(self):
        """Test basic SQLite cache operations."""
        cache = SQLiteCache(":memory:")  # In-memory SQLite
        
        # Initially empty
        assert cache.get("nonexistent") is None
        
        # Set and get
        cache.set("key1", {"data": "value1"})
        entry = cache.get("key1")
        
        assert entry is not None
        assert entry.value == {"data": "value1"}
        assert entry.access_count == 1
        
        # Delete
        assert cache.delete("key1") is True
        assert cache.get("key1") is None
    
    def test_ttl_with_sqlite(self):
        """Test TTL handling in SQLite."""
        cache = SQLiteCache(":memory:")
        
        # Set with short TTL
        cache.set("key", "value", ttl=0.001)
        
        # Should exist immediately
        assert cache.get("key") is not None
        
        # Wait and check expiration
        time.sleep(0.002)
        assert cache.get("key") is None
    
    def test_persistence_behavior(self):
        """Test that data persists between instances (with real file)."""
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            db_path = tmp.name
        
        try:
            # Create cache and add data
            cache1 = SQLiteCache(db_path)
            cache1.set("persistent_key", "persistent_value")
            
            # Create new instance with same file
            cache2 = SQLiteCache(db_path)
            entry = cache2.get("persistent_key")
            
            assert entry is not None
            assert entry.value == "persistent_value"
            
        finally:
            os.unlink(db_path)
    
    def test_cleanup_expired(self):
        """Test cleanup of expired entries."""
        cache = SQLiteCache(":memory:")
        
        # Add entries with different TTL
        cache.set("key1", "value1", ttl=0.001)  # Will expire
        cache.set("key2", "value2")  # No expiration
        
        # Wait for first to expire
        time.sleep(0.002)
        
        # Cleanup expired
        cleaned = cache.cleanup_expired()
        assert cleaned == 1
        
        # Check remaining
        assert cache.get("key1") is None
        assert cache.get("key2") is not None


class TestPipelineCache:
    """Test high-level PipelineCache interface."""
    
    def setup_method(self):
        """Set up test cache."""
        self.backend = MemoryCache()
        self.cache = PipelineCache(self.backend)
    
    def test_content_extraction_caching(self):
        """Test caching of content extraction results."""
        content = "This is some content to extract from"
        extractor_name = "test_extractor"
        result = {"extracted": "data", "metadata": {"count": 5}}
        
        # Initially no cached result
        cached = self.cache.get_extracted_content(content, extractor_name)
        assert cached is None
        
        # Cache the result
        self.cache.cache_extracted_content(content, extractor_name, result)
        
        # Should now be cached
        cached = self.cache.get_extracted_content(content, extractor_name)
        assert cached == result
    
    def test_analysis_result_caching(self):
        """Test caching of analysis results."""
        content = "Content to analyze"
        analyzer_name = "sentiment_analyzer"
        result = {"sentiment": "positive", "confidence": 0.85}
        
        # Initially no cached result
        cached = self.cache.get_analysis_result(content, analyzer_name)
        assert cached is None
        
        # Cache the result
        self.cache.cache_analysis_result(content, analyzer_name, result)
        
        # Should now be cached
        cached = self.cache.get_analysis_result(content, analyzer_name)
        assert cached == result
    
    def test_different_content_different_keys(self):
        """Test that different content gets different cache keys."""
        extractor = "test_extractor"
        
        self.cache.cache_extracted_content("content1", extractor, {"data": 1})
        self.cache.cache_extracted_content("content2", extractor, {"data": 2})
        
        # Should get different results for different content
        result1 = self.cache.get_extracted_content("content1", extractor)
        result2 = self.cache.get_extracted_content("content2", extractor)
        
        assert result1 == {"data": 1}
        assert result2 == {"data": 2}
    
    def test_different_extractors_different_keys(self):
        """Test that different extractors get different cache keys."""
        content = "same content"
        
        self.cache.cache_extracted_content(content, "extractor1", {"data": 1})
        self.cache.cache_extracted_content(content, "extractor2", {"data": 2})
        
        # Should get different results for different extractors
        result1 = self.cache.get_extracted_content(content, "extractor1")
        result2 = self.cache.get_extracted_content(content, "extractor2")
        
        assert result1 == {"data": 1}
        assert result2 == {"data": 2}
    
    def test_stats_delegation(self):
        """Test that stats are delegated to backend."""
        stats = self.cache.get_stats()
        backend_stats = self.backend.stats()
        
        assert stats == backend_stats
    
    def test_clear_delegation(self):
        """Test that clear is delegated to backend."""
        # Add some data
        self.cache.cache_extracted_content("content", "extractor", {"data": 1})
        assert self.backend.stats()['size'] == 1
        
        # Clear through cache
        cleared = self.cache.clear()
        assert cleared == 1
        assert self.backend.stats()['size'] == 0


class TestCachedExtractor:
    """Test CachedExtractor wrapper."""
    
    def setup_method(self):
        """Set up test components."""
        self.backend = MemoryCache()
        self.cache = PipelineCache(self.backend)
        self.mock_extractor = Mock()
        self.mock_extractor.name = "test_extractor"
        
        self.cached_extractor = CachedExtractor(self.mock_extractor, self.cache)
    
    def test_can_extract_delegation(self):
        """Test can_extract is delegated to underlying extractor."""
        mock_block = Mock()
        self.mock_extractor.can_extract.return_value = True
        
        assert self.cached_extractor.can_extract(mock_block) is True
        self.mock_extractor.can_extract.assert_called_once_with(mock_block)
    
    def test_extract_cache_miss(self):
        """Test extraction when not in cache (cache miss)."""
        mock_block = Mock()
        mock_block.content = "test content"
        
        expected_result = {"extracted": "data"}
        self.mock_extractor.extract.return_value = expected_result
        
        result = self.cached_extractor.extract(mock_block)
        
        # Should call underlying extractor
        self.mock_extractor.extract.assert_called_once_with(mock_block)
        assert result == expected_result
        
        # Should be cached now
        cached = self.cache.get_extracted_content("test content", "test_extractor")
        assert cached == expected_result
    
    def test_extract_cache_hit(self):
        """Test extraction when in cache (cache hit)."""
        content = "test content"
        cached_result = {"cached": "data"}
        
        # Pre-populate cache
        self.cache.cache_extracted_content(content, "test_extractor", cached_result)
        
        mock_block = Mock()
        mock_block.content = content
        
        result = self.cached_extractor.extract(mock_block)
        
        # Should NOT call underlying extractor
        self.mock_extractor.extract.assert_not_called()
        assert result == cached_result
    
    def test_extract_empty_content(self):
        """Test extraction with empty content."""
        mock_block = Mock()
        mock_block.content = ""
        
        result = self.cached_extractor.extract(mock_block)
        
        assert result is None
        self.mock_extractor.extract.assert_not_called()
    
    def test_extract_no_result_not_cached(self):
        """Test that None results are not cached."""
        mock_block = Mock()
        mock_block.content = "test content"
        
        self.mock_extractor.extract.return_value = None
        
        result = self.cached_extractor.extract(mock_block)
        
        assert result is None
        
        # Should not be cached
        cached = self.cache.get_extracted_content("test content", "test_extractor")
        assert cached is None
    
    def test_name_fallback(self):
        """Test name fallback when extractor has no name attribute."""
        extractor_without_name = Mock(spec=[])  # No name attribute
        cached_extractor = CachedExtractor(extractor_without_name, self.cache)
        
        assert cached_extractor.name == "unknown"


class TestCachedAnalyzer:
    """Test CachedAnalyzer wrapper."""
    
    def setup_method(self):
        """Set up test components."""
        self.backend = MemoryCache()
        self.cache = PipelineCache(self.backend)
        self.mock_analyzer = Mock()
        self.mock_analyzer.name = "test_analyzer"
        
        self.cached_analyzer = CachedAnalyzer(self.mock_analyzer, self.cache)
    
    def test_can_analyze_delegation(self):
        """Test can_analyze is delegated to underlying analyzer."""
        content = "test content"
        self.mock_analyzer.can_analyze.return_value = True
        
        assert self.cached_analyzer.can_analyze(content) is True
        self.mock_analyzer.can_analyze.assert_called_once_with(content)
    
    def test_analyze_cache_miss(self):
        """Test analysis when not in cache (cache miss)."""
        content = "test content"
        expected_result = {"sentiment": "positive"}
        self.mock_analyzer.analyze.return_value = expected_result
        
        result = self.cached_analyzer.analyze(content)
        
        # Should call underlying analyzer
        self.mock_analyzer.analyze.assert_called_once_with(content)
        assert result == expected_result
        
        # Should be cached now
        cached = self.cache.get_analysis_result(content, "test_analyzer")
        assert cached == expected_result
    
    def test_analyze_cache_hit(self):
        """Test analysis when in cache (cache hit)."""
        content = "test content"
        cached_result = {"cached": "analysis"}
        
        # Pre-populate cache
        self.cache.cache_analysis_result(content, "test_analyzer", cached_result)
        
        result = self.cached_analyzer.analyze(content)
        
        # Should NOT call underlying analyzer
        self.mock_analyzer.analyze.assert_not_called()
        assert result == cached_result
    
    def test_analyze_empty_content(self):
        """Test analysis with empty content."""
        result = self.cached_analyzer.analyze("")
        
        assert result is None
        self.mock_analyzer.analyze.assert_not_called()


class TestFactoryFunctions:
    """Test cache factory functions."""
    
    def test_create_memory_cache(self):
        """Test memory cache factory."""
        cache = create_memory_cache(max_size=500)
        
        assert isinstance(cache, PipelineCache)
        assert isinstance(cache.backend, MemoryCache)
        assert cache.backend.max_size == 500
    
    def test_create_sqlite_cache(self):
        """Test SQLite cache factory."""
        cache = create_sqlite_cache(":memory:")
        
        assert isinstance(cache, PipelineCache)
        assert isinstance(cache.backend, SQLiteCache)


class TestCachedDecorator:
    """Test the @cached decorator."""
    
    def setup_method(self):
        """Set up test cache."""
        self.cache = create_memory_cache()
    
    def test_cached_function(self):
        """Test basic function caching."""
        call_count = 0
        
        @cached(self.cache, ttl=60)
        def expensive_function(x, y):
            nonlocal call_count
            call_count += 1
            return x + y
        
        # First call
        result1 = expensive_function(1, 2)
        assert result1 == 3
        assert call_count == 1
        
        # Second call with same args - should use cache
        result2 = expensive_function(1, 2)
        assert result2 == 3
        assert call_count == 1  # Not called again
        
        # Different args - should call function
        result3 = expensive_function(2, 3)
        assert result3 == 5
        assert call_count == 2
    
    def test_cached_with_custom_key_function(self):
        """Test cached decorator with custom key function."""
        def key_func(obj):
            return f"object:{obj.id}"
        
        @cached(self.cache, key_func=key_func)
        def process_object(obj):
            return f"processed_{obj.value}"
        
        # Create mock objects
        obj1 = Mock()
        obj1.id = "123"
        obj1.value = "data1"
        
        obj2 = Mock()
        obj2.id = "123"  # Same ID
        obj2.value = "data2"  # Different value
        
        # First call
        result1 = process_object(obj1)
        assert result1 == "processed_data1"
        
        # Second call with same ID should use cache
        result2 = process_object(obj2)
        assert result2 == "processed_data1"  # Cached result, not data2