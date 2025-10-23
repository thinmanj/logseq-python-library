#!/usr/bin/env python3
"""
Async Content Processor Script

Processes logseq graphs with async rate-limited queue system for
enhanced video, Twitter, and PDF content extraction.

Usage:
    python run_async_processor.py [graph_name] [base_path]
    
Examples:
    python run_async_processor.py Test
    python run_async_processor.py Learning ~/Documents/logseq
"""

import sys
import logging
import os
from pathlib import Path
import time

# Setup logging
logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

from logseq_py.pipeline.async_comprehensive_processor import AsyncComprehensiveContentProcessor

# Default base path can be overridden by environment variable
DEFAULT_BASE_PATH = os.environ.get(
    'LOGSEQ_BASE_PATH',
    str(Path.home() / "Library/Mobile Documents/iCloud~com~logseq~logseq/Documents")
)


def get_graph_path(graph_name: str, base_path: str = None) -> Path:
    """Get the full path to a logseq graph.
    
    Args:
        graph_name: Name of the graph (e.g., 'Test', 'Learning')
        base_path: Base path to logseq graphs. If None, uses DEFAULT_BASE_PATH
        
    Returns:
        Path to the graph directory
    """
    if base_path is None:
        base_path = DEFAULT_BASE_PATH
    
    base_path = Path(base_path).expanduser()
    graph_path = base_path / graph_name
    
    if not graph_path.exists():
        raise ValueError(f"Graph not found: {graph_path}")
    
    return graph_path


def format_time(seconds: float) -> str:
    """Format seconds into human-readable time."""
    minutes = int(seconds / 60)
    secs = int(seconds % 60)
    if minutes > 0:
        return f"{minutes}m {secs}s"
    return f"{secs}s"


def run_processor(graph_name: str, base_path: str = None, config: dict = None):
    """Run the async processor on a graph.
    
    Args:
        graph_name: Name of the graph to process
        base_path: Base path to logseq graphs directory
        config: Optional configuration dict
    """
    # Get graph path
    try:
        graph_path = get_graph_path(graph_name, base_path)
    except ValueError as e:
        print(f"✗ Error: {e}")
        return
    
    # Default configuration
    default_config = {
        'enable_async': True,
        'max_concurrent': 8,
        'retry_delay': 30,
        'dry_run': False,
        'backup_enabled': True,
        'process_videos': True,
        'process_twitter': True,
        'process_pdfs': True,
        'min_subtitle_length': 100,
        'max_topics_per_item': 3,
        'batch_size': 0,  # 0 = process all
        'batch_offset': 0,
        'streaming_mode': True
    }
    
    # Merge with provided config
    if config:
        default_config.update(config)
    
    config = default_config
    
    # Print header
    print("=" * 70)
    print(f"Async Content Processor - {graph_name}")
    print("=" * 70)
    print()
    print("Configuration:")
    print(f"  Graph: {graph_name}")
    print(f"  Path: {graph_path}")
    print(f"  Workers: {config['max_concurrent']}")
    print(f"  Backup: {'Enabled' if config['backup_enabled'] else 'Disabled'}")
    batch_text = 'ALL blocks' if config['batch_size'] == 0 else f"{config['batch_size']} blocks"
    print(f"  Batch: {batch_text}")
    print()
    print("Processing:")
    print(f"  Videos: {'✓' if config['process_videos'] else '✗'}")
    print(f"  Twitter: {'✓' if config['process_twitter'] else '✗'}")
    print(f"  PDFs: {'✓' if config['process_pdfs'] else '✗'}")
    print()
    print("⏱️  Processing in progress...")
    print()
    
    # Run processor
    processor = AsyncComprehensiveContentProcessor(str(graph_path), config)
    start_time = time.time()
    
    try:
        results = processor.run()
        elapsed = time.time() - start_time
        
        # Print results
        print()
        print("=" * 70)
        print("✓ PROCESSING COMPLETE")
        print("=" * 70)
        print()
        print(f"⏱️  Time: {format_time(elapsed)}")
        print()
        
        if 'stats' in results:
            stats = results['stats']
            print("📊 Content Stats:")
            print(f"  Blocks processed: {stats.get('blocks_processed', 0):,}")
            print(f"  Videos enhanced: {stats.get('videos_enhanced', 0):,} / {stats.get('videos_found', 0):,}")
            print(f"  Tweets enhanced: {stats.get('tweets_enhanced', 0):,} / {stats.get('tweets_found', 0):,}")
            print(f"  PDFs enhanced: {stats.get('pdfs_enhanced', 0):,} / {stats.get('pdfs_found', 0):,}")
            print(f"  Subtitles extracted: {stats.get('subtitles_extracted', 0):,}")
            print(f"  Topic pages created: {stats.get('topic_pages_created', 0):,}")
            if stats.get('errors', 0) > 0:
                print(f"  ⚠️  Errors: {stats.get('errors', 0):,}")
            print()
        
        if 'async_stats' in results:
            astats = results['async_stats']
            print("⚡ Async Performance:")
            print(f"  Total tasks: {astats.get('total_tasks', 0):,}")
            print(f"  Completed: {astats.get('completed', 0):,}")
            print(f"  Failed: {astats.get('failed', 0):,}")
            print(f"  Rate limited (429): {astats.get('rate_limited', 0):,}")
            print(f"  Retried: {astats.get('retried', 0):,}")
            
            if elapsed > 0 and astats.get('total_tasks', 0) > 0:
                throughput = astats.get('total_tasks', 0) / elapsed
                avg_time = elapsed / astats.get('total_tasks', 0)
                print(f"  Throughput: {throughput:.2f} tasks/sec")
                print(f"  Avg task time: {avg_time:.2f}s")
            print()
        
        print(f"✓ {graph_name} graph enhanced!")
        print()
        print("Check your graph for:")
        print("  - Enhanced video blocks with metadata")
        print("  - Enhanced Twitter blocks with metadata")
        print("  - Topic pages (topic-*)")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        elapsed = time.time() - start_time
        print(f"Partial processing time: {format_time(elapsed)}")
        print("Changes made so far have been saved.")
        
    except Exception as e:
        print()
        print("=" * 70)
        print("✗ ERROR")
        print("=" * 70)
        print(f"Exception: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python run_async_processor.py [graph_name] [base_path]")
        print()
        print("Arguments:")
        print("  graph_name  Name of the graph to process")
        print("  base_path   Optional. Base path to logseq graphs directory")
        print(f"              Default: {DEFAULT_BASE_PATH}")
        print()
        print("Environment Variables:")
        print("  LOGSEQ_BASE_PATH  Set default base path for graphs")
        print()
        print("Examples:")
        print("  python run_async_processor.py Test")
        print("  python run_async_processor.py Learning ~/Documents/logseq")
        print("  LOGSEQ_BASE_PATH=~/docs python run_async_processor.py Test")
        print()
        
        # Try to list available graphs
        base_path = Path(DEFAULT_BASE_PATH)
        if base_path.exists():
            graphs = [d.name for d in base_path.iterdir() if d.is_dir() and not d.name.startswith('.')]
            if graphs:
                print("Available graphs:")
                for graph in sorted(graphs):
                    print(f"  - {graph}")
        
        sys.exit(1)
    
    graph_name = sys.argv[1]
    base_path = sys.argv[2] if len(sys.argv) > 2 else None
    run_processor(graph_name, base_path)


if __name__ == '__main__':
    main()
