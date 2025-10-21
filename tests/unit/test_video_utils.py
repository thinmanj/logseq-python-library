"""
Unit tests for video title extraction utilities.
"""

import pytest
from unittest.mock import Mock, patch
from logseq_py.utils import LogseqUtils


class TestVideoUtils:
    """Test video utility functions."""
    
    def test_extract_video_urls_youtube(self):
        """Test extracting YouTube URLs from text."""
        text = """
        Check out these videos:
        - https://www.youtube.com/watch?v=dQw4w9WgXcQ
        - Short link: https://youtu.be/dQw4w9WgXcQ
        - Embed: https://www.youtube.com/embed/dQw4w9WgXcQ
        - Shorts: https://www.youtube.com/shorts/dQw4w9WgXcQ
        """
        
        urls = LogseqUtils.extract_video_urls(text)
        
        assert len(urls) == 4
        assert "https://www.youtube.com/watch?v=dQw4w9WgXcQ" in urls
        assert "https://youtu.be/dQw4w9WgXcQ" in urls
        assert "https://www.youtube.com/embed/dQw4w9WgXcQ" in urls
        assert "https://www.youtube.com/shorts/dQw4w9WgXcQ" in urls
    
    def test_extract_video_urls_vimeo(self):
        """Test extracting Vimeo URLs from text."""
        text = """
        Vimeo videos:
        - https://vimeo.com/148751763
        - Channel: https://vimeo.com/channels/staffpicks/123456
        - Group: https://vimeo.com/groups/shortfilms/videos/789012
        """
        
        urls = LogseqUtils.extract_video_urls(text)
        
        assert len(urls) == 3
        assert "https://vimeo.com/148751763" in urls
        assert "https://vimeo.com/channels/staffpicks/123456" in urls
        assert "https://vimeo.com/groups/shortfilms/videos/789012" in urls
    
    def test_extract_video_urls_mixed_platforms(self):
        """Test extracting URLs from multiple platforms."""
        text = """
        Mixed platform videos:
        - YouTube: https://www.youtube.com/watch?v=dQw4w9WgXcQ
        - Vimeo: https://vimeo.com/148751763
        - TikTok: https://www.tiktok.com/@user/video/1234567890
        - Twitch: https://www.twitch.tv/videos/123456
        - Dailymotion: https://www.dailymotion.com/video/x2jvvep
        - Regular link: https://www.example.com (should be ignored)
        """
        
        urls = LogseqUtils.extract_video_urls(text)
        
        assert len(urls) == 4  # TikTok pattern doesn't match, should not include example.com
        assert "https://www.youtube.com/watch?v=dQw4w9WgXcQ" in urls
        assert "https://vimeo.com/148751763" in urls
        assert "https://www.twitch.tv/videos/123456" in urls
        assert "https://www.dailymotion.com/video/x2jvvep" in urls
        assert "https://www.example.com" not in urls
    
    def test_extract_video_urls_empty_text(self):
        """Test extracting URLs from empty text."""
        assert LogseqUtils.extract_video_urls("") == []
        assert LogseqUtils.extract_video_urls("No videos here!") == []
    
    @patch('logseq_py.pipeline.extractors.YouTubeExtractor')
    @patch('logseq_py.pipeline.extractors.VideoPlatformExtractor')
    def test_get_video_title_youtube(self, mock_platform_extractor, mock_youtube_extractor):
        """Test getting video title from YouTube URL."""
        # Mock YouTube extractor
        mock_yt_instance = Mock()
        mock_yt_instance.can_extract.return_value = True
        mock_yt_instance.extract.return_value = {
            'videos': [{'title': 'Never Gonna Give You Up'}]
        }
        mock_youtube_extractor.return_value = mock_yt_instance
        
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        title = LogseqUtils.get_video_title(url)
        
        assert title == "Never Gonna Give You Up"
        mock_yt_instance.can_extract.assert_called_once()
        mock_yt_instance.extract.assert_called_once()
    
    @patch('logseq_py.pipeline.extractors.YouTubeExtractor')
    @patch('logseq_py.pipeline.extractors.VideoPlatformExtractor')
    def test_get_video_title_vimeo(self, mock_platform_extractor, mock_youtube_extractor):
        """Test getting video title from Vimeo URL."""
        # Mock YouTube extractor (should not match)
        mock_yt_instance = Mock()
        mock_yt_instance.can_extract.return_value = False
        mock_youtube_extractor.return_value = mock_yt_instance
        
        # Mock platform extractor
        mock_platform_instance = Mock()
        mock_platform_instance.can_extract.return_value = True
        mock_platform_instance.extract.return_value = {
            'videos': [{'title': 'Awesome Vimeo Video'}]
        }
        mock_platform_extractor.return_value = mock_platform_instance
        
        url = "https://vimeo.com/148751763"
        title = LogseqUtils.get_video_title(url)
        
        assert title == "Awesome Vimeo Video"
        mock_platform_instance.can_extract.assert_called_once()
        mock_platform_instance.extract.assert_called_once()
    
    @patch('logseq_py.pipeline.extractors.YouTubeExtractor')
    @patch('logseq_py.pipeline.extractors.VideoPlatformExtractor')
    def test_get_video_title_unsupported(self, mock_platform_extractor, mock_youtube_extractor):
        """Test getting video title from unsupported URL."""
        # Mock both extractors to not match
        mock_yt_instance = Mock()
        mock_yt_instance.can_extract.return_value = False
        mock_youtube_extractor.return_value = mock_yt_instance
        
        mock_platform_instance = Mock()
        mock_platform_instance.can_extract.return_value = False
        mock_platform_extractor.return_value = mock_platform_instance
        
        url = "https://www.example.com/video"
        title = LogseqUtils.get_video_title(url)
        
        assert title is None
    
    @patch('logseq_py.pipeline.extractors.YouTubeExtractor')
    @patch('logseq_py.pipeline.extractors.VideoPlatformExtractor')
    def test_get_video_info_comprehensive(self, mock_platform_extractor, mock_youtube_extractor):
        """Test getting comprehensive video information."""
        # Mock YouTube extractor
        mock_yt_instance = Mock()
        mock_yt_instance.can_extract.return_value = True
        mock_yt_instance.extract.return_value = {
            'videos': [{
                'title': 'Never Gonna Give You Up',
                'author_name': 'Rick Astley',
                'duration': 'PT3M33S',
                'view_count': 1000000,
                'status': 'success'
            }]
        }
        mock_youtube_extractor.return_value = mock_yt_instance
        
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        info = LogseqUtils.get_video_info(url)
        
        assert info is not None
        assert info['title'] == 'Never Gonna Give You Up'
        assert info['author_name'] == 'Rick Astley'
        assert info['duration'] == 'PT3M33S'
        assert info['view_count'] == 1000000
        assert info['status'] == 'success'
    
    @patch('logseq_py.utils.LogseqUtils.get_video_title')
    def test_get_multiple_video_titles(self, mock_get_title):
        """Test getting multiple video titles at once."""
        # Mock the get_video_title function
        def mock_title_func(url, youtube_api_key=None):
            titles = {
                "https://www.youtube.com/watch?v=dQw4w9WgXcQ": "Never Gonna Give You Up",
                "https://vimeo.com/148751763": "Vimeo Video",
                "https://www.tiktok.com/@user/video/123": None  # Failed extraction
            }
            return titles.get(url)
        
        mock_get_title.side_effect = mock_title_func
        
        urls = [
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "https://vimeo.com/148751763",
            "https://www.tiktok.com/@user/video/123"
        ]
        
        results = LogseqUtils.get_multiple_video_titles(urls)
        
        assert len(results) == 3
        assert results["https://www.youtube.com/watch?v=dQw4w9WgXcQ"] == "Never Gonna Give You Up"
        assert results["https://vimeo.com/148751763"] == "Vimeo Video"
        assert results["https://www.tiktok.com/@user/video/123"] is None
        
        # Verify each URL was called once
        assert mock_get_title.call_count == 3
    
    def test_get_multiple_video_titles_empty_list(self):
        """Test getting titles for empty URL list."""
        results = LogseqUtils.get_multiple_video_titles([])
        assert results == {}
    
    @patch('logseq_py.pipeline.extractors.YouTubeExtractor')
    @patch('logseq_py.pipeline.extractors.VideoPlatformExtractor')
    def test_get_video_info_with_api_key(self, mock_platform_extractor, mock_youtube_extractor):
        """Test getting video info with YouTube API key."""
        mock_yt_instance = Mock()
        mock_yt_instance.can_extract.return_value = True
        mock_yt_instance.extract.return_value = {
            'videos': [{'title': 'Enhanced Video Info'}]
        }
        mock_youtube_extractor.return_value = mock_yt_instance
        
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        api_key = "fake_api_key"
        
        info = LogseqUtils.get_video_info(url, api_key)
        
        assert info is not None
        assert info['title'] == 'Enhanced Video Info'
        
        # Verify API key was passed to extractor
        mock_youtube_extractor.assert_called_once_with(api_key=api_key)
    
    @patch('logseq_py.pipeline.extractors.YouTubeExtractor')
    @patch('logseq_py.pipeline.extractors.VideoPlatformExtractor')
    def test_get_video_title_with_api_key(self, mock_platform_extractor, mock_youtube_extractor):
        """Test getting video title with YouTube API key."""
        mock_yt_instance = Mock()
        mock_yt_instance.can_extract.return_value = True
        mock_yt_instance.extract.return_value = {
            'videos': [{'title': 'Enhanced Video Title'}]
        }
        mock_youtube_extractor.return_value = mock_yt_instance
        
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        api_key = "fake_api_key"
        
        title = LogseqUtils.get_video_title(url, api_key)
        
        assert title == 'Enhanced Video Title'
        
        # Verify API key was passed through
        mock_youtube_extractor.assert_called_once_with(api_key=api_key)