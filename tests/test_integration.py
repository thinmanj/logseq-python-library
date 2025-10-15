"""
Integration tests for logseq-python pipeline workflows.

Tests complete end-to-end scenarios including extraction, analysis, and generation.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, patch

from logseq_py.pipeline.core import ProcessingContext, Pipeline, create_pipeline
from logseq_py.pipeline.steps import (
    LoadContentStep, FilterBlocksStep, ExtractContentStep,
    AnalyzeContentStep, GenerateContentStep, ReportProgressStep
)
from logseq_py.pipeline.filters import create_content_filter
from logseq_py.models import Block, Page


@pytest.fixture
def sample_graph_data():
    """Create sample Logseq graph data for testing."""
    pages = [
        Page(
            name="Research Notes",
            blocks=[
                Block(content="Interesting research paper: https://arxiv.org/abs/1234.5678"),
                Block(content="TODO Review the methodology section"),
                Block(content="The study shows promising results for machine learning applications."),
            ]
        ),
        Page(
            name="Social Media",
            blocks=[
                Block(content="Great video: https://youtube.com/watch?v=abcd1234"),
                Block(content="Twitter thread about AI: https://twitter.com/user/status/123456789"),
                Block(content="This content is absolutely amazing! #AI #MachineLearning"),
            ]
        ),
        Page(
            name="Project Notes",
            blocks=[
                Block(content="TODO Implement feature X"),
                Block(content="DONE Set up development environment"),
                Block(content="GitHub repo: https://github.com/user/project"),
            ]
        )
    ]
    return pages


@pytest.fixture
def mock_logseq_client(sample_graph_data):
    """Mock LogseqClient for testing."""
    with patch('logseq_py.pipeline.steps.LogseqClient') as mock_client_class:
        mock_client = Mock()
        mock_client.get_all_pages.return_value = sample_graph_data
        mock_client_class.return_value = mock_client
        yield mock_client


class TestBasicPipeline:
    """Test basic pipeline functionality."""
    
    def test_basic_pipeline_creation(self):
        """Test creating a basic pipeline."""
        pipeline = (create_pipeline("test_pipeline", "Test pipeline")
                   .step(LoadContentStep("/fake/path"))
                   .step(AnalyzeContentStep(["sentiment", "topics"]))
                   .step(ReportProgressStep())
                   .build())
        
        assert pipeline.name == "test_pipeline"
        assert len(pipeline.steps) == 3
        assert pipeline.steps[0].name == "load_content"
        assert pipeline.steps[1].name == "analyze_content"
        assert pipeline.steps[2].name == "report_progress"
    
    def test_pipeline_validation(self):
        """Test pipeline validation."""
        pipeline = Pipeline("empty_pipeline")
        issues = pipeline.validate_pipeline()
        assert "Pipeline has no steps" in issues
        
        # Add steps and validate
        pipeline.add_step(LoadContentStep("/fake/path"))
        pipeline.add_step(AnalyzeContentStep())
        issues = pipeline.validate_pipeline()
        assert len(issues) == 0


class TestContentProcessing:
    """Test content processing workflows."""
    
    def test_content_extraction_workflow(self, mock_logseq_client):
        """Test content extraction workflow."""
        context = ProcessingContext(graph_path="/fake/graph")
        
        # Mock extractors
        with patch('logseq_py.pipeline.steps.get_extractor') as mock_get_extractor:
            mock_extractor = Mock()
            mock_extractor.can_extract.return_value = True
            mock_extractor.extract.return_value = {
                'url': 'https://example.com',
                'title': 'Example Page',
                'text': 'This is example content'
            }
            mock_get_extractor.return_value = mock_extractor
            
            # Create and run extraction step
            step = ExtractContentStep(['url'])
            
            # Set up blocks in context
            context.blocks = [
                Block(content="Check this out: https://example.com"),
                Block(content="Another interesting link: https://test.com")
            ]
            
            result_context = step.execute(context)
            
            assert 'items' in result_context.extracted_content
            assert result_context.extracted_content['count'] > 0
    
    def test_content_analysis_workflow(self):
        """Test content analysis workflow."""
        context = ProcessingContext(graph_path="/fake/graph")
        context.blocks = [
            Block(content="This is absolutely amazing! I love this new feature."),
            Block(content="The research paper discusses machine learning algorithms."),
            Block(content="TODO Review the implementation details")
        ]
        
        # Mock analyzers
        with patch('logseq_py.pipeline.steps.get_analyzer') as mock_get_analyzer:
            mock_analyzer = Mock()
            mock_analyzer.analyze.return_value = {
                'sentiment': 'positive',
                'polarity': 0.8,
                'topics': [{'topic': 'technology', 'score': 5}]
            }
            mock_get_analyzer.return_value = mock_analyzer
            
            step = AnalyzeContentStep(['sentiment', 'topics'])
            result_context = step.execute(context)
            
            assert 'sentiment' in result_context.analysis_results
            assert 'topics' in result_context.analysis_results
            assert result_context.analysis_results['sentiment']['count'] > 0
    
    def test_content_generation_workflow(self):
        """Test content generation workflow."""
        context = ProcessingContext(graph_path="/fake/graph")
        context.analysis_results = {
            'sentiment': {
                'results': [
                    {
                        'block_id': '123',
                        'analysis': {'sentiment': 'positive', 'polarity': 0.8}
                    }
                ],
                'count': 1
            }
        }
        
        # Mock generators
        with patch('logseq_py.pipeline.steps.get_generator') as mock_get_generator:
            mock_generator = Mock()
            mock_generator.can_generate.return_value = True
            mock_generator.generate.return_value = {
                'type': 'summary_page',
                'title': 'Analysis Summary',
                'content': 'Generated summary content'
            }
            mock_get_generator.return_value = mock_generator
            
            step = GenerateContentStep(['summary_page'])
            result_context = step.execute(context)
            
            assert 'summary_page' in result_context.generated_content


class TestEndToEndPipelines:
    """Test complete end-to-end pipeline scenarios."""
    
    def test_research_pipeline_workflow(self, mock_logseq_client):
        """Test research-focused pipeline workflow."""
        context = ProcessingContext(graph_path="/fake/graph")
        
        # Mock all components
        with patch('logseq_py.pipeline.steps.get_extractor') as mock_get_extractor, \
             patch('logseq_py.pipeline.steps.get_analyzer') as mock_get_analyzer, \
             patch('logseq_py.pipeline.steps.get_generator') as mock_get_generator:
            
            # Mock extractor
            mock_extractor = Mock()
            mock_extractor.can_extract.return_value = True
            mock_extractor.extract.return_value = {'title': 'Research Paper', 'abstract': 'Study results'}
            mock_get_extractor.return_value = mock_extractor
            
            # Mock analyzer
            mock_analyzer = Mock()
            mock_analyzer.analyze.return_value = {
                'topics': [{'topic': 'research', 'score': 10}],
                'summary': 'Research summary'
            }
            mock_get_analyzer.return_value = mock_analyzer
            
            # Mock generator
            mock_generator = Mock()
            mock_generator.can_generate.return_value = True
            mock_generator.generate.return_value = {
                'type': 'research_summary',
                'content': 'Generated research insights'
            }
            mock_get_generator.return_value = mock_generator
            
            # Create research pipeline
            pipeline = (create_pipeline("research_pipeline", "Research workflow")
                       .step(LoadContentStep("/fake/graph"))
                       .step(FilterBlocksStep(lambda b: 'research' in b.content.lower()))
                       .step(ExtractContentStep(['url', 'academic']))
                       .step(AnalyzeContentStep(['topics', 'summary']))
                       .step(GenerateContentStep(['summary_page']))
                       .build())
            
            result_context = pipeline.execute(context)
            
            assert result_context.current_step == len(pipeline.steps)
            assert result_context.get_progress() >= 0
    
    def test_social_media_pipeline_workflow(self, mock_logseq_client):
        """Test social media curation pipeline workflow."""
        context = ProcessingContext(graph_path="/fake/graph")
        
        with patch('logseq_py.pipeline.steps.get_extractor') as mock_get_extractor, \
             patch('logseq_py.pipeline.steps.get_analyzer') as mock_get_analyzer:
            
            # Mock social media extractor
            mock_extractor = Mock()
            mock_extractor.can_extract.return_value = True
            mock_extractor.extract.return_value = {
                'platform': 'youtube',
                'title': 'Great Video',
                'engagement': 'high'
            }
            mock_get_extractor.return_value = mock_extractor
            
            # Mock sentiment analyzer
            mock_analyzer = Mock()
            mock_analyzer.analyze.return_value = {
                'sentiment': 'positive',
                'polarity': 0.9
            }
            mock_get_analyzer.return_value = mock_analyzer
            
            # Create social media pipeline
            def social_filter(block):
                content = block.content.lower() if block.content else ''
                return any(term in content for term in ['youtube.com', 'twitter.com', '@', '#'])
            
            pipeline = (create_pipeline("social_pipeline", "Social media workflow")
                       .step(LoadContentStep("/fake/graph"))
                       .step(FilterBlocksStep(social_filter))
                       .step(ExtractContentStep(['youtube', 'twitter']))
                       .step(AnalyzeContentStep(['sentiment']))
                       .build())
            
            result_context = pipeline.execute(context)
            
            assert result_context.current_step == len(pipeline.steps)
            assert len(result_context.errors) == 0  # No errors expected


class TestPipelineErrorHandling:
    """Test pipeline error handling and recovery."""
    
    def test_pipeline_continues_on_error(self, mock_logseq_client):
        """Test pipeline continues execution when configured to handle errors."""
        context = ProcessingContext(graph_path="/fake/graph")
        
        # Create a step that will fail
        class FailingStep(ExtractContentStep):
            def execute(self, context):
                raise ValueError("Simulated extraction error")
        
        pipeline = Pipeline("error_test_pipeline")
        pipeline.continue_on_error = True
        pipeline.add_step(LoadContentStep("/fake/graph"))
        pipeline.add_step(FailingStep(['url']))
        pipeline.add_step(ReportProgressStep())
        
        # Should not raise exception
        result_context = pipeline.execute(context)
        
        assert len(result_context.errors) > 0
        assert result_context.current_step == len(pipeline.steps)
    
    def test_pipeline_stops_on_error(self, mock_logseq_client):
        """Test pipeline stops execution when configured to stop on errors."""
        context = ProcessingContext(graph_path="/fake/graph")
        
        class FailingStep(ExtractContentStep):
            def execute(self, context):
                raise ValueError("Simulated extraction error")
        
        pipeline = Pipeline("error_test_pipeline")
        pipeline.continue_on_error = False
        pipeline.add_step(LoadContentStep("/fake/graph"))
        pipeline.add_step(FailingStep(['url']))
        pipeline.add_step(ReportProgressStep())
        
        # Should raise exception
        with pytest.raises(ValueError):
            pipeline.execute(context)


class TestFilteringAndSelection:
    """Test content filtering and selection functionality."""
    
    def test_content_filtering(self):
        """Test various content filtering strategies."""
        blocks = [
            Block(content="TODO: Finish the project documentation"),
            Block(content="DONE: Set up CI/CD pipeline"),
            Block(content="Check out this article: https://example.com"),
            Block(content="Random note without special markers"),
        ]
        
        # Test task filter
        task_filter = create_content_filter(contains_any=["TODO", "DONE"])
        task_blocks = task_filter.filter_blocks(blocks)
        assert len(task_blocks) == 2
        
        # Test URL filter
        url_filter = create_content_filter(contains="http")
        url_blocks = url_filter.filter_blocks(blocks)
        assert len(url_blocks) == 1
        
        # Test combined filter
        combined_filter = create_content_filter(min_length=10)
        long_blocks = combined_filter.filter_blocks(blocks)
        assert len(long_blocks) > 0


class TestPerformanceAndScaling:
    """Test performance characteristics and scaling behavior."""
    
    def test_large_content_processing(self):
        """Test processing large amounts of content."""
        # Create a large number of blocks
        blocks = []
        for i in range(1000):
            blocks.append(Block(content=f"Block {i}: This is test content with some keywords like research and analysis."))
        
        context = ProcessingContext(graph_path="/fake/graph")
        context.blocks = blocks
        context.total_items = len(blocks)
        
        # Mock fast analyzers
        with patch('logseq_py.pipeline.steps.get_analyzer') as mock_get_analyzer:
            mock_analyzer = Mock()
            mock_analyzer.analyze.return_value = {'sentiment': 'neutral'}
            mock_get_analyzer.return_value = mock_analyzer
            
            step = AnalyzeContentStep(['sentiment'])
            
            start_time = datetime.now()
            result_context = step.execute(context)
            end_time = datetime.now()
            
            processing_time = (end_time - start_time).total_seconds()
            
            # Should process reasonably quickly (less than 5 seconds for 1000 items in test)
            assert processing_time < 5.0
            assert result_context.analysis_results['sentiment']['count'] == 1000


@pytest.mark.integration
class TestRealWorldScenarios:
    """Integration tests for real-world usage scenarios."""
    
    def test_full_research_workflow(self, mock_logseq_client):
        """Test complete research paper processing workflow."""
        context = ProcessingContext(graph_path="/fake/graph")
        
        # Mock all required components
        with patch('logseq_py.pipeline.steps.get_extractor') as mock_get_extractor, \
             patch('logseq_py.pipeline.steps.get_analyzer') as mock_get_analyzer, \
             patch('logseq_py.pipeline.steps.get_generator') as mock_get_generator:
            
            # Set up mocks
            mock_extractor = Mock()
            mock_extractor.can_extract.return_value = True
            mock_extractor.extract.return_value = {'type': 'academic', 'title': 'Research Paper'}
            mock_get_extractor.return_value = mock_extractor
            
            mock_analyzer = Mock()
            mock_analyzer.analyze.return_value = {'topics': [{'topic': 'AI', 'score': 8}]}
            mock_get_analyzer.return_value = mock_analyzer
            
            mock_generator = Mock()
            mock_generator.can_generate.return_value = True
            mock_generator.generate.return_value = {'type': 'insights', 'content': 'AI research insights'}
            mock_get_generator.return_value = mock_generator
            
            # Build and execute full pipeline
            pipeline = (create_pipeline("full_research", "Complete research workflow")
                       .step(LoadContentStep("/fake/graph"))
                       .step(FilterBlocksStep(lambda b: any(term in b.content.lower() 
                                                          for term in ['research', 'study', 'paper'])))
                       .step(ExtractContentStep(['academic', 'url']))
                       .step(AnalyzeContentStep(['topics', 'summary']))
                       .step(GenerateContentStep(['insights_blocks', 'summary_page']))
                       .step(ReportProgressStep())
                       .configure(continue_on_error=True, save_intermediate_state=False)
                       .build())
            
            result_context = pipeline.execute(context)
            
            # Verify pipeline completion
            assert result_context.current_step == len(pipeline.steps)
            assert result_context.get_status_summary()['status'] == 'completed'
            
            # Verify all stages produced results
            summary = result_context.get_status_summary()
            assert summary['progress'] >= 0
            assert summary['elapsed_time'] > 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])