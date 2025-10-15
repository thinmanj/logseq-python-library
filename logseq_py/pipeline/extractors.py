"""
Content Extractors for Pipeline Processing

Provides extractors for various external content sources including URLs,
YouTube videos, Twitter posts, and other web content.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Union
import re
import requests
from urllib.parse import urlparse, parse_qs
from datetime import datetime
import logging

from ..models import Block


class ContentExtractor(ABC):
    """Abstract base class for content extractors."""
    
    def __init__(self, name: str):
        self.name = name
        self.logger = logging.getLogger(f"extractor.{name}")
    
    @abstractmethod
    def can_extract(self, block: Block) -> bool:
        """Check if this extractor can process the given block."""
        pass
    
    @abstractmethod
    def extract(self, block: Block) -> Optional[Dict[str, Any]]:
        """Extract content from the block."""
        pass
    
    def get_urls_from_block(self, block: Block) -> List[str]:
        """Extract URLs from block content."""
        if not block.content:
            return []
        
        # Match various URL patterns
        url_pattern = r'https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:[\w.])*)?)?'
        return re.findall(url_pattern, block.content, re.IGNORECASE)


class URLExtractor(ContentExtractor):
    """Extract content from general web URLs."""
    
    def __init__(self):
        super().__init__("url")
        self.timeout = 10
        self.max_content_length = 50000  # 50KB limit
        
    def can_extract(self, block: Block) -> bool:
        """Check if block contains extractable URLs."""
        urls = self.get_urls_from_block(block)
        return len(urls) > 0
    
    def extract(self, block: Block) -> Optional[Dict[str, Any]]:
        """Extract content from URLs in the block."""
        urls = self.get_urls_from_block(block)
        if not urls:
            return None
        
        extracted_content = []
        
        for url in urls:
            try:
                content = self._extract_url_content(url)
                if content:
                    extracted_content.append(content)
                    
            except Exception as e:
                self.logger.warning(f"Failed to extract from {url}: {e}")
        
        if not extracted_content:
            return None
        
        return {
            'type': 'url',
            'urls': urls,
            'content': extracted_content,
            'extracted_at': datetime.now().isoformat()
        }
    
    def _extract_url_content(self, url: str) -> Optional[Dict[str, Any]]:
        """Extract content from a single URL."""
        try:
            # Set user agent to avoid blocking
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=self.timeout, stream=True)
            response.raise_for_status()
            
            # Check content type
            content_type = response.headers.get('content-type', '').lower()
            if 'text/html' not in content_type:
                return {
                    'url': url,
                    'title': None,
                    'text': None,
                    'error': f'Unsupported content type: {content_type}'
                }
            
            # Read content with size limit
            content = ''
            size = 0
            for chunk in response.iter_content(chunk_size=1024, decode_unicode=True):
                if chunk:
                    content += chunk
                    size += len(chunk)
                    if size > self.max_content_length:
                        break
            
            # Parse HTML content
            title, text = self._parse_html_content(content)
            
            return {
                'url': url,
                'title': title,
                'text': text,
                'content_type': content_type,
                'size': size
            }
            
        except requests.RequestException as e:
            return {
                'url': url,
                'title': None, 
                'text': None,
                'error': str(e)
            }
    
    def _parse_html_content(self, html_content: str) -> tuple[Optional[str], Optional[str]]:
        """Parse HTML to extract title and text content."""
        try:
            from bs4 import BeautifulSoup
            
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Extract title
            title_tag = soup.find('title')
            title = title_tag.get_text().strip() if title_tag else None
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Extract text content
            text = soup.get_text()
            
            # Clean up text
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            # Limit text length
            if len(text) > 5000:
                text = text[:5000] + "..."
            
            return title, text
            
        except ImportError:
            # Fallback without BeautifulSoup
            self.logger.warning("BeautifulSoup not available, using regex fallback")
            
            # Extract title with regex
            title_match = re.search(r'<title[^>]*>([^<]+)</title>', html_content, re.IGNORECASE)
            title = title_match.group(1).strip() if title_match else None
            
            # Remove HTML tags for text
            text = re.sub(r'<[^>]+>', ' ', html_content)
            text = re.sub(r'\s+', ' ', text).strip()
            
            if len(text) > 5000:
                text = text[:5000] + "..."
            
            return title, text


class YouTubeExtractor(ContentExtractor):
    """Extract metadata from YouTube URLs."""
    
    def __init__(self):
        super().__init__("youtube")
        self.youtube_patterns = [
            r'(?:youtube\.com/watch\?v=|youtu\.be/)([a-zA-Z0-9_-]{11})',
            r'youtube\.com/embed/([a-zA-Z0-9_-]{11})',
            r'youtube\.com/v/([a-zA-Z0-9_-]{11})'
        ]
    
    def can_extract(self, block: Block) -> bool:
        """Check if block contains YouTube URLs."""
        if not block.content:
            return False
        
        for pattern in self.youtube_patterns:
            if re.search(pattern, block.content, re.IGNORECASE):
                return True
        
        return False
    
    def extract(self, block: Block) -> Optional[Dict[str, Any]]:
        """Extract YouTube video information."""
        if not block.content:
            return None
        
        video_ids = []
        for pattern in self.youtube_patterns:
            matches = re.findall(pattern, block.content, re.IGNORECASE)
            video_ids.extend(matches)
        
        if not video_ids:
            return None
        
        # Remove duplicates while preserving order
        unique_video_ids = list(dict.fromkeys(video_ids))
        
        extracted_videos = []
        for video_id in unique_video_ids:
            try:
                video_info = self._extract_video_info(video_id)
                if video_info:
                    extracted_videos.append(video_info)
            except Exception as e:
                self.logger.warning(f"Failed to extract YouTube video {video_id}: {e}")
        
        if not extracted_videos:
            return None
        
        return {
            'type': 'youtube',
            'videos': extracted_videos,
            'extracted_at': datetime.now().isoformat()
        }
    
    def _extract_video_info(self, video_id: str) -> Optional[Dict[str, Any]]:
        """Extract information for a single YouTube video."""
        # Try to get video info from YouTube's oEmbed API
        try:
            oembed_url = f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={video_id}&format=json"
            response = requests.get(oembed_url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'video_id': video_id,
                    'url': f"https://www.youtube.com/watch?v={video_id}",
                    'title': data.get('title'),
                    'author_name': data.get('author_name'),
                    'author_url': data.get('author_url'),
                    'thumbnail_url': data.get('thumbnail_url'),
                    'width': data.get('width'),
                    'height': data.get('height')
                }
            else:
                # Fallback with basic info
                return {
                    'video_id': video_id,
                    'url': f"https://www.youtube.com/watch?v={video_id}",
                    'title': None,
                    'error': f'Could not fetch video info: {response.status_code}'
                }
                
        except Exception as e:
            return {
                'video_id': video_id,
                'url': f"https://www.youtube.com/watch?v={video_id}",
                'title': None,
                'error': str(e)
            }


class TwitterExtractor(ContentExtractor):
    """Extract information from Twitter URLs."""
    
    def __init__(self):
        super().__init__("twitter")
        self.twitter_patterns = [
            r'twitter\.com/\w+/status/(\d+)',
            r'x\.com/\w+/status/(\d+)'
        ]
    
    def can_extract(self, block: Block) -> bool:
        """Check if block contains Twitter URLs."""
        if not block.content:
            return False
        
        for pattern in self.twitter_patterns:
            if re.search(pattern, block.content, re.IGNORECASE):
                return True
        
        return False
    
    def extract(self, block: Block) -> Optional[Dict[str, Any]]:
        """Extract Twitter post information."""
        if not block.content:
            return None
        
        tweet_ids = []
        for pattern in self.twitter_patterns:
            matches = re.findall(pattern, block.content, re.IGNORECASE)
            tweet_ids.extend(matches)
        
        if not tweet_ids:
            return None
        
        # Remove duplicates while preserving order
        unique_tweet_ids = list(dict.fromkeys(tweet_ids))
        
        extracted_tweets = []
        for tweet_id in unique_tweet_ids:
            try:
                tweet_info = self._extract_tweet_info(tweet_id)
                if tweet_info:
                    extracted_tweets.append(tweet_info)
            except Exception as e:
                self.logger.warning(f"Failed to extract tweet {tweet_id}: {e}")
        
        if not extracted_tweets:
            return None
        
        return {
            'type': 'twitter',
            'tweets': extracted_tweets,
            'extracted_at': datetime.now().isoformat()
        }
    
    def _extract_tweet_info(self, tweet_id: str) -> Dict[str, Any]:
        """Extract information for a single tweet."""
        # Note: Twitter API requires authentication, so this is a basic implementation
        # For production use, integrate with Twitter API v2
        
        twitter_url = f"https://twitter.com/i/status/{tweet_id}"
        x_url = f"https://x.com/i/status/{tweet_id}"
        
        return {
            'tweet_id': tweet_id,
            'twitter_url': twitter_url,
            'x_url': x_url,
            'title': f"Tweet {tweet_id}",
            'text': None,  # Would need API access to get content
            'author': None,
            'created_at': None,
            'note': 'Full content extraction requires Twitter API access'
        }


class GitHubExtractor(ContentExtractor):
    """Extract information from GitHub URLs."""
    
    def __init__(self):
        super().__init__("github")
        self.github_patterns = [
            r'github\.com/([^/]+)/([^/]+)(?:/([^?\s]+))?',
            r'raw\.githubusercontent\.com/([^/]+)/([^/]+)/([^/]+)/(.+)'
        ]
    
    def can_extract(self, block: Block) -> bool:
        """Check if block contains GitHub URLs."""
        if not block.content:
            return False
        
        return bool(re.search(r'github\.com|raw\.githubusercontent\.com', block.content, re.IGNORECASE))
    
    def extract(self, block: Block) -> Optional[Dict[str, Any]]:
        """Extract GitHub repository/file information."""
        urls = self.get_urls_from_block(block)
        github_urls = [url for url in urls if 'github.com' in url or 'githubusercontent.com' in url]
        
        if not github_urls:
            return None
        
        extracted_repos = []
        for url in github_urls:
            try:
                repo_info = self._extract_repo_info(url)
                if repo_info:
                    extracted_repos.append(repo_info)
            except Exception as e:
                self.logger.warning(f"Failed to extract GitHub info from {url}: {e}")
        
        if not extracted_repos:
            return None
        
        return {
            'type': 'github',
            'repositories': extracted_repos,
            'extracted_at': datetime.now().isoformat()
        }
    
    def _extract_repo_info(self, url: str) -> Optional[Dict[str, Any]]:
        """Extract repository information from GitHub URL."""
        # Parse GitHub URL
        match = re.search(r'github\.com/([^/]+)/([^/]+)(?:/([^?\s]+))?', url)
        if not match:
            return None
        
        owner, repo_name, path = match.groups()
        
        # Clean repo name
        repo_name = repo_name.rstrip('/')
        if repo_name.endswith('.git'):
            repo_name = repo_name[:-4]
        
        try:
            # Try to get repository information from GitHub API
            api_url = f"https://api.github.com/repos/{owner}/{repo_name}"
            response = requests.get(api_url, timeout=5)
            
            if response.status_code == 200:
                repo_data = response.json()
                return {
                    'url': url,
                    'owner': owner,
                    'name': repo_name,
                    'full_name': repo_data.get('full_name'),
                    'description': repo_data.get('description'),
                    'language': repo_data.get('language'),
                    'stars': repo_data.get('stargazers_count'),
                    'forks': repo_data.get('forks_count'),
                    'created_at': repo_data.get('created_at'),
                    'updated_at': repo_data.get('updated_at'),
                    'path': path
                }
            else:
                # Fallback with basic info
                return {
                    'url': url,
                    'owner': owner,
                    'name': repo_name,
                    'full_name': f"{owner}/{repo_name}",
                    'path': path,
                    'error': f'Could not fetch repo info: {response.status_code}'
                }
                
        except Exception as e:
            return {
                'url': url,
                'owner': owner,
                'name': repo_name,
                'path': path,
                'error': str(e)
            }


class ExtractorRegistry:
    """Registry for managing content extractors."""
    
    def __init__(self):
        self.extractors: Dict[str, ContentExtractor] = {}
        self.logger = logging.getLogger("extractor.registry")
        
        # Register default extractors
        self.register_defaults()
    
    def register(self, extractor: ContentExtractor):
        """Register an extractor."""
        self.extractors[extractor.name] = extractor
        self.logger.info(f"Registered extractor: {extractor.name}")
    
    def get(self, name: str) -> Optional[ContentExtractor]:
        """Get extractor by name."""
        return self.extractors.get(name)
    
    def get_all(self) -> Dict[str, ContentExtractor]:
        """Get all registered extractors."""
        return self.extractors.copy()
    
    def get_applicable_extractors(self, block: Block) -> List[ContentExtractor]:
        """Get extractors that can process the given block."""
        applicable = []
        for extractor in self.extractors.values():
            if extractor.can_extract(block):
                applicable.append(extractor)
        return applicable
    
    def register_defaults(self):
        """Register default extractors."""
        self.register(URLExtractor())
        self.register(YouTubeExtractor())
        self.register(TwitterExtractor())
        self.register(GitHubExtractor())


# Global registry instance
extractor_registry = ExtractorRegistry()


# Convenience functions for getting extractors
def get_extractor(name: str) -> Optional[ContentExtractor]:
    """Get extractor by name from global registry."""
    return extractor_registry.get(name)


def get_all_extractors() -> Dict[str, ContentExtractor]:
    """Get all extractors from global registry."""
    return extractor_registry.get_all()


def extract_from_block(block: Block, extractor_names: List[str] = None) -> Dict[str, Any]:
    """Extract content from block using specified extractors."""
    results = {}
    
    if extractor_names:
        extractors = [get_extractor(name) for name in extractor_names]
        extractors = [e for e in extractors if e is not None]
    else:
        extractors = extractor_registry.get_applicable_extractors(block)
    
    for extractor in extractors:
        try:
            if extractor.can_extract(block):
                result = extractor.extract(block)
                if result:
                    results[extractor.name] = result
        except Exception as e:
            results[extractor.name] = {'error': str(e)}
    
    return results