"""
Caching System for Pipeline Processing

Provides intelligent caching for extracted content and analysis results
to improve performance and reduce redundant processing.
"""

import hashlib
import json
import pickle
import time
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, List, Union, Callable
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path
import logging

try:
    import sqlite3
except ImportError:
    sqlite3 = None

try:
    import redis
except ImportError:
    redis = None


@dataclass
class CacheEntry:
    """Represents a cached item with metadata."""
    key: str
    value: Any
    created_at: datetime
    expires_at: Optional[datetime] = None
    access_count: int = 0
    last_accessed: Optional[datetime] = None
    tags: List[str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.last_accessed is None:
            self.last_accessed = self.created_at
    
    def is_expired(self) -> bool:
        """Check if cache entry has expired."""
        if self.expires_at is None:
            return False
        return datetime.now() > self.expires_at
    
    def access(self):
        """Mark this entry as accessed."""
        self.access_count += 1
        self.last_accessed = datetime.now()


class CacheBackend(ABC):
    """Abstract base class for cache backends."""
    
    @abstractmethod
    def get(self, key: str) -> Optional[CacheEntry]:
        """Get a cache entry by key."""
        pass
    
    @abstractmethod
    def set(self, key: str, value: Any, ttl: Optional[int] = None, tags: List[str] = None):
        """Set a cache entry."""
        pass
    
    @abstractmethod
    def delete(self, key: str) -> bool:
        """Delete a cache entry."""
        pass
    
    @abstractmethod
    def clear(self) -> int:
        """Clear all cache entries."""
        pass
    
    @abstractmethod
    def keys(self, pattern: str = "*") -> List[str]:
        """Get cache keys matching pattern."""
        pass
    
    @abstractmethod
    def stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        pass


class MemoryCache(CacheBackend):
    """In-memory cache backend."""
    
    def __init__(self, max_size: int = 10000):
        self.cache: Dict[str, CacheEntry] = {}
        self.max_size = max_size
        self.hits = 0
        self.misses = 0
    
    def get(self, key: str) -> Optional[CacheEntry]:
        """Get entry from memory cache."""
        entry = self.cache.get(key)
        
        if entry is None:
            self.misses += 1
            return None
        
        if entry.is_expired():
            del self.cache[key]
            self.misses += 1
            return None
        
        entry.access()
        self.hits += 1
        return entry
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None, tags: List[str] = None):
        """Set entry in memory cache."""
        # Evict if at capacity
        if len(self.cache) >= self.max_size:
            self._evict_lru()
        
        expires_at = None
        if ttl:
            expires_at = datetime.now() + timedelta(seconds=ttl)
        
        entry = CacheEntry(
            key=key,
            value=value,
            created_at=datetime.now(),
            expires_at=expires_at,
            tags=tags or []
        )
        
        self.cache[key] = entry
    
    def delete(self, key: str) -> bool:
        """Delete entry from memory cache."""
        if key in self.cache:
            del self.cache[key]
            return True
        return False
    
    def clear(self) -> int:
        """Clear memory cache."""
        count = len(self.cache)
        self.cache.clear()
        self.hits = 0
        self.misses = 0
        return count
    
    def keys(self, pattern: str = "*") -> List[str]:
        """Get keys matching pattern."""
        if pattern == "*":
            return list(self.cache.keys())
        
        # Simple pattern matching
        import fnmatch
        return [key for key in self.cache.keys() if fnmatch.fnmatch(key, pattern)]
    
    def stats(self) -> Dict[str, Any]:
        """Get memory cache statistics."""
        total_requests = self.hits + self.misses
        hit_rate = self.hits / total_requests if total_requests > 0 else 0
        
        return {
            'backend': 'memory',
            'size': len(self.cache),
            'max_size': self.max_size,
            'hits': self.hits,
            'misses': self.misses,
            'hit_rate': hit_rate,
            'total_requests': total_requests
        }
    
    def _evict_lru(self):
        """Evict least recently used entry."""
        if not self.cache:
            return
        
        # Find LRU entry
        lru_key = min(self.cache.keys(), 
                     key=lambda k: self.cache[k].last_accessed)
        del self.cache[lru_key]


class SQLiteCache(CacheBackend):
    """SQLite-based persistent cache backend."""
    
    def __init__(self, db_path: str = ":memory:"):
        if sqlite3 is None:
            raise ImportError("sqlite3 is required for SQLiteCache")
        
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self._init_db()
        self.hits = 0
        self.misses = 0
    
    def _init_db(self):
        """Initialize database schema."""
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS cache_entries (
                key TEXT PRIMARY KEY,
                value BLOB,
                created_at TIMESTAMP,
                expires_at TIMESTAMP,
                access_count INTEGER DEFAULT 0,
                last_accessed TIMESTAMP,
                tags TEXT
            )
        """)
        
        self.conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_expires_at ON cache_entries(expires_at)
        """)
        
        self.conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_last_accessed ON cache_entries(last_accessed)
        """)
        
        self.conn.commit()
    
    def get(self, key: str) -> Optional[CacheEntry]:
        """Get entry from SQLite cache."""
        cursor = self.conn.execute("""
            SELECT key, value, created_at, expires_at, access_count, last_accessed, tags
            FROM cache_entries WHERE key = ?
        """, (key,))
        
        row = cursor.fetchone()
        if row is None:
            self.misses += 1
            return None
        
        # Deserialize entry
        entry = CacheEntry(
            key=row[0],
            value=pickle.loads(row[1]),
            created_at=datetime.fromisoformat(row[2]),
            expires_at=datetime.fromisoformat(row[3]) if row[3] else None,
            access_count=row[4],
            last_accessed=datetime.fromisoformat(row[5]),
            tags=json.loads(row[6]) if row[6] else []
        )
        
        # Check expiration
        if entry.is_expired():
            self.delete(key)
            self.misses += 1
            return None
        
        # Update access info
        entry.access()
        self.conn.execute("""
            UPDATE cache_entries 
            SET access_count = ?, last_accessed = ?
            WHERE key = ?
        """, (entry.access_count, entry.last_accessed.isoformat(), key))
        self.conn.commit()
        
        self.hits += 1
        return entry
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None, tags: List[str] = None):
        """Set entry in SQLite cache."""
        expires_at = None
        if ttl:
            expires_at = datetime.now() + timedelta(seconds=ttl)
        
        entry = CacheEntry(
            key=key,
            value=value,
            created_at=datetime.now(),
            expires_at=expires_at,
            tags=tags or []
        )
        
        self.conn.execute("""
            INSERT OR REPLACE INTO cache_entries 
            (key, value, created_at, expires_at, access_count, last_accessed, tags)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            entry.key,
            pickle.dumps(entry.value),
            entry.created_at.isoformat(),
            entry.expires_at.isoformat() if entry.expires_at else None,
            entry.access_count,
            entry.last_accessed.isoformat(),
            json.dumps(entry.tags)
        ))
        
        self.conn.commit()
    
    def delete(self, key: str) -> bool:
        """Delete entry from SQLite cache."""
        cursor = self.conn.execute("DELETE FROM cache_entries WHERE key = ?", (key,))
        self.conn.commit()
        return cursor.rowcount > 0
    
    def clear(self) -> int:
        """Clear SQLite cache."""
        cursor = self.conn.execute("DELETE FROM cache_entries")
        self.conn.commit()
        return cursor.rowcount
    
    def keys(self, pattern: str = "*") -> List[str]:
        """Get keys matching pattern."""
        if pattern == "*":
            cursor = self.conn.execute("SELECT key FROM cache_entries")
        else:
            # SQLite GLOB pattern
            cursor = self.conn.execute("SELECT key FROM cache_entries WHERE key GLOB ?", (pattern,))
        
        return [row[0] for row in cursor.fetchall()]
    
    def stats(self) -> Dict[str, Any]:
        """Get SQLite cache statistics."""
        cursor = self.conn.execute("SELECT COUNT(*) FROM cache_entries")
        size = cursor.fetchone()[0]
        
        total_requests = self.hits + self.misses
        hit_rate = self.hits / total_requests if total_requests > 0 else 0
        
        return {
            'backend': 'sqlite',
            'db_path': self.db_path,
            'size': size,
            'hits': self.hits,
            'misses': self.misses,
            'hit_rate': hit_rate,
            'total_requests': total_requests
        }
    
    def cleanup_expired(self) -> int:
        """Remove expired entries."""
        cursor = self.conn.execute("""
            DELETE FROM cache_entries 
            WHERE expires_at IS NOT NULL AND expires_at < ?
        """, (datetime.now().isoformat(),))
        self.conn.commit()
        return cursor.rowcount


class RedisCache(CacheBackend):
    """Redis-based distributed cache backend."""
    
    def __init__(self, host: str = "localhost", port: int = 6379, db: int = 0, prefix: str = "logseq:"):
        if redis is None:
            raise ImportError("redis is required for RedisCache")
        
        self.redis_client = redis.Redis(host=host, port=port, db=db, decode_responses=False)
        self.prefix = prefix
        self.hits = 0
        self.misses = 0
    
    def _make_key(self, key: str) -> str:
        """Add prefix to key."""
        return f"{self.prefix}{key}"
    
    def get(self, key: str) -> Optional[CacheEntry]:
        """Get entry from Redis cache."""
        redis_key = self._make_key(key)
        data = self.redis_client.get(redis_key)
        
        if data is None:
            self.misses += 1
            return None
        
        # Deserialize entry
        entry = pickle.loads(data)
        
        # Check expiration (Redis handles TTL, but check anyway)
        if entry.is_expired():
            self.redis_client.delete(redis_key)
            self.misses += 1
            return None
        
        # Update access info
        entry.access()
        self.redis_client.set(redis_key, pickle.dumps(entry))
        
        self.hits += 1
        return entry
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None, tags: List[str] = None):
        """Set entry in Redis cache."""
        expires_at = None
        if ttl:
            expires_at = datetime.now() + timedelta(seconds=ttl)
        
        entry = CacheEntry(
            key=key,
            value=value,
            created_at=datetime.now(),
            expires_at=expires_at,
            tags=tags or []
        )
        
        redis_key = self._make_key(key)
        data = pickle.dumps(entry)
        
        if ttl:
            self.redis_client.setex(redis_key, ttl, data)
        else:
            self.redis_client.set(redis_key, data)
    
    def delete(self, key: str) -> bool:
        """Delete entry from Redis cache."""
        redis_key = self._make_key(key)
        return self.redis_client.delete(redis_key) > 0
    
    def clear(self) -> int:
        """Clear Redis cache with prefix."""
        pattern = self._make_key("*")
        keys = self.redis_client.keys(pattern)
        if keys:
            return self.redis_client.delete(*keys)
        return 0
    
    def keys(self, pattern: str = "*") -> List[str]:
        """Get keys matching pattern."""
        redis_pattern = self._make_key(pattern)
        redis_keys = self.redis_client.keys(redis_pattern)
        
        # Remove prefix from keys
        prefix_len = len(self.prefix)
        return [key.decode('utf-8')[prefix_len:] for key in redis_keys]
    
    def stats(self) -> Dict[str, Any]:
        """Get Redis cache statistics."""
        info = self.redis_client.info()
        
        total_requests = self.hits + self.misses
        hit_rate = self.hits / total_requests if total_requests > 0 else 0
        
        return {
            'backend': 'redis',
            'redis_version': info.get('redis_version'),
            'used_memory': info.get('used_memory'),
            'connected_clients': info.get('connected_clients'),
            'hits': self.hits,
            'misses': self.misses,
            'hit_rate': hit_rate,
            'total_requests': total_requests
        }


class PipelineCache:
    """High-level cache interface for pipeline processing."""
    
    def __init__(self, backend: CacheBackend, default_ttl: int = 3600):
        self.backend = backend
        self.default_ttl = default_ttl
        self.logger = logging.getLogger("pipeline.cache")
    
    def _make_content_key(self, content: str, extractor: str) -> str:
        """Create cache key for extracted content."""
        content_hash = hashlib.sha256(content.encode()).hexdigest()[:16]
        return f"extract:{extractor}:{content_hash}"
    
    def _make_analysis_key(self, content: str, analyzer: str) -> str:
        """Create cache key for analysis results."""
        content_hash = hashlib.sha256(content.encode()).hexdigest()[:16]
        return f"analyze:{analyzer}:{content_hash}"
    
    def get_extracted_content(self, content: str, extractor: str) -> Optional[Dict[str, Any]]:
        """Get cached extraction results."""
        key = self._make_content_key(content, extractor)
        entry = self.backend.get(key)
        return entry.value if entry else None
    
    def cache_extracted_content(self, content: str, extractor: str, result: Dict[str, Any], 
                               ttl: Optional[int] = None):
        """Cache extraction results."""
        key = self._make_content_key(content, extractor)
        self.backend.set(key, result, ttl or self.default_ttl, tags=['extraction', extractor])
        self.logger.debug(f"Cached extraction result for {extractor}")
    
    def get_analysis_result(self, content: str, analyzer: str) -> Optional[Dict[str, Any]]:
        """Get cached analysis results."""
        key = self._make_analysis_key(content, analyzer)
        entry = self.backend.get(key)
        return entry.value if entry else None
    
    def cache_analysis_result(self, content: str, analyzer: str, result: Dict[str, Any],
                             ttl: Optional[int] = None):
        """Cache analysis results."""
        key = self._make_analysis_key(content, analyzer)
        self.backend.set(key, result, ttl or self.default_ttl, tags=['analysis', analyzer])
        self.logger.debug(f"Cached analysis result for {analyzer}")
    
    def invalidate_by_tag(self, tag: str) -> int:
        """Invalidate all cache entries with specific tag."""
        # This is a simplified implementation
        # A more sophisticated version would maintain tag->key mappings
        count = 0
        for key in self.backend.keys():
            entry = self.backend.get(key)
            if entry and tag in entry.tags:
                self.backend.delete(key)
                count += 1
        return count
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return self.backend.stats()
    
    def clear(self) -> int:
        """Clear all cache entries."""
        return self.backend.clear()


class CachedExtractor:
    """Wrapper that adds caching to content extractors."""
    
    def __init__(self, extractor, cache: PipelineCache):
        self.extractor = extractor
        self.cache = cache
        self.name = getattr(extractor, 'name', 'unknown')
    
    def can_extract(self, block) -> bool:
        """Check if extractor can process block."""
        return self.extractor.can_extract(block)
    
    def extract(self, block):
        """Extract content with caching."""
        content = getattr(block, 'content', '')
        if not content:
            return None
        
        # Check cache first
        cached_result = self.cache.get_extracted_content(content, self.name)
        if cached_result:
            return cached_result
        
        # Extract and cache result
        result = self.extractor.extract(block)
        if result:
            self.cache.cache_extracted_content(content, self.name, result)
        
        return result


class CachedAnalyzer:
    """Wrapper that adds caching to content analyzers."""
    
    def __init__(self, analyzer, cache: PipelineCache):
        self.analyzer = analyzer
        self.cache = cache
        self.name = getattr(analyzer, 'name', 'unknown')
    
    def can_analyze(self, content: str) -> bool:
        """Check if analyzer can process content."""
        return self.analyzer.can_analyze(content)
    
    def analyze(self, content: str):
        """Analyze content with caching."""
        if not content:
            return None
        
        # Check cache first
        cached_result = self.cache.get_analysis_result(content, self.name)
        if cached_result:
            return cached_result
        
        # Analyze and cache result
        result = self.analyzer.analyze(content)
        if result:
            self.cache.cache_analysis_result(content, self.name, result)
        
        return result


# Factory functions for creating caches
def create_memory_cache(max_size: int = 10000) -> PipelineCache:
    """Create memory-based cache."""
    backend = MemoryCache(max_size)
    return PipelineCache(backend)


def create_sqlite_cache(db_path: str = None) -> PipelineCache:
    """Create SQLite-based cache."""
    if db_path is None:
        db_path = Path.home() / ".logseq-python" / "cache.db"
        db_path.parent.mkdir(parents=True, exist_ok=True)
    
    backend = SQLiteCache(str(db_path))
    return PipelineCache(backend)


def create_redis_cache(host: str = "localhost", port: int = 6379, db: int = 0) -> PipelineCache:
    """Create Redis-based cache."""
    backend = RedisCache(host, port, db)
    return PipelineCache(backend)


# Decorator for caching function results
def cached(cache: PipelineCache, ttl: Optional[int] = None, key_func: Optional[Callable] = None):
    """Decorator to cache function results."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Create cache key
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                # Simple key based on function name and arguments
                key_data = f"{func.__name__}:{hash((args, tuple(sorted(kwargs.items()))))}"
                cache_key = hashlib.sha256(key_data.encode()).hexdigest()[:16]
            
            # Try cache first
            entry = cache.backend.get(cache_key)
            if entry:
                return entry.value
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache.backend.set(cache_key, result, ttl)
            
            return result
        
        return wrapper
    return decorator