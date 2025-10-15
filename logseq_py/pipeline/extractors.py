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
    
    def __init__(self, timeout: int = 10, max_content_length: int = 100000):
        super().__init__("url")
        self.timeout = timeout
        self.max_content_length = max_content_length  # 100KB default limit
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
    def can_extract(self, block: Block) -> bool:
        """Check if block contains extractable URLs."""
        urls = self.get_urls_from_block(block)
        return len(urls) > 0
    
    def extract(self, block: Block) -> Optional[Dict[str, Any]]:
        """Extract content from URLs in the block."""
        urls = self.get_urls_from_block(block)
        if not urls:
            return None
        
        # Filter out specialized URLs handled by other extractors
        general_urls = self._filter_general_urls(urls)
        if not general_urls:
            return None
        
        extracted_content = []
        
        for url in general_urls:
            try:
                content = self._extract_url_content(url)
                if content:
                    extracted_content.append(content)
                    
            except Exception as e:
                self.logger.warning(f"Failed to extract from {url}: {e}")
                extracted_content.append({
                    'url': url,
                    'error': str(e),
                    'extracted_at': datetime.now().isoformat()
                })
        
        if not extracted_content:
            return None
        
        return {
            'extractor': self.name,
            'type': 'url',
            'urls': general_urls,
            'content': extracted_content,
            'total_urls': len(general_urls),
            'successful_extractions': len([c for c in extracted_content if 'error' not in c]),
            'extracted_at': datetime.now().isoformat()
        }
    
    def _filter_general_urls(self, urls: List[str]) -> List[str]:
        """Filter out URLs that should be handled by specialized extractors."""
        specialized_patterns = [
            r'youtube\.com|youtu\.be',
            r'twitter\.com|x\.com',
            r'github\.com|githubusercontent\.com',
            r'vimeo\.com',
            r'tiktok\.com',
            r'twitch\.tv|clips\.twitch\.tv',
            r'dailymotion\.com|dai\.ly',
        ]
        
        general_urls = []
        for url in urls:
            is_specialized = any(re.search(pattern, url, re.IGNORECASE) for pattern in specialized_patterns)
            if not is_specialized:
                general_urls.append(url)
        
        return general_urls
    
    def _extract_url_content(self, url: str) -> Optional[Dict[str, Any]]:
        """Extract content from a single URL."""
        try:
            response = self.session.get(url, timeout=self.timeout, stream=True)
            response.raise_for_status()
            
            # Check content type
            content_type = response.headers.get('content-type', '').lower()
            if 'text/html' not in content_type:
                return {
                    'url': url,
                    'title': None,
                    'text': None,
                    'content_type': content_type,
                    'status': 'unsupported_content_type',
                    'extracted_at': datetime.now().isoformat()
                }
            
            # Read content with size limit
            content = ''
            size = 0
            for chunk in response.iter_content(chunk_size=1024, decode_unicode=True):
                if chunk:
                    content += chunk
                    size += len(chunk)
                    if size > self.max_content_length:
                        self.logger.info(f"Content truncated at {self.max_content_length} bytes for {url}")
                        break
            
            # Parse HTML content
            parsed_data = self._parse_html_content(content)
            
            result = {
                'url': url,
                'status': 'success',
                'content_type': content_type,
                'size': size,
                'extracted_at': datetime.now().isoformat()
            }
            result.update(parsed_data)
            
            return result
            
        except requests.RequestException as e:
            return {
                'url': url,
                'title': None, 
                'text': None,
                'status': 'request_error',
                'error': str(e),
                'extracted_at': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'url': url,
                'title': None,
                'text': None, 
                'status': 'processing_error',
                'error': str(e),
                'extracted_at': datetime.now().isoformat()
            }
    
    def _parse_html_content(self, html_content: str) -> Dict[str, Any]:
        """Parse HTML to extract title, text content, and metadata."""
        try:
            from bs4 import BeautifulSoup
            
            soup = BeautifulSoup(html_content, 'html.parser')
            result = {}
            
            # Extract title (try multiple sources)
            title = None
            if soup.find('title'):
                title = soup.find('title').get_text().strip()
            elif soup.find('meta', {'property': 'og:title'}):
                title = soup.find('meta', {'property': 'og:title'}).get('content', '').strip()
            elif soup.find('meta', {'name': 'twitter:title'}):
                title = soup.find('meta', {'name': 'twitter:title'}).get('content', '').strip()
            elif soup.find('h1'):
                title = soup.find('h1').get_text().strip()
            
            result['title'] = title if title else None
            
            # Extract description
            description = None
            if soup.find('meta', {'name': 'description'}):
                description = soup.find('meta', {'name': 'description'}).get('content', '').strip()
            elif soup.find('meta', {'property': 'og:description'}):
                description = soup.find('meta', {'property': 'og:description'}).get('content', '').strip()
            elif soup.find('meta', {'name': 'twitter:description'}):
                description = soup.find('meta', {'name': 'twitter:description'}).get('content', '').strip()
            
            result['description'] = description if description else None
            
            # Extract Open Graph metadata
            og_data = {}
            for og_tag in soup.find_all('meta', {'property': lambda x: x and x.startswith('og:')}):
                property_name = og_tag.get('property', '')[3:]  # Remove 'og:' prefix
                content = og_tag.get('content', '')
                if property_name and content:
                    og_data[property_name] = content
            
            result['open_graph'] = og_data if og_data else None
            
            # Extract author information
            author = None
            if soup.find('meta', {'name': 'author'}):
                author = soup.find('meta', {'name': 'author'}).get('content', '').strip()
            elif soup.find('meta', {'name': 'article:author'}):
                author = soup.find('meta', {'name': 'article:author'}).get('content', '').strip()
            
            result['author'] = author if author else None
            
            # Extract keywords
            keywords = None
            if soup.find('meta', {'name': 'keywords'}):
                keywords = soup.find('meta', {'name': 'keywords'}).get('content', '').strip().split(',')
                keywords = [k.strip() for k in keywords if k.strip()]
            
            result['keywords'] = keywords if keywords else None
            
            # Extract publication date
            pub_date = None
            for date_selector in [
                {'name': 'article:published_time'},
                {'property': 'article:published_time'},
                {'name': 'publication_date'},
                {'name': 'date'}
            ]:
                date_tag = soup.find('meta', date_selector)
                if date_tag:
                    pub_date = date_tag.get('content', '').strip()
                    break
            
            result['published_date'] = pub_date if pub_date else None
            
            # Remove script, style, and navigation elements
            for element in soup(["script", "style", "nav", "header", "footer", "aside"]):
                element.decompose()
            
            # Extract main content (prioritize article, main, or content divs)
            main_content = None
            for selector in ['article', 'main', '[role="main"]', '.content', '#content', '.post-content', '.entry-content']:
                content_elem = soup.select_one(selector)
                if content_elem:
                    main_content = content_elem
                    break
            
            # Fallback to body if no main content found
            if main_content is None:
                main_content = soup.find('body') or soup
            
            # Extract text content
            text = main_content.get_text()
            
            # Clean up text
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            # Extract headings
            headings = []
            for i in range(1, 7):  # h1 to h6
                for heading in main_content.find_all(f'h{i}'):
                    heading_text = heading.get_text().strip()
                    if heading_text:
                        headings.append({
                            'level': i,
                            'text': heading_text
                        })
            
            result['headings'] = headings if headings else None
            
            # Extract links
            links = []
            for link in main_content.find_all('a', href=True):
                link_text = link.get_text().strip()
                href = link.get('href')
                if href and link_text:
                    links.append({
                        'text': link_text,
                        'url': href
                    })
            
            result['links'] = links[:20] if links else None  # Limit to first 20 links
            
            # Limit main text length and add summary
            if len(text) > 10000:
                result['text'] = text[:10000] + "..."
                result['text_truncated'] = True
            else:
                result['text'] = text
                result['text_truncated'] = False
            
            result['text_length'] = len(text)
            result['word_count'] = len(text.split()) if text else 0
            
            return result
            
        except ImportError:
            # Fallback without BeautifulSoup
            self.logger.warning("BeautifulSoup not available, using regex fallback")
            
            result = {}
            
            # Extract title with regex
            title_match = re.search(r'<title[^>]*>([^<]+)</title>', html_content, re.IGNORECASE)
            result['title'] = title_match.group(1).strip() if title_match else None
            
            # Extract description
            desc_match = re.search(r'<meta[^>]*name=["\']description["\'][^>]*content=["\']([^"\'>]*)["\']', html_content, re.IGNORECASE)
            result['description'] = desc_match.group(1).strip() if desc_match else None
            
            # Remove HTML tags for text
            text = re.sub(r'<script[^>]*>.*?</script>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
            text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL | re.IGNORECASE)
            text = re.sub(r'<[^>]+>', ' ', text)
            text = re.sub(r'\s+', ' ', text).strip()
            
            if len(text) > 10000:
                result['text'] = text[:10000] + "..."
                result['text_truncated'] = True
            else:
                result['text'] = text
                result['text_truncated'] = False
            
            result['text_length'] = len(text)
            result['word_count'] = len(text.split()) if text else 0
            result['parsing_method'] = 'regex_fallback'
            
            return result


class YouTubeExtractor(ContentExtractor):
    """Extract metadata from YouTube URLs."""
    
    def __init__(self, api_key: Optional[str] = None):
        super().__init__("youtube")
        self.api_key = api_key
        self.youtube_patterns = [
            r'(?:youtube\.com/watch\?v=|youtu\.be/)([a-zA-Z0-9_-]{11})',
            r'youtube\.com/embed/([a-zA-Z0-9_-]{11})',
            r'youtube\.com/v/([a-zA-Z0-9_-]{11})',
            r'youtube\.com/shorts/([a-zA-Z0-9_-]{11})'
        ]
        self.session = requests.Session()
    
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
            'extractor': self.name,
            'type': 'youtube',
            'videos': extracted_videos,
            'total_videos': len(unique_video_ids),
            'successful_extractions': len(extracted_videos),
            'api_used': self.api_key is not None,
            'extracted_at': datetime.now().isoformat()
        }
    
    def _extract_video_info(self, video_id: str) -> Optional[Dict[str, Any]]:
        """Extract information for a single YouTube video."""
        base_info = {
            'video_id': video_id,
            'url': f"https://www.youtube.com/watch?v={video_id}",
            'short_url': f"https://youtu.be/{video_id}",
            'extracted_at': datetime.now().isoformat()
        }
        
        # Try YouTube Data API first if available
        if self.api_key:
            try:
                api_info = self._get_video_from_api(video_id)
                if api_info:
                    base_info.update(api_info)
                    base_info['data_source'] = 'youtube_api'
                    return base_info
            except Exception as e:
                self.logger.warning(f"YouTube API failed for {video_id}: {e}")
        
        # Fallback to oEmbed API
        try:
            oembed_url = f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={video_id}&format=json"
            response = self.session.get(oembed_url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                base_info.update({
                    'title': data.get('title'),
                    'author_name': data.get('author_name'),
                    'author_url': data.get('author_url'),
                    'thumbnail_url': data.get('thumbnail_url'),
                    'width': data.get('width'),
                    'height': data.get('height'),
                    'data_source': 'oembed',
                    'status': 'success'
                })
                return base_info
            else:
                base_info.update({
                    'title': None,
                    'status': 'failed',
                    'error': f'oEmbed API returned {response.status_code}',
                    'data_source': 'oembed'
                })
                return base_info
                
        except Exception as e:
            base_info.update({
                'title': None,
                'status': 'error',
                'error': str(e),
                'data_source': 'oembed'
            })
            return base_info
    
    def _get_video_from_api(self, video_id: str) -> Optional[Dict[str, Any]]:
        """Get video information from YouTube Data API."""
        if not self.api_key:
            return None
        
        api_url = "https://www.googleapis.com/youtube/v3/videos"
        params = {
            'part': 'snippet,statistics,contentDetails,status',
            'id': video_id,
            'key': self.api_key
        }
        
        response = self.session.get(api_url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        if not data.get('items'):
            return None
        
        video_data = data['items'][0]
        snippet = video_data.get('snippet', {})
        statistics = video_data.get('statistics', {})
        content_details = video_data.get('contentDetails', {})
        status = video_data.get('status', {})
        
        # Parse duration from ISO 8601 format (e.g., PT4M13S)
        duration_iso = content_details.get('duration', '')
        duration_seconds = self._parse_duration(duration_iso) if duration_iso else None
        
        return {
            'title': snippet.get('title'),
            'description': snippet.get('description'),
            'channel_id': snippet.get('channelId'),
            'channel_title': snippet.get('channelTitle'),
            'published_at': snippet.get('publishedAt'),
            'duration': duration_iso,
            'duration_seconds': duration_seconds,
            'view_count': int(statistics.get('viewCount', 0)) if statistics.get('viewCount') else None,
            'like_count': int(statistics.get('likeCount', 0)) if statistics.get('likeCount') else None,
            'comment_count': int(statistics.get('commentCount', 0)) if statistics.get('commentCount') else None,
            'tags': snippet.get('tags', []),
            'category_id': snippet.get('categoryId'),
            'default_language': snippet.get('defaultLanguage'),
            'thumbnail_url': self._get_best_thumbnail(snippet.get('thumbnails', {})),
            'privacy_status': status.get('privacyStatus'),
            'upload_status': status.get('uploadStatus'),
            'status': 'success'
        }
    
    def _parse_duration(self, duration_iso: str) -> Optional[int]:
        """Parse ISO 8601 duration to seconds."""
        import re
        
        # Match PT1H30M45S or PT30M45S or PT45S etc.
        match = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', duration_iso)
        if not match:
            return None
        
        hours, minutes, seconds = match.groups()
        total_seconds = 0
        
        if hours:
            total_seconds += int(hours) * 3600
        if minutes:
            total_seconds += int(minutes) * 60
        if seconds:
            total_seconds += int(seconds)
        
        return total_seconds
    
    def _get_best_thumbnail(self, thumbnails: Dict[str, Any]) -> Optional[str]:
        """Get the best available thumbnail URL."""
        # Priority: maxres > high > medium > default
        for quality in ['maxres', 'high', 'medium', 'default']:
            if quality in thumbnails:
                return thumbnails[quality].get('url')
        return None


class TwitterExtractor(ContentExtractor):
    """Extract information from Twitter URLs with API v2 support."""
    
    def __init__(self, bearer_token: Optional[str] = None):
        super().__init__("twitter")
        self.bearer_token = bearer_token
        self.twitter_patterns = [
            r'(?:twitter|x)\.com/(\w+)/status/(\d+)',
            r'(?:twitter|x)\.com/i/status/(\d+)'
        ]
        self.session = requests.Session()
        if self.bearer_token:
            self.session.headers.update({
                'Authorization': f'Bearer {self.bearer_token}',
                'User-Agent': 'LogseqPython/1.0'
            })
    
    def can_extract(self, block: Block) -> bool:
        """Check if block contains Twitter URLs."""
        if not block.content:
            return False
        
        return bool(re.search(r'(?:twitter|x)\.com/(?:\w+/)?status/\d+', block.content, re.IGNORECASE))
    
    def extract(self, block: Block) -> Optional[Dict[str, Any]]:
        """Extract Twitter post information."""
        if not block.content:
            return None
        
        # Extract tweet IDs and usernames
        tweet_data = []
        
        # Pattern for tweets with username
        username_pattern = r'(?:twitter|x)\.com/(\w+)/status/(\d+)'
        matches = re.findall(username_pattern, block.content, re.IGNORECASE)
        for username, tweet_id in matches:
            tweet_data.append((tweet_id, username))
        
        # Pattern for tweets without username (i/status format)
        id_pattern = r'(?:twitter|x)\.com/i/status/(\d+)'
        id_matches = re.findall(id_pattern, block.content, re.IGNORECASE)
        for tweet_id in id_matches:
            tweet_data.append((tweet_id, None))
        
        if not tweet_data:
            return None
        
        # Remove duplicates while preserving order
        unique_tweets = list(dict.fromkeys(tweet_data))
        
        extracted_tweets = []
        for tweet_id, username in unique_tweets:
            try:
                tweet_info = self._extract_tweet_info(tweet_id, username)
                if tweet_info:
                    extracted_tweets.append(tweet_info)
            except Exception as e:
                self.logger.warning(f"Failed to extract tweet {tweet_id}: {e}")
                extracted_tweets.append({
                    'tweet_id': tweet_id,
                    'username': username,
                    'status': 'error',
                    'error': str(e),
                    'extracted_at': datetime.now().isoformat()
                })
        
        if not extracted_tweets:
            return None
        
        return {
            'extractor': self.name,
            'type': 'twitter',
            'tweets': extracted_tweets,
            'total_tweets': len(unique_tweets),
            'successful_extractions': len([t for t in extracted_tweets if t.get('status') == 'success']),
            'api_used': self.bearer_token is not None,
            'extracted_at': datetime.now().isoformat()
        }
    
    def _extract_tweet_info(self, tweet_id: str, username: Optional[str] = None) -> Dict[str, Any]:
        """Extract information for a single tweet."""
        base_info = {
            'tweet_id': tweet_id,
            'username': username,
            'twitter_url': f"https://twitter.com/{'i' if not username else username}/status/{tweet_id}",
            'x_url': f"https://x.com/{'i' if not username else username}/status/{tweet_id}",
            'extracted_at': datetime.now().isoformat()
        }
        
        # Try Twitter API v2 first if available
        if self.bearer_token:
            try:
                api_info = self._get_tweet_from_api(tweet_id)
                if api_info:
                    base_info.update(api_info)
                    base_info['data_source'] = 'twitter_api_v2'
                    return base_info
            except Exception as e:
                self.logger.warning(f"Twitter API failed for {tweet_id}: {e}")
        
        # Fallback to basic info
        base_info.update({
            'title': f"Tweet {tweet_id}",
            'text': None,
            'author': username,
            'created_at': None,
            'public_metrics': None,
            'data_source': 'basic',
            'status': 'limited',
            'note': 'Full content extraction requires Twitter API v2 access'
        })
        
        return base_info
    
    def _get_tweet_from_api(self, tweet_id: str) -> Optional[Dict[str, Any]]:
        """Get tweet information from Twitter API v2."""
        if not self.bearer_token:
            return None
        
        api_url = "https://api.twitter.com/2/tweets"
        params = {
            'ids': tweet_id,
            'tweet.fields': 'author_id,created_at,public_metrics,context_annotations,entities,geo,in_reply_to_user_id,lang,possibly_sensitive,referenced_tweets,reply_settings,source,withheld',
            'expansions': 'author_id,referenced_tweets.id,in_reply_to_user_id,entities.mentions.username',
            'user.fields': 'id,name,username,created_at,description,public_metrics,verified,profile_image_url'
        }
        
        try:
            response = self.session.get(api_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if 'data' not in data or not data['data']:
                return None
            
            tweet = data['data'][0]
            users = {user['id']: user for user in data.get('includes', {}).get('users', [])}
            
            # Get author information
            author_id = tweet.get('author_id')
            author = users.get(author_id, {}) if author_id else {}
            
            # Parse metrics
            metrics = tweet.get('public_metrics', {})
            
            # Parse entities (URLs, mentions, hashtags)
            entities = self._parse_tweet_entities(tweet.get('entities', {}))
            
            # Parse referenced tweets
            referenced_tweets = self._parse_referenced_tweets(tweet.get('referenced_tweets', []))
            
            return {
                'text': tweet.get('text'),
                'author': {
                    'id': author.get('id'),
                    'name': author.get('name'),
                    'username': author.get('username'),
                    'description': author.get('description'),
                    'verified': author.get('verified', False),
                    'followers_count': author.get('public_metrics', {}).get('followers_count'),
                    'following_count': author.get('public_metrics', {}).get('following_count'),
                    'profile_image_url': author.get('profile_image_url')
                },
                'created_at': tweet.get('created_at'),
                'lang': tweet.get('lang'),
                'possibly_sensitive': tweet.get('possibly_sensitive', False),
                'public_metrics': {
                    'retweet_count': metrics.get('retweet_count', 0),
                    'like_count': metrics.get('like_count', 0),
                    'reply_count': metrics.get('reply_count', 0),
                    'quote_count': metrics.get('quote_count', 0)
                },
                'entities': entities,
                'referenced_tweets': referenced_tweets,
                'context_annotations': tweet.get('context_annotations', []),
                'source': tweet.get('source'),
                'reply_settings': tweet.get('reply_settings'),
                'status': 'success'
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def _parse_tweet_entities(self, entities: Dict[str, Any]) -> Dict[str, Any]:
        """Parse tweet entities (URLs, mentions, hashtags)."""
        parsed = {}
        
        if 'urls' in entities:
            parsed['urls'] = [{
                'url': url.get('url'),
                'expanded_url': url.get('expanded_url'),
                'display_url': url.get('display_url'),
                'title': url.get('title'),
                'description': url.get('description')
            } for url in entities['urls']]
        
        if 'mentions' in entities:
            parsed['mentions'] = [{
                'username': mention.get('username'),
                'id': mention.get('id')
            } for mention in entities['mentions']]
        
        if 'hashtags' in entities:
            parsed['hashtags'] = [tag.get('tag') for tag in entities['hashtags']]
        
        if 'cashtags' in entities:
            parsed['cashtags'] = [tag.get('tag') for tag in entities['cashtags']]
        
        return parsed
    
    def _parse_referenced_tweets(self, referenced: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Parse referenced tweets (replies, retweets, quotes)."""
        return [{
            'type': ref.get('type'),  # 'replied_to', 'retweeted', 'quoted'
            'id': ref.get('id')
        } for ref in referenced]


class RSSFeedExtractor(ContentExtractor):
    """Extract information from RSS feeds and news articles."""
    
    def __init__(self):
        super().__init__("rss")
        self.feed_patterns = [
            r'https?://[^\s]+\.xml(?:[?#][^\s]*)?',
            r'https?://[^\s]+/rss(?:[?#/][^\s]*)?',
            r'https?://[^\s]+/feed(?:[?#/][^\s]*)?',
            r'https?://feeds\.[^\s]+',
            r'https?://[^\s]+/atom\.xml(?:[?#][^\s]*)?'
        ]
        self.news_domains = [
            'bbc.com', 'cnn.com', 'reuters.com', 'nytimes.com', 'washingtonpost.com',
            'theguardian.com', 'techcrunch.com', 'wired.com', 'arstechnica.com',
            'medium.com', 'substack.com', 'dev.to', 'hackernews.com'
        ]
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'LogseqPython/1.0 RSS Reader'
        })
    
    def can_extract(self, block: Block) -> bool:
        """Check if block contains RSS feeds or news article URLs."""
        if not block.content:
            return False
        
        # Check for RSS/feed patterns
        for pattern in self.feed_patterns:
            if re.search(pattern, block.content, re.IGNORECASE):
                return True
        
        # Check for news domains
        for domain in self.news_domains:
            if domain in block.content.lower():
                return True
        
        return False
    
    def extract(self, block: Block) -> Optional[Dict[str, Any]]:
        """Extract RSS feed and news article information."""
        if not block.content:
            return None
        
        urls = self.get_urls_from_block(block)
        if not urls:
            return None
        
        extracted_feeds = []
        extracted_articles = []
        
        for url in urls:
            try:
                # First try to parse as RSS feed
                if self._is_feed_url(url):
                    feed_info = self._extract_feed_info(url)
                    if feed_info:
                        extracted_feeds.append(feed_info)
                        continue
                
                # Then try as news article
                if self._is_news_url(url):
                    article_info = self._extract_article_info(url)
                    if article_info:
                        extracted_articles.append(article_info)
                        
            except Exception as e:
                self.logger.warning(f"Failed to extract from {url}: {e}")
        
        if not extracted_feeds and not extracted_articles:
            return None
        
        result = {
            'extractor': self.name,
            'type': 'rss_news',
            'extracted_at': datetime.now().isoformat()
        }
        
        if extracted_feeds:
            result['feeds'] = extracted_feeds
            result['total_feeds'] = len(extracted_feeds)
        
        if extracted_articles:
            result['articles'] = extracted_articles
            result['total_articles'] = len(extracted_articles)
        
        return result
    
    def _is_feed_url(self, url: str) -> bool:
        """Check if URL appears to be a feed."""
        for pattern in self.feed_patterns:
            if re.search(pattern, url, re.IGNORECASE):
                return True
        return False
    
    def _is_news_url(self, url: str) -> bool:
        """Check if URL is from a news domain."""
        return any(domain in url.lower() for domain in self.news_domains)
    
    def _extract_feed_info(self, url: str) -> Optional[Dict[str, Any]]:
        """Extract information from RSS/Atom feed."""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            # Try to parse with feedparser if available
            try:
                import feedparser
                feed = feedparser.parse(response.content)
                
                if feed.bozo and feed.bozo_exception:
                    # Feed parsing failed, treat as regular content
                    return None
                
                # Extract feed metadata
                feed_info = {
                    'url': url,
                    'title': getattr(feed.feed, 'title', None),
                    'description': getattr(feed.feed, 'description', None),
                    'link': getattr(feed.feed, 'link', None),
                    'language': getattr(feed.feed, 'language', None),
                    'updated': getattr(feed.feed, 'updated', None),
                    'generator': getattr(feed.feed, 'generator', None),
                    'entries_count': len(feed.entries),
                    'status': 'success',
                    'feed_type': 'rss' if 'rss' in response.text.lower() else 'atom',
                    'extracted_at': datetime.now().isoformat()
                }
                
                # Extract recent entries
                entries = []
                for entry in feed.entries[:10]:  # Limit to 10 most recent
                    entry_info = {
                        'title': getattr(entry, 'title', None),
                        'link': getattr(entry, 'link', None),
                        'description': getattr(entry, 'description', None),
                        'published': getattr(entry, 'published', None),
                        'updated': getattr(entry, 'updated', None),
                        'author': getattr(entry, 'author', None)
                    }
                    
                    # Clean up description (remove HTML tags)
                    if entry_info['description']:
                        entry_info['description'] = re.sub(r'<[^>]+>', '', entry_info['description'])
                        entry_info['description'] = entry_info['description'][:500]  # Limit length
                    
                    entries.append(entry_info)
                
                feed_info['recent_entries'] = entries
                return feed_info
                
            except ImportError:
                # Fallback without feedparser
                self.logger.info("feedparser not available, using basic XML parsing")
                return self._parse_feed_basic(url, response.content)
                
        except Exception as e:
            return {
                'url': url,
                'status': 'error',
                'error': str(e),
                'extracted_at': datetime.now().isoformat()
            }
    
    def _parse_feed_basic(self, url: str, content: bytes) -> Dict[str, Any]:
        """Basic feed parsing without feedparser."""
        try:
            import xml.etree.ElementTree as ET
            root = ET.fromstring(content)
            
            # Detect feed type
            feed_type = 'atom' if root.tag.endswith('feed') else 'rss'
            
            if feed_type == 'rss':
                channel = root.find('channel')
                if channel is not None:
                    title = channel.find('title')
                    description = channel.find('description')
                    link = channel.find('link')
                    
                    return {
                        'url': url,
                        'title': title.text if title is not None else None,
                        'description': description.text if description is not None else None,
                        'link': link.text if link is not None else None,
                        'feed_type': 'rss',
                        'status': 'success',
                        'parsing_method': 'basic_xml',
                        'extracted_at': datetime.now().isoformat()
                    }
            else:
                # Atom feed
                title = root.find('{http://www.w3.org/2005/Atom}title')
                subtitle = root.find('{http://www.w3.org/2005/Atom}subtitle')
                link = root.find('{http://www.w3.org/2005/Atom}link[@rel="alternate"]')
                
                return {
                    'url': url,
                    'title': title.text if title is not None else None,
                    'description': subtitle.text if subtitle is not None else None,
                    'link': link.get('href') if link is not None else None,
                    'feed_type': 'atom',
                    'status': 'success',
                    'parsing_method': 'basic_xml',
                    'extracted_at': datetime.now().isoformat()
                }
                
        except Exception as e:
            return {
                'url': url,
                'status': 'error',
                'error': f'XML parsing failed: {str(e)}',
                'extracted_at': datetime.now().isoformat()
            }
    
    def _extract_article_info(self, url: str) -> Optional[Dict[str, Any]]:
        """Extract information from news article."""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            # Try to parse with newspaper3k if available
            try:
                from newspaper import Article
                
                article = Article(url)
                article.download()
                article.parse()
                
                # Try to extract keywords and summary
                try:
                    article.nlp()
                except:
                    # NLP processing failed, continue without it
                    pass
                
                return {
                    'url': url,
                    'title': article.title,
                    'text': article.text[:5000] if article.text else None,  # Limit to 5KB
                    'authors': list(article.authors) if article.authors else None,
                    'publish_date': article.publish_date.isoformat() if article.publish_date else None,
                    'top_image': article.top_image,
                    'keywords': list(article.keywords) if hasattr(article, 'keywords') else None,
                    'summary': article.summary if hasattr(article, 'summary') else None,
                    'source_url': article.source_url,
                    'status': 'success',
                    'extraction_method': 'newspaper3k',
                    'extracted_at': datetime.now().isoformat()
                }
                
            except ImportError:
                # Fallback to basic HTML parsing
                self.logger.info("newspaper3k not available, using basic HTML parsing")
                return self._parse_article_basic(url, response.text)
                
        except Exception as e:
            return {
                'url': url,
                'status': 'error',
                'error': str(e),
                'extracted_at': datetime.now().isoformat()
            }
    
    def _parse_article_basic(self, url: str, html_content: str) -> Dict[str, Any]:
        """Basic article parsing using HTML."""
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Extract title
            title = None
            if soup.find('h1'):
                title = soup.find('h1').get_text().strip()
            elif soup.find('title'):
                title = soup.find('title').get_text().strip()
            
            # Extract meta description
            description = None
            meta_desc = soup.find('meta', {'name': 'description'})
            if meta_desc:
                description = meta_desc.get('content', '')
            
            # Extract author
            author = None
            meta_author = soup.find('meta', {'name': 'author'})
            if meta_author:
                author = meta_author.get('content', '')
            
            # Extract main content
            content_text = None
            for selector in ['article', 'main', '[role="main"]', '.content', '.post-content']:
                content_elem = soup.select_one(selector)
                if content_elem:
                    content_text = content_elem.get_text().strip()[:3000]
                    break
            
            return {
                'url': url,
                'title': title,
                'description': description,
                'author': author,
                'text': content_text,
                'status': 'success',
                'extraction_method': 'basic_html',
                'extracted_at': datetime.now().isoformat()
            }
            
        except ImportError:
            return {
                'url': url,
                'status': 'error',
                'error': 'HTML parsing libraries not available',
                'extracted_at': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'url': url,
                'status': 'error',
                'error': str(e),
                'extracted_at': datetime.now().isoformat()
            }


class GitHubExtractor(ContentExtractor):
    """Extract information from GitHub URLs."""
    
    def __init__(self, access_token: Optional[str] = None):
        super().__init__("github")
        self.access_token = access_token
        self.github_patterns = [
            r'github\.com/([^/]+)/([^/]+)(?:/([^?\s]+))?',
            r'raw\.githubusercontent\.com/([^/]+)/([^/]+)/([^/]+)/(.+)'
        ]
        self.session = requests.Session()
        if self.access_token:
            self.session.headers.update({
                'Authorization': f'token {self.access_token}',
                'Accept': 'application/vnd.github.v3+json'
            })
    
    def can_extract(self, block: Block) -> bool:
        """Check if block contains GitHub URLs."""
        if not block.content:
            return False
        
        return bool(re.search(r'github\.com|raw\.githubusercontent\.com', block.content, re.IGNORECASE))
    
    def extract(self, block: Block) -> Optional[Dict[str, Any]]:
        """Extract GitHub repository/file/issue information."""
        urls = self.get_urls_from_block(block)
        github_urls = [url for url in urls if 'github.com' in url or 'githubusercontent.com' in url]
        
        if not github_urls:
            return None
        
        extracted_items = []
        for url in github_urls:
            try:
                item_info = self._extract_github_info(url)
                if item_info:
                    extracted_items.append(item_info)
            except Exception as e:
                self.logger.warning(f"Failed to extract GitHub info from {url}: {e}")
                extracted_items.append({
                    'url': url,
                    'status': 'error',
                    'error': str(e),
                    'extracted_at': datetime.now().isoformat()
                })
        
        if not extracted_items:
            return None
        
        return {
            'extractor': self.name,
            'type': 'github',
            'items': extracted_items,
            'total_items': len(github_urls),
            'successful_extractions': len([item for item in extracted_items if item.get('status') == 'success']),
            'extracted_at': datetime.now().isoformat()
        }
    
    def _extract_github_info(self, url: str) -> Optional[Dict[str, Any]]:
        """Extract information from GitHub URL."""
        # Parse different GitHub URL patterns
        url_type = self._identify_github_url_type(url)
        
        if url_type == 'repository':
            return self._extract_repository_info(url)
        elif url_type == 'file':
            return self._extract_file_info(url)
        elif url_type == 'issue':
            return self._extract_issue_info(url)
        elif url_type == 'pull_request':
            return self._extract_pull_request_info(url)
        elif url_type == 'raw_file':
            return self._extract_raw_file_info(url)
        else:
            return self._extract_repository_info(url)  # Default fallback
    
    def _identify_github_url_type(self, url: str) -> str:
        """Identify the type of GitHub URL."""
        if '/issues/' in url:
            return 'issue'
        elif '/pull/' in url:
            return 'pull_request'
        elif '/blob/' in url or '/tree/' in url:
            return 'file'
        elif 'raw.githubusercontent.com' in url:
            return 'raw_file'
        else:
            return 'repository'
    
    def _extract_repository_info(self, url: str) -> Dict[str, Any]:
        """Extract repository information."""
        match = re.search(r'github\.com/([^/]+)/([^/]+)(?:/([^?\s]+))?', url)
        if not match:
            return {'url': url, 'status': 'error', 'error': 'Invalid GitHub URL'}
        
        owner, repo_name, path = match.groups()
        repo_name = repo_name.rstrip('/').replace('.git', '')
        
        base_info = {
            'url': url,
            'type': 'repository',
            'owner': owner,
            'name': repo_name,
            'full_name': f"{owner}/{repo_name}",
            'path': path,
            'extracted_at': datetime.now().isoformat()
        }
        
        try:
            api_url = f"https://api.github.com/repos/{owner}/{repo_name}"
            response = self.session.get(api_url, timeout=10)
            
            if response.status_code == 200:
                repo_data = response.json()
                base_info.update({
                    'description': repo_data.get('description'),
                    'language': repo_data.get('language'),
                    'stars': repo_data.get('stargazers_count'),
                    'forks': repo_data.get('forks_count'),
                    'watchers': repo_data.get('watchers_count'),
                    'open_issues': repo_data.get('open_issues_count'),
                    'created_at': repo_data.get('created_at'),
                    'updated_at': repo_data.get('updated_at'),
                    'pushed_at': repo_data.get('pushed_at'),
                    'size': repo_data.get('size'),
                    'default_branch': repo_data.get('default_branch'),
                    'license': repo_data.get('license', {}).get('name') if repo_data.get('license') else None,
                    'topics': repo_data.get('topics', []),
                    'homepage': repo_data.get('homepage'),
                    'private': repo_data.get('private', False),
                    'archived': repo_data.get('archived', False),
                    'disabled': repo_data.get('disabled', False),
                    'status': 'success'
                })
                
                # Get README if available
                if not path:  # Only for root repository URLs
                    readme_content = self._get_readme_content(owner, repo_name)
                    if readme_content:
                        base_info['readme'] = readme_content
                
            else:
                base_info.update({
                    'status': 'limited',
                    'error': f'API returned {response.status_code}'
                })
            
            return base_info
            
        except Exception as e:
            base_info.update({
                'status': 'error',
                'error': str(e)
            })
            return base_info
    
    def _extract_file_info(self, url: str) -> Dict[str, Any]:
        """Extract file information from GitHub URL."""
        match = re.search(r'github\.com/([^/]+)/([^/]+)/(?:blob|tree)/([^/]+)/(.+)', url)
        if not match:
            return {'url': url, 'status': 'error', 'error': 'Invalid GitHub file URL'}
        
        owner, repo_name, branch, file_path = match.groups()
        
        base_info = {
            'url': url,
            'type': 'file',
            'owner': owner,
            'repository': repo_name,
            'branch': branch,
            'file_path': file_path,
            'extracted_at': datetime.now().isoformat()
        }
        
        try:
            # Get file content from API
            api_url = f"https://api.github.com/repos/{owner}/{repo_name}/contents/{file_path}"
            params = {'ref': branch} if branch != 'main' and branch != 'master' else {}
            
            response = self.session.get(api_url, params=params, timeout=10)
            
            if response.status_code == 200:
                file_data = response.json()
                
                # Handle directory vs file
                if isinstance(file_data, list):
                    base_info.update({
                        'type': 'directory',
                        'files': [{'name': item['name'], 'type': item['type']} for item in file_data],
                        'file_count': len(file_data),
                        'status': 'success'
                    })
                else:
                    base_info.update({
                        'name': file_data.get('name'),
                        'size': file_data.get('size'),
                        'encoding': file_data.get('encoding'),
                        'download_url': file_data.get('download_url'),
                        'status': 'success'
                    })
                    
                    # Get file content if it's text and small enough
                    if (file_data.get('size', 0) < 100000 and  # Less than 100KB
                        file_data.get('encoding') == 'base64'):
                        try:
                            import base64
                            content = base64.b64decode(file_data['content']).decode('utf-8')
                            base_info['content'] = content[:10000]  # Limit to 10KB
                            base_info['content_truncated'] = len(content) > 10000
                        except (UnicodeDecodeError, KeyError):
                            base_info['content'] = None
                            base_info['content_note'] = 'Binary file or encoding error'
            else:
                base_info.update({
                    'status': 'error',
                    'error': f'API returned {response.status_code}'
                })
            
            return base_info
            
        except Exception as e:
            base_info.update({
                'status': 'error',
                'error': str(e)
            })
            return base_info
    
    def _extract_issue_info(self, url: str) -> Dict[str, Any]:
        """Extract issue information from GitHub URL."""
        match = re.search(r'github\.com/([^/]+)/([^/]+)/issues/(\d+)', url)
        if not match:
            return {'url': url, 'status': 'error', 'error': 'Invalid GitHub issue URL'}
        
        owner, repo_name, issue_number = match.groups()
        
        base_info = {
            'url': url,
            'type': 'issue',
            'owner': owner,
            'repository': repo_name,
            'issue_number': int(issue_number),
            'extracted_at': datetime.now().isoformat()
        }
        
        try:
            api_url = f"https://api.github.com/repos/{owner}/{repo_name}/issues/{issue_number}"
            response = self.session.get(api_url, timeout=10)
            
            if response.status_code == 200:
                issue_data = response.json()
                
                base_info.update({
                    'title': issue_data.get('title'),
                    'body': issue_data.get('body', '')[:2000] if issue_data.get('body') else None,
                    'state': issue_data.get('state'),
                    'author': issue_data.get('user', {}).get('login'),
                    'assignees': [assignee['login'] for assignee in issue_data.get('assignees', [])],
                    'labels': [label['name'] for label in issue_data.get('labels', [])],
                    'comments_count': issue_data.get('comments'),
                    'created_at': issue_data.get('created_at'),
                    'updated_at': issue_data.get('updated_at'),
                    'closed_at': issue_data.get('closed_at'),
                    'milestone': issue_data.get('milestone', {}).get('title') if issue_data.get('milestone') else None,
                    'status': 'success'
                })
            else:
                base_info.update({
                    'status': 'error',
                    'error': f'API returned {response.status_code}'
                })
            
            return base_info
            
        except Exception as e:
            base_info.update({
                'status': 'error',
                'error': str(e)
            })
            return base_info
    
    def _extract_pull_request_info(self, url: str) -> Dict[str, Any]:
        """Extract pull request information from GitHub URL."""
        match = re.search(r'github\.com/([^/]+)/([^/]+)/pull/(\d+)', url)
        if not match:
            return {'url': url, 'status': 'error', 'error': 'Invalid GitHub PR URL'}
        
        owner, repo_name, pr_number = match.groups()
        
        base_info = {
            'url': url,
            'type': 'pull_request',
            'owner': owner,
            'repository': repo_name,
            'pr_number': int(pr_number),
            'extracted_at': datetime.now().isoformat()
        }
        
        try:
            api_url = f"https://api.github.com/repos/{owner}/{repo_name}/pulls/{pr_number}"
            response = self.session.get(api_url, timeout=10)
            
            if response.status_code == 200:
                pr_data = response.json()
                
                base_info.update({
                    'title': pr_data.get('title'),
                    'body': pr_data.get('body', '')[:2000] if pr_data.get('body') else None,
                    'state': pr_data.get('state'),
                    'author': pr_data.get('user', {}).get('login'),
                    'assignees': [assignee['login'] for assignee in pr_data.get('assignees', [])],
                    'reviewers': [reviewer['login'] for reviewer in pr_data.get('requested_reviewers', [])],
                    'labels': [label['name'] for label in pr_data.get('labels', [])],
                    'base_branch': pr_data.get('base', {}).get('ref'),
                    'head_branch': pr_data.get('head', {}).get('ref'),
                    'commits_count': pr_data.get('commits'),
                    'additions': pr_data.get('additions'),
                    'deletions': pr_data.get('deletions'),
                    'changed_files': pr_data.get('changed_files'),
                    'mergeable': pr_data.get('mergeable'),
                    'merged': pr_data.get('merged'),
                    'created_at': pr_data.get('created_at'),
                    'updated_at': pr_data.get('updated_at'),
                    'closed_at': pr_data.get('closed_at'),
                    'merged_at': pr_data.get('merged_at'),
                    'status': 'success'
                })
            else:
                base_info.update({
                    'status': 'error', 
                    'error': f'API returned {response.status_code}'
                })
            
            return base_info
            
        except Exception as e:
            base_info.update({
                'status': 'error',
                'error': str(e)
            })
            return base_info
    
    def _extract_raw_file_info(self, url: str) -> Dict[str, Any]:
        """Extract information from raw.githubusercontent.com URL."""
        match = re.search(r'raw\.githubusercontent\.com/([^/]+)/([^/]+)/([^/]+)/(.+)', url)
        if not match:
            return {'url': url, 'status': 'error', 'error': 'Invalid raw GitHub URL'}
        
        owner, repo_name, branch, file_path = match.groups()
        
        base_info = {
            'url': url,
            'type': 'raw_file',
            'owner': owner,
            'repository': repo_name,
            'branch': branch,
            'file_path': file_path,
            'extracted_at': datetime.now().isoformat()
        }
        
        try:
            response = self.session.head(url, timeout=10)
            
            if response.status_code == 200:
                headers = response.headers
                base_info.update({
                    'content_type': headers.get('content-type'),
                    'content_length': headers.get('content-length'),
                    'last_modified': headers.get('last-modified'),
                    'status': 'success'
                })
                
                # Try to get actual content if it's small and text
                content_length = int(headers.get('content-length', 0))
                if content_length < 50000:  # Less than 50KB
                    try:
                        content_response = self.session.get(url, timeout=10)
                        if content_response.status_code == 200:
                            base_info['content'] = content_response.text[:10000]
                            base_info['content_truncated'] = len(content_response.text) > 10000
                    except Exception:
                        pass  # Content extraction failed, but we have metadata
            else:
                base_info.update({
                    'status': 'error',
                    'error': f'HTTP {response.status_code}'
                })
            
            return base_info
            
        except Exception as e:
            base_info.update({
                'status': 'error',
                'error': str(e)
            })
            return base_info
    
    def _get_readme_content(self, owner: str, repo_name: str) -> Optional[Dict[str, Any]]:
        """Get README content for repository."""
        try:
            api_url = f"https://api.github.com/repos/{owner}/{repo_name}/readme"
            response = self.session.get(api_url, timeout=10)
            
            if response.status_code == 200:
                readme_data = response.json()
                
                # Decode base64 content
                import base64
                content = base64.b64decode(readme_data['content']).decode('utf-8')
                
                return {
                    'name': readme_data.get('name'),
                    'size': readme_data.get('size'),
                    'content': content[:5000],  # Limit to 5KB
                    'content_truncated': len(content) > 5000,
                    'download_url': readme_data.get('download_url')
                }
            
        except Exception:
            pass  # README extraction failed
        
        return None


class VideoPlatformExtractor(ContentExtractor):
    """Extract metadata from various video platforms (Vimeo, TikTok, etc.)."""
    
    def __init__(self):
        super().__init__("video_platform")
        self.platform_patterns = {
            'vimeo': [
                r'vimeo\.com/(\d+)',
                r'vimeo\.com/channels/[^/]+/(\d+)',
                r'vimeo\.com/groups/[^/]+/videos/(\d+)'
            ],
            'tiktok': [
                r'tiktok\.com/@[^/]+/video/(\d+)',
                r'vm\.tiktok\.com/([^/]+)'
            ],
            'twitch': [
                r'twitch\.tv/videos/(\d+)',
                r'twitch\.tv/[^/]+/clip/([^/?\s]+)',
                r'clips\.twitch\.tv/([^/?\s]+)'
            ],
            'dailymotion': [
                r'dailymotion\.com/video/([^/?\s]+)',
                r'dai\.ly/([^/?\s]+)'
            ]
        }
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'LogseqPython/1.0 Video Extractor'
        })
    
    def can_extract(self, block: Block) -> bool:
        """Check if block contains supported video platform URLs."""
        if not block.content:
            return False
        
        for platform, patterns in self.platform_patterns.items():
            for pattern in patterns:
                if re.search(pattern, block.content, re.IGNORECASE):
                    return True
        
        return False
    
    def extract(self, block: Block) -> Optional[Dict[str, Any]]:
        """Extract video information from various platforms."""
        if not block.content:
            return None
        
        extracted_videos = []
        
        for platform, patterns in self.platform_patterns.items():
            for pattern in patterns:
                matches = re.findall(pattern, block.content, re.IGNORECASE)
                for video_id in matches:
                    try:
                        video_info = self._extract_platform_video(platform, video_id, block.content)
                        if video_info:
                            extracted_videos.append(video_info)
                    except Exception as e:
                        self.logger.warning(f"Failed to extract {platform} video {video_id}: {e}")
        
        if not extracted_videos:
            return None
        
        return {
            'extractor': self.name,
            'type': 'video_platform',
            'videos': extracted_videos,
            'total_videos': len(extracted_videos),
            'extracted_at': datetime.now().isoformat()
        }
    
    def _extract_platform_video(self, platform: str, video_id: str, content: str) -> Optional[Dict[str, Any]]:
        """Extract video information based on platform."""
        if platform == 'vimeo':
            return self._extract_vimeo_video(video_id)
        elif platform == 'tiktok':
            return self._extract_tiktok_video(video_id, content)
        elif platform == 'twitch':
            return self._extract_twitch_video(video_id)
        elif platform == 'dailymotion':
            return self._extract_dailymotion_video(video_id)
        else:
            return None
    
    def _extract_vimeo_video(self, video_id: str) -> Dict[str, Any]:
        """Extract Vimeo video information."""
        base_info = {
            'platform': 'vimeo',
            'video_id': video_id,
            'url': f"https://vimeo.com/{video_id}",
            'extracted_at': datetime.now().isoformat()
        }
        
        try:
            # Try Vimeo oEmbed API
            oembed_url = f"https://vimeo.com/api/oembed.json?url=https://vimeo.com/{video_id}"
            response = self.session.get(oembed_url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                base_info.update({
                    'title': data.get('title'),
                    'description': data.get('description'),
                    'author_name': data.get('author_name'),
                    'author_url': data.get('author_url'),
                    'thumbnail_url': data.get('thumbnail_url'),
                    'duration': data.get('duration'),
                    'upload_date': data.get('upload_date'),
                    'width': data.get('width'),
                    'height': data.get('height'),
                    'status': 'success',
                    'data_source': 'oembed'
                })
            else:
                base_info.update({
                    'status': 'limited',
                    'error': f'oEmbed API returned {response.status_code}'
                })
            
            return base_info
            
        except Exception as e:
            base_info.update({
                'status': 'error',
                'error': str(e)
            })
            return base_info
    
    def _extract_tiktok_video(self, video_id: str, content: str) -> Dict[str, Any]:
        """Extract TikTok video information."""
        # Extract full URL from content for TikTok
        tiktok_match = re.search(r'(https?://(?:www\.|vm\.)?tiktok\.com/[^\s]+)', content, re.IGNORECASE)
        full_url = tiktok_match.group(1) if tiktok_match else f"https://tiktok.com/video/{video_id}"
        
        base_info = {
            'platform': 'tiktok',
            'video_id': video_id,
            'url': full_url,
            'extracted_at': datetime.now().isoformat()
        }
        
        try:
            # Try to extract from HTML (limited without API)
            response = self.session.get(full_url, timeout=10)
            
            if response.status_code == 200:
                # Basic HTML parsing for metadata
                title_match = re.search(r'<title[^>]*>([^<]+)</title>', response.text, re.IGNORECASE)
                desc_match = re.search(r'<meta[^>]*name=["\']description["\'][^>]*content=["\']([^"\'>]*)["\']', response.text, re.IGNORECASE)
                
                base_info.update({
                    'title': title_match.group(1).strip() if title_match else None,
                    'description': desc_match.group(1).strip() if desc_match else None,
                    'status': 'limited',
                    'data_source': 'html_parsing',
                    'note': 'Full metadata requires TikTok API access'
                })
            else:
                base_info.update({
                    'status': 'error',
                    'error': f'HTTP {response.status_code}'
                })
            
            return base_info
            
        except Exception as e:
            base_info.update({
                'status': 'error',
                'error': str(e)
            })
            return base_info
    
    def _extract_twitch_video(self, video_id: str) -> Dict[str, Any]:
        """Extract Twitch video/clip information."""
        # Determine if it's a video or clip
        if video_id.isdigit():
            url = f"https://twitch.tv/videos/{video_id}"
            content_type = 'video'
        else:
            url = f"https://clips.twitch.tv/{video_id}"
            content_type = 'clip'
        
        base_info = {
            'platform': 'twitch',
            'video_id': video_id,
            'url': url,
            'content_type': content_type,
            'extracted_at': datetime.now().isoformat()
        }
        
        try:
            # Basic HTML parsing (Twitch API requires authentication)
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                # Extract basic metadata from HTML
                title_match = re.search(r'<title[^>]*>([^<]+)</title>', response.text, re.IGNORECASE)
                
                base_info.update({
                    'title': title_match.group(1).strip() if title_match else None,
                    'status': 'limited',
                    'data_source': 'html_parsing',
                    'note': 'Full metadata requires Twitch API access'
                })
            else:
                base_info.update({
                    'status': 'error',
                    'error': f'HTTP {response.status_code}'
                })
            
            return base_info
            
        except Exception as e:
            base_info.update({
                'status': 'error',
                'error': str(e)
            })
            return base_info
    
    def _extract_dailymotion_video(self, video_id: str) -> Dict[str, Any]:
        """Extract Dailymotion video information."""
        base_info = {
            'platform': 'dailymotion',
            'video_id': video_id,
            'url': f"https://dailymotion.com/video/{video_id}",
            'extracted_at': datetime.now().isoformat()
        }
        
        try:
            # Try Dailymotion oEmbed API
            oembed_url = f"https://www.dailymotion.com/services/oembed?url=https://dailymotion.com/video/{video_id}&format=json"
            response = self.session.get(oembed_url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                base_info.update({
                    'title': data.get('title'),
                    'author_name': data.get('author_name'),
                    'author_url': data.get('author_url'),
                    'thumbnail_url': data.get('thumbnail_url'),
                    'width': data.get('width'),
                    'height': data.get('height'),
                    'status': 'success',
                    'data_source': 'oembed'
                })
            else:
                base_info.update({
                    'status': 'limited',
                    'error': f'oEmbed API returned {response.status_code}'
                })
            
            return base_info
            
        except Exception as e:
            base_info.update({
                'status': 'error',
                'error': str(e)
            })
            return base_info


class PDFExtractor(ContentExtractor):
    """Extract text and metadata from PDF documents."""
    
    def __init__(self):
        super().__init__("pdf")
        self.pdf_patterns = [
            r'https?://[^\s]+\.pdf(?:[?#][^\s]*)?',
            r'arxiv\.org/pdf/[^\s]+',
            r'biorxiv\.org/[^\s]+\.full\.pdf'
        ]
    
    def can_extract(self, block: Block) -> bool:
        """Check if block contains PDF URLs."""
        if not block.content:
            return False
        
        for pattern in self.pdf_patterns:
            if re.search(pattern, block.content, re.IGNORECASE):
                return True
        
        return False
    
    def extract(self, block: Block) -> Optional[Dict[str, Any]]:
        """Extract PDF metadata and text content."""
        if not block.content:
            return None
        
        pdf_urls = []
        for pattern in self.pdf_patterns:
            matches = re.findall(pattern, block.content, re.IGNORECASE)
            pdf_urls.extend(matches)
        
        if not pdf_urls:
            return None
        
        unique_urls = list(dict.fromkeys(pdf_urls))
        extracted_pdfs = []
        
        for url in unique_urls:
            try:
                pdf_info = self._extract_pdf_info(url)
                if pdf_info:
                    extracted_pdfs.append(pdf_info)
            except Exception as e:
                self.logger.warning(f"Failed to extract PDF {url}: {e}")
                extracted_pdfs.append({
                    'url': url,
                    'status': 'error',
                    'error': str(e)
                })
        
        if not extracted_pdfs:
            return None
        
        return {
            'extractor': self.name,
            'type': 'pdf',
            'documents': extracted_pdfs,
            'total_documents': len(unique_urls),
            'successful_extractions': len([p for p in extracted_pdfs if p.get('status') == 'success']),
            'extracted_at': datetime.now().isoformat()
        }
    
    def _extract_pdf_info(self, url: str) -> Dict[str, Any]:
        """Extract information from a PDF URL."""
        base_info = {
            'url': url,
            'extracted_at': datetime.now().isoformat()
        }
        
        try:
            # Try to extract text with PyPDF2/pdfplumber if available
            try:
                text_content = self._extract_pdf_text(url)
                base_info.update(text_content)
            except ImportError:
                self.logger.info("PDF text extraction libraries not available")
                base_info['text_extraction'] = 'unavailable'
            
            # Get basic metadata from headers
            response = requests.head(url, timeout=10)
            if response.status_code == 200:
                headers = response.headers
                base_info.update({
                    'content_type': headers.get('content-type'),
                    'content_length': headers.get('content-length'),
                    'last_modified': headers.get('last-modified'),
                    'status': 'success'
                })
            else:
                base_info.update({
                    'status': 'failed',
                    'error': f'HTTP {response.status_code}'
                })
            
            return base_info
            
        except Exception as e:
            base_info.update({
                'status': 'error',
                'error': str(e)
            })
            return base_info
    
    def _extract_pdf_text(self, url: str) -> Dict[str, Any]:
        """Extract text content from PDF (requires PDF libraries)."""
        try:
            import PyPDF2
            from io import BytesIO
            
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            pdf_file = BytesIO(response.content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            text_pages = []
            for page_num, page in enumerate(pdf_reader.pages[:10]):  # Limit to first 10 pages
                text = page.extract_text()
                if text.strip():
                    text_pages.append({
                        'page': page_num + 1,
                        'text': text.strip()[:2000]  # Limit text per page
                    })
            
            full_text = ' '.join([page['text'] for page in text_pages])
            
            return {
                'text': full_text[:10000] if len(full_text) > 10000 else full_text,  # 10KB limit
                'text_truncated': len(full_text) > 10000,
                'pages_extracted': len(text_pages),
                'total_pages': len(pdf_reader.pages),
                'text_extraction': 'success'
            }
            
        except ImportError:
            raise  # Re-raise to be caught by caller
        except Exception as e:
            return {
                'text_extraction': 'failed',
                'extraction_error': str(e)
            }


class AcademicPaperExtractor(ContentExtractor):
    """Extract metadata from academic papers (arXiv, DOI, etc.)."""
    
    def __init__(self):
        super().__init__("academic")
        self.arxiv_pattern = r'arxiv\.org/(?:abs|pdf)/([\d.]+(?:v\d+)?)'  
        self.doi_pattern = r'doi\.org/([\d.]+/[^\s]+)'
        self.session = requests.Session()
    
    def can_extract(self, block: Block) -> bool:
        """Check if block contains academic paper URLs."""
        if not block.content:
            return False
        
        return bool(re.search(self.arxiv_pattern, block.content, re.IGNORECASE) or 
                   re.search(self.doi_pattern, block.content, re.IGNORECASE))
    
    def extract(self, block: Block) -> Optional[Dict[str, Any]]:
        """Extract academic paper metadata."""
        if not block.content:
            return None
        
        papers = []
        
        # Extract arXiv papers
        arxiv_ids = re.findall(self.arxiv_pattern, block.content, re.IGNORECASE)
        for arxiv_id in set(arxiv_ids):  # Remove duplicates
            try:
                paper_info = self._extract_arxiv_info(arxiv_id)
                if paper_info:
                    papers.append(paper_info)
            except Exception as e:
                self.logger.warning(f"Failed to extract arXiv paper {arxiv_id}: {e}")
        
        # Extract DOI papers
        dois = re.findall(self.doi_pattern, block.content, re.IGNORECASE)
        for doi in set(dois):  # Remove duplicates
            try:
                paper_info = self._extract_doi_info(doi)
                if paper_info:
                    papers.append(paper_info)
            except Exception as e:
                self.logger.warning(f"Failed to extract DOI paper {doi}: {e}")
        
        if not papers:
            return None
        
        return {
            'extractor': self.name,
            'type': 'academic_paper',
            'papers': papers,
            'total_papers': len(papers),
            'extracted_at': datetime.now().isoformat()
        }
    
    def _extract_arxiv_info(self, arxiv_id: str) -> Optional[Dict[str, Any]]:
        """Extract information from arXiv paper."""
        try:
            # Use arXiv API
            api_url = f"http://export.arxiv.org/api/query?id_list={arxiv_id}"
            response = self.session.get(api_url, timeout=10)
            response.raise_for_status()
            
            # Parse XML response
            import xml.etree.ElementTree as ET
            root = ET.fromstring(response.content)
            
            # Find entry
            entry = root.find('{http://www.w3.org/2005/Atom}entry')
            if entry is None:
                return None
            
            # Extract metadata
            title = entry.find('{http://www.w3.org/2005/Atom}title')
            summary = entry.find('{http://www.w3.org/2005/Atom}summary')
            published = entry.find('{http://www.w3.org/2005/Atom}published')
            updated = entry.find('{http://www.w3.org/2005/Atom}updated')
            
            # Extract authors
            authors = []
            for author in entry.findall('{http://www.w3.org/2005/Atom}author'):
                name = author.find('{http://www.w3.org/2005/Atom}name')
                if name is not None:
                    authors.append(name.text)
            
            # Extract categories
            categories = []
            for category in entry.findall('{http://www.w3.org/2005/Atom}category'):
                term = category.get('term')
                if term:
                    categories.append(term)
            
            return {
                'source': 'arxiv',
                'arxiv_id': arxiv_id,
                'title': title.text.strip() if title is not None else None,
                'abstract': summary.text.strip() if summary is not None else None,
                'authors': authors,
                'categories': categories,
                'published_date': published.text if published is not None else None,
                'updated_date': updated.text if updated is not None else None,
                'arxiv_url': f"https://arxiv.org/abs/{arxiv_id}",
                'pdf_url': f"https://arxiv.org/pdf/{arxiv_id}.pdf",
                'status': 'success'
            }
            
        except Exception as e:
            return {
                'source': 'arxiv',
                'arxiv_id': arxiv_id,
                'status': 'error',
                'error': str(e)
            }
    
    def _extract_doi_info(self, doi: str) -> Optional[Dict[str, Any]]:
        """Extract information from DOI."""
        try:
            # Use Crossref API
            api_url = f"https://api.crossref.org/works/{doi}"
            headers = {
                'User-Agent': 'LogseqPython/1.0 (https://github.com/thinmanj/logseq-python-library)'
            }
            
            response = self.session.get(api_url, headers=headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            work = data.get('message', {})
            
            # Extract authors
            authors = []
            for author in work.get('author', []):
                given = author.get('given', '')
                family = author.get('family', '')
                if given and family:
                    authors.append(f"{given} {family}")
                elif family:
                    authors.append(family)
            
            # Extract publication date
            pub_date = None
            if 'published-print' in work:
                date_parts = work['published-print'].get('date-parts', [[]])[0]
                if date_parts:
                    pub_date = '-'.join(str(part) for part in date_parts)
            elif 'published-online' in work:
                date_parts = work['published-online'].get('date-parts', [[]])[0] 
                if date_parts:
                    pub_date = '-'.join(str(part) for part in date_parts)
            
            return {
                'source': 'doi',
                'doi': doi,
                'title': work.get('title', [None])[0],
                'abstract': work.get('abstract'),
                'authors': authors,
                'journal': work.get('container-title', [None])[0],
                'publisher': work.get('publisher'),
                'published_date': pub_date,
                'volume': work.get('volume'),
                'issue': work.get('issue'),
                'pages': work.get('page'),
                'doi_url': f"https://doi.org/{doi}",
                'type': work.get('type'),
                'status': 'success'
            }
            
        except Exception as e:
            return {
                'source': 'doi',
                'doi': doi,
                'status': 'error', 
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
        self.register(RSSFeedExtractor())
        self.register(VideoPlatformExtractor())
        self.register(GitHubExtractor())
        self.register(PDFExtractor())
        self.register(AcademicPaperExtractor())


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