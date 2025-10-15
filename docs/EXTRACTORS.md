# Content Extractors

The logseq-python library includes a comprehensive suite of content extractors that can automatically identify and extract information from various sources linked in Logseq blocks.

## Overview

Content extractors provide intelligent processing of external content referenced in your Logseq notes. They automatically detect different types of URLs and content sources, then fetch and structure the relevant information for analysis and integration into your knowledge graph.

## Available Extractors

### 1. URLExtractor
**Purpose**: Extract content and metadata from general web pages.

**Features**:
- Enhanced HTML parsing with BeautifulSoup support and regex fallback
- Comprehensive metadata extraction (title, description, author, keywords, Open Graph)
- Content structure analysis (headings, links)
- Intelligent content area detection (prioritizes `<article>`, `<main>`, etc.)
- Text summarization and length management
- Filtering of specialized URLs handled by other extractors

**Example Usage**:
```python
from logseq_py.pipeline.extractors import URLExtractor

extractor = URLExtractor()
block = Block(uuid="1", content="Check out https://example.com/article")

if extractor.can_extract(block):
    result = extractor.extract(block)
    print(f"Title: {result['content'][0]['title']}")
    print(f"Description: {result['content'][0]['description']}")
```

### 2. YouTubeExtractor
**Purpose**: Extract metadata from YouTube videos.

**Features**:
- Support for all YouTube URL formats (watch, youtu.be, embed, shorts)
- Optional YouTube Data API integration for comprehensive metadata
- oEmbed API fallback for basic information
- Video duration parsing (ISO 8601 format)
- View counts, like counts, comment counts
- Thumbnail URL selection (best quality available)
- Channel information and video tags

**API Integration**:
```python
# With YouTube Data API key
extractor = YouTubeExtractor(api_key="your_api_key")

# Without API key (uses oEmbed)
extractor = YouTubeExtractor()
```

### 3. TwitterExtractor
**Purpose**: Extract information from Twitter/X posts.

**Features**:
- Support for both twitter.com and x.com URLs
- Tweet ID extraction
- Basic post metadata (currently limited without API access)
- Extensible structure for future Twitter API v2 integration

### 4. GitHubExtractor
**Purpose**: Extract repository information from GitHub URLs.

**Features**:
- GitHub API integration for repository metadata
- Repository statistics (stars, forks, language)
- Repository description and timestamps
- Support for repository and file URLs
- Graceful fallback when API is unavailable

### 5. PDFExtractor
**Purpose**: Extract text and metadata from PDF documents.

**Features**:
- PDF text extraction with PyPDF2 (optional dependency)
- HTTP header analysis for basic metadata
- Support for arXiv and bioRxiv PDF patterns
- Configurable text length limits
- Graceful degradation without PDF libraries

### 6. AcademicPaperExtractor
**Purpose**: Extract metadata from academic papers via arXiv and DOI.

**Features**:
- arXiv API integration for preprint metadata
- Crossref API for DOI resolution
- Author information extraction
- Abstract and paper categories
- Publication date handling
- Journal and publisher information

## Architecture

### Base Class: ContentExtractor
All extractors inherit from the abstract `ContentExtractor` class:

```python
class ContentExtractor(ABC):
    @abstractmethod
    def can_extract(self, block: Block) -> bool:
        """Check if this extractor can process the given block."""
        pass
    
    @abstractmethod
    def extract(self, block: Block) -> Optional[Dict[str, Any]]:
        """Extract content from the block."""
        pass
```

### Registry System
The `ExtractorRegistry` manages all available extractors:

```python
from logseq_py.pipeline.extractors import get_extractor, get_all_extractors

# Get specific extractor
youtube_extractor = get_extractor('youtube')

# Get all available extractors
all_extractors = get_all_extractors()

# Extract from block using applicable extractors
results = extract_from_block(block)
```

## Integration with Caching

All extractors work seamlessly with the intelligent caching system:

```python
from logseq_py.pipeline.cache import create_memory_cache, CachedExtractor
from logseq_py.pipeline.extractors import YouTubeExtractor

cache = create_memory_cache()
extractor = YouTubeExtractor(api_key="your_key")
cached_extractor = CachedExtractor(extractor, cache)

# First call extracts and caches
result1 = cached_extractor.extract(block)

# Second call returns cached result
result2 = cached_extractor.extract(block)  # Fast!
```

## Data Structure

### Common Response Format
All extractors return a consistent structure:

```python
{
    'extractor': 'extractor_name',
    'type': 'content_type',
    'extracted_at': '2023-12-01T12:00:00Z',
    'total_items': 2,
    'successful_extractions': 1,
    # Type-specific data...
}
```

### URL Extractor Response
```python
{
    'extractor': 'url',
    'type': 'url',
    'urls': ['https://example.com'],
    'content': [{
        'url': 'https://example.com',
        'status': 'success',
        'title': 'Page Title',
        'description': 'Page description',
        'author': 'Author Name',
        'text': 'Main content text...',
        'headings': [
            {'level': 1, 'text': 'Main Heading'},
            {'level': 2, 'text': 'Subheading'}
        ],
        'links': [
            {'text': 'Link Text', 'url': 'https://linked-page.com'}
        ],
        'word_count': 150,
        'extracted_at': '2023-12-01T12:00:00Z'
    }]
}
```

### YouTube Extractor Response
```python
{
    'extractor': 'youtube',
    'type': 'youtube',
    'api_used': True,
    'videos': [{
        'video_id': 'dQw4w9WgXcQ',
        'url': 'https://youtube.com/watch?v=dQw4w9WgXcQ',
        'title': 'Video Title',
        'description': 'Video description',
        'channel_title': 'Channel Name',
        'duration_seconds': 240,
        'view_count': 1000000,
        'like_count': 50000,
        'thumbnail_url': 'https://img.youtube.com/vi/dQw4w9WgXcQ/maxres.jpg',
        'data_source': 'youtube_api',
        'status': 'success'
    }]
}
```

### Academic Paper Response
```python
{
    'extractor': 'academic',
    'type': 'academic_paper',
    'papers': [{
        'source': 'arxiv',
        'arxiv_id': '2301.00001',
        'title': 'Paper Title',
        'abstract': 'Paper abstract...',
        'authors': ['John Doe', 'Jane Smith'],
        'categories': ['cs.AI', 'cs.LG'],
        'published_date': '2023-01-01T00:00:00Z',
        'arxiv_url': 'https://arxiv.org/abs/2301.00001',
        'pdf_url': 'https://arxiv.org/pdf/2301.00001.pdf',
        'status': 'success'
    }]
}
```

## Configuration

### Environment Variables
Some extractors benefit from API keys:

```bash
# YouTube Data API
export YOUTUBE_API_KEY="your_youtube_api_key"

# Twitter API (future)
export TWITTER_BEARER_TOKEN="your_twitter_token"
```

### Extractor Initialization
```python
# Configure extractors with specific settings
url_extractor = URLExtractor(
    timeout=15,
    max_content_length=200000  # 200KB
)

youtube_extractor = YouTubeExtractor(
    api_key=os.getenv('YOUTUBE_API_KEY')
)
```

## Error Handling

All extractors implement robust error handling:

1. **Network Errors**: Graceful handling of timeouts, connection issues
2. **API Errors**: Fallback mechanisms when APIs are unavailable
3. **Content Errors**: Safe processing of malformed content
4. **Dependency Errors**: Optional dependencies handled gracefully

Example error response:
```python
{
    'url': 'https://failed-site.com',
    'status': 'error',
    'error': 'Connection timeout after 10 seconds',
    'extracted_at': '2023-12-01T12:00:00Z'
}
```

## Performance Considerations

1. **Caching**: All extractors support intelligent caching to avoid redundant API calls
2. **Rate Limiting**: Built-in respect for API rate limits
3. **Concurrent Processing**: Safe for concurrent use with async pipelines
4. **Content Limits**: Configurable limits to prevent memory issues
5. **Timeout Handling**: Reasonable timeouts prevent hanging operations

## Testing

Comprehensive unit tests cover:
- URL pattern detection
- Content extraction accuracy
- API integration
- Error handling
- Caching integration
- Registry functionality

Run tests with:
```bash
python -m pytest tests/unit/test_extractors.py -v
```

## Future Enhancements

The extractor system is designed for easy extension:

1. **RSS/Feed Extractor**: For news feeds and blog subscriptions
2. **Video Platform Extractors**: Vimeo, TikTok, Twitch support
3. **Enhanced Twitter Integration**: Full Twitter API v2 support
4. **Document Extractors**: Word documents, presentations
5. **Code Repository Extractors**: GitLab, Bitbucket support

## Best Practices

1. **API Keys**: Use environment variables for API keys
2. **Caching**: Always use caching for production deployments
3. **Error Handling**: Check extraction status before using results
4. **Rate Limiting**: Implement delays for bulk processing
5. **Content Filtering**: Use appropriate extractors for specific content types

The content extractor system provides a solid foundation for intelligent content processing in your Logseq workflow, with robust error handling, comprehensive testing, and seamless integration with the caching and async pipeline systems.