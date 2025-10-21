#!/usr/bin/env python3
"""
Example: Video Processing Pipeline for Logseq

This example demonstrates how to use the video processing pipeline to:
1. Scan a Logseq graph for video URLs
2. Extract video metadata and subtitles
3. Enhance blocks with {{video}} syntax
4. Generate tags from video content
5. Create tagged pages with source information

The pipeline can process YouTube, Vimeo, TikTok, Twitch, and Dailymotion videos.
"""

import sys
import logging
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from logseq_py.pipeline.video_processor import VideoProcessingPipeline


def main():
    print("🎬 Video Processing Pipeline Example\n")
    
    # Example configuration
    graph_path = "/Volumes/Projects/logseq/Test"  # Your Logseq graph path
    
    config = {
        'dry_run': True,  # Set to False to actually modify files
        'youtube_api_key': None,  # Add your YouTube API key for enhanced features
        'tag_prefix': 'video-topic',
        'min_subtitle_length': 100,
        'max_tags_per_video': 5,
        'backup_enabled': True
    }
    
    print("Configuration:")
    for key, value in config.items():
        print(f"  {key}: {value}")
    print()
    
    # Set up logging to see what's happening
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    try:
        # Initialize the pipeline
        pipeline = VideoProcessingPipeline(graph_path, config)
        
        print("🚀 Running video processing pipeline...")
        print("   This will:")
        print("   1. 🔍 Scan all pages for video URLs")
        print("   2. 📹 Extract video metadata")
        print("   3. 📝 Extract subtitles (YouTube only)")
        print("   4. 🏷️  Analyze content for tags")
        print("   5. ✨ Enhance blocks with {{video}} syntax")
        print("   6. 📄 Create tagged pages")
        print()
        
        # Run the pipeline
        result = pipeline.run()
        
        # Display results
        if result['success']:
            print("✅ Pipeline completed successfully!")
            print("\n📊 Results:")
            stats = result['stats']
            print(f"   Blocks processed: {stats['blocks_processed']}")
            print(f"   Videos found: {stats['videos_found']}")
            print(f"   Videos enhanced: {stats['videos_enhanced']}")
            print(f"   Subtitles extracted: {stats['subtitles_extracted']}")
            print(f"   Tags created: {stats['tags_created']}")
            print(f"   Pages created: {stats['pages_created']}")
            
            if stats['errors'] > 0:
                print(f"   ⚠️  Errors: {stats['errors']}")
        else:
            print(f"❌ Pipeline failed: {result.get('error')}")
    
    except Exception as e:
        print(f"💥 Error running pipeline: {e}")
        import traceback
        traceback.print_exc()


def demonstrate_individual_features():
    """Demonstrate individual pipeline features."""
    print("\n" + "="*60)
    print("🔧 INDIVIDUAL FEATURE DEMONSTRATIONS")
    print("="*60)
    
    from logseq_py.pipeline.subtitle_extractor import YouTubeSubtitleExtractor, VideoContentAnalyzer
    from logseq_py.utils import LogseqUtils
    
    # 1. Video URL extraction
    print("\n1. 📹 Video URL Extraction")
    sample_text = """
    Here are some interesting videos I found:
    - https://www.youtube.com/watch?v=dQw4w9WgXcQ
    - https://vimeo.com/148751763
    - Some other content here
    - https://www.twitch.tv/videos/123456
    """
    
    video_urls = LogseqUtils.extract_video_urls(sample_text)
    print(f"Found {len(video_urls)} video URLs:")
    for url in video_urls:
        print(f"  • {url}")
    
    # 2. Video metadata extraction
    print("\n2. 📊 Video Metadata Extraction")
    for url in video_urls[:2]:  # Just test first 2
        info = LogseqUtils.get_video_info(url)
        if info:
            print(f"  {url}")
            print(f"    Title: {info.get('title', 'Unknown')}")
            print(f"    Author: {info.get('author_name', 'Unknown')}")
            print(f"    Platform: {info.get('platform', 'unknown')}")
        else:
            print(f"  {url} - Could not extract info")
    
    # 3. Content analysis
    print("\n3. 🏷️  Content Analysis")
    analyzer = VideoContentAnalyzer(max_tags=3)
    
    sample_subtitle = """
    Welcome to this tutorial on machine learning and artificial intelligence.
    Today we'll be covering neural networks, deep learning algorithms,
    and how to implement them in Python. We'll discuss data science
    techniques and show you how to build predictive models for
    business applications and research purposes.
    """
    
    tags = analyzer.extract_tags(sample_subtitle, "Machine Learning Tutorial")
    print(f"Extracted tags: {tags}")
    
    # 4. Subtitle extraction (requires youtube-transcript-api)
    print("\n4. 📝 Subtitle Extraction")
    extractor = YouTubeSubtitleExtractor()
    
    # This would only work with the actual library installed
    print("  Note: Subtitle extraction requires 'youtube-transcript-api' package")
    print("  Install with: pip install youtube-transcript-api")
    print("  Then subtitles can be extracted from YouTube videos")


if __name__ == "__main__":
    print("Choose an option:")
    print("1. Run full pipeline example")
    print("2. Demonstrate individual features")
    print("3. Both")
    
    choice = input("Enter choice (1/2/3): ").strip()
    
    if choice in ['1', '3']:
        main()
    
    if choice in ['2', '3']:
        demonstrate_individual_features()
    
    print("\n🎉 Example completed!")
    print("\nTo run the pipeline on your actual Logseq graph:")
    print("python scripts/video_processor_cli.py /path/to/your/logseq/graph --dry-run")