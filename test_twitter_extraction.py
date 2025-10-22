#!/usr/bin/env python3
"""Test Twitter content extraction."""

import logging
from logseq_py.pipeline.enhanced_extractors import XTwitterExtractor

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s - %(message)s')

# Test URL
test_url = "https://x.com/elonmusk/status/1234567890"  # Example URL

print("=" * 80)
print(f"Testing Twitter extraction for: {test_url}")
print("=" * 80)

# Create extractor
extractor = XTwitterExtractor()

# Extract tweet info
tweet_info = extractor.extract_tweet_info(test_url)

if tweet_info:
    print("\n✅ SUCCESS! Extracted tweet info:")
    print("-" * 80)
    print(f"Title: {tweet_info.get('title')}")
    print(f"Author: {tweet_info.get('author')}")
    print(f"Username: {tweet_info.get('username')}")
    print(f"Content: {tweet_info.get('content', 'NO CONTENT EXTRACTED')}")
    print(f"Data Source: {tweet_info.get('data_source')}")
    
    if tweet_info.get('embedded_urls'):
        print(f"\nEmbedded URLs ({len(tweet_info['embedded_urls'])}):")
        for url in tweet_info['embedded_urls']:
            print(f"  - {url}")
    print("-" * 80)
else:
    print("\n❌ FAILED - No tweet info extracted")

print("=" * 80)
