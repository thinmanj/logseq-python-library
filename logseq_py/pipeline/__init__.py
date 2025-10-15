"""
Logseq Pipeline System

A flexible pipeline framework for processing Logseq content in stages:
- Extract information from various sources (YouTube, Twitter, web pages)
- Analyze content to identify facets and themes  
- Generate new structured content (pages, blocks, summaries)
- Update Logseq graphs with processed information

Key Features:
- Configurable multi-step processing pipelines
- Block filtering and property-based state tracking
- Extensible content extractors and analyzers
- Integration with unified builder system
- Resumable processing with progress tracking
"""

# Core pipeline components
from .core import (
    Pipeline, PipelineStep, ProcessingContext, ProcessingStatus,
    PipelineBuilder, create_pipeline
)

# Filtering system
from .filters import (
    BlockFilter, PropertyFilter, ContentFilter, TypeFilter,
    DateFilter, TagFilter, CompositeFilter, PredicateFilter,
    PageFilter, create_task_filter, create_code_filter,
    create_property_filter, create_content_filter, create_tag_filter,
    create_and_filter, create_or_filter, create_predicate_filter
)

# Pipeline steps
from .steps import (
    LoadContentStep, FilterBlocksStep, MarkProcessedStep,
    ExtractContentStep, AnalyzeContentStep, GenerateContentStep,
    SaveResultsStep, UpdateProcessingStatusStep, ReportProgressStep,
    create_basic_pipeline_steps, create_analysis_pipeline_steps
)

# Content processing components
from .extractors import (
    ContentExtractor, URLExtractor, YouTubeExtractor, TwitterExtractor, GitHubExtractor,
    ExtractorRegistry, get_extractor, get_all_extractors, extract_from_block
)

from .analyzers import (
    ContentAnalyzer, SentimentAnalyzer, TopicAnalyzer, SummaryAnalyzer, StructureAnalyzer,
    AnalyzerRegistry, get_analyzer, get_all_analyzers, analyze_content, analyze_block
)

from .generators import (
    ContentGenerator, SummaryPageGenerator, InsightsBlockGenerator, TaskAnalysisGenerator,
    GeneratorRegistry, get_generator, get_all_generators, generate_content
)

# Async pipeline components
try:
    from .async_pipeline import (
        AsyncPipeline,
        AsyncBatchProcessor,
        AsyncProgressTracker
    )
    ASYNC_AVAILABLE = True
except ImportError:
    ASYNC_AVAILABLE = False

# Caching system
try:
    from .cache import (
        CacheEntry,
        CacheBackend,
        MemoryCache,
        SQLiteCache,
        PipelineCache,
        CachedExtractor,
        CachedAnalyzer,
        create_memory_cache,
        create_sqlite_cache,
        cached
    )
    CACHE_AVAILABLE = True
except ImportError:
    CACHE_AVAILABLE = False

__all__ = [
    # Core pipeline components
    'Pipeline',
    'PipelineStep', 
    'ProcessingContext',
    'ProcessingStatus',
    'PipelineBuilder',
    'create_pipeline',
    
    # Filtering system
    'BlockFilter',
    'PropertyFilter',
    'ContentFilter',
    'TypeFilter',
    'DateFilter',
    'TagFilter',
    'CompositeFilter',
    'PredicateFilter',
    'PageFilter',
    
    # Filter factory functions
    'create_task_filter',
    'create_code_filter', 
    'create_property_filter',
    'create_content_filter',
    'create_tag_filter',
    'create_and_filter',
    'create_or_filter',
    'create_predicate_filter',
    
    # Pipeline steps
    'LoadContentStep',
    'FilterBlocksStep',
    'MarkProcessedStep',
    'ExtractContentStep',
    'AnalyzeContentStep',
    'GenerateContentStep',
    'SaveResultsStep',
    'UpdateProcessingStatusStep',
    'ReportProgressStep',
    
    # Step factory functions
    'create_basic_pipeline_steps',
    'create_analysis_pipeline_steps',
    
    # Content extractors
    'ContentExtractor',
    'URLExtractor',
    'YouTubeExtractor',
    'TwitterExtractor',
    'GitHubExtractor',
    'ExtractorRegistry',
    'get_extractor',
    'get_all_extractors',
    'extract_from_block',
    
    # Content analyzers
    'ContentAnalyzer',
    'SentimentAnalyzer',
    'TopicAnalyzer',
    'SummaryAnalyzer',
    'StructureAnalyzer',
    'AnalyzerRegistry',
    'get_analyzer',
    'get_all_analyzers',
    'analyze_content',
    'analyze_block',
    
    # Content generators
    'ContentGenerator',
    'SummaryPageGenerator',
    'InsightsBlockGenerator',
    'TaskAnalysisGenerator',
    'GeneratorRegistry',
    'get_generator',
    'get_all_generators',
    'generate_content'
]

# Conditionally add async and cache components to __all__
if ASYNC_AVAILABLE:
    __all__.extend([
        'AsyncPipeline',
        'AsyncBatchProcessor', 
        'AsyncProgressTracker'
    ])

if CACHE_AVAILABLE:
    __all__.extend([
        'CacheEntry',
        'CacheBackend',
        'MemoryCache',
        'SQLiteCache',
        'PipelineCache',
        'CachedExtractor',
        'CachedAnalyzer',
        'create_memory_cache',
        'create_sqlite_cache',
        'cached'
    ])
