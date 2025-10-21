#!/usr/bin/env python3
"""
Example: Video Title Extraction

This example demonstrates how to extract video titles and information
from various video platform URLs using logseq-py.

Supported platforms:
- YouTube
- Vimeo  
- TikTok
- Twitch
- Dailymotion
"""

from logseq_py import LogseqUtils

def main():
    print("🎬 Video Title Extraction Example\n")
    
    # Example URLs from different platforms
    video_urls = [
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",  # Classic Rick Roll
        "https://youtu.be/dQw4w9WgXcQ",                 # Short YouTube URL
        "https://vimeo.com/148751763",                   # Vimeo example
        "https://www.dailymotion.com/video/x2jvvep",    # Dailymotion example
    ]
    
    print("1. Extract video titles from individual URLs:")
    print("-" * 50)
    
    for url in video_urls:
        print(f"\nURL: {url}")
        title = LogseqUtils.get_video_title(url)
        if title:
            print(f"✓ Title: {title}")
        else:
            print("✗ Could not extract title")
    
    print("\n\n2. Get comprehensive video information:")
    print("-" * 50)
    
    # Get detailed info for YouTube video
    youtube_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    print(f"\nDetailed info for: {youtube_url}")
    
    video_info = LogseqUtils.get_video_info(youtube_url)
    if video_info:
        print(f"✓ Title: {video_info.get('title', 'N/A')}")
        print(f"✓ Author: {video_info.get('author_name', 'N/A')}")
        print(f"✓ Duration: {video_info.get('duration', 'N/A')}")
        print(f"✓ Platform: {video_info.get('platform', 'youtube')}")
        print(f"✓ Status: {video_info.get('status', 'N/A')}")
        
        if 'view_count' in video_info:
            print(f"✓ Views: {video_info['view_count']:,}")
        if 'published_at' in video_info:
            print(f"✓ Published: {video_info['published_at']}")
    else:
        print("✗ Could not extract video information")
    
    print("\n\n3. Extract video URLs from text:")
    print("-" * 50)
    
    text_with_videos = \"\"\"
    Check out these awesome videos:
    - https://www.youtube.com/watch?v=dQw4w9WgXcQ
    - Here's a Vimeo link: https://vimeo.com/148751763
    - And a TikTok: https://www.tiktok.com/@username/video/1234567890
    Some regular text here...
    - Dailymotion: https://www.dailymotion.com/video/x2jvvep
    \"\"\"
    
    video_urls_found = LogseqUtils.extract_video_urls(text_with_videos)
    print(f"Found {len(video_urls_found)} video URLs:")
    for url in video_urls_found:
        print(f"  • {url}")
    
    print("\n\n4. Get multiple video titles at once:")
    print("-" * 50)
    
    multiple_titles = LogseqUtils.get_multiple_video_titles(video_urls_found)
    for url, title in multiple_titles.items():
        print(f"\n{url}")
        if title:
            print(f"  → {title}")
        else:
            print(f"  → (Could not extract title)")
    
    print("\n\n5. Using with YouTube API key (optional):")
    print("-" * 50)
    
    # If you have a YouTube Data API key, you can get enhanced information
    # Uncomment and add your API key to test this:
    
    # youtube_api_key = "YOUR_YOUTUBE_API_KEY_HERE"
    # enhanced_info = LogseqUtils.get_video_info(youtube_url, youtube_api_key)
    # if enhanced_info and 'description' in enhanced_info:
    #     print(f"✓ Description: {enhanced_info['description'][:100]}...")
    #     print(f"✓ Channel: {enhanced_info.get('channel_title', 'N/A')}")
    #     print(f"✓ Tags: {enhanced_info.get('tags', [])}")
    
    print("ℹ️  To get enhanced YouTube data (description, tags, etc.), ")
    print("   provide a YouTube Data API key to get_video_info()")
    
    print("\n🎉 Video title extraction complete!")

if __name__ == "__main__":
    main()