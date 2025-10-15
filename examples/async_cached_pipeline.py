"""
Example: Asynchronous Pipeline with Intelligent Caching

This example demonstrates how to integrate the caching system with
the async pipeline framework for optimal performance.
"""

import asyncio
import time
from typing import List, Dict, Any
from pathlib import Path

# Mock imports for demonstration
from logseq_py.models import Block, Page
from logseq_py.pipeline.cache import create_memory_cache, create_sqlite_cache, CachedExtractor, CachedAnalyzer
from logseq_py.pipeline.async_pipeline import AsyncPipeline, AsyncBatchProcessor


class MockContentExtractor:
    """Mock content extractor that simulates expensive extraction."""
    
    def __init__(self, name: str, delay: float = 0.1):
        self.name = name
        self.delay = delay
        self.call_count = 0
    
    def can_extract(self, block: Block) -> bool:
        return True
    
    def extract(self, block: Block) -> Dict[str, Any]:
        """Simulate expensive extraction work."""
        self.call_count += 1
        time.sleep(self.delay)  # Simulate work
        
        return {
            'extracted_text': block.content[:100],
            'word_count': len(block.content.split()),
            'extraction_time': time.time(),
            'extractor': self.name
        }


class MockContentAnalyzer:
    """Mock content analyzer that simulates expensive analysis."""
    
    def __init__(self, name: str, delay: float = 0.2):
        self.name = name
        self.delay = delay
        self.call_count = 0
    
    def can_analyze(self, content: str) -> bool:
        return len(content) > 0
    
    def analyze(self, content: str) -> Dict[str, Any]:
        """Simulate expensive analysis work."""
        self.call_count += 1
        time.sleep(self.delay)  # Simulate work
        
        # Mock sentiment analysis
        positive_words = ['good', 'great', 'excellent', 'amazing', 'wonderful']
        negative_words = ['bad', 'terrible', 'awful', 'horrible', 'worse']
        
        pos_count = sum(1 for word in positive_words if word in content.lower())
        neg_count = sum(1 for word in negative_words if word in content.lower())
        
        if pos_count > neg_count:
            sentiment = 'positive'
        elif neg_count > pos_count:
            sentiment = 'negative'
        else:
            sentiment = 'neutral'
        
        return {
            'sentiment': sentiment,
            'positive_score': pos_count,
            'negative_score': neg_count,
            'confidence': abs(pos_count - neg_count) / max(1, pos_count + neg_count),
            'analysis_time': time.time(),
            'analyzer': self.name
        }


async def demonstrate_caching_performance():
    """Demonstrate the performance benefits of caching."""
    
    print("=== Pipeline Performance Comparison ===\n")
    
    # Create sample blocks with some duplicate content
    sample_blocks = [
        Block(uuid="1", content="This is great content that's really amazing!"),
        Block(uuid="2", content="This is terrible content that's really awful!"),
        Block(uuid="3", content="This is great content that's really amazing!"),  # Duplicate
        Block(uuid="4", content="Neutral content with no strong sentiment words."),
        Block(uuid="5", content="This is terrible content that's really awful!"),  # Duplicate
        Block(uuid="6", content="More great and excellent content for analysis!"),
        Block(uuid="7", content="This is great content that's really amazing!"),  # Duplicate
    ]
    
    # Test 1: Without caching
    print("Test 1: Processing without caching...")
    start_time = time.time()
    
    extractor = MockContentExtractor("basic_extractor", delay=0.05)
    analyzer = MockContentAnalyzer("sentiment_analyzer", delay=0.1)
    
    results_no_cache = []
    for block in sample_blocks:
        extracted = extractor.extract(block)
        analyzed = analyzer.analyze(block.content)
        results_no_cache.append({
            'block_id': block.uuid,
            'extracted': extracted,
            'analyzed': analyzed
        })
    
    no_cache_time = time.time() - start_time
    print(f"Time without caching: {no_cache_time:.2f}s")
    print(f"Extractor calls: {extractor.call_count}")
    print(f"Analyzer calls: {analyzer.call_count}\n")
    
    # Test 2: With memory caching
    print("Test 2: Processing with memory caching...")
    start_time = time.time()
    
    # Create cache and wrapped components
    cache = create_memory_cache(max_size=1000)
    cached_extractor = CachedExtractor(MockContentExtractor("cached_extractor", delay=0.05), cache)
    cached_analyzer = CachedAnalyzer(MockContentAnalyzer("cached_sentiment_analyzer", delay=0.1), cache)
    
    results_with_cache = []
    for block in sample_blocks:
        extracted = cached_extractor.extract(block)
        analyzed = cached_analyzer.analyze(block.content)
        results_with_cache.append({
            'block_id': block.uuid,
            'extracted': extracted,
            'analyzed': analyzed
        })
    
    cache_time = time.time() - start_time
    print(f"Time with caching: {cache_time:.2f}s")
    print(f"Extractor calls: {cached_extractor.extractor.call_count}")
    print(f"Analyzer calls: {cached_analyzer.analyzer.call_count}")
    
    # Show cache statistics
    stats = cache.get_stats()
    print(f"Cache hits: {stats['hits']}")
    print(f"Cache misses: {stats['misses']}")
    print(f"Hit rate: {stats['hit_rate']:.2%}")
    print(f"Performance improvement: {((no_cache_time - cache_time) / no_cache_time) * 100:.1f}%\n")


async def demonstrate_persistent_caching():
    """Demonstrate persistent caching with SQLite."""
    
    print("=== Persistent Caching Demonstration ===\n")
    
    # Create a temporary cache file
    cache_file = Path.home() / ".logseq-python" / "demo_cache.db"
    cache_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Create sample content
    content = "This is excellent content that demonstrates persistent caching capabilities!"
    extractor_name = "demo_extractor"
    analyzer_name = "demo_analyzer"
    
    print("Creating SQLite cache...")
    cache = create_sqlite_cache(str(cache_file))
    
    # Simulate expensive extraction and analysis
    print("Performing expensive extraction and analysis...")
    extraction_result = {
        'extracted_text': content[:50],
        'word_count': len(content.split()),
        'complexity_score': 0.75,
        'timestamp': time.time()
    }
    
    analysis_result = {
        'sentiment': 'positive',
        'confidence': 0.9,
        'key_phrases': ['excellent content', 'persistent caching', 'capabilities'],
        'timestamp': time.time()
    }
    
    # Cache the results
    cache.cache_extracted_content(content, extractor_name, extraction_result)
    cache.cache_analysis_result(content, analyzer_name, analysis_result)
    
    print("Results cached successfully!")
    print(f"Cache stats: {cache.get_stats()}")
    
    # Simulate new session - create new cache instance
    print("\nSimulating new session with fresh cache instance...")
    cache2 = create_sqlite_cache(str(cache_file))
    
    # Retrieve cached results
    cached_extraction = cache2.get_extracted_content(content, extractor_name)
    cached_analysis = cache2.get_analysis_result(content, analyzer_name)
    
    if cached_extraction and cached_analysis:
        print("✓ Successfully retrieved cached results from persistent storage!")
        print(f"Cached extraction: {cached_extraction}")
        print(f"Cached analysis: {cached_analysis}")
        
        stats = cache2.get_stats()
        print(f"New session cache stats: {stats}")
    else:
        print("✗ Failed to retrieve cached results")
    
    # Cleanup
    cache_file.unlink(missing_ok=True)


async def demonstrate_async_pipeline_with_caching():
    """Demonstrate async pipeline with caching integration."""
    
    print("=== Async Pipeline with Caching ===\n")
    
    # Create cache
    cache = create_memory_cache(max_size=500)
    
    # Create sample blocks
    blocks = [
        Block(uuid=f"block_{i}", content=f"Sample content block {i} with various sentiments.")
        for i in range(1, 21)  # 20 blocks
    ]
    
    # Add some duplicate content to demonstrate caching benefits
    blocks.extend([
        Block(uuid="dup1", content="Sample content block 5 with various sentiments."),
        Block(uuid="dup2", content="Sample content block 10 with various sentiments."),
        Block(uuid="dup3", content="Sample content block 15 with various sentiments."),
    ])
    
    print(f"Processing {len(blocks)} blocks...")
    
    # Create cached components
    cached_extractor = CachedExtractor(
        MockContentExtractor("async_extractor", delay=0.02), 
        cache
    )
    cached_analyzer = CachedAnalyzer(
        MockContentAnalyzer("async_analyzer", delay=0.05), 
        cache
    )
    
    # Async processing function
    async def process_block(block: Block) -> Dict[str, Any]:
        # Simulate async extraction and analysis
        extracted = cached_extractor.extract(block)
        analyzed = cached_analyzer.analyze(block.content)
        
        return {
            'block_id': block.uuid,
            'extracted': extracted,
            'analyzed': analyzed
        }
    
    # Process with batch processor for controlled concurrency
    batch_processor = AsyncBatchProcessor(max_concurrent=5, batch_size=10)
    
    start_time = time.time()
    
    async def process_batch(batch):
        tasks = [process_block(block) for block in batch]
        return await asyncio.gather(*tasks)
    
    all_results = []
    async for batch_results in batch_processor.process_batches(blocks, process_batch):
        all_results.extend(batch_results)
    
    processing_time = time.time() - start_time
    
    print(f"Processed {len(all_results)} blocks in {processing_time:.2f}s")
    print(f"Average time per block: {processing_time / len(blocks):.3f}s")
    
    # Show caching benefits
    stats = cache.get_stats()
    print(f"\nCaching statistics:")
    print(f"Total requests: {stats['total_requests']}")
    print(f"Cache hits: {stats['hits']}")
    print(f"Cache misses: {stats['misses']}")
    print(f"Hit rate: {stats['hit_rate']:.2%}")
    print(f"Cache size: {stats['size']} entries")


async def demonstrate_cache_management():
    """Demonstrate cache management and optimization features."""
    
    print("=== Cache Management Demonstration ===\n")
    
    # Create cache with small size to demonstrate eviction
    cache = create_memory_cache(max_size=5)
    
    # Add content beyond cache capacity
    print("Adding content beyond cache capacity...")
    
    for i in range(10):
        content = f"Content item {i} with unique data"
        result = {'processed': True, 'item': i, 'timestamp': time.time()}
        
        cache.cache_extracted_content(content, "test_extractor", result)
        
        stats = cache.get_stats()
        print(f"Added item {i}: Cache size = {stats['size']}")
    
    print(f"\nFinal cache size: {cache.get_stats()['size']} (max: 5)")
    
    # Demonstrate TTL expiration
    print("\nDemonstrating TTL expiration...")
    temp_cache = create_memory_cache()
    
    # Add item with short TTL
    temp_cache.backend.set("short_lived", "data", ttl=0.1)
    print(f"Item exists: {temp_cache.backend.get('short_lived') is not None}")
    
    # Wait for expiration
    await asyncio.sleep(0.15)
    print(f"After TTL expiration: {temp_cache.backend.get('short_lived') is not None}")
    
    # Demonstrate pattern-based key retrieval
    print("\nDemonstrating pattern-based operations...")
    pattern_cache = create_memory_cache()
    
    # Add items with different patterns
    for category in ['user', 'post', 'comment']:
        for i in range(3):
            key = f"{category}:{i}"
            pattern_cache.backend.set(key, f"{category}_data_{i}")
    
    all_keys = pattern_cache.backend.keys("*")
    user_keys = pattern_cache.backend.keys("user:*")
    
    print(f"All keys: {all_keys}")
    print(f"User keys: {user_keys}")


async def main():
    """Run all demonstrations."""
    
    print("Logseq Python - Caching System Demonstration")
    print("=" * 50)
    
    try:
        await demonstrate_caching_performance()
        print("\n" + "="*50 + "\n")
        
        await demonstrate_persistent_caching()
        print("\n" + "="*50 + "\n")
        
        await demonstrate_async_pipeline_with_caching()
        print("\n" + "="*50 + "\n")
        
        await demonstrate_cache_management()
        
        print("\nAll demonstrations completed successfully!")
        
    except Exception as e:
        print(f"Error during demonstration: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())