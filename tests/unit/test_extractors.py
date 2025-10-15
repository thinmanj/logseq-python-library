"""
Unit tests for content extractors.

Tests the various extractor classes and their functionality.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from logseq_py.models import Block
from logseq_py.pipeline.extractors import (
    URLExtractor,
    YouTubeExtractor,
    TwitterExtractor, 
    GitHubExtractor,
    PDFExtractor,
    AcademicPaperExtractor,
    ExtractorRegistry,
    get_extractor,
    get_all_extractors,
    extract_from_block
)


class TestURLExtractor:
    """Test URLExtractor functionality."""
    
    def setup_method(self):
        """Set up test extractor."""
        self.extractor = URLExtractor()
    
    def test_can_extract_with_urls(self):
        """Test can_extract with blocks containing URLs."""
        block = Block(uuid="1", content="Check out https://example.com for more info!")
        assert self.extractor.can_extract(block) is True
        
        block = Block(uuid="2", content="Visit http://test.org and https://another.site/path")
        assert self.extractor.can_extract(block) is True
    
    def test_can_extract_without_urls(self):
        """Test can_extract with blocks without URLs."""
        block = Block(uuid="1", content="Just some regular text without links")
        assert self.extractor.can_extract(block) is False
        
        block = Block(uuid="2", content="")
        assert self.extractor.can_extract(block) is False
        
        block = Block(uuid="3", content=None)
        assert self.extractor.can_extract(block) is False
    
    def test_filter_general_urls(self):
        """Test filtering of specialized URLs."""
        urls = [
            "https://example.com",
            "https://youtube.com/watch?v=abc123",
            "https://twitter.com/user/status/123",
            "https://github.com/user/repo",
            "https://test.org/page"
        ]
        
        general_urls = self.extractor._filter_general_urls(urls)
        
        assert "https://example.com" in general_urls
        assert "https://test.org/page" in general_urls
        assert "https://youtube.com/watch?v=abc123" not in general_urls
        assert "https://twitter.com/user/status/123" not in general_urls
        assert "https://github.com/user/repo" not in general_urls
    
    @patch('logseq_py.pipeline.extractors.requests.Session.get')
    def test_successful_extraction(self, mock_get):
        """Test successful URL content extraction."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {'content-type': 'text/html; charset=utf-8'}
        mock_response.iter_content.return_value = [
            '<html><head><title>Test Page</title></head>',
            '<body><h1>Hello World</h1><p>Test content</p></body></html>'
        ]
        mock_get.return_value = mock_response
        
        block = Block(uuid="1", content="Check out https://example.com")
        
        with patch.object(self.extractor, '_parse_html_content') as mock_parse:
            mock_parse.return_value = {
                'title': 'Test Page',
                'text': 'Hello World Test content',
                'word_count': 4
            }
            
            result = self.extractor.extract(block)
            
            assert result is not None
            assert result['extractor'] == 'url'
            assert result['type'] == 'url'
            assert len(result['content']) == 1
            assert result['content'][0]['status'] == 'success'
            assert result['content'][0]['title'] == 'Test Page'
    
    @patch('logseq_py.pipeline.extractors.requests.Session.get')
    def test_failed_extraction(self, mock_get):
        """Test failed URL content extraction."""
        # Mock failed response
        mock_get.side_effect = Exception("Connection timeout")
        
        block = Block(uuid="1", content="Check out https://example.com")
        result = self.extractor.extract(block)
        
        assert result is not None
        assert result['successful_extractions'] == 0
        assert 'error' in result['content'][0]
    
    def test_parse_html_content_with_beautifulsoup(self):
        """Test HTML parsing with BeautifulSoup."""
        html_content = """
        <html>
        <head>
            <title>Test Article</title>
            <meta name="description" content="Test description">
            <meta name="author" content="Test Author">
            <meta property="og:title" content="OG Title">
        </head>
        <body>
            <article>
                <h1>Main Heading</h1>
                <p>This is test content.</p>
                <h2>Subheading</h2>
                <p>More content here.</p>
                <a href="https://example.com">Example Link</a>
            </article>
        </body>
        </html>
        """
        
        result = self.extractor._parse_html_content(html_content)
        
        assert result['title'] == 'Test Article'
        assert result['description'] == 'Test description'
        assert result['author'] == 'Test Author'
        assert result['open_graph']['title'] == 'OG Title'
        assert len(result['headings']) == 2
        assert result['headings'][0]['level'] == 1
        assert result['headings'][0]['text'] == 'Main Heading'
        assert len(result['links']) == 1
        assert result['links'][0]['url'] == 'https://example.com'
        assert 'This is test content' in result['text']
    
    @patch('logseq_py.pipeline.extractors.BeautifulSoup', side_effect=ImportError)
    def test_parse_html_fallback(self, mock_bs):
        """Test HTML parsing fallback without BeautifulSoup."""
        html_content = '<html><head><title>Test</title></head><body>Content</body></html>'
        
        result = self.extractor._parse_html_content(html_content)
        
        assert result['title'] == 'Test'
        assert result['parsing_method'] == 'regex_fallback'
        assert 'Content' in result['text']


class TestYouTubeExtractor:
    """Test YouTubeExtractor functionality."""
    
    def setup_method(self):
        """Set up test extractor."""
        self.extractor = YouTubeExtractor()
    
    def test_can_extract_youtube_urls(self):
        """Test detection of YouTube URLs."""
        test_cases = [
            "Watch https://youtube.com/watch?v=dQw4w9WgXcQ",
            "Short link: https://youtu.be/dQw4w9WgXcQ",
            "Embedded: https://youtube.com/embed/dQw4w9WgXcQ",
            "Old format: https://youtube.com/v/dQw4w9WgXcQ",
            "Shorts: https://youtube.com/shorts/dQw4w9WgXcQ"
        ]
        
        for content in test_cases:
            block = Block(uuid="1", content=content)
            assert self.extractor.can_extract(block) is True
    
    def test_cannot_extract_non_youtube(self):
        """Test rejection of non-YouTube URLs."""
        block = Block(uuid="1", content="Check out https://vimeo.com/123456789")
        assert self.extractor.can_extract(block) is False
        
        block = Block(uuid="2", content="No URLs here")
        assert self.extractor.can_extract(block) is False
    
    @patch('logseq_py.pipeline.extractors.requests.Session.get')
    def test_extract_with_oembed(self, mock_get):
        """Test extraction using oEmbed API."""
        # Mock successful oEmbed response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'title': 'Test Video',
            'author_name': 'Test Channel',
            'author_url': 'https://youtube.com/channel/test',
            'thumbnail_url': 'https://img.youtube.com/vi/dQw4w9WgXcQ/maxresdefault.jpg'
        }
        mock_get.return_value = mock_response
        
        block = Block(uuid="1", content="Watch https://youtube.com/watch?v=dQw4w9WgXcQ")
        result = self.extractor.extract(block)
        
        assert result is not None
        assert result['type'] == 'youtube'
        assert len(result['videos']) == 1
        
        video = result['videos'][0]
        assert video['video_id'] == 'dQw4w9WgXcQ'
        assert video['title'] == 'Test Video'
        assert video['author_name'] == 'Test Channel'
        assert video['data_source'] == 'oembed'
        assert video['status'] == 'success'
    
    def test_extract_with_api_key(self):
        """Test extraction using YouTube API."""
        extractor = YouTubeExtractor(api_key="test_key")
        
        with patch.object(extractor, '_get_video_from_api') as mock_api:
            mock_api.return_value = {
                'title': 'API Video Title',
                'description': 'Video description',
                'channel_title': 'API Channel',
                'view_count': 1000000,
                'duration_seconds': 240,
                'status': 'success'
            }
            
            block = Block(uuid="1", content="https://youtube.com/watch?v=dQw4w9WgXcQ")
            result = extractor.extract(block)
            
            assert result['api_used'] is True
            video = result['videos'][0]
            assert video['data_source'] == 'youtube_api'
            assert video['title'] == 'API Video Title'
            assert video['view_count'] == 1000000
    
    def test_parse_duration(self):
        """Test ISO 8601 duration parsing."""
        test_cases = [
            ('PT4M13S', 253),  # 4 minutes 13 seconds
            ('PT1H30M', 5400),  # 1 hour 30 minutes
            ('PT45S', 45),  # 45 seconds
            ('PT2H5M10S', 7510),  # 2 hours 5 minutes 10 seconds
        ]
        
        for duration_iso, expected_seconds in test_cases:
            result = self.extractor._parse_duration(duration_iso)
            assert result == expected_seconds
    
    def test_get_best_thumbnail(self):
        """Test thumbnail URL selection."""
        thumbnails = {
            'default': {'url': 'https://img.youtube.com/vi/test/default.jpg'},
            'medium': {'url': 'https://img.youtube.com/vi/test/medium.jpg'},
            'high': {'url': 'https://img.youtube.com/vi/test/high.jpg'},
            'maxres': {'url': 'https://img.youtube.com/vi/test/maxres.jpg'}
        }
        
        result = self.extractor._get_best_thumbnail(thumbnails)
        assert result == 'https://img.youtube.com/vi/test/maxres.jpg'
        
        # Test with partial thumbnails
        partial_thumbnails = {
            'default': {'url': 'https://img.youtube.com/vi/test/default.jpg'},
            'medium': {'url': 'https://img.youtube.com/vi/test/medium.jpg'}
        }
        
        result = self.extractor._get_best_thumbnail(partial_thumbnails)
        assert result == 'https://img.youtube.com/vi/test/medium.jpg'


class TestTwitterExtractor:
    """Test TwitterExtractor functionality."""
    
    def setup_method(self):
        """Set up test extractor."""
        self.extractor = TwitterExtractor()
    
    def test_can_extract_twitter_urls(self):
        """Test detection of Twitter URLs."""
        test_cases = [
            "Check this tweet: https://twitter.com/user/status/1234567890",
            "On X: https://x.com/user/status/1234567890"
        ]
        
        for content in test_cases:
            block = Block(uuid="1", content=content)
            assert self.extractor.can_extract(block) is True
    
    def test_extract_basic_info(self):
        """Test basic tweet information extraction."""
        block = Block(uuid="1", content="See https://twitter.com/test/status/1234567890")
        result = self.extractor.extract(block)
        
        assert result is not None
        assert result['type'] == 'twitter'
        assert len(result['tweets']) == 1
        
        tweet = result['tweets'][0]
        assert tweet['tweet_id'] == '1234567890'
        assert 'twitter_url' in tweet
        assert 'x_url' in tweet


class TestGitHubExtractor:
    """Test GitHubExtractor functionality."""
    
    def setup_method(self):
        """Set up test extractor."""
        self.extractor = GitHubExtractor()
    
    def test_can_extract_github_urls(self):
        """Test detection of GitHub URLs."""
        block = Block(uuid="1", content="Repository: https://github.com/user/repo")
        assert self.extractor.can_extract(block) is True
        
        block = Block(uuid="2", content="Raw file: https://raw.githubusercontent.com/user/repo/main/file.py")
        assert self.extractor.can_extract(block) is True
    
    @patch('logseq_py.pipeline.extractors.requests.get')
    def test_extract_repo_info(self, mock_get):
        """Test GitHub repository information extraction."""
        # Mock GitHub API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'full_name': 'user/repo',
            'description': 'A test repository',
            'language': 'Python',
            'stargazers_count': 100,
            'forks_count': 25,
            'created_at': '2023-01-01T00:00:00Z',
            'updated_at': '2023-12-01T00:00:00Z'
        }
        mock_get.return_value = mock_response
        
        block = Block(uuid="1", content="Check out https://github.com/user/repo")
        result = self.extractor.extract(block)
        
        assert result is not None
        assert result['type'] == 'github'
        assert len(result['repositories']) == 1
        
        repo = result['repositories'][0]
        assert repo['owner'] == 'user'
        assert repo['name'] == 'repo'
        assert repo['description'] == 'A test repository'
        assert repo['language'] == 'Python'
        assert repo['stars'] == 100


class TestPDFExtractor:
    """Test PDFExtractor functionality."""
    
    def setup_method(self):
        """Set up test extractor."""
        self.extractor = PDFExtractor()
    
    def test_can_extract_pdf_urls(self):
        """Test detection of PDF URLs."""
        test_cases = [
            "Document: https://example.com/paper.pdf",
            "arXiv paper: https://arxiv.org/pdf/2301.00001.pdf",
            "bioRxiv: https://biorxiv.org/content/early/2023/paper.full.pdf"
        ]
        
        for content in test_cases:
            block = Block(uuid="1", content=content)
            assert self.extractor.can_extract(block) is True
    
    @patch('logseq_py.pipeline.extractors.requests.head')
    def test_extract_basic_info(self, mock_head):
        """Test basic PDF information extraction."""
        # Mock HEAD response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {
            'content-type': 'application/pdf',
            'content-length': '1048576',
            'last-modified': 'Wed, 01 Jan 2023 00:00:00 GMT'
        }
        mock_head.return_value = mock_response
        
        block = Block(uuid="1", content="Document: https://example.com/paper.pdf")
        
        with patch.object(self.extractor, '_extract_pdf_text', side_effect=ImportError):
            result = self.extractor.extract(block)
            
            assert result is not None
            assert result['type'] == 'pdf'
            assert len(result['documents']) == 1
            
            doc = result['documents'][0]
            assert doc['content_type'] == 'application/pdf'
            assert doc['text_extraction'] == 'unavailable'


class TestAcademicPaperExtractor:
    """Test AcademicPaperExtractor functionality."""
    
    def setup_method(self):
        """Set up test extractor."""
        self.extractor = AcademicPaperExtractor()
    
    def test_can_extract_arxiv_urls(self):
        """Test detection of arXiv URLs."""
        block = Block(uuid="1", content="Paper: https://arxiv.org/abs/2301.00001")
        assert self.extractor.can_extract(block) is True
        
        block = Block(uuid="2", content="PDF: https://arxiv.org/pdf/2301.00001v2.pdf")
        assert self.extractor.can_extract(block) is True
    
    def test_can_extract_doi_urls(self):
        """Test detection of DOI URLs."""
        block = Block(uuid="1", content="Paper: https://doi.org/10.1000/182")
        assert self.extractor.can_extract(block) is True
    
    @patch('logseq_py.pipeline.extractors.requests.Session.get')
    def test_extract_arxiv_info(self, mock_get):
        """Test arXiv paper information extraction."""
        # Mock arXiv API XML response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b'''<?xml version="1.0" encoding="UTF-8"?>
        <feed xmlns="http://www.w3.org/2005/Atom">
            <entry>
                <title>Test Paper Title</title>
                <summary>This is a test abstract for the paper.</summary>
                <published>2023-01-01T00:00:00Z</published>
                <updated>2023-01-02T00:00:00Z</updated>
                <author><name>John Doe</name></author>
                <author><name>Jane Smith</name></author>
                <category term="cs.AI" />
                <category term="cs.LG" />
            </entry>
        </feed>'''
        mock_get.return_value = mock_response
        
        block = Block(uuid="1", content="Paper: https://arxiv.org/abs/2301.00001")
        result = self.extractor.extract(block)
        
        assert result is not None
        assert result['type'] == 'academic_paper'
        assert len(result['papers']) == 1
        
        paper = result['papers'][0]
        assert paper['source'] == 'arxiv'
        assert paper['arxiv_id'] == '2301.00001'
        assert paper['title'] == 'Test Paper Title'
        assert 'test abstract' in paper['abstract'].lower()
        assert 'John Doe' in paper['authors']
        assert 'Jane Smith' in paper['authors']
        assert 'cs.AI' in paper['categories']
    
    @patch('logseq_py.pipeline.extractors.requests.Session.get')
    def test_extract_doi_info(self, mock_get):
        """Test DOI paper information extraction."""
        # Mock Crossref API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'message': {
                'title': ['Test Journal Article'],
                'abstract': 'This is a test abstract.',
                'author': [
                    {'given': 'John', 'family': 'Doe'},
                    {'given': 'Jane', 'family': 'Smith'}
                ],
                'container-title': ['Test Journal'],
                'publisher': 'Test Publisher',
                'published-print': {'date-parts': [[2023, 1, 15]]},
                'volume': '42',
                'issue': '1',
                'page': '1-20',
                'type': 'journal-article'
            }
        }
        mock_get.return_value = mock_response
        
        block = Block(uuid="1", content="Paper: https://doi.org/10.1000/182")
        result = self.extractor.extract(block)
        
        assert result is not None
        paper = result['papers'][0]
        assert paper['source'] == 'doi'
        assert paper['doi'] == '10.1000/182'
        assert paper['title'] == 'Test Journal Article'
        assert paper['journal'] == 'Test Journal'
        assert paper['publisher'] == 'Test Publisher'
        assert 'John Doe' in paper['authors']


class TestExtractorRegistry:
    """Test ExtractorRegistry functionality."""
    
    def setup_method(self):
        """Set up test registry."""
        self.registry = ExtractorRegistry()
    
    def test_default_extractors_registered(self):
        """Test that default extractors are registered."""
        extractors = self.registry.get_all()
        
        expected_extractors = ['url', 'youtube', 'twitter', 'github', 'pdf', 'academic']
        for extractor_name in expected_extractors:
            assert extractor_name in extractors
    
    def test_get_extractor(self):
        """Test getting extractor by name."""
        url_extractor = self.registry.get('url')
        assert isinstance(url_extractor, URLExtractor)
        
        nonexistent = self.registry.get('nonexistent')
        assert nonexistent is None
    
    def test_register_custom_extractor(self):
        """Test registering custom extractor."""
        class CustomExtractor:
            def __init__(self):
                self.name = 'custom'
        
        custom = CustomExtractor()
        self.registry.register(custom)
        
        retrieved = self.registry.get('custom')
        assert retrieved is custom
    
    def test_get_applicable_extractors(self):
        """Test getting applicable extractors for a block."""
        # Block with YouTube URL
        block = Block(uuid="1", content="Watch https://youtube.com/watch?v=test")
        applicable = self.registry.get_applicable_extractors(block)
        
        # Should include YouTube extractor but not others for this specific URL
        extractor_names = [e.name for e in applicable]
        assert 'youtube' in extractor_names
    
    def test_global_functions(self):
        """Test global convenience functions."""
        # Test get_extractor
        url_extractor = get_extractor('url')
        assert isinstance(url_extractor, URLExtractor)
        
        # Test get_all_extractors
        all_extractors = get_all_extractors()
        assert 'youtube' in all_extractors
        assert len(all_extractors) >= 6  # At least our 6 default extractors
    
    def test_extract_from_block(self):
        """Test extract_from_block convenience function."""
        block = Block(uuid="1", content="Check https://example.com and https://youtube.com/watch?v=test")
        
        with patch('logseq_py.pipeline.extractors.URLExtractor.extract') as mock_url:
            with patch('logseq_py.pipeline.extractors.YouTubeExtractor.extract') as mock_yt:
                mock_url.return_value = {'type': 'url', 'data': 'test'}
                mock_yt.return_value = {'type': 'youtube', 'data': 'test'}
                
                results = extract_from_block(block)
                
                # Should have attempted both extractors
                assert 'url' in results or 'youtube' in results
    
    def test_extract_from_block_with_specific_extractors(self):
        """Test extract_from_block with specific extractor names."""
        block = Block(uuid="1", content="https://youtube.com/watch?v=test")
        
        with patch('logseq_py.pipeline.extractors.YouTubeExtractor.extract') as mock_yt:
            mock_yt.return_value = {'type': 'youtube', 'videos': []}
            
            results = extract_from_block(block, extractor_names=['youtube'])
            
            assert 'youtube' in results
            mock_yt.assert_called_once()


class TestExtractorIntegration:
    """Test integration between extractors and other components."""
    
    def test_extractor_error_handling(self):
        """Test extractor error handling."""
        extractor = URLExtractor()
        
        # Test with malformed block
        block = Block(uuid="1", content="https://malformed-url-that-will-fail")
        
        with patch.object(extractor, '_extract_url_content', side_effect=Exception("Network error")):
            result = extractor.extract(block)
            
            # Should handle error gracefully
            assert result is not None
            assert result['successful_extractions'] == 0
            assert 'error' in result['content'][0]
    
    def test_multiple_url_extraction(self):
        """Test extraction from block with multiple URLs."""
        content = '''
        Check these links:
        - https://example.com/page1
        - https://example.com/page2
        - https://youtube.com/watch?v=abc123 (this should be filtered out)
        - https://test.org/another-page
        '''
        
        block = Block(uuid="1", content=content)
        extractor = URLExtractor()
        
        with patch.object(extractor, '_extract_url_content') as mock_extract:
            mock_extract.return_value = {
                'title': 'Test Page',
                'status': 'success'
            }
            
            result = extractor.extract(block)
            
            # Should extract 3 URLs (YouTube filtered out)
            assert result['total_urls'] == 3
            assert mock_extract.call_count == 3
    
    def test_extractor_with_caching_compatibility(self):
        """Test that extractors work with caching system."""
        from logseq_py.pipeline.cache import create_memory_cache, CachedExtractor
        
        cache = create_memory_cache()
        extractor = YouTubeExtractor()
        cached_extractor = CachedExtractor(extractor, cache)
        
        block = Block(uuid="1", content="https://youtube.com/watch?v=test123")
        
        with patch.object(extractor, 'extract') as mock_extract:
            mock_extract.return_value = {'type': 'youtube', 'videos': [{'title': 'Test'}]}
            
            # First call - should hit extractor
            result1 = cached_extractor.extract(block)
            assert mock_extract.call_count == 1
            
            # Second call - should hit cache
            result2 = cached_extractor.extract(block)
            assert mock_extract.call_count == 1  # Not called again
            
            assert result1 == result2