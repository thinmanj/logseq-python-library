#!/usr/bin/env python3
"""
Complete Pipeline System Demo

Demonstrates the full pipeline framework including content extraction,
analysis, and generation with real extractors, analyzers, and generators.
"""

import logging
from pathlib import Path
import sys
from datetime import datetime

# Add the project root to the path so we can import logseq_py
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from logseq_py.pipeline import (
    # Core components
    ProcessingContext, create_pipeline, ProcessingStatus,
    
    # Filters
    create_content_filter, create_task_filter, create_and_filter,
    
    # Steps
    LoadContentStep, FilterBlocksStep, ExtractContentStep,
    AnalyzeContentStep, GenerateContentStep, SaveResultsStep,
    ReportProgressStep,
    
    # Extractors
    URLExtractor, YouTubeExtractor, extract_from_block,
    
    # Analyzers
    analyze_content, SentimentAnalyzer, TopicAnalyzer,
    
    # Generators
    SummaryPageGenerator, InsightsBlockGenerator
)

from logseq_py.models import Block, Page


def setup_logging():
    """Setup logging for the demo."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('complete_pipeline_demo.log')
        ]
    )


def create_sample_blocks() -> list:
    """Create sample blocks for testing."""
    sample_blocks = [
        Block(
            content="TODO: Check out this amazing tutorial https://www.youtube.com/watch?v=dQw4w9WgXcQ about machine learning",
            properties={"type": "task", "priority": "high"}
        ),
        Block(
            content="I love working with this new Python framework! It's absolutely fantastic and makes development so much easier.",
            properties={"topic": "technology"}
        ),
        Block(
            content="The meeting was terrible and the project is failing badly. Nothing seems to work properly.",
            properties={"topic": "work"}
        ),
        Block(
            content="DONE: Implement the authentication system. This was a great learning experience.",
            properties={"type": "task", "completed": True}
        ),
        Block(
            content="Research paper on AI: https://arxiv.org/abs/1706.03762 - Attention is All You Need. Revolutionary work in transformers.",
            properties={"type": "research"}
        ),
        Block(
            content="GitHub repository for data analysis: https://github.com/pandas-dev/pandas - excellent library for data manipulation.",
            properties={"topic": "technology"}
        )
    ]
    
    return sample_blocks


def demo_individual_components():
    """Demonstrate individual pipeline components."""
    print("=== Individual Components Demo ===")
    
    # Test extractors
    print("\n--- Content Extraction ---")
    test_block = Block(content="Check out https://www.youtube.com/watch?v=dQw4w9WgXcQ and https://github.com/python/cpython")
    
    extraction_results = extract_from_block(test_block, ["youtube", "github", "url"])
    print(f"Extracted content from {len(extraction_results)} extractors")
    
    for extractor_name, result in extraction_results.items():
        if 'error' in result:
            print(f"  {extractor_name}: Error - {result['error']}")
        else:
            print(f"  {extractor_name}: {result.get('type', 'unknown')} - extracted successfully")
    
    # Test analyzers  
    print("\n--- Content Analysis ---")
    test_content = "I absolutely love this fantastic new technology! It's amazing and works perfectly."
    
    analysis_results = analyze_content(test_content, ["sentiment", "topics", "structure"])
    print(f"Analyzed content with {len(analysis_results)} analyzers")
    
    for analyzer_name, result in analysis_results.items():
        if 'error' in result:
            print(f"  {analyzer_name}: Error - {result['error']}")
        else:
            print(f"  {analyzer_name}: Analysis completed")
            if analyzer_name == 'sentiment':
                sentiment = result.get('sentiment')
                polarity = result.get('polarity', 0)
                print(f"    Sentiment: {sentiment} (polarity: {polarity:.2f})")
    
    # Test generators (requires context)
    print("\n--- Content Generation ---")
    context = ProcessingContext(graph_path="/tmp/test")
    context.blocks = create_sample_blocks()
    context.analysis_results = {
        'sentiment': {
            'results': [
                {'analysis': {'sentiment': 'positive', 'polarity': 0.8}},
                {'analysis': {'sentiment': 'negative', 'polarity': -0.6}},
                {'analysis': {'sentiment': 'positive', 'polarity': 0.9}}
            ],
            'count': 3
        }
    }
    
    generator = SummaryPageGenerator()
    if generator.can_generate(context):
        result = generator.generate(context)
        print(f"Generated summary page: {result['type']}")
        print(f"Page title: {result['title']}")


def demo_real_pipeline():
    """Demonstrate a complete real pipeline."""
    print("\n=== Complete Pipeline Demo ===")
    
    # Create context with sample data
    context = ProcessingContext(graph_path="/tmp/test")
    
    # Create sample pages with blocks
    sample_page = Page(
        name="Sample Content",
        blocks=create_sample_blocks(),
        properties={"created": datetime.now().isoformat()}
    )
    
    context.pages = [sample_page]
    context.blocks = sample_page.blocks
    context.total_items = len(context.blocks)
    
    # Create comprehensive pipeline
    pipeline = (create_pipeline("complete_demo", "Full feature demonstration pipeline")
                # Filter for content with URLs or tasks
                .step(FilterBlocksStep(create_content_filter(pattern=r'https?://|TODO|DONE')))
                
                # Extract content from URLs
                .step(ExtractContentStep(["url", "youtube", "github"]))
                
                # Analyze all content
                .step(AnalyzeContentStep(["sentiment", "topics", "summary", "structure"]))
                
                # Generate insights and summaries
                .step(GenerateContentStep(["summary_page", "insights_blocks", "task_analysis"]))
                
                # Report results
                .step(ReportProgressStep())
                
                .configure(continue_on_error=True, save_intermediate_state=True)
                .build())
    
    print(f"Created pipeline with {len(pipeline.steps)} steps")
    
    # Execute pipeline
    try:
        print("\nExecuting pipeline...")
        result_context = pipeline.execute(context)
        
        print(f"\n--- Pipeline Results ---")
        print(f"Processed: {result_context.processed_items}/{result_context.total_items} items")
        print(f"Errors: {len(result_context.errors)}")
        
        # Show extraction results
        if result_context.extracted_content:
            extracted_count = result_context.extracted_content.get('count', 0)
            print(f"Extracted: {extracted_count} content items")
            
            if 'items' in result_context.extracted_content:
                for item in result_context.extracted_content['items'][:3]:  # Show first 3
                    extractor = item.get('extractor')
                    content_type = item.get('content', {}).get('type', 'unknown')
                    print(f"  - {extractor}: {content_type}")
        
        # Show analysis results
        if result_context.analysis_results:
            print(f"Analysis results:")
            for analyzer, results in result_context.analysis_results.items():
                if isinstance(results, dict):
                    count = results.get('count', 0)
                    print(f"  - {analyzer}: {count} analyses")
        
        # Show generated content
        if result_context.generated_content:
            print(f"Generated content:")
            for generator, content in result_context.generated_content.items():
                if isinstance(content, dict):
                    content_type = content.get('type', 'unknown')
                    print(f"  - {generator}: {content_type}")
                    
                    # Show sample of summary page content
                    if generator == 'summary_page' and 'content' in content:
                        summary_lines = content['content'].split('\n')[:5]  # First 5 lines
                        print(f"    Preview: {summary_lines[0]}")
        
        print(f"\nPipeline completed successfully!")
        
    except Exception as e:
        print(f"Pipeline failed: {e}")
        import traceback
        traceback.print_exc()


def demo_custom_pipeline_with_filtering():
    """Demonstrate custom pipeline with advanced filtering."""
    print("\n=== Custom Pipeline with Advanced Filtering ===")
    
    context = ProcessingContext(graph_path="/tmp/test")
    
    # Create blocks with different characteristics
    mixed_blocks = [
        Block(content="TODO: Review the paper https://arxiv.org/abs/1706.03762", properties={"priority": "high"}),
        Block(content="This is just a regular note about daily life."),
        Block(content="DONE: Fixed the bug in authentication system", properties={"type": "task"}),
        Block(content="Check out this YouTube video: https://www.youtube.com/watch?v=dQw4w9WgXcQ"),
        Block(content="Meeting notes: The project is going well and we're making great progress."),
        Block(content="Repository link: https://github.com/microsoft/vscode - great editor!")
    ]
    
    context.blocks = mixed_blocks
    context.total_items = len(mixed_blocks)
    
    # Create pipeline focusing on task and URL content
    url_or_task_filter = create_content_filter(pattern=r'https?://|TODO|DONE')
    
    pipeline = (create_pipeline("filtered_demo", "Filtered content processing")
                .step(FilterBlocksStep(url_or_task_filter))
                .step(ExtractContentStep(["url", "youtube", "github"]))
                .step(AnalyzeContentStep(["sentiment", "structure"]))
                .step(GenerateContentStep(["insights_blocks"]))
                .step(ReportProgressStep())
                .build())
    
    try:
        result_context = pipeline.execute(context)
        
        filtered_count = len([b for b in mixed_blocks if url_or_task_filter.matches(b)])
        print(f"Filtered {len(mixed_blocks)} blocks down to {filtered_count} relevant blocks")
        
        # Show which blocks were processed
        print("Processed blocks:")
        for i, block in enumerate(mixed_blocks):
            if url_or_task_filter.matches(block):
                preview = block.content[:50] + "..." if len(block.content) > 50 else block.content
                print(f"  ✓ Block {i+1}: {preview}")
        
    except Exception as e:
        print(f"Filtered pipeline failed: {e}")


def demo_error_handling():
    """Demonstrate error handling and recovery."""
    print("\n=== Error Handling Demo ===")
    
    context = ProcessingContext(graph_path="/tmp/test")
    
    # Create blocks that might cause errors
    problematic_blocks = [
        Block(content="Valid content for processing"),
        Block(content=""),  # Empty content
        Block(content=None),  # None content
        Block(content="More valid content with https://example.com")
    ]
    
    context.blocks = problematic_blocks
    context.total_items = len(problematic_blocks)
    
    # Create pipeline that continues on errors
    pipeline = (create_pipeline("error_demo", "Error handling demonstration")
                .step(ExtractContentStep(["url"]))
                .step(AnalyzeContentStep(["sentiment", "topics"]))
                .step(ReportProgressStep())
                .configure(continue_on_error=True)  # Continue even if steps fail
                .build())
    
    try:
        result_context = pipeline.execute(context)
        
        print(f"Pipeline completed with {len(result_context.errors)} errors")
        
        if result_context.errors:
            print("Errors encountered:")
            for error in result_context.errors[:3]:  # Show first 3 errors
                error_type = error.get('type', 'Unknown')
                error_msg = error.get('error', 'No message')
                step = error.get('step', 'Unknown step')
                print(f"  - {error_type} in {step}: {error_msg}")
        
    except Exception as e:
        print(f"Error handling demo failed: {e}")


def main():
    """Main demo function."""
    setup_logging()
    
    print("Complete Pipeline System Demo")
    print("============================")
    print()
    
    try:
        # Test individual components
        demo_individual_components()
        
        # Test complete pipeline
        demo_real_pipeline()
        
        # Test advanced filtering
        demo_custom_pipeline_with_filtering()
        
        # Test error handling
        demo_error_handling()
        
        print("\n🎉 All demos completed successfully!")
        
    except Exception as e:
        print(f"Demo failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()