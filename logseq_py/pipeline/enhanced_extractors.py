"""
Enhanced Content Extractors for X/Twitter and PDF Processing

This module provides extractors for X/Twitter posts and PDF documents,
extending the video processing pipeline to handle diverse content types.
"""

import re
import logging
import requests
import json
from typing import Optional, List, Dict, Any, Set
from urllib.parse import urlparse, parse_qs
from datetime import datetime
import tempfile
import os


class XTwitterExtractor:
    """Extract content from X (Twitter) URLs."""
    
    def __init__(self, bearer_token: Optional[str] = None):
        """Initialize the X/Twitter extractor.
        
        Args:
            bearer_token: Optional Twitter API Bearer Token for enhanced features
        """
        self.bearer_token = bearer_token
        self.logger = logging.getLogger(__name__)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
        
        # Twitter URL patterns
        self.twitter_patterns = [
            r'(?:twitter\.com|x\.com)/([^/]+)/status/(\d+)',
            r'(?:twitter\.com|x\.com)/([^/]+)/status/(\d+)\?.*',
            r't\.co/([a-zA-Z0-9]+)'  # Shortened Twitter links
        ]
    
    def can_extract(self, url: str) -> bool:
        """Check if URL is a Twitter/X link."""
        for pattern in self.twitter_patterns:
            if re.search(pattern, url, re.IGNORECASE):
                return True
        return False
    
    def extract_tweet_info(self, url: str) -> Optional[Dict[str, Any]]:
        """Extract tweet information from Twitter/X URL."""
        self.logger.info(f"Processing X/Twitter URL: {url}")
        
        # Extract tweet ID from URL
        tweet_id = self._extract_tweet_id(url)
        if not tweet_id:
            return None
        
        base_info = {
            'url': url,
            'tweet_id': tweet_id,
            'platform': 'x-twitter',
            'extracted_at': datetime.now().isoformat()
        }
        
        # Try multiple extraction methods
        methods = [
            self._extract_with_api,
            self._extract_with_oembed,
            self._extract_from_page
        ]
        
        for method in methods:
            try:
                result = method(tweet_id, url)
                if result:
                    base_info.update(result)
                    return base_info
            except Exception as e:
                self.logger.debug(f"Method {method.__name__} failed: {e}")
        
        # Return basic info if all methods fail
        base_info.update({
            'status': 'limited',
            'title': f"X/Twitter Post {tweet_id}",
            'error': 'Could not extract full tweet content'
        })
        return base_info
    
    def _extract_tweet_id(self, url: str) -> Optional[str]:
        """Extract tweet ID from various Twitter URL formats."""
        # Handle t.co shortened URLs by following redirects
        if 't.co/' in url:
            try:
                response = self.session.head(url, allow_redirects=True, timeout=10)
                url = response.url
            except:
                pass
        
        for pattern in self.twitter_patterns[:-1]:  # Skip t.co pattern
            match = re.search(pattern, url, re.IGNORECASE)
            if match:
                return match.group(2)  # Tweet ID is second group
        
        return None
    
    def _extract_with_api(self, tweet_id: str, url: str) -> Optional[Dict[str, Any]]:
        """Extract using Twitter API v2 (if bearer token available)."""
        if not self.bearer_token:
            return None
        
        api_url = f"https://api.twitter.com/2/tweets/{tweet_id}"
        headers = {
            'Authorization': f'Bearer {self.bearer_token}',
            'User-Agent': 'LogseqPython/1.0'
        }
        
        params = {
            'expansions': 'author_id',
            'tweet.fields': 'created_at,public_metrics,context_annotations,lang',
            'user.fields': 'name,username,verified'
        }
        
        response = self.session.get(api_url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        if 'data' not in data:
            return None
        
        tweet = data['data']
        author = data.get('includes', {}).get('users', [{}])[0] if data.get('includes') else {}
        
        return {
            'title': f"Tweet by @{author.get('username', 'unknown')}",
            'content': tweet.get('text'),
            'author': author.get('name'),
            'username': author.get('username'),
            'created_at': tweet.get('created_at'),
            'language': tweet.get('lang'),
            'retweet_count': tweet.get('public_metrics', {}).get('retweet_count', 0),
            'like_count': tweet.get('public_metrics', {}).get('like_count', 0),
            'verified': author.get('verified', False),
            'status': 'success',
            'data_source': 'twitter_api'
        }
    
    def _extract_with_oembed(self, tweet_id: str, url: str) -> Optional[Dict[str, Any]]:
        """Extract using Twitter oEmbed API."""
        oembed_url = "https://publish.twitter.com/oembed"
        params = {
            'url': url,
            'omit_script': 'true',
            'dnt': 'true'
        }
        
        response = self.session.get(oembed_url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        # Extract author from HTML
        html = data.get('html', '')
        author_match = re.search(r'(@\w+)', html)
        
        return {
            'title': f"Tweet {data.get('author_name', 'Unknown')}",
            'author': data.get('author_name'),
            'username': author_match.group(1) if author_match else None,
            'html_content': html,
            'status': 'success',
            'data_source': 'oembed'
        }
    
    def _extract_from_page(self, tweet_id: str, url: str) -> Optional[Dict[str, Any]]:
        """Extract by parsing the Twitter page HTML."""
        try:
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            
            content = response.text
            
            # Try to extract basic info from HTML
            title_match = re.search(r'<title[^>]*>([^<]+)</title>', content)
            
            # Look for JSON-LD structured data
            json_ld_match = re.search(r'<script[^>]*type="application/ld\+json"[^>]*>([^<]+)</script>', content)
            
            result = {
                'title': title_match.group(1).strip() if title_match else f"X/Twitter Post {tweet_id}",
                'status': 'limited',
                'data_source': 'html_parsing'
            }
            
            if json_ld_match:
                try:
                    json_data = json.loads(json_ld_match.group(1))
                    if isinstance(json_data, dict):
                        result.update({
                            'title': json_data.get('headline', result['title']),
                            'author': json_data.get('author', {}).get('name'),
                            'date_published': json_data.get('datePublished')
                        })
                except:
                    pass
            
            return result
            
        except Exception as e:
            self.logger.debug(f"HTML parsing failed: {e}")
            return None


class PDFExtractor:
    """Extract content from PDF URLs."""
    
    def __init__(self, max_content_length: int = 5000):
        """Initialize PDF extractor.
        
        Args:
            max_content_length: Maximum content length to extract from PDFs
        """
        self.max_content_length = max_content_length
        self.logger = logging.getLogger(__name__)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
    
    def can_extract(self, url: str) -> bool:
        """Check if URL points to a PDF."""
        return (url.lower().endswith('.pdf') or 
                'pdf' in url.lower() or
                self._check_pdf_header(url))
    
    def _check_pdf_header(self, url: str) -> bool:
        """Check if URL serves a PDF by checking headers."""
        try:
            response = self.session.head(url, timeout=10)
            content_type = response.headers.get('content-type', '').lower()
            return 'pdf' in content_type
        except:
            return False
    
    def extract_pdf_info(self, url: str) -> Optional[Dict[str, Any]]:
        """Extract PDF document information."""
        self.logger.info(f"Processing PDF URL: {url}")
        
        base_info = {
            'url': url,
            'platform': 'pdf',
            'extracted_at': datetime.now().isoformat()
        }
        
        try:
            # Download PDF headers and basic info
            response = self.session.head(url, timeout=10)
            response.raise_for_status()
            
            content_length = response.headers.get('content-length')
            content_type = response.headers.get('content-type')
            
            base_info.update({
                'content_type': content_type,
                'size_bytes': int(content_length) if content_length else None,
                'size_mb': round(int(content_length) / (1024 * 1024), 2) if content_length else None
            })
            
            # Try to extract PDF metadata
            pdf_info = self._extract_pdf_metadata(url)
            if pdf_info:
                base_info.update(pdf_info)
            else:
                # Fallback: generate title from URL
                base_info.update({
                    'title': self._generate_title_from_url(url),
                    'status': 'limited',
                    'note': 'Basic info only - PDF parsing not available'
                })
            
            return base_info
            
        except Exception as e:
            base_info.update({
                'title': self._generate_title_from_url(url),
                'status': 'error',
                'error': str(e)
            })
            return base_info
    
    def _extract_pdf_metadata(self, url: str) -> Optional[Dict[str, Any]]:
        """Extract PDF metadata using PyPDF2 if available."""
        try:
            import PyPDF2
            import io
        except ImportError:
            self.logger.debug("PyPDF2 not available for PDF parsing")
            return None
        
        try:
            # Download PDF content (limited size)
            response = self.session.get(url, stream=True, timeout=30)
            response.raise_for_status()
            
            # Read limited content
            pdf_content = b''
            downloaded_size = 0
            max_download = 10 * 1024 * 1024  # 10MB limit
            
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    pdf_content += chunk
                    downloaded_size += len(chunk)
                    if downloaded_size > max_download:
                        break
            
            # Parse PDF
            pdf_file = io.BytesIO(pdf_content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            # Extract metadata
            metadata = pdf_reader.metadata or {}
            
            # Extract some text content
            text_content = ""
            num_pages = len(pdf_reader.pages)
            pages_to_read = min(3, num_pages)  # Read first 3 pages max
            
            for i in range(pages_to_read):
                try:
                    page_text = pdf_reader.pages[i].extract_text()
                    text_content += page_text + "\n"
                    if len(text_content) > self.max_content_length:
                        text_content = text_content[:self.max_content_length]
                        break
                except:
                    continue
            
            return {
                'title': metadata.get('/Title') or self._generate_title_from_url(url),
                'author': metadata.get('/Author'),
                'subject': metadata.get('/Subject'),
                'creator': metadata.get('/Creator'),
                'producer': metadata.get('/Producer'),
                'creation_date': str(metadata.get('/CreationDate')) if metadata.get('/CreationDate') else None,
                'modification_date': str(metadata.get('/ModDate')) if metadata.get('/ModDate') else None,
                'num_pages': num_pages,
                'content_preview': text_content.strip()[:500] + "..." if text_content.strip() else None,
                'status': 'success',
                'data_source': 'pdf_extraction'
            }
            
        except Exception as e:
            self.logger.debug(f"PDF parsing failed: {e}")
            return None
    
    def _generate_title_from_url(self, url: str) -> str:
        """Generate a title from PDF URL."""
        # Extract filename from URL
        path = urlparse(url).path
        filename = os.path.basename(path)
        
        if filename and filename.lower().endswith('.pdf'):
            # Clean up filename
            title = filename[:-4]  # Remove .pdf extension
            title = title.replace('-', ' ').replace('_', ' ')
            title = ' '.join(word.capitalize() for word in title.split())
            return title
        
        return "PDF Document"


class ContentAnalyzer:
    """Enhanced content analyzer for videos, tweets, and PDFs using TF-IDF and NLP."""
    
    def __init__(self, max_topics: int = 5):
        """Initialize the content analyzer.
        
        Args:
            max_topics: Maximum number of topics to extract per content item
        """
        self.max_topics = max_topics
        self.logger = logging.getLogger(__name__)
        
        # Try to use nltk for better text processing
        self.use_nltk = False
        try:
            import nltk
            from nltk.corpus import stopwords
            from nltk.tokenize import word_tokenize
            try:
                self.stopwords = set(stopwords.words('english'))
                self.use_nltk = True
            except LookupError:
                self.logger.debug("NLTK stopwords not found, using basic stopwords")
        except ImportError:
            self.logger.debug("NLTK not available, using basic text processing")
        
        # Enhanced topic keywords for different content types
        self.topic_keywords = {
            'technology': ['tech', 'software', 'computer', 'programming', 'code', 'app', 'digital', 'ai', 'machine learning', 'algorithm', 'data', 'python', 'javascript'],
            'science': ['science', 'research', 'study', 'experiment', 'theory', 'discovery', 'analysis', 'physics', 'chemistry', 'biology', 'medical'],
            'education': ['learn', 'teach', 'lesson', 'course', 'tutorial', 'guide', 'explain', 'instruction', 'knowledge', 'skill', 'university', 'school'],
            'business': ['business', 'company', 'market', 'finance', 'money', 'economy', 'startup', 'entrepreneur', 'sales', 'management', 'strategy'],
            'health': ['health', 'medical', 'doctor', 'medicine', 'treatment', 'wellness', 'fitness', 'exercise', 'nutrition', 'diet', 'mental health'],
            'entertainment': ['music', 'movie', 'game', 'show', 'entertainment', 'fun', 'comedy', 'drama', 'performance', 'art', 'creative'],
            'news': ['news', 'current', 'event', 'politics', 'government', 'election', 'policy', 'international', 'breaking', 'report', 'journalism'],
            'lifestyle': ['lifestyle', 'fashion', 'travel', 'food', 'cooking', 'home', 'family', 'personal', 'daily', 'routine', 'culture'],
            'social': ['social', 'community', 'discussion', 'opinion', 'debate', 'communication', 'network', 'relationship', 'society'],
            'academic': ['paper', 'journal', 'academic', 'research', 'publication', 'thesis', 'conference', 'peer review', 'citation', 'scholarly']
        }
        
        # Common words to filter out
        self.stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with',
            'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had',
            'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must',
            'can', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we',
            'they', 'me', 'him', 'her', 'us', 'them', 'my', 'your', 'his', 'her', 'its',
            'our', 'their', 'what', 'where', 'when', 'why', 'how', 'who', 'which', 'all',
            'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no',
            'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 'now',
            'here', 'there', 'then', 'also', 'just', 'like', 'get', 'go', 'know', 'see',
            'come', 'think', 'take', 'want', 'use', 'make', 'way', 'time', 'people'
        }
    
    def extract_topics(self, content: str, title: str = None, platform: str = 'unknown') -> List[str]:
        """Extract relevant topics from content using advanced NLP techniques.
        
        Args:
            content: Text content to analyze
            title: Content title (optional)
            platform: Content platform type
            
        Returns:
            List of extracted topics
        """
        if not content:
            return []
        
        # Combine title and content, giving more weight to title
        full_text = f"{title or ''} {title or ''} {content}".lower()
        
        # Extract topics using multiple methods
        topics = set()
        
        # Method 1: Multi-word phrase extraction (bigrams, trigrams)
        phrases = self._extract_key_phrases(full_text)
        topics.update(phrases)
        
        # Method 2: Topic-based keyword matching (domain categories)
        topic_matches = self._extract_topic_keywords(full_text)
        topics.update(topic_matches)
        
        # Method 3: Important single words with TF-IDF scoring
        important_words = self._extract_important_words_tfidf(full_text)
        topics.update(important_words)
        
        # Method 4: Platform-specific extraction
        if platform == 'x-twitter':
            hashtag_topics = self._extract_hashtags(content)
            topics.update(hashtag_topics)
        elif platform == 'pdf':
            academic_topics = self._extract_academic_topics(full_text)
            topics.update(academic_topics)
        
        # Method 5: Extract from title explicitly
        if title:
            title_topics = self._extract_from_title(title)
            topics.update(title_topics)
        
        # Rank and filter topics using advanced scoring
        final_topics = self._rank_topics_advanced(list(topics), full_text, title)
        
        return final_topics[:self.max_topics]
    
    def _extract_topic_keywords(self, text: str) -> Set[str]:
        """Extract topics based on keyword matching."""
        topics = set()
        
        for topic, keywords in self.topic_keywords.items():
            for keyword in keywords:
                if keyword in text:
                    topics.add(topic)
                    break
        
        return topics
    
    def _extract_important_words(self, text: str) -> Set[str]:
        """Extract important words that aren't stop words."""
        words = re.findall(r'\b[a-zA-Z]{4,}\b', text.lower())
        
        word_freq = {}
        for word in words:
            if word not in self.stop_words and len(word) >= 4:
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Get words that appear multiple times
        important_words = {word for word, freq in word_freq.items() 
                          if freq >= 2 and len(word) >= 4}
        
        return important_words
    
    def _extract_hashtags(self, content: str) -> Set[str]:
        """Extract topics from hashtags in Twitter content."""
        hashtags = re.findall(r'#(\w+)', content)
        return {tag.lower() for tag in hashtags if len(tag) >= 3}
    
    def _extract_academic_topics(self, text: str) -> Set[str]:
        """Extract topics specific to academic/PDF content."""
        academic_indicators = ['abstract', 'introduction', 'methodology', 'results', 'conclusion', 
                             'references', 'doi', 'journal', 'volume', 'issue']
        
        topics = set()
        for indicator in academic_indicators:
            if indicator in text:
                topics.add('academic')
                break
        
        return topics
    
    def _extract_key_phrases(self, text: str) -> Set[str]:
        """Extract meaningful multi-word phrases (bigrams, trigrams)."""
        words = re.findall(r'\b[a-z]{3,}\b', text.lower())
        if not words:
            return set()
        
        phrases = set()
        
        # Extract bigrams (two-word combinations)
        for i in range(len(words) - 1):
            word1, word2 = words[i], words[i+1]
            if word1 not in self.stop_words and word2 not in self.stop_words:
                bigram = f"{word1}-{word2}"
                # Only keep if appears multiple times or contains domain keywords
                if text.count(f"{word1} {word2}") >= 2 or self._is_domain_term(word1, word2):
                    phrases.add(bigram)
        
        # Extract trigrams (three-word combinations) for highly specific topics
        for i in range(len(words) - 2):
            word1, word2, word3 = words[i], words[i+1], words[i+2]
            if (word1 not in self.stop_words and 
                word2 not in self.stop_words and 
                word3 not in self.stop_words):
                trigram = f"{word1}-{word2}-{word3}"
                if text.count(f"{word1} {word2} {word3}") >= 2:
                    phrases.add(trigram)
        
        return phrases
    
    def _is_domain_term(self, word1: str, word2: str) -> bool:
        """Check if word combination is a known domain term."""
        domain_terms = {
            ('machine', 'learning'), ('deep', 'learning'), ('data', 'science'),
            ('natural', 'language'), ('computer', 'vision'), ('neural', 'network'),
            ('artificial', 'intelligence'), ('software', 'engineering'),
            ('web', 'development'), ('cloud', 'computing'), ('big', 'data'),
            ('business', 'intelligence'), ('data', 'analysis'), ('time', 'series'),
            ('reinforcement', 'learning'), ('computer', 'science'), ('machine', 'vision'),
            ('quantum', 'computing'), ('distributed', 'systems'), ('operating', 'system')
        }
        return (word1, word2) in domain_terms
    
    def _extract_from_title(self, title: str) -> Set[str]:
        """Extract topics specifically from title."""
        topics = set()
        title_lower = title.lower()
        
        # Extract capitalized words (likely important nouns/topics)
        capitalized = re.findall(r'\b[A-Z][a-z]{2,}\b', title)
        for word in capitalized:
            word_lower = word.lower()
            if word_lower not in self.stop_words and len(word_lower) >= 3:
                topics.add(word_lower)
        
        # Extract words in special formatting (quotes, brackets, etc.)
        special_words = re.findall(r'["\']([^"\'\ ]{4,})["\']', title)
        topics.update([w.lower() for w in special_words if w.lower() not in self.stop_words])
        
        return topics
    
    def _extract_important_words_tfidf(self, text: str) -> Set[str]:
        """Extract important words using TF-IDF-like scoring."""
        words = re.findall(r'\b[a-zA-Z]{4,}\b', text.lower())
        
        if not words:
            return set()
        
        # Calculate term frequency
        word_freq = {}
        total_words = len(words)
        
        for word in words:
            if word not in self.stop_words:
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Calculate TF score (normalized frequency)
        tf_scores = {}
        for word, freq in word_freq.items():
            # TF with sublinear scaling
            tf = 1 + (freq / total_words) * 100
            
            # Bonus for words that appear in multiple forms (plurals, etc.)
            variations = sum(1 for w in word_freq if w.startswith(word[:4]))
            
            # Final score
            score = tf * (1 + variations * 0.1)
            tf_scores[word] = score
        
        # Get top scoring words
        sorted_words = sorted(tf_scores.items(), key=lambda x: x[1], reverse=True)
        
        # Return top words that appear at least twice
        important = set()
        for word, score in sorted_words[:15]:
            if word_freq[word] >= 2 and len(word) >= 4:
                important.add(word)
        
        return important
    
    def _rank_topics_advanced(self, topics: List[str], text: str, title: str = None) -> List[str]:
        """Rank topics by relevance using advanced scoring."""
        if not topics:
            return []
        
        topic_scores = {}
        text_lower = text.lower()
        title_lower = (title or "").lower()
        
        for topic in topics:
            score = 0
            topic_clean = topic.replace('-', ' ')
            
            # 1. Frequency in content
            freq = text_lower.count(topic_clean)
            score += freq * 2
            
            # 2. Title presence (very important)
            if title_lower and topic_clean in title_lower:
                score += 10
            
            # 3. Category topics get bonus
            if topic in self.topic_keywords:
                score += 5
            
            # 4. Length bonus (more specific is better)
            words_in_topic = len(topic.split('-')) if '-' in topic else 1
            score += words_in_topic * 2
            
            # 5. Domain term bonus
            if '-' in topic:
                words = topic.split('-')
                if len(words) == 2 and self._is_domain_term(words[0], words[1]):
                    score += 8
            
            # 6. Penalize very common words even if not in stopwords
            if freq > len(text_lower.split()) * 0.05:  # More than 5% of words
                score -= 3
            
            # 7. Bonus for words with numbers or special technical terms
            if re.search(r'\d|api|sql|http|tech|data', topic_clean):
                score += 2
            
            topic_scores[topic] = max(score, 0)
        
        # Sort by score
        sorted_topics = sorted(topic_scores.items(), key=lambda x: x[1], reverse=True)
        
        # Filter out low-scoring topics and duplicates
        final_topics = []
        seen_roots = set()
        
        for topic, score in sorted_topics:
            if score < 1:
                continue
            
            # Avoid near-duplicates (e.g., "learning" and "machine-learning")
            topic_root = topic.split('-')[0] if '-' in topic else topic
            if topic_root not in seen_roots or '-' in topic:
                final_topics.append(topic)
                seen_roots.add(topic_root)
        
        return final_topics
    
    def _rank_topics(self, topics: List[str], text: str) -> List[str]:
        """Legacy rank topics by relevance (kept for compatibility)."""
        return self._rank_topics_advanced(topics, text)
