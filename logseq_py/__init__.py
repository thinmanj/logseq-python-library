"""
Logseq Python Library

A Python library for interacting with Logseq knowledge graphs.
Provides functionality to read, query, and modify Logseq data.
"""

from .logseq_client import LogseqClient
from .models import (
    Block, Page, LogseqGraph,
    TaskState, Priority, BlockType,
    BlockEmbed, ScheduledDate, LogseqQuery,
    Template, Annotation, WhiteboardElement
)
from .query import QueryBuilder
from .utils import LogseqUtils

# Import builders for programmatic content generation
from .builders import (
    # Core builders
    ContentBuilder, BlockBuilder, LogseqBuilder,
    # Content type builders
    TextBuilder, HeadingBuilder, ListBuilder, TaskBuilder,
    CodeBlockBuilder, MathBuilder, QuoteBuilder, TableBuilder,
    MediaBuilder, DrawingBuilder,
    # Page builders
    PageBuilder, PropertyBuilder, TemplateBuilder,
    # Advanced builders
    QueryBuilder as BuilderQueryBuilder, JournalBuilder, 
    WorkflowBuilder, DemoBuilder
)

# Import pipeline functionality
try:
    from .pipeline import (
        # Core pipeline components
        Pipeline, PipelineStep, ProcessingContext, ProcessingStatus,
        PipelineBuilder, create_pipeline,
        # Content processing
        ContentExtractor, ContentAnalyzer, ContentGenerator,
        ExtractorRegistry, AnalyzerRegistry, GeneratorRegistry,
        # Filters
        PropertyFilter, ContentFilter, TypeFilter, DateFilter, TagFilter, 
        CompositeFilter, PredicateFilter, PageFilter
    )
    
    # Try to import optional async and cache components
    try:
        from .pipeline import AsyncPipeline, AsyncBatchProcessor, AsyncProgressTracker
        ASYNC_PIPELINE_AVAILABLE = True
    except ImportError:
        ASYNC_PIPELINE_AVAILABLE = False
    
    try:
        from .pipeline import (
            PipelineCache, CachedExtractor, CachedAnalyzer,
            create_memory_cache, create_sqlite_cache
        )
        CACHE_AVAILABLE = True
    except ImportError:
        CACHE_AVAILABLE = False
    
    PIPELINE_AVAILABLE = True
except ImportError:
    PIPELINE_AVAILABLE = False

__version__ = "0.1.0"
__author__ = "Julio Ona"
__email__ = "thinmanj@gmail.com"

__all__ = [
    "LogseqClient",
    "Block", 
    "Page",
    "LogseqGraph",
    "QueryBuilder",
    "LogseqUtils",
    # Advanced models
    "TaskState",
    "Priority",
    "BlockType",
    "BlockEmbed",
    "ScheduledDate",
    "LogseqQuery",
    "Template",
    "Annotation",
    "WhiteboardElement",
    
    # Content builders
    "ContentBuilder", "BlockBuilder", "LogseqBuilder",
    "TextBuilder", "HeadingBuilder", "ListBuilder", "TaskBuilder",
    "CodeBlockBuilder", "MathBuilder", "QuoteBuilder", "TableBuilder",
    "MediaBuilder", "DrawingBuilder",
    "PageBuilder", "PropertyBuilder", "TemplateBuilder",
    "BuilderQueryBuilder", "JournalBuilder", "WorkflowBuilder", "DemoBuilder"
]

# Conditionally add pipeline components based on availability
if PIPELINE_AVAILABLE:
    __all__.extend([
        "Pipeline", "PipelineStep", "ProcessingContext", "ProcessingStatus",
        "PipelineBuilder", "create_pipeline",
        "ContentExtractor", "ContentAnalyzer", "ContentGenerator",
        "ExtractorRegistry", "AnalyzerRegistry", "GeneratorRegistry",
        "PropertyFilter", "ContentFilter", "TypeFilter", "DateFilter", "TagFilter",
        "CompositeFilter", "PredicateFilter", "PageFilter"
    ])
    
    if ASYNC_PIPELINE_AVAILABLE:
        __all__.extend(["AsyncPipeline", "AsyncBatchProcessor", "AsyncProgressTracker"])
    
    if CACHE_AVAILABLE:
        __all__.extend([
            "PipelineCache", "CachedExtractor", "CachedAnalyzer",
            "create_memory_cache", "create_sqlite_cache"
        ])
