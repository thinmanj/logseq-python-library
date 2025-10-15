"""
Shared test configuration and fixtures for logseq-python tests.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

from logseq_py.models import Block, Page
from logseq_py.pipeline.core import ProcessingContext


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)


@pytest.fixture
def sample_blocks() -> List[Block]:
    """Create sample blocks for testing."""
    return [
        Block(
            id="block-1",
            content="TODO: Complete the project documentation",
            properties={"type": "task", "priority": "high"}
        ),
        Block(
            id="block-2", 
            content="I love working with Python! It's fantastic and makes development enjoyable.",
            properties={"topic": "technology", "sentiment": "positive"}
        ),
        Block(
            id="block-3",
            content="The meeting was disappointing and the results were terrible.",
            properties={"topic": "work", "sentiment": "negative"}
        ),
        Block(
            id="block-4",
            content="DONE: Implement user authentication system",
            properties={"type": "task", "completed": True}
        ),
        Block(
            id="block-5",
            content="Check out this YouTube video: https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            properties={"type": "media"}
        ),
        Block(
            id="block-6",
            content="GitHub repository: https://github.com/python/cpython - core Python implementation",
            properties={"type": "reference"}
        )
    ]


@pytest.fixture
def sample_pages(sample_blocks) -> List[Page]:
    """Create sample pages for testing."""
    return [
        Page(
            name="Daily Notes - 2024-01-15",
            blocks=sample_blocks[:3],
            properties={"date": "2024-01-15", "type": "daily"}
        ),
        Page(
            name="Project Planning", 
            blocks=sample_blocks[3:],
            properties={"project": "logseq-python", "status": "active"}
        ),
        Page(
            name="Empty Page",
            blocks=[],
            properties={"status": "draft"}
        )
    ]


@pytest.fixture
def processing_context(temp_dir, sample_blocks) -> ProcessingContext:
    """Create a processing context for pipeline tests."""
    context = ProcessingContext(graph_path=str(temp_dir))
    context.blocks = sample_blocks
    context.total_items = len(sample_blocks)
    return context


@pytest.fixture
def mock_web_content():
    """Mock web content for extractor tests."""
    return {
        "html_content": """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Test Web Page</title>
        </head>
        <body>
            <h1>Welcome to Test Page</h1>
            <p>This is a test web page with some content.</p>
            <p>It contains multiple paragraphs for testing.</p>
        </body>
        </html>
        """,
        "plain_text": "Welcome to Test Page\nThis is a test web page with some content.\nIt contains multiple paragraphs for testing.",
        "title": "Test Web Page"
    }


@pytest.fixture
def mock_youtube_data():
    """Mock YouTube API response data."""
    return {
        "title": "Amazing Tutorial Video",
        "author_name": "Test Channel",
        "author_url": "https://www.youtube.com/channel/UC123456789",
        "thumbnail_url": "https://img.youtube.com/vi/dQw4w9WgXcQ/maxresdefault.jpg",
        "width": 1280,
        "height": 720
    }


@pytest.fixture
def mock_github_data():
    """Mock GitHub API response data."""
    return {
        "full_name": "python/cpython",
        "description": "The Python programming language",
        "language": "Python",
        "stargazers_count": 50000,
        "forks_count": 25000,
        "created_at": "2008-02-21T00:00:00Z",
        "updated_at": "2024-01-15T12:00:00Z"
    }


@pytest.fixture
def sentiment_test_cases():
    """Test cases for sentiment analysis."""
    return [
        {
            "text": "I love this amazing product! It's fantastic and wonderful.",
            "expected_sentiment": "positive",
            "expected_polarity_range": (0.5, 1.0)
        },
        {
            "text": "This is terrible and awful. I hate it completely.",
            "expected_sentiment": "negative", 
            "expected_polarity_range": (-1.0, -0.5)
        },
        {
            "text": "The weather is okay today. Nothing special.",
            "expected_sentiment": "neutral",
            "expected_polarity_range": (-0.1, 0.1)
        },
        {
            "text": "I don't like this very much. It's not good.",
            "expected_sentiment": "negative",
            "expected_polarity_range": (-1.0, -0.1)
        }
    ]


@pytest.fixture
def topic_test_cases():
    """Test cases for topic analysis."""
    return [
        {
            "text": "Python programming language software development coding algorithms",
            "expected_topics": ["technology"],
            "expected_keywords": ["python", "programming", "software", "development"]
        },
        {
            "text": "Marketing strategy sales revenue customer growth business profit",
            "expected_topics": ["business"],
            "expected_keywords": ["marketing", "sales", "revenue", "customer"]
        },
        {
            "text": "Medical doctor patient treatment health diagnosis medicine",
            "expected_topics": ["health"],
            "expected_keywords": ["medical", "doctor", "patient", "treatment"]
        }
    ]


@pytest.fixture
def summary_test_cases():
    """Test cases for content summarization."""
    return [
        {
            "text": "This is the first sentence. This is the second sentence. This is the third sentence. This is the fourth sentence.",
            "max_sentences": 2,
            "expected_sentence_count": 2
        },
        {
            "text": "Short text.",
            "max_sentences": 3,
            "expected_compression_ratio": 1.0  # No compression needed
        }
    ]


class MockRequests:
    """Mock requests for HTTP testing."""
    
    def __init__(self):
        self.responses = {}
        self.call_count = 0
    
    def add_response(self, url: str, status_code: int = 200, json_data: Dict = None, text: str = None, headers: Dict = None):
        """Add a mock response for a URL."""
        self.responses[url] = {
            'status_code': status_code,
            'json_data': json_data,
            'text': text,
            'headers': headers or {}
        }
    
    def get(self, url: str, **kwargs):
        """Mock GET request."""
        self.call_count += 1
        if url in self.responses:
            response_data = self.responses[url]
            mock_response = MockResponse(
                status_code=response_data['status_code'],
                json_data=response_data['json_data'],
                text=response_data['text'],
                headers=response_data['headers']
            )
            return mock_response
        else:
            # Return 404 for unknown URLs
            return MockResponse(status_code=404)


class MockResponse:
    """Mock HTTP response object."""
    
    def __init__(self, status_code: int = 200, json_data: Dict = None, text: str = None, headers: Dict = None):
        self.status_code = status_code
        self._json_data = json_data
        self.text = text or ""
        self.headers = headers or {}
    
    def json(self):
        """Return JSON data."""
        if self._json_data is not None:
            return self._json_data
        raise ValueError("No JSON data available")
    
    def raise_for_status(self):
        """Raise HTTPError for bad status codes."""
        if self.status_code >= 400:
            raise Exception(f"HTTP {self.status_code}")
    
    def iter_content(self, chunk_size=1024, decode_unicode=False):
        """Mock content iteration."""
        if self.text:
            for i in range(0, len(self.text), chunk_size):
                yield self.text[i:i+chunk_size]


@pytest.fixture
def mock_requests():
    """Provide a mock requests object for testing."""
    return MockRequests()


# Pytest marks
def pytest_configure(config):
    """Configure custom pytest markers."""
    config.addinivalue_line("markers", "unit: mark test as unit test")
    config.addinivalue_line("markers", "integration: mark test as integration test")
    config.addinivalue_line("markers", "slow: mark test as slow running")
    config.addinivalue_line("markers", "pipeline: mark test as pipeline related")


# Skip markers for optional dependencies
def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers."""
    for item in items:
        # Add unit marker to tests in unit/ directory
        if "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        
        # Add integration marker to tests in integration/ directory
        elif "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
            
        # Add pipeline marker to tests in pipeline/ directory
        elif "pipeline" in str(item.fspath):
            item.add_marker(pytest.mark.pipeline)