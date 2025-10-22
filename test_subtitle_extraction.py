#!/usr/bin/env python3
"""Test YouTube subtitle extraction."""

import logging
from logseq_py.pipeline.subtitle_extractor import YouTubeSubtitleExtractor

# Set up detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Test video URL
test_url = "https://www.youtube.com/watch?v=QdnxjYj1pS0"

print("=" * 80)
print(f"Testing subtitle extraction for: {test_url}")
print("=" * 80)

# Create extractor
extractor = YouTubeSubtitleExtractor()

# Try to extract subtitles
print("\nAttempting to extract subtitles...")
subtitles = extractor.extract_subtitles(test_url)

if subtitles:
    print(f"\n✅ SUCCESS! Extracted {len(subtitles)} characters")
    print(f"\nFirst 500 characters:")
    print("-" * 80)
    print(subtitles[:500])
    print("-" * 80)
    print(f"\nLast 500 characters:")
    print("-" * 80)
    print(subtitles[-500:])
    print("-" * 80)
else:
    print("\n❌ FAILED - No subtitles extracted")
    print("\nTrying to get video ID...")
    video_id = extractor._extract_video_id(test_url)
    print(f"Video ID: {video_id}")
    
    if video_id:
        print("\nTrying manual transcript API call...")
        try:
            from youtube_transcript_api import YouTubeTranscriptApi
            
            # List available transcripts
            print("\nListing available transcripts...")
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            
            print("Available transcripts:")
            for transcript in transcript_list:
                print(f"  - Language: {transcript.language}")
                print(f"    Code: {transcript.language_code}")
                print(f"    Auto-generated: {transcript.is_generated}")
                print()
                
        except Exception as e:
            print(f"Error: {e}")

print("=" * 80)
