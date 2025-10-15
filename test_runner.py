#!/usr/bin/env python3
"""
Simple test runner to verify the logseq-python implementation.
"""

import sys
import traceback
from pathlib import Path

# Add the current directory to path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Test that all modules import correctly."""
    print("Testing imports...")
    
    try:
        # Test core models
        from logseq_py.models import Block, Page
        print("  ✓ Core models imported")
        
        # Test pipeline components
        from logseq_py.pipeline import (
            create_pipeline, ProcessingContext, 
            analyze_content, extract_from_block
        )
        print("  ✓ Pipeline core imported")
        
        from logseq_py.pipeline.filters import create_task_filter, create_content_filter
        print("  ✓ Pipeline filters imported")
        
        from logseq_py.pipeline.analyzers import SentimentAnalyzer, TopicAnalyzer
        print("  ✓ Pipeline analyzers imported")
        
        from logseq_py.pipeline.generators import SummaryPageGenerator
        print("  ✓ Pipeline generators imported")
        
        return True
        
    except Exception as e:
        print(f"  ✗ Import error: {e}")
        traceback.print_exc()
        return False


def test_models():
    """Test basic model functionality."""
    print("Testing models...")
    
    try:
        from logseq_py.models import Block, Page
        
        # Test block creation
        block = Block(content="Test content", properties={"type": "test"})
        assert block.content == "Test content"
        assert block.properties["type"] == "test"
        print("  ✓ Block creation works")
        
        # Test page creation
        page = Page(name="Test Page", blocks=[block])
        assert page.name == "Test Page"
        assert len(page.blocks) == 1
        print("  ✓ Page creation works")
        
        return True
        
    except Exception as e:
        print(f"  ✗ Model test error: {e}")
        traceback.print_exc()
        return False


def test_analyzers():
    """Test analyzer functionality."""
    print("Testing analyzers...")
    
    try:
        from logseq_py.pipeline.analyzers import analyze_content
        
        # Test sentiment analysis
        text = "I love this fantastic product!"
        results = analyze_content(text, ['sentiment'])
        
        assert 'sentiment' in results
        assert results['sentiment']['sentiment'] == 'positive'
        print("  ✓ Sentiment analysis works")
        
        # Test topic analysis
        tech_text = "Python programming software development"
        results = analyze_content(tech_text, ['topics'])
        
        assert 'topics' in results
        topics = [t['topic'] for t in results['topics']['topics']]
        assert 'technology' in topics
        print("  ✓ Topic analysis works")
        
        return True
        
    except Exception as e:
        print(f"  ✗ Analyzer test error: {e}")
        traceback.print_exc()
        return False


def test_filters():
    """Test filter functionality."""
    print("Testing filters...")
    
    try:
        from logseq_py.models import Block
        from logseq_py.pipeline.filters import create_task_filter, create_content_filter
        
        # Test task filter
        task_block = Block(content="TODO: Complete project")
        regular_block = Block(content="Just a note")
        
        task_filter = create_task_filter()
        assert task_filter.matches(task_block) is True
        assert task_filter.matches(regular_block) is False
        print("  ✓ Task filter works")
        
        # Test content filter
        url_block = Block(content="Visit https://example.com")
        text_block = Block(content="No links here")
        
        url_filter = create_content_filter(pattern=r'https?://')
        assert url_filter.matches(url_block) is True
        assert url_filter.matches(text_block) is False
        print("  ✓ Content filter works")
        
        return True
        
    except Exception as e:
        print(f"  ✗ Filter test error: {e}")
        traceback.print_exc()
        return False


def test_extractors():
    """Test extractor functionality."""
    print("Testing extractors...")
    
    try:
        from logseq_py.models import Block
        from logseq_py.pipeline.extractors import YouTubeExtractor, URLExtractor
        
        # Test YouTube extractor
        youtube_block = Block(content="Check this video: https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        youtube_extractor = YouTubeExtractor()
        
        assert youtube_extractor.can_extract(youtube_block) is True
        print("  ✓ YouTube extractor detection works")
        
        # Test URL extractor
        url_block = Block(content="Visit https://example.com for info")
        url_extractor = URLExtractor()
        
        assert url_extractor.can_extract(url_block) is True
        print("  ✓ URL extractor detection works")
        
        return True
        
    except Exception as e:
        print(f"  ✗ Extractor test error: {e}")
        traceback.print_exc()
        return False


def test_pipeline():
    """Test basic pipeline functionality."""
    print("Testing pipeline...")
    
    try:
        from logseq_py.pipeline import create_pipeline, ProcessingContext
        from logseq_py.pipeline.steps import ReportProgressStep
        from logseq_py.models import Block
        
        # Create a simple pipeline
        pipeline = (create_pipeline("test_pipeline", "Test pipeline")
                   .step(ReportProgressStep())
                   .build())
        
        # Create context with sample data
        context = ProcessingContext(graph_path="/tmp/test")
        context.blocks = [Block(content="Test block")]
        context.total_items = 1
        
        # Execute pipeline
        result = pipeline.execute(context)
        
        assert result is not None
        print("  ✓ Basic pipeline execution works")
        
        return True
        
    except Exception as e:
        print(f"  ✗ Pipeline test error: {e}")
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("🧪 Running logseq-python implementation tests...\n")
    
    tests = [
        test_imports,
        test_models,
        test_analyzers,
        test_filters,
        test_extractors,
        test_pipeline
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"  ✗ Test failed with exception: {e}")
        print()
    
    print(f"📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The implementation is working correctly.")
        return 0
    else:
        print("❌ Some tests failed. Check the output above for details.")
        return 1


if __name__ == "__main__":
    sys.exit(main())