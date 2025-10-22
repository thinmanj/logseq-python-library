#!/usr/bin/env python3
"""
Comprehensive Content Processing CLI for Logseq

Command-line interface for the enhanced content processor that handles
videos, X/Twitter posts, and PDFs with property-based organization.

Usage:
    python comprehensive_processor_cli.py /path/to/logseq/graph [options]

Examples:
    # Basic run with dry run mode
    python comprehensive_processor_cli.py /Volumes/Projects/logseq/Test --dry-run
    
    # Full processing with API keys
    python comprehensive_processor_cli.py /Volumes/Projects/logseq/Test \
        --youtube-api-key YOUR_YOUTUBE_KEY --twitter-bearer-token YOUR_TWITTER_TOKEN
    
    # Process only specific content types
    python comprehensive_processor_cli.py /Volumes/Projects/logseq/Test \
        --no-videos --process-pdfs
"""

import argparse
import json
import logging
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path so we can import logseq_py
sys.path.insert(0, str(Path(__file__).parent.parent))

from logseq_py.pipeline.comprehensive_processor import ComprehensiveContentProcessor


def setup_logging(log_level: str, log_file: str = None):
    """Set up logging configuration."""
    level = getattr(logging, log_level.upper())
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    
    # Root logger setup
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.addHandler(console_handler)
    
    # File handler if specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)


def create_config(args) -> dict:
    """Create configuration dictionary from CLI arguments."""
    config = {
        'dry_run': args.dry_run,
        'youtube_api_key': args.youtube_api_key,
        'twitter_bearer_token': args.twitter_bearer_token,
        'property_prefix': args.property_prefix,
        'min_subtitle_length': args.min_subtitle_length,
        'max_topics_per_item': args.max_topics,
        'backup_enabled': not args.no_backup,
        'process_videos': not args.no_videos,
        'process_twitter': not args.no_twitter,
        'process_pdfs': not args.no_pdfs
    }
    
    # Remove None values
    return {k: v for k, v in config.items() if v is not None}


def print_report(result: dict):
    """Print a formatted processing report."""
    print("\n" + "="*60)
    print("🎯 COMPREHENSIVE CONTENT PROCESSING REPORT")
    print("="*60)
    
    if not result.get('success'):
        print(f"❌ FAILED: {result.get('error', 'Unknown error')}")
        return
    
    print("✅ SUCCESS")
    print(f"📁 Graph: {result['graph_path']}")
    print(f"🕐 Time: {result['processing_time'][:19]}")  # Remove microseconds
    
    stats = result.get('stats', {})
    print(f"\n📊 STATISTICS:")
    print(f"   • Blocks processed: {stats.get('blocks_processed', 0):,}")
    
    # Content found
    videos_found = stats.get('videos_found', 0)
    tweets_found = stats.get('tweets_found', 0)
    pdfs_found = stats.get('pdfs_found', 0)
    total_found = videos_found + tweets_found + pdfs_found
    
    print(f"   • Total content items found: {total_found:,}")
    if videos_found > 0:
        print(f"     - Videos: {videos_found:,}")
    if tweets_found > 0:
        print(f"     - X/Twitter posts: {tweets_found:,}")
    if pdfs_found > 0:
        print(f"     - PDFs: {pdfs_found:,}")
    
    # Content enhanced
    videos_enhanced = stats.get('videos_enhanced', 0)
    tweets_enhanced = stats.get('tweets_enhanced', 0)
    pdfs_enhanced = stats.get('pdfs_enhanced', 0)
    total_enhanced = videos_enhanced + tweets_enhanced + pdfs_enhanced
    
    print(f"   • Total items enhanced: {total_enhanced:,}")
    if videos_enhanced > 0:
        print(f"     - Videos: {videos_enhanced:,}")
    if tweets_enhanced > 0:
        print(f"     - X/Twitter posts: {tweets_enhanced:,}")
    if pdfs_enhanced > 0:
        print(f"     - PDFs: {pdfs_enhanced:,}")
    
    # Other stats
    print(f"   • Subtitles extracted: {stats.get('subtitles_extracted', 0):,}")
    print(f"   • Properties added: {stats.get('properties_added', 0):,}")
    print(f"   • Topic pages created: {stats.get('topic_pages_created', 0):,}")
    
    if stats.get('errors', 0) > 0:
        print(f"   ⚠️  Errors: {stats['errors']:,}")
    
    print("\n" + "="*60)


def main():
    parser = argparse.ArgumentParser(
        description="Process video, X/Twitter, and PDF content in Logseq graphs",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s /path/to/logseq/Test --dry-run
  %(prog)s /path/to/logseq/Test --youtube-api-key YOUR_KEY
  %(prog)s /path/to/logseq/Test --max-topics 3 --property-prefix topic
  %(prog)s /path/to/logseq/Test --no-videos --process-pdfs
        """
    )
    
    # Required arguments
    parser.add_argument(
        'graph_path',
        help='Path to the Logseq graph directory'
    )
    
    # Processing options
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Run in dry-run mode (no files will be modified)'
    )
    
    parser.add_argument(
        '--youtube-api-key',
        help='YouTube Data API key for enhanced subtitle extraction'
    )
    
    parser.add_argument(
        '--twitter-bearer-token',
        help='Twitter API Bearer Token for enhanced tweet extraction'
    )
    
    # Content type toggles
    parser.add_argument(
        '--no-videos',
        action='store_true',
        help='Skip video processing'
    )
    
    parser.add_argument(
        '--no-twitter',
        action='store_true',
        help='Skip X/Twitter processing'
    )
    
    parser.add_argument(
        '--no-pdfs',
        action='store_true',
        help='Skip PDF processing'
    )
    
    # Configuration options
    parser.add_argument(
        '--property-prefix',
        default='topic',
        help='Prefix for generated topic properties (default: topic)'
    )
    
    parser.add_argument(
        '--min-subtitle-length',
        type=int,
        default=100,
        help='Minimum subtitle length to process (default: 100)'
    )
    
    parser.add_argument(
        '--max-topics',
        type=int,
        default=3,
        help='Maximum topics to extract per content item (default: 3)'
    )
    
    parser.add_argument(
        '--no-backup',
        action='store_true',
        help='Disable automatic backup creation'
    )
    
    # Logging options
    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help='Logging level (default: INFO)'
    )
    
    parser.add_argument(
        '--log-file',
        help='Log to file in addition to console'
    )
    
    # Output options
    parser.add_argument(
        '--report-file',
        help='Save processing report to JSON file'
    )
    
    args = parser.parse_args()
    
    # Validate graph path
    graph_path = Path(args.graph_path)
    if not graph_path.exists():
        print(f"❌ Error: Graph path does not exist: {graph_path}")
        sys.exit(1)
    
    if not graph_path.is_dir():
        print(f"❌ Error: Graph path is not a directory: {graph_path}")
        sys.exit(1)
    
    # Check that at least one content type is enabled
    if args.no_videos and args.no_twitter and args.no_pdfs:
        print("❌ Error: At least one content type must be enabled")
        sys.exit(1)
    
    # Set up logging
    setup_logging(args.log_level, args.log_file)
    
    # Create configuration
    config = create_config(args)
    
    print("🚀 Starting Comprehensive Content Processing Pipeline")
    print(f"📁 Graph: {graph_path}")
    
    if args.dry_run:
        print("🔍 DRY RUN MODE - No files will be modified")
    
    # Show what content types will be processed
    content_types = []
    if config.get('process_videos', True):
        content_types.append("Videos")
    if config.get('process_twitter', True):
        content_types.append("X/Twitter")
    if config.get('process_pdfs', True):
        content_types.append("PDFs")
    
    print(f"📝 Processing: {', '.join(content_types)}")
    
    if config.get('youtube_api_key'):
        print("🔑 YouTube API key provided - Enhanced subtitle extraction enabled")
    if config.get('twitter_bearer_token'):
        print("🐦 Twitter Bearer token provided - Enhanced tweet extraction enabled")
    
    print(f"🏷️  Property prefix: {config.get('property_prefix', 'topic')}")
    print(f"📊 Max topics per item: {config.get('max_topics_per_item', 3)}")
    print()
    
    try:
        # Initialize and run the pipeline
        processor = ComprehensiveContentProcessor(str(graph_path), config)
        result = processor.run()
        
        # Print report
        print_report(result)
        
        # Save report to file if requested
        if args.report_file:
            with open(args.report_file, 'w') as f:
                json.dump(result, f, indent=2)
            print(f"📄 Report saved to: {args.report_file}")
        
        # Exit with appropriate code
        if result.get('success'):
            if result.get('stats', {}).get('errors', 0) > 0:
                print("⚠️  Completed with some errors")
                sys.exit(2)
            else:
                print("🎉 Processing completed successfully!")
                sys.exit(0)
        else:
            print("❌ Processing failed")
            sys.exit(1)
    
    except KeyboardInterrupt:
        print("\n⏹️  Processing interrupted by user")
        sys.exit(130)
    
    except Exception as e:
        logging.exception("Unexpected error during processing")
        print(f"💥 Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()