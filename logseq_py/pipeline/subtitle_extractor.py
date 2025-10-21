"""
Subtitle Extraction for Video Processing

This module handles extraction of subtitles/captions from video platforms,
primarily YouTube, for content analysis and tagging.
"""

import re
import logging
import requests
from typing import Optional, List, Dict, Any, Set
from urllib.parse import parse_qs, urlparse


class YouTubeSubtitleExtractor:
    """Extract subtitles from YouTube videos using multiple methods."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the subtitle extractor.
        
        Args:
            api_key: Optional YouTube Data API key for enhanced features
        """
        self.api_key = api_key
        self.logger = logging.getLogger(__name__)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
    
    def extract_subtitles(self, url: str) -> Optional[str]:
        """Extract subtitles from a YouTube video URL.
        
        Args:
            url: YouTube video URL
            
        Returns:
            Subtitle text as string, or None if extraction fails
        """
        video_id = self._extract_video_id(url)
        if not video_id:
            self.logger.warning(f"Could not extract video ID from URL: {url}")
            return None
        
        # Try multiple methods in order of preference
        methods = [
            self._extract_with_transcript_api,
            self._extract_with_captions_api,
            self._extract_from_video_page
        ]
        
        for method in methods:
            try:
                subtitles = method(video_id)
                if subtitles and len(subtitles.strip()) > 50:  # Minimum content check
                    self.logger.info(f"Successfully extracted {len(subtitles)} characters of subtitles")
                    return subtitles
            except Exception as e:
                self.logger.debug(f"Method {method.__name__} failed: {e}")
                continue
        
        self.logger.warning(f"All subtitle extraction methods failed for video: {video_id}")
        return None
    
    def _extract_video_id(self, url: str) -> Optional[str]:
        """Extract YouTube video ID from various URL formats."""
        patterns = [
            r'(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/|youtube\.com/v/)([a-zA-Z0-9_-]{11})',
            r'youtube\.com/shorts/([a-zA-Z0-9_-]{11})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        return None
    
    def _extract_with_transcript_api(self, video_id: str) -> Optional[str]:
        """Extract subtitles using youtube-transcript-api library (if available)."""
        try:
            # Try to import and use youtube-transcript-api
            from youtube_transcript_api import YouTubeTranscriptApi
            
            # Get transcript
            transcript = YouTubeTranscriptApi.get_transcript(video_id)
            
            # Combine all text entries
            subtitle_text = ' '.join([entry['text'] for entry in transcript])
            
            # Clean up the text
            subtitle_text = self._clean_subtitle_text(subtitle_text)
            
            return subtitle_text
            
        except ImportError:
            self.logger.debug("youtube-transcript-api not available")
            return None
        except Exception as e:
            self.logger.debug(f"Transcript API extraction failed: {e}")
            return None
    
    def _extract_with_captions_api(self, video_id: str) -> Optional[str]:
        """Extract subtitles using YouTube Data API (if API key available)."""
        if not self.api_key:
            return None
        
        try:
            # Get video details to find caption tracks
            video_url = f"https://www.googleapis.com/youtube/v3/videos"
            video_params = {
                'part': 'snippet',
                'id': video_id,
                'key': self.api_key
            }
            
            video_response = self.session.get(video_url, params=video_params, timeout=10)
            video_response.raise_for_status()
            video_data = video_response.json()
            
            if not video_data.get('items'):
                return None
            
            # Get captions list
            captions_url = f"https://www.googleapis.com/youtube/v3/captions"
            captions_params = {
                'part': 'snippet',
                'videoId': video_id,
                'key': self.api_key
            }
            
            captions_response = self.session.get(captions_url, params=captions_params, timeout=10)
            captions_response.raise_for_status()
            captions_data = captions_response.json()
            
            if not captions_data.get('items'):
                return None
            
            # Find the best caption track (prefer auto-generated English)
            best_caption = None
            for caption in captions_data['items']:
                snippet = caption['snippet']
                if snippet['language'] == 'en':
                    if snippet.get('trackKind') == 'asr':  # Auto-generated
                        best_caption = caption
                        break
                    elif not best_caption:  # Manual captions as fallback
                        best_caption = caption
            
            if not best_caption:
                best_caption = captions_data['items'][0]  # Use first available
            
            # Download the caption content
            caption_url = f"https://www.googleapis.com/youtube/v3/captions/{best_caption['id']}"
            caption_params = {
                'key': self.api_key,
                'tfmt': 'srt'  # SubRip format
            }
            
            caption_response = self.session.get(caption_url, params=caption_params, timeout=10)
            caption_response.raise_for_status()
            
            # Parse SRT content
            subtitle_text = self._parse_srt_content(caption_response.text)
            return self._clean_subtitle_text(subtitle_text)
            
        except Exception as e:
            self.logger.debug(f"API caption extraction failed: {e}")
            return None
    
    def _extract_from_video_page(self, video_id: str) -> Optional[str]:
        """Extract subtitles by parsing the YouTube video page."""
        try:
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            response = self.session.get(video_url, timeout=15)
            response.raise_for_status()
            
            page_content = response.text
            
            # Look for caption track URLs in the page source
            # This is a simplified approach - YouTube's actual implementation is more complex
            caption_patterns = [
                r'"captionTracks":\[(.*?)\]',
                r'"captions":.*?"playerCaptionsTracklistRenderer".*?"captionTracks":\[(.*?)\]'
            ]
            
            for pattern in caption_patterns:
                match = re.search(pattern, page_content, re.DOTALL)
                if match:
                    # Try to extract and parse caption data
                    # This would require more complex parsing of the JSON data
                    self.logger.debug("Found caption tracks in page, but full parsing not implemented")
                    break
            
            # For now, return None as full implementation would be quite complex
            return None
            
        except Exception as e:
            self.logger.debug(f"Page-based extraction failed: {e}")
            return None
    
    def _parse_srt_content(self, srt_content: str) -> str:
        """Parse SRT subtitle format and extract text."""
        lines = srt_content.split('\n')
        text_lines = []
        
        for line in lines:
            line = line.strip()
            # Skip sequence numbers, timestamps, and empty lines
            if (line.isdigit() or 
                '-->' in line or 
                not line or
                re.match(r'^\d{2}:\d{2}:\d{2}', line)):
                continue
            
            text_lines.append(line)
        
        return ' '.join(text_lines)
    
    def _clean_subtitle_text(self, text: str) -> str:
        """Clean and normalize subtitle text."""
        if not text:
            return text
        
        # Remove common caption artifacts
        text = re.sub(r'\[.*?\]', '', text)  # Remove [Music], [Applause], etc.
        text = re.sub(r'\(.*?\)', '', text)  # Remove (inaudible), etc.
        text = re.sub(r'<.*?>', '', text)   # Remove HTML tags
        
        # Normalize whitespace
        text = ' '.join(text.split())
        
        # Remove repeated phrases (common in auto-generated captions)
        words = text.split()
        cleaned_words = []
        last_phrase = []
        
        for word in words:
            # Simple repetition detection
            if len(last_phrase) >= 3 and word in last_phrase[-3:]:
                continue
            
            cleaned_words.append(word)
            last_phrase.append(word)
            if len(last_phrase) > 10:
                last_phrase.pop(0)
        
        return ' '.join(cleaned_words)


class VideoContentAnalyzer:
    """Analyze video content (subtitles, titles) to extract tags and topics."""
    
    def __init__(self, max_tags: int = 5):
        """Initialize the content analyzer.
        
        Args:
            max_tags: Maximum number of tags to extract per video
        """
        self.max_tags = max_tags
        self.logger = logging.getLogger(__name__)
        
        # Common words to filter out
        self.stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with',
            'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had',
            'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must',
            'can', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we',
            'they', 'me', 'him', 'her', 'us', 'them', 'my', 'your', 'his', 'her', 'its',
            'our', 'their', 'what', 'where', 'when', 'why', 'how', 'who', 'which', 'all',
            'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no',
            'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't',
            'd', 'll', 've', 're', 'now', 'here', 'there', 'then', 'also', 'just', 'like',
            'get', 'go', 'know', 'see', 'come', 'think', 'take', 'want', 'use', 'make',
            'way', 'time', 'people', 'thing', 'things', 'really', 'actually', 'kind',
            'going', 'little', 'good', 'right', 'back', 'work', 'first', 'last', 'long',
            'new', 'old', 'different', 'great', 'small', 'large', 'big'
        }
        
        # Topic keywords for common video categories
        self.topic_keywords = {
            'technology': ['tech', 'software', 'computer', 'programming', 'code', 'app', 'digital', 'ai', 'machine learning', 'algorithm'],
            'science': ['science', 'research', 'study', 'experiment', 'theory', 'discovery', 'analysis', 'data', 'physics', 'chemistry'],
            'education': ['learn', 'teach', 'lesson', 'course', 'tutorial', 'guide', 'explain', 'instruction', 'knowledge', 'skill'],
            'business': ['business', 'company', 'market', 'finance', 'money', 'economy', 'startup', 'entrepreneur', 'sales', 'management'],
            'health': ['health', 'medical', 'doctor', 'medicine', 'treatment', 'wellness', 'fitness', 'exercise', 'nutrition', 'diet'],
            'entertainment': ['music', 'movie', 'game', 'show', 'entertainment', 'fun', 'comedy', 'drama', 'performance', 'art'],
            'news': ['news', 'current', 'event', 'politics', 'government', 'election', 'policy', 'international', 'breaking', 'report'],
            'lifestyle': ['lifestyle', 'fashion', 'travel', 'food', 'cooking', 'home', 'family', 'personal', 'daily', 'routine']
        }
    
    def extract_tags(self, subtitle_text: str, title: str = None) -> List[str]:
        """Extract relevant tags from subtitle text and video title.
        
        Args:
            subtitle_text: Full subtitle/transcript text
            title: Video title (optional)
            
        Returns:
            List of extracted tags
        """
        if not subtitle_text:
            return []
        
        # Combine title and subtitle text
        full_text = f"{title or ''} {subtitle_text}".lower()
        
        # Extract key phrases and words
        tags = set()
        
        # Method 1: Extract topic-based tags
        topic_tags = self._extract_topic_tags(full_text)
        tags.update(topic_tags)
        
        # Method 2: Extract important nouns and phrases
        important_words = self._extract_important_words(full_text)
        tags.update(important_words)
        
        # Method 3: Extract named entities (simplified)
        entities = self._extract_simple_entities(full_text)
        tags.update(entities)
        
        # Filter and rank tags
        final_tags = self._rank_and_filter_tags(list(tags), full_text)
        
        return final_tags[:self.max_tags]
    
    def _extract_topic_tags(self, text: str) -> Set[str]:
        """Extract topic-based tags using keyword matching."""
        tags = set()
        
        for topic, keywords in self.topic_keywords.items():
            for keyword in keywords:
                if keyword in text:
                    tags.add(topic)
                    break  # Don't add same topic multiple times
        
        return tags
    
    def _extract_important_words(self, text: str) -> Set[str]:
        """Extract important words that aren't stop words."""
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        
        # Count word frequency
        word_freq = {}
        for word in words:
            if word not in self.stop_words:
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Get words that appear multiple times
        important_words = {word for word, freq in word_freq.items() 
                          if freq >= 2 and len(word) >= 4}
        
        return important_words
    
    def _extract_simple_entities(self, text: str) -> Set[str]:
        """Extract simple named entities (capitalized words)."""
        # This is a simplified approach - for better results, use NLP libraries
        entities = set()
        
        # Look for capitalized words (potential proper nouns)
        capitalized_words = re.findall(r'\b[A-Z][a-z]{2,}\b', text)
        
        for word in capitalized_words:
            if (word.lower() not in self.stop_words and 
                len(word) >= 3 and 
                not word.isupper()):  # Avoid ALL CAPS
                entities.add(word.lower())
        
        return entities
    
    def _rank_and_filter_tags(self, tags: List[str], text: str) -> List[str]:
        """Rank and filter tags by relevance."""
        if not tags:
            return []
        
        # Score tags based on frequency and other factors
        tag_scores = {}
        
        for tag in tags:
            score = 0
            
            # Base frequency score
            score += text.count(tag) * 1
            
            # Bonus for topic tags (they're more general/useful)
            if tag in self.topic_keywords:
                score += 5
            
            # Bonus for longer, more specific tags
            score += len(tag) * 0.1
            
            # Penalty for very common words
            if text.count(tag) > len(text.split()) * 0.01:  # More than 1% of words
                score -= 2
            
            tag_scores[tag] = score
        
        # Sort by score and return top tags
        sorted_tags = sorted(tag_scores.items(), key=lambda x: x[1], reverse=True)
        
        return [tag for tag, score in sorted_tags if score > 0]