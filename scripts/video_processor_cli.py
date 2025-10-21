#!/usr/bin/env python3
"""
Video Processing CLI for Logseq

Command-line interface for running the video processing pipeline
that enhances Logseq graphs with video content analysis.

Usage:
    python video_processor_cli.py /path/to/logseq/graph [options]

Examples:
    # Basic run with dry run mode
    python video_processor_cli.py /Volumes/Projects/logseq/Test --dry-run
    
    # Full processing with YouTube API key
    python video_processor_cli.py /Volumes/Projects/logseq/Test --youtube-api-key YOUR_KEY
    
    # Custom configuration
    python video_processor_cli.py /Volumes/Projects/logseq/Test --max-tags 3 --tag-prefix topic
"""

import argparse
import json
import logging
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path so we can import logseq_py
sys.path.insert(0, str(Path(__file__).parent.parent))

from logseq_py.pipeline.video_processor import VideoProcessingPipeline


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
        'tag_prefix': args.tag_prefix,
        'min_subtitle_length': args.min_subtitle_length,
        'max_tags_per_video': args.max_tags,
        'backup_enabled': not args.no_backup
    }
    
    # Remove None values
    return {k: v for k, v in config.items() if v is not None}


def print_report(result: dict):
    """Print a formatted processing report."""
    print("\n" + "="*60)
    print("📹 VIDEO PROCESSING REPORT")
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
    print(f"   • Videos found: {stats.get('videos_found', 0):,}")
    print(f"   • Videos enhanced: {stats.get('videos_enhanced', 0):,}")
    print(f"   • Subtitles extracted: {stats.get('subtitles_extracted', 0):,}")
    print(f"   • Tags created: {stats.get('tags_created', 0):,}")
    print(f"   • Pages created: {stats.get('pages_created', 0):,}")
    
    if stats.get('errors', 0) > 0:
        print(f"   ⚠️  Errors: {stats['errors']:,}")
    
    print("\n" + "="*60)


def main():
    parser = argparse.ArgumentParser(
        description="Process video content in Logseq graphs",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s /path/to/logseq/Test --dry-run
  %(prog)s /path/to/logseq/Test --youtube-api-key YOUR_KEY
  %(prog)s /path/to/logseq/Test --max-tags 3 --tag-prefix topic
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
    
    # Configuration options
    parser.add_argument(
        '--tag-prefix',
        default='video-topic',
        help='Prefix for generated tag pages (default: video-topic)'
    )
    
    parser.add_argument(
        '--min-subtitle-length',
        type=int,
        default=100,
        help='Minimum subtitle length to process (default: 100)'
    )
    
    parser.add_argument(
        '--max-tags',
        type=int,
        default=5,
        help='Maximum tags to extract per video (default: 5)'
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
    
    # Set up logging
    setup_logging(args.log_level, args.log_file)
    
    # Create configuration
    config = create_config(args)
    
    print("🚀 Starting Logseq Video Processing Pipeline")
    print(f"📁 Graph: {graph_path}")
    
    if args.dry_run:
        print("🔍 DRY RUN MODE - No files will be modified")
    
    if config.get('youtube_api_key'):
        print("🔑 YouTube API key provided - Enhanced subtitle extraction enabled")
    else:
        print("ℹ️  No YouTube API key - Using basic subtitle extraction")
    
    print(f"🏷️  Tag prefix: {config.get('tag_prefix', 'video-topic')}")
    print(f"📊 Max tags per video: {config.get('max_tags_per_video', 5)}")
    print()
    
    try:
        # Initialize and run the pipeline
        pipeline = VideoProcessingPipeline(str(graph_path), config)
        result = pipeline.run()
        
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