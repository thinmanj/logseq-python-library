# Logseq Python Pipeline System - Complete Guide

The Logseq Python Pipeline System is a powerful framework for processing and analyzing Logseq knowledge graphs using AI-powered extractors, analyzers, and content generators.

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Quick Start](#quick-start)
- [Core Components](#core-components)
- [Pipeline Examples](#pipeline-examples)
- [CLI Usage](#cli-usage)
- [API Reference](#api-reference)
- [Advanced Topics](#advanced-topics)
- [Performance Optimization](#performance-optimization)

## Overview

The pipeline system provides a complete solution for:

- **Content Extraction**: Extract metadata from URLs, YouTube videos, Twitter threads, academic papers, and more
- **Content Analysis**: Sentiment analysis, topic extraction, summarization, and structural analysis
- **Content Generation**: Create summary pages, insight reports, and task analysis dashboards
- **Pipeline Orchestration**: Chain operations with error handling, progress tracking, and resumable execution

### Key Features

- 🔗 **8 Specialized Extractors**: URL, YouTube, Twitter, RSS/News, Video Platforms, GitHub, PDF, Academic Papers
- 📊 **4 Content Analyzers**: Sentiment, Topics, Summary, Structure
- 📝 **3 Content Generators**: Summary Pages, Insights Blocks, Task Analysis
- 🔧 **Flexible Pipeline Framework**: Build custom workflows with ease
- 💻 **Rich CLI Interface**: Complete command-line tools for all operations
- 🧪 **Comprehensive Testing**: Full integration test suite

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Extractors    │────│    Analyzers    │────│   Generators    │
│                 │    │                 │    │                 │
│ • URL Content   │    │ • Sentiment     │    │ • Summary Pages│
│ • YouTube       │    │ • Topics        │    │ • Insights      │
│ • Twitter       │    │ • Summaries     │    │ • Task Reports  │
│ • Academic      │    │ • Structure     │    │                 │
│ • GitHub        │    │                 │    │                 │
│ • PDF           │    │                 │    │                 │
│ • RSS/News      │    │                 │    │                 │
│ • Video         │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
        │                       │                       │
        └───────────────────────┼───────────────────────┘
                               │
                    ┌─────────────────┐
                    │Pipeline Engine  │
                    │                 │
                    │ • Orchestration │
                    │ • Error Handling│
                    │ • Progress Track│
                    │ • State Mgmt    │
                    └─────────────────┘
```

## Quick Start

### Installation

```bash
# Install with all dependencies
pip install logseq-python[pipeline]

# Or install development version
git clone https://github.com/your-repo/logseq-python
cd logseq-python
pip install -e .[pipeline]
```

### Basic Usage

```python
from logseq_py.pipeline import create_pipeline, ProcessingContext

# Create a processing context
context = ProcessingContext(graph_path="/path/to/your/logseq/graph")

# Build a basic pipeline
pipeline = (create_pipeline("my_pipeline", "Process my content")
           .step(LoadContentStep("/path/to/graph"))
           .step(ExtractContentStep(['url', 'youtube']))
           .step(AnalyzeContentStep(['sentiment', 'topics']))
           .step(GenerateContentStep(['summary_page']))
           .build())

# Execute the pipeline
result = pipeline.execute(context)
print(f"Processed {result.processed_items} items")
```

### CLI Quick Start

```bash
# Analyze text content
logseq-py analyze text "This is amazing content about AI research"

# Process a Logseq graph
logseq-py pipeline run /path/to/graph --analyzers sentiment topics

# Run example workflows
logseq-py examples research-pipeline /path/to/graph --output results/
```

## Core Components

### 1. Content Extractors

Extract rich metadata and content from various sources:

#### URL Extractor
```python
from logseq_py.pipeline.extractors import URLExtractor

extractor = URLExtractor()
result = extractor.extract(block_with_url)
# Returns: {'url': '...', 'title': '...', 'text': '...', 'meta': {...}}
```

#### YouTube Extractor
```python
from logseq_py.pipeline.extractors import YouTubeExtractor

extractor = YouTubeExtractor()
result = extractor.extract(block_with_youtube_url)
# Returns: video metadata, transcripts, channel info
```

#### Academic Paper Extractor
```python
from logseq_py.pipeline.extractors import AcademicExtractor

extractor = AcademicExtractor()
result = extractor.extract(block_with_arxiv_url)
# Returns: paper metadata, abstract, authors, citations
```

### 2. Content Analyzers

Analyze extracted content with AI-powered insights:

#### Sentiment Analyzer
```python
from logseq_py.pipeline.analyzers import SentimentAnalyzer

analyzer = SentimentAnalyzer()
result = analyzer.analyze("This is absolutely amazing!")
# Returns: {'sentiment': 'positive', 'polarity': 0.8, ...}
```

#### Topic Analyzer
```python
from logseq_py.pipeline.analyzers import TopicAnalyzer

analyzer = TopicAnalyzer()
result = analyzer.analyze("Research paper on machine learning algorithms")
# Returns: {'topics': [...], 'keywords': [...], 'entities': [...]}
```

### 3. Content Generators

Generate new Logseq content from analysis results:

#### Summary Page Generator
```python
from logseq_py.pipeline.generators import SummaryPageGenerator

generator = SummaryPageGenerator()
result = generator.generate(processing_context)
# Returns: Complete summary page with insights
```

## Pipeline Examples

### Research Paper Processing

Process academic content and generate research insights:

```python
def create_research_pipeline(graph_path: str):
    """Create a research-focused pipeline."""
    return (create_pipeline("research", "Academic content processing")
            .step(LoadContentStep(graph_path))
            .step(FilterBlocksStep(lambda b: 'research' in b.content.lower()))
            .step(ExtractContentStep(['url', 'academic', 'pdf']))
            .step(AnalyzeContentStep(['topics', 'summary', 'structure']))
            .step(GenerateContentStep(['summary_page', 'insights_blocks']))
            .configure(continue_on_error=True)
            .build())

# Execute
context = ProcessingContext(graph_path="/path/to/graph")
result = create_research_pipeline("/path/to/graph").execute(context)
```

### Social Media Curation

Curate and analyze social media content:

```python
def create_social_pipeline(graph_path: str):
    """Create social media curation pipeline."""
    def social_filter(block):
        content = block.content.lower()
        return any(term in content for term in ['twitter.com', 'youtube.com', '@', '#'])
    
    return (create_pipeline("social", "Social media curation")
            .step(LoadContentStep(graph_path))
            .step(FilterBlocksStep(social_filter))
            .step(ExtractContentStep(['youtube', 'twitter', 'url']))
            .step(AnalyzeContentStep(['sentiment', 'topics']))
            .step(GenerateContentStep(['insights_blocks']))
            .build())
```

### News Summarization

Process news articles and generate summaries:

```python
def create_news_pipeline(graph_path: str):
    """Create news processing pipeline."""
    return (create_pipeline("news", "News article processing")
            .step(LoadContentStep(graph_path))
            .step(FilterBlocksStep(lambda b: 'news' in b.content.lower()))
            .step(ExtractContentStep(['url', 'rss']))
            .step(AnalyzeContentStep(['summary', 'topics', 'sentiment']))
            .step(GenerateContentStep(['summary_page']))
            .build())
```

## CLI Usage

The CLI provides comprehensive access to all pipeline functionality:

### Analysis Commands

```bash
# Analyze text directly
logseq-py analyze text "Your content here" --analyzers sentiment topics

# Analyze Logseq graph content
logseq-py analyze graph /path/to/graph --page "My Page" --limit 100

# Use specific analyzers
logseq-py analyze text "Content" -a sentiment -a topics -a summary
```

### Pipeline Commands

```bash
# Run complete pipeline
logseq-py pipeline run /path/to/graph \
  --extractors url youtube \
  --analyzers sentiment topics \
  --generators summary_page

# Get graph information
logseq-py pipeline info /path/to/graph --output graph_stats.json

# Use pipeline templates
logseq-py pipeline templates --list-templates
logseq-py pipeline templates --template research --save-config research.json
```

### Example Workflows

```bash
# Research paper processing
logseq-py examples research-pipeline /path/to/graph --output research_results/

# Social media curation
logseq-py examples social-curation /path/to/graph --output social_results/

# News summarization
logseq-py examples news-summarization /path/to/graph --output news_results/
```

### Content Extraction

```bash
# Extract content from URLs
logseq-py extract "Check out https://example.com and https://youtube.com/watch?v=123"

# Use specific extractors
logseq-py extract "Content with URLs" --extractors url youtube github
```

## API Reference

### Core Classes

#### ProcessingContext
Central context object that maintains state throughout pipeline execution:

```python
class ProcessingContext:
    graph_path: str           # Path to Logseq graph
    pipeline_id: str          # Unique pipeline identifier
    session_id: str           # Execution session ID
    
    # Data containers
    blocks: List[Block]                      # Loaded blocks
    pages: List[Page]                        # Loaded pages  
    extracted_content: Dict[str, Any]        # Extraction results
    analysis_results: Dict[str, Any]         # Analysis results
    generated_content: Dict[str, Any]        # Generated content
    
    # Progress tracking
    processed_items: int      # Items processed
    total_items: int          # Total items to process
    errors: List[Dict]        # Error log
```

#### Pipeline
Main pipeline orchestrator:

```python
class Pipeline:
    def __init__(self, name: str, description: str = None)
    def add_step(self, step: PipelineStep) -> 'Pipeline'
    def execute(self, context: ProcessingContext) -> ProcessingContext
    def validate_pipeline(self) -> List[str]
```

#### PipelineStep
Abstract base for all pipeline steps:

```python
class PipelineStep(ABC):
    def __init__(self, name: str, description: str = None)
    
    @abstractmethod
    def execute(self, context: ProcessingContext) -> ProcessingContext
    
    def can_execute(self, context: ProcessingContext) -> bool
    def validate_context(self, context: ProcessingContext) -> bool
```

### Pipeline Steps

#### LoadContentStep
```python
LoadContentStep(
    graph_path: str = None,
    load_pages: bool = True,
    load_blocks: bool = True,
    page_filter: PageFilter = None
)
```

#### FilterBlocksStep
```python
FilterBlocksStep(
    block_filter: Union[BlockFilter, Callable[[Block], bool]] = None
)
```

#### ExtractContentStep
```python
ExtractContentStep(
    extractors: List[str] = None  # Default: ['url', 'youtube', 'twitter']
)
```

#### AnalyzeContentStep
```python
AnalyzeContentStep(
    analyzers: List[str] = None  # Default: ['sentiment', 'topics', 'summary']
)
```

#### GenerateContentStep
```python
GenerateContentStep(
    generators: List[str] = None  # Default: ['summary_page', 'insights_blocks']
)
```

### Filters

Create content filters for preprocessing:

```python
from logseq_py.pipeline.filters import create_content_filter

# Filter by content
task_filter = create_content_filter(contains_any=["TODO", "DONE"])
url_filter = create_content_filter(contains="http")

# Filter by properties
date_filter = create_content_filter(
    has_properties=["created_at"],
    min_length=50
)

# Combine filters
combined_filter = create_and_filter([task_filter, url_filter])
```

## Advanced Topics

### Custom Extractors

Create specialized extractors for your content:

```python
from logseq_py.pipeline.extractors import ContentExtractor

class MyCustomExtractor(ContentExtractor):
    def __init__(self):
        super().__init__("custom")
    
    def can_extract(self, block: Block) -> bool:
        return "custom:" in block.content
    
    def extract(self, block: Block) -> Optional[Dict[str, Any]]:
        # Custom extraction logic
        return {"type": "custom", "data": "extracted_data"}

# Register the extractor
from logseq_py.pipeline.extractors import extractor_registry
extractor_registry.register(MyCustomExtractor())
```

### Custom Analyzers

Build domain-specific analyzers:

```python
from logseq_py.pipeline.analyzers import ContentAnalyzer

class MyCustomAnalyzer(ContentAnalyzer):
    def __init__(self):
        super().__init__("custom_analysis")
    
    def analyze(self, content: str) -> Optional[Dict[str, Any]]:
        # Custom analysis logic
        return {
            "custom_score": 0.85,
            "insights": ["insight1", "insight2"],
            "analyzed_at": datetime.now().isoformat()
        }

# Register the analyzer
from logseq_py.pipeline.analyzers import analyzer_registry
analyzer_registry.register(MyCustomAnalyzer())
```

### Custom Generators

Create specialized content generators:

```python
from logseq_py.pipeline.generators import ContentGenerator

class MyCustomGenerator(ContentGenerator):
    def __init__(self):
        super().__init__("custom_generator")
    
    def generate(self, context: ProcessingContext) -> Optional[Dict[str, Any]]:
        # Custom generation logic
        from logseq_py.builders import PageBuilder
        
        page = (PageBuilder("Custom Report")
                .add_content("# Custom Analysis Report\n\nGenerated insights...")
                .add_property("generated_by", "custom_generator"))
        
        return {
            'type': 'custom_page',
            'builder': page,
            'content': page.build()
        }

# Register the generator  
from logseq_py.pipeline.generators import generator_registry
generator_registry.register(MyCustomGenerator())
```

### Pipeline Hooks

Add custom hooks for monitoring and extending pipeline behavior:

```python
def on_pipeline_start(context: ProcessingContext):
    print(f"Starting pipeline {context.pipeline_id}")

def on_step_complete(step: PipelineStep, context: ProcessingContext):
    print(f"Completed step: {step.name}")

pipeline = create_pipeline("my_pipeline")
pipeline.on_pipeline_start = on_pipeline_start
pipeline.on_step_complete = on_step_complete
```

### Error Handling and Recovery

Configure robust error handling:

```python
pipeline = (create_pipeline("robust_pipeline")
           .configure(
               continue_on_error=True,
               save_intermediate_state=True
           )
           .build())

# Resume from specific step
context = pipeline.resume_from_step(context, "analyze_content")
```

## Performance Optimization

### Parallel Processing

Process large datasets efficiently:

```python
# Use batching for large content sets
class BatchedAnalysisStep(AnalyzeContentStep):
    def __init__(self, analyzers: List[str], batch_size: int = 100):
        super().__init__(analyzers)
        self.batch_size = batch_size
    
    def execute(self, context: ProcessingContext) -> ProcessingContext:
        # Process blocks in batches
        for i in range(0, len(context.blocks), self.batch_size):
            batch = context.blocks[i:i + self.batch_size]
            # Process batch...
        return context
```

### Memory Management

Optimize memory usage for large graphs:

```python
# Stream processing for large datasets
class StreamingLoadStep(LoadContentStep):
    def execute(self, context: ProcessingContext) -> ProcessingContext:
        # Load content in chunks to manage memory
        for page_batch in self.load_pages_in_batches():
            # Process batch and yield memory
            pass
        return context
```

### Caching and Persistence

Cache analysis results to avoid reprocessing:

```python
# Enable result caching
pipeline = (create_pipeline("cached_pipeline")
           .configure(
               save_intermediate_state=True,
               cache_analysis_results=True
           )
           .build())
```

## Testing

Run the comprehensive test suite:

```bash
# Run all tests
pytest tests/ -v

# Run integration tests only
pytest tests/test_integration.py -v -m integration

# Run with coverage
pytest tests/ --cov=logseq_py --cov-report=html
```

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Add tests for new functionality
4. Ensure all tests pass: `pytest tests/ -v`
5. Submit a pull request

### Development Setup

```bash
# Clone and setup development environment
git clone https://github.com/your-repo/logseq-python
cd logseq-python

# Install in development mode
pip install -e .[dev,pipeline]

# Install pre-commit hooks
pre-commit install

# Run tests
pytest tests/ -v
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- **Documentation**: [Full API Documentation](docs/)
- **Examples**: See `examples/` directory
- **Issues**: [GitHub Issues](https://github.com/your-repo/logseq-python/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-repo/logseq-python/discussions)

---

*This pipeline system transforms your Logseq knowledge graph into an intelligent, analyzable, and actionable knowledge base.*