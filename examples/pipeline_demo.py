#!/usr/bin/env python3
"""
Pipeline System Demo

Demonstrates the pipeline framework for processing Logseq content with 
filtering, analysis, and generation capabilities.
"""

import logging
from pathlib import Path
import sys

# Add the project root to the path so we can import logseq_py
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from logseq_py.pipeline.core import ProcessingContext, create_pipeline
from logseq_py.pipeline.filters import (
    create_task_filter, create_content_filter, create_property_filter,
    create_and_filter, create_tag_filter
)
from logseq_py.pipeline.steps import (
    LoadContentStep, FilterBlocksStep, MarkProcessedStep, 
    ExtractContentStep, AnalyzeContentStep, GenerateContentStep,
    SaveResultsStep, UpdateProcessingStatusStep, ReportProgressStep
)


def setup_logging():
    """Setup logging for the demo."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('pipeline_demo.log')
        ]
    )


def demo_basic_pipeline():
    """Demonstrate a basic content processing pipeline."""
    print("=== Basic Pipeline Demo ===")
    
    # This would be the path to your Logseq graph
    graph_path = "/path/to/your/logseq/graph"
    
    # Create processing context
    context = ProcessingContext(graph_path=graph_path)
    
    # Create a basic pipeline using the builder
    pipeline = (create_pipeline("basic_content_processor", "Process and analyze Logseq content")
                .step(LoadContentStep(graph_path))
                .step(FilterBlocksStep(create_content_filter(contains="TODO")))
                .step(MarkProcessedStep())
                .step(AnalyzeContentStep(["sentiment", "summary"]))
                .step(GenerateContentStep(["summary_page"]))
                .step(SaveResultsStep())
                .step(ReportProgressStep())
                .configure(continue_on_error=True)
                .build())
    
    # Execute the pipeline
    try:
        result_context = pipeline.execute(context)
        print(f"Pipeline completed successfully!")
        print(f"Processed {result_context.processed_items} items")
        print(f"Generated {len(result_context.generated_content)} content items")
        
    except Exception as e:
        print(f"Pipeline failed: {e}")
        print(f"Errors: {len(context.errors)}")


def demo_task_analysis_pipeline():
    """Demonstrate a pipeline focused on analyzing task blocks."""
    print("\n=== Task Analysis Pipeline Demo ===")
    
    graph_path = "/path/to/your/logseq/graph"
    context = ProcessingContext(graph_path=graph_path)
    
    # Create filters for task analysis
    task_filter = create_task_filter()  # Blocks with TODO/DOING/DONE
    recent_filter = create_property_filter("created", operator="gte")  # Recent items
    combined_filter = create_and_filter(task_filter, recent_filter)
    
    # Build task analysis pipeline
    pipeline = (create_pipeline("task_analyzer", "Analyze task completion patterns")
                .step(LoadContentStep(graph_path))
                .step(FilterBlocksStep(combined_filter))
                .step(AnalyzeContentStep(["sentiment", "topics"]))
                .step(GenerateContentStep(["insights_blocks"]))
                .step(ReportProgressStep())
                .build())
    
    try:
        result_context = pipeline.execute(context)
        print(f"Task analysis completed!")
        
        # Show analysis results summary
        if result_context.analysis_results:
            for analyzer, results in result_context.analysis_results.items():
                count = results.get('count', 0) if isinstance(results, dict) else 0
                print(f"  {analyzer}: {count} analyses")
                
    except Exception as e:
        print(f"Task analysis failed: {e}")


def demo_content_extraction_pipeline():
    """Demonstrate content extraction and analysis."""
    print("\n=== Content Extraction Pipeline Demo ===")
    
    graph_path = "/path/to/your/logseq/graph"
    context = ProcessingContext(graph_path=graph_path)
    
    # Filter for blocks containing URLs or media links
    url_filter = create_content_filter(pattern=r'https?://\S+')
    
    pipeline = (create_pipeline("content_extractor", "Extract and analyze external content")
                .step(LoadContentStep(graph_path))
                .step(FilterBlocksStep(url_filter))
                .step(ExtractContentStep(["url", "youtube"]))
                .step(AnalyzeContentStep(["summary", "topics"]))
                .step(GenerateContentStep(["summary_page"]))
                .step(SaveResultsStep(target_page="Content Analysis Summary"))
                .step(ReportProgressStep())
                .build())
    
    try:
        result_context = pipeline.execute(context)
        print(f"Content extraction completed!")
        
        extracted_count = result_context.extracted_content.get('count', 0)
        print(f"Extracted content from {extracted_count} sources")
        
    except Exception as e:
        print(f"Content extraction failed: {e}")


def demo_custom_pipeline_step():
    """Demonstrate creating a custom pipeline step."""
    print("\n=== Custom Pipeline Step Demo ===")
    
    from logseq_py.pipeline.core import PipelineStep, ProcessingContext
    
    class CustomAnalysisStep(PipelineStep):
        """Custom step that performs domain-specific analysis."""
        
        def __init__(self, analysis_type: str = "custom"):
            super().__init__("custom_analysis", f"Perform {analysis_type} analysis")
            self.analysis_type = analysis_type
        
        def execute(self, context: ProcessingContext) -> ProcessingContext:
            """Execute custom analysis."""
            self.logger.info(f"Running {self.analysis_type} analysis...")
            
            # Example: Count different types of content
            analysis_results = {
                'total_blocks': len(context.blocks),
                'blocks_with_tags': 0,
                'code_blocks': 0,
                'task_blocks': 0
            }
            
            for block in context.blocks:
                if block.content:
                    # Check for hashtags
                    if '#' in block.content:
                        analysis_results['blocks_with_tags'] += 1
                    
                    # Check for code blocks
                    if '```' in block.content:
                        analysis_results['code_blocks'] += 1
                    
                    # Check for tasks
                    if any(marker in block.content for marker in ['TODO', 'DOING', 'DONE']):
                        analysis_results['task_blocks'] += 1
            
            # Store results
            context.analysis_results['custom_stats'] = {
                'results': [analysis_results],
                'count': 1
            }
            
            self.logger.info(f"Custom analysis completed: {analysis_results}")
            return context
    
    # Create pipeline with custom step
    graph_path = "/path/to/your/logseq/graph"
    context = ProcessingContext(graph_path=graph_path)
    
    pipeline = (create_pipeline("custom_analyzer", "Custom content analysis")
                .step(LoadContentStep(graph_path))
                .step(CustomAnalysisStep("content_statistics"))
                .step(ReportProgressStep())
                .build())
    
    try:
        result_context = pipeline.execute(context)
        print("Custom pipeline completed!")
        
        # Display custom analysis results
        if 'custom_stats' in result_context.analysis_results:
            stats = result_context.analysis_results['custom_stats']['results'][0]
            print("Content Statistics:")
            for key, value in stats.items():
                print(f"  {key}: {value}")
                
    except Exception as e:
        print(f"Custom pipeline failed: {e}")


def demo_pipeline_resumption():
    """Demonstrate pipeline resumption from a specific step."""
    print("\n=== Pipeline Resumption Demo ===")
    
    graph_path = "/path/to/your/logseq/graph"
    context = ProcessingContext(graph_path=graph_path)
    
    # Create a multi-step pipeline
    pipeline = (create_pipeline("resumable_pipeline", "Pipeline with resumption capability")
                .step(LoadContentStep(graph_path))
                .step(FilterBlocksStep(create_content_filter(min_length=10)))
                .step(MarkProcessedStep())
                .step(ExtractContentStep())
                .step(AnalyzeContentStep())
                .step(GenerateContentStep())
                .step(SaveResultsStep())
                .step(ReportProgressStep())
                .build())
    
    try:
        # Execute first few steps
        print("Executing first 3 steps...")
        partial_context = pipeline.execute(context, end_at=3)
        
        print(f"Partial execution completed. Progress: {partial_context.get_progress():.1f}%")
        
        # Resume from step 4 (AnalyzeContentStep)
        print("Resuming from analysis step...")
        final_context = pipeline.resume_from_step(partial_context, "extract_content")
        
        print("Pipeline resumption completed!")
        
    except Exception as e:
        print(f"Pipeline resumption failed: {e}")


def main():
    """Main demo function."""
    setup_logging()
    
    print("Pipeline System Demo")
    print("===================")
    print()
    
    # Note: These demos use placeholder graph paths
    # In actual usage, provide real Logseq graph paths
    
    try:
        demo_basic_pipeline()
        demo_task_analysis_pipeline() 
        demo_content_extraction_pipeline()
        demo_custom_pipeline_step()
        demo_pipeline_resumption()
        
    except Exception as e:
        print(f"Demo failed: {e}")
        import traceback
        traceback.print_exc()
    
    print("\nDemo completed!")


if __name__ == "__main__":
    main()