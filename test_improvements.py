#!/usr/bin/env python3
"""Test script for improved comprehensive processor."""

import logging
from logseq_py.pipeline.enhanced_extractors import ContentAnalyzer

# Set up logging
logging.basicConfig(level=logging.INFO)

# Test the improved topic extraction
analyzer = ContentAnalyzer(max_topics=5)

# Test cases
test_cases = [
    {
        'title': 'Learn Python - Full Course for Beginners [Tutorial]',
        'content': 'This python tutorial for beginners teaches you python programming from scratch. Learn python fundamentals, data structures, functions, and more. Python is a powerful programming language used in data science and machine learning.',
        'platform': 'video'
    },
    {
        'title': 'Machine Learning Basics - Deep Learning Neural Networks',
        'content': 'Introduction to machine learning and deep learning. Learn about neural networks, training models, and artificial intelligence. We cover supervised learning, unsupervised learning, and reinforcement learning techniques.',
        'platform': 'video'
    },
    {
        'title': 'Attention is All you Need',
        'content': 'Abstract: The dominant sequence transduction models are based on complex recurrent or convolutional neural networks that include an encoder and a decoder. The best performing models also connect the encoder and decoder through an attention mechanism. We propose a new simple network architecture, the Transformer, based solely on attention mechanisms.',
        'platform': 'pdf'
    },
]

print("=" * 80)
print("TESTING IMPROVED TOPIC EXTRACTION")
print("=" * 80)

for i, test in enumerate(test_cases, 1):
    print(f"\n{'='*80}")
    print(f"TEST CASE {i}")
    print(f"{'='*80}")
    print(f"Title: {test['title']}")
    print(f"Platform: {test['platform']}")
    print(f"\nContent preview: {test['content'][:100]}...")
    
    topics = analyzer.extract_topics(
        test['content'],
        test['title'],
        test['platform']
    )
    
    print(f"\nExtracted Topics ({len(topics)}):")
    for j, topic in enumerate(topics, 1):
        print(f"  {j}. {topic}")
    print()

print("=" * 80)
print("TEST COMPLETE")
print("=" * 80)
