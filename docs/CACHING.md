# Caching System

The logseq-python library includes a comprehensive caching system designed to optimize pipeline processing performance by storing and reusing extracted content and analysis results.

## Overview

The caching system provides:

- **Multiple Backend Support**: Memory, SQLite, and Redis backends
- **Intelligent Key Generation**: Content-based cache keys with hash-based deduplication
- **TTL Support**: Time-based cache expiration
- **LRU Eviction**: Least Recently Used eviction for memory-constrained environments
- **Statistics**: Hit rate tracking and cache performance metrics
- **Thread Safety**: Concurrent access support
- **Pipeline Integration**: Seamless integration with extraction and analysis components

## Architecture

### Core Components

#### CacheEntry
Represents a cached item with metadata:
```python
@dataclass
class CacheEntry:
    key: str
    value: Any
    created_at: datetime
    expires_at: Optional[datetime] = None
    access_count: int = 0
    last_accessed: Optional[datetime] = None
    tags: List[str] = None
```

#### CacheBackend (Abstract Base Class)
Defines the interface for cache backends:
- `get(key)` - Retrieve cache entry
- `set(key, value, ttl, tags)` - Store cache entry
- `delete(key)` - Remove cache entry
- `clear()` - Remove all entries
- `keys(pattern)` - List keys matching pattern
- `stats()` - Get cache statistics

### Backend Implementations

#### MemoryCache
In-memory cache with LRU eviction:
```python
cache = MemoryCache(max_size=10000)
```

Features:
- Fast access (O(1) for get/set operations)
- LRU eviction when at capacity
- TTL expiration support
- Pattern-based key matching
- No persistence between sessions

#### SQLiteCache
Persistent cache using SQLite database:
```python
cache = SQLiteCache(db_path="/path/to/cache.db")
```

Features:
- Persistent storage
- ACID transactions
- Efficient indexed lookups
- Cleanup operations for expired entries
- Cross-session data persistence

#### RedisCache
Distributed cache using Redis:
```python
cache = RedisCache(host="localhost", port=6379, db=0)
```

Features:
- Distributed caching
- Network-based storage
- Redis-native TTL handling
- High availability support
- Shared cache across multiple processes

### High-Level Interface

#### PipelineCache
High-level interface for pipeline processing:
```python
cache = PipelineCache(backend, default_ttl=3600)
```

Methods:
- `get_extracted_content(content, extractor)` - Get cached extraction results
- `cache_extracted_content(content, extractor, result, ttl)` - Cache extraction results
- `get_analysis_result(content, analyzer)` - Get cached analysis results  
- `cache_analysis_result(content, analyzer, result, ttl)` - Cache analysis results

#### Cached Wrappers
Automatic caching wrappers for extractors and analyzers:

```python
cached_extractor = CachedExtractor(extractor, cache)
cached_analyzer = CachedAnalyzer(analyzer, cache)
```

## Usage Examples

### Basic Memory Caching

```python
from logseq_py.pipeline.cache import create_memory_cache

# Create memory cache
cache = create_memory_cache(max_size=5000)

# Cache extraction results
content = "Some content to extract from"
extractor_name = "url_extractor"
result = {"extracted": "data", "metadata": {"count": 5}}

cache.cache_extracted_content(content, extractor_name, result)

# Retrieve cached results
cached = cache.get_extracted_content(content, extractor_name)
```

### Persistent SQLite Caching

```python
from logseq_py.pipeline.cache import create_sqlite_cache

# Create SQLite cache (persists between sessions)
cache = create_sqlite_cache("/path/to/cache.db")

# Cache analysis results with TTL
content = "Content to analyze"
analyzer_name = "sentiment_analyzer"
result = {"sentiment": "positive", "confidence": 0.85}

cache.cache_analysis_result(content, analyzer_name, result, ttl=3600)
```

### Wrapped Extractors and Analyzers

```python
from logseq_py.pipeline.cache import create_memory_cache, CachedExtractor, CachedAnalyzer

# Create cache
cache = create_memory_cache()

# Create cached wrappers
cached_extractor = CachedExtractor(my_extractor, cache)
cached_analyzer = CachedAnalyzer(my_analyzer, cache)

# Use as normal - caching happens automatically
for block in blocks:
    # Check cache first, extract if not found, cache the result
    extracted = cached_extractor.extract(block)
    analyzed = cached_analyzer.analyze(block.content)
```

### Performance Monitoring

```python
# Get cache statistics
stats = cache.get_stats()
print(f"Hit rate: {stats['hit_rate']:.2%}")
print(f"Cache size: {stats['size']} entries")
print(f"Total requests: {stats['total_requests']}")
```

### Function-Level Caching

```python
from logseq_py.pipeline.cache import cached

@cached(cache, ttl=300)
def expensive_computation(data):
    # Expensive operation that benefits from caching
    return process_data(data)

# First call executes function and caches result
result1 = expensive_computation(data)

# Second call returns cached result
result2 = expensive_computation(data)  # Fast!
```

## Configuration

### Cache Size Management

```python
# Memory cache with size limit
cache = create_memory_cache(max_size=1000)

# SQLite cache (size managed by disk space)
cache = create_sqlite_cache("/path/to/cache.db")

# Clear cache when needed
cleared_count = cache.clear()
```

### TTL Configuration

```python
# Default TTL for all cache operations
cache = PipelineCache(backend, default_ttl=7200)  # 2 hours

# Override TTL for specific operations
cache.cache_extracted_content(content, extractor, result, ttl=300)  # 5 minutes
```

### Cache Keys

Cache keys are automatically generated based on:
- Content hash (SHA-256, first 16 characters)
- Extractor/analyzer name
- Operation type (extract/analyze)

Example key: `extract:url_extractor:a1b2c3d4e5f6g7h8`

## Best Practices

### 1. Choose Appropriate Backend
- **Memory**: Fast, single-process, development/testing
- **SQLite**: Persistent, single-machine, production
- **Redis**: Distributed, multi-process, high-scale production

### 2. Set Reasonable TTL Values
```python
# Short TTL for frequently changing data
cache.cache_analysis_result(content, "news_analyzer", result, ttl=300)  # 5 min

# Long TTL for stable data
cache.cache_extracted_content(content, "pdf_extractor", result, ttl=86400)  # 24 hours
```

### 3. Monitor Cache Performance
```python
def log_cache_stats(cache):
    stats = cache.get_stats()
    if stats['hit_rate'] < 0.5:
        logger.warning(f"Low cache hit rate: {stats['hit_rate']:.2%}")
```

### 4. Handle Cache Failures Gracefully
```python
try:
    result = cache.get_extracted_content(content, extractor)
    if result is None:
        result = extractor.extract(content)
        cache.cache_extracted_content(content, extractor, result)
except Exception as e:
    logger.warning(f"Cache operation failed: {e}")
    result = extractor.extract(content)  # Fallback to direct extraction
```

### 5. Use Tags for Cache Management
```python
# Tag cache entries for easier management
cache.backend.set("key", "value", tags=["extraction", "youtube"])

# Invalidate by tag when needed
cache.invalidate_by_tag("youtube")
```

## Integration with Async Pipeline

The caching system integrates seamlessly with the async pipeline:

```python
import asyncio
from logseq_py.pipeline.async_pipeline import AsyncBatchProcessor
from logseq_py.pipeline.cache import create_memory_cache, CachedExtractor

async def process_with_caching():
    cache = create_memory_cache()
    cached_extractor = CachedExtractor(my_extractor, cache)
    
    batch_processor = AsyncBatchProcessor(max_concurrent=10)
    
    async def process_batch(blocks):
        tasks = [cached_extractor.extract(block) for block in blocks]
        return await asyncio.gather(*tasks)
    
    async for results in batch_processor.process_batches(blocks, process_batch):
        # Process results with cached extraction
        handle_results(results)
```

## Troubleshooting

### Common Issues

1. **High Memory Usage**
   - Reduce cache size: `cache = create_memory_cache(max_size=1000)`
   - Use shorter TTL: `ttl=300`
   - Switch to SQLite backend

2. **Low Hit Rate**
   - Check if content is being processed multiple times
   - Verify cache keys are consistent
   - Consider longer TTL values

3. **SQLite Database Locks**
   - Use connection pooling
   - Set appropriate timeout values
   - Consider WAL mode for better concurrency

4. **Redis Connection Issues**
   - Check Redis server status
   - Verify network connectivity
   - Implement connection retry logic

### Debugging

Enable detailed logging:
```python
import logging
logging.getLogger("pipeline.cache").setLevel(logging.DEBUG)
```

Check cache statistics regularly:
```python
stats = cache.get_stats()
print(f"Cache performance: {stats}")
```

## Performance Considerations

### Memory Backend
- **Pros**: Fastest access, no I/O overhead
- **Cons**: Limited by memory, no persistence
- **Best for**: Development, single-process applications

### SQLite Backend
- **Pros**: Persistent, ACID compliant, good performance
- **Cons**: File I/O overhead, single-writer limitation
- **Best for**: Single-machine production applications

### Redis Backend
- **Pros**: Distributed, high availability, excellent performance
- **Cons**: Network overhead, additional infrastructure
- **Best for**: Multi-process, distributed applications

## Migration and Maintenance

### Migrating Between Backends
```python
# Export from one cache
old_cache = create_memory_cache()
new_cache = create_sqlite_cache("/path/to/new.db")

# Migrate data (example)
for key in old_cache.backend.keys("*"):
    entry = old_cache.backend.get(key)
    if entry and not entry.is_expired():
        new_cache.backend.set(key, entry.value, tags=entry.tags)
```

### Cache Maintenance
```python
# Clean up expired entries (SQLite)
if hasattr(cache.backend, 'cleanup_expired'):
    expired_count = cache.backend.cleanup_expired()
    print(f"Cleaned up {expired_count} expired entries")

# Monitor cache size
stats = cache.get_stats()
if stats.get('size', 0) > 10000:
    # Consider clearing old entries or increasing capacity
    pass
```

The caching system provides powerful performance optimization capabilities for your Logseq pipeline processing while maintaining flexibility and ease of use.