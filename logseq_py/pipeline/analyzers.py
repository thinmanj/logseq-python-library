"""
Content Analyzers for Pipeline Processing

Provides analyzers for content understanding including sentiment analysis,
topic extraction, summarization, and other text analysis capabilities.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Union, Tuple
import re
import logging
from datetime import datetime
from collections import Counter, defaultdict
import json

from ..models import Block


class ContentAnalyzer(ABC):
    """Abstract base class for content analyzers."""
    
    def __init__(self, name: str):
        self.name = name
        self.logger = logging.getLogger(f"analyzer.{name}")
    
    @abstractmethod
    def analyze(self, content: str) -> Optional[Dict[str, Any]]:
        """Analyze the given content and return results."""
        pass
    
    def can_analyze(self, content: str) -> bool:
        """Check if this analyzer can process the given content."""
        return bool(content and content.strip())
    
    def preprocess_content(self, content: str) -> str:
        """Preprocess content before analysis."""
        if not content:
            return ""
        
        # Basic preprocessing
        content = content.strip()
        # Remove excessive whitespace
        content = re.sub(r'\s+', ' ', content)
        
        return content


class SentimentAnalyzer(ContentAnalyzer):
    """Basic sentiment analysis using lexicon-based approach."""
    
    def __init__(self):
        super().__init__("sentiment")
        
        # Basic sentiment lexicon (in practice, you'd use a more comprehensive one)
        self.positive_words = {
            'good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic',
            'awesome', 'love', 'like', 'enjoy', 'happy', 'pleased', 'satisfied',
            'success', 'successful', 'win', 'winning', 'best', 'perfect',
            'brilliant', 'outstanding', 'superb', 'magnificent', 'marvelous'
        }
        
        self.negative_words = {
            'bad', 'terrible', 'awful', 'horrible', 'hate', 'dislike', 
            'angry', 'sad', 'disappointed', 'frustrated', 'annoyed',
            'fail', 'failure', 'worst', 'useless', 'worthless', 'stupid',
            'ridiculous', 'disgusting', 'pathetic', 'miserable', 'tragic'
        }
        
        # Intensifiers and negations
        self.intensifiers = {'very', 'extremely', 'incredibly', 'really', 'quite', 'absolutely'}
        self.negations = {'not', 'no', 'never', 'none', 'nothing', 'nowhere', 'nobody'}
    
    def analyze(self, content: str) -> Optional[Dict[str, Any]]:
        """Perform sentiment analysis on content."""
        if not self.can_analyze(content):
            return None
        
        content = self.preprocess_content(content).lower()
        words = re.findall(r'\b\w+\b', content)
        
        if not words:
            return None
        
        positive_score = 0
        negative_score = 0
        
        # Simple sentiment scoring
        for i, word in enumerate(words):
            # Check for negation in previous 2 words
            negated = any(neg in words[max(0, i-2):i] for neg in self.negations)
            
            # Check for intensifiers in previous 2 words
            intensified = any(intensifier in words[max(0, i-2):i] for intensifier in self.intensifiers)
            multiplier = 2 if intensified else 1
            
            if word in self.positive_words:
                score = multiplier
                if negated:
                    negative_score += score
                else:
                    positive_score += score
                    
            elif word in self.negative_words:
                score = multiplier
                if negated:
                    positive_score += score
                else:
                    negative_score += score
        
        # Calculate final sentiment
        total_score = positive_score + negative_score
        if total_score == 0:
            sentiment = 'neutral'
            polarity = 0.0
        else:
            polarity = (positive_score - negative_score) / total_score
            if polarity > 0.1:
                sentiment = 'positive'
            elif polarity < -0.1:
                sentiment = 'negative'
            else:
                sentiment = 'neutral'
        
        return {
            'sentiment': sentiment,
            'polarity': polarity,
            'positive_score': positive_score,
            'negative_score': negative_score,
            'total_words': len(words),
            'analyzed_at': datetime.now().isoformat()
        }


class TopicAnalyzer(ContentAnalyzer):
    """Basic topic analysis using keyword extraction."""
    
    def __init__(self):
        super().__init__("topics")
        
        # Common stop words
        self.stop_words = {
            'a', 'an', 'and', 'are', 'as', 'at', 'be', 'been', 'by', 'for',
            'from', 'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that',
            'the', 'to', 'was', 'will', 'with', 'would', 'you', 'your',
            'i', 'me', 'my', 'we', 'our', 'they', 'them', 'their', 'this',
            'these', 'those', 'can', 'could', 'should', 'have', 'had', 'do',
            'does', 'did', 'get', 'got', 'go', 'going', 'come', 'came'
        }
        
        # Domain-specific keyword patterns
        self.topic_patterns = {
            'technology': ['software', 'hardware', 'computer', 'programming', 'code', 'algorithm', 'data', 'api', 'database'],
            'business': ['marketing', 'sales', 'revenue', 'profit', 'customer', 'market', 'strategy', 'growth'],
            'research': ['study', 'analysis', 'research', 'experiment', 'hypothesis', 'theory', 'methodology'],
            'education': ['learning', 'teaching', 'student', 'course', 'lesson', 'education', 'knowledge'],
            'health': ['health', 'medical', 'doctor', 'patient', 'treatment', 'diagnosis', 'medicine'],
            'finance': ['money', 'investment', 'financial', 'budget', 'cost', 'price', 'economic']
        }
    
    def analyze(self, content: str) -> Optional[Dict[str, Any]]:
        """Perform topic analysis on content."""
        if not self.can_analyze(content):
            return None
        
        content = self.preprocess_content(content).lower()
        
        # Extract keywords
        keywords = self._extract_keywords(content)
        
        # Identify topics
        topics = self._identify_topics(content, keywords)
        
        # Extract entities (simple approach)
        entities = self._extract_entities(content)
        
        return {
            'keywords': keywords,
            'topics': topics,
            'entities': entities,
            'analyzed_at': datetime.now().isoformat()
        }
    
    def _extract_keywords(self, content: str) -> List[Dict[str, Any]]:
        """Extract important keywords from content."""
        # Simple word frequency approach
        words = re.findall(r'\b[a-zA-Z]{3,}\b', content.lower())
        
        # Filter stop words and short words
        filtered_words = [word for word in words if word not in self.stop_words and len(word) >= 3]
        
        # Count word frequencies
        word_counts = Counter(filtered_words)
        
        # Get top keywords
        top_keywords = []
        total_words = len(filtered_words)
        
        for word, count in word_counts.most_common(10):
            frequency = count / total_words if total_words > 0 else 0
            top_keywords.append({
                'word': word,
                'count': count,
                'frequency': frequency
            })
        
        return top_keywords
    
    def _identify_topics(self, content: str, keywords: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify topics based on keyword patterns."""
        topic_scores = defaultdict(int)
        
        # Score topics based on pattern matching
        for topic, patterns in self.topic_patterns.items():
            score = 0
            matched_patterns = []
            
            for pattern in patterns:
                if pattern in content:
                    score += content.count(pattern)
                    matched_patterns.append(pattern)
            
            if score > 0:
                topic_scores[topic] = {
                    'score': score,
                    'matched_patterns': matched_patterns
                }
        
        # Convert to sorted list
        topics = []
        for topic, data in sorted(topic_scores.items(), key=lambda x: x[1]['score'], reverse=True):
            topics.append({
                'topic': topic,
                'score': data['score'],
                'matched_patterns': data['matched_patterns'],
                'confidence': min(data['score'] / 10.0, 1.0)  # Normalize confidence
            })
        
        return topics
    
    def _extract_entities(self, content: str) -> List[Dict[str, Any]]:
        """Extract named entities (basic approach)."""
        entities = []
        
        # Extract URLs
        urls = re.findall(r'https?://[^\s]+', content)
        for url in urls:
            entities.append({'text': url, 'type': 'url'})
        
        # Extract email addresses
        emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', content)
        for email in emails:
            entities.append({'text': email, 'type': 'email'})
        
        # Extract mentions (Twitter-style @username)
        mentions = re.findall(r'@\w+', content)
        for mention in mentions:
            entities.append({'text': mention, 'type': 'mention'})
        
        # Extract hashtags
        hashtags = re.findall(r'#\w+', content)
        for hashtag in hashtags:
            entities.append({'text': hashtag, 'type': 'hashtag'})
        
        # Extract dates (basic patterns)
        date_patterns = [
            r'\b\d{1,2}/\d{1,2}/\d{4}\b',  # MM/DD/YYYY
            r'\b\d{4}-\d{2}-\d{2}\b',      # YYYY-MM-DD
            r'\b\w+ \d{1,2}, \d{4}\b'      # Month DD, YYYY
        ]
        
        for pattern in date_patterns:
            dates = re.findall(pattern, content)
            for date in dates:
                entities.append({'text': date, 'type': 'date'})
        
        return entities


class SummaryAnalyzer(ContentAnalyzer):
    """Generate summaries of content using extractive approach."""
    
    def __init__(self):
        super().__init__("summary")
        self.max_sentences = 3
        self.min_sentence_length = 10
    
    def analyze(self, content: str) -> Optional[Dict[str, Any]]:
        """Generate summary of content."""
        if not self.can_analyze(content):
            return None
        
        content = self.preprocess_content(content)
        
        # Split into sentences
        sentences = self._split_sentences(content)
        
        if len(sentences) <= self.max_sentences:
            # Content is already short enough
            return {
                'summary': content,
                'sentences': sentences,
                'compression_ratio': 1.0,
                'method': 'full_content',
                'analyzed_at': datetime.now().isoformat()
            }
        
        # Score sentences for importance
        scored_sentences = self._score_sentences(sentences, content)
        
        # Select top sentences
        top_sentences = sorted(scored_sentences, key=lambda x: x['score'], reverse=True)[:self.max_sentences]
        
        # Reorder by original position
        summary_sentences = sorted(top_sentences, key=lambda x: x['position'])
        
        summary = ' '.join([s['text'] for s in summary_sentences])
        compression_ratio = len(summary) / len(content) if len(content) > 0 else 0
        
        return {
            'summary': summary,
            'sentences': [s['text'] for s in summary_sentences],
            'compression_ratio': compression_ratio,
            'method': 'extractive',
            'sentence_scores': [{'text': s['text'], 'score': s['score']} for s in top_sentences],
            'analyzed_at': datetime.now().isoformat()
        }
    
    def _split_sentences(self, content: str) -> List[str]:
        """Split content into sentences."""
        # Simple sentence splitting
        sentences = re.split(r'[.!?]+', content)
        
        # Clean and filter sentences
        clean_sentences = []
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) >= self.min_sentence_length:
                clean_sentences.append(sentence)
        
        return clean_sentences
    
    def _score_sentences(self, sentences: List[str], full_content: str) -> List[Dict[str, Any]]:
        """Score sentences for importance."""
        # Calculate word frequencies
        words = re.findall(r'\b\w+\b', full_content.lower())
        word_freq = Counter(words)
        
        scored_sentences = []
        
        for i, sentence in enumerate(sentences):
            score = self._calculate_sentence_score(sentence, word_freq)
            
            scored_sentences.append({
                'text': sentence,
                'position': i,
                'score': score,
                'length': len(sentence)
            })
        
        return scored_sentences
    
    def _calculate_sentence_score(self, sentence: str, word_freq: Counter) -> float:
        """Calculate importance score for a sentence."""
        words = re.findall(r'\b\w+\b', sentence.lower())
        
        if not words:
            return 0.0
        
        # Sum of word frequencies
        freq_sum = sum(word_freq.get(word, 0) for word in words)
        
        # Normalize by sentence length
        score = freq_sum / len(words)
        
        # Bonus for sentence position (first and last sentences are often important)
        # This would need the sentence position in the full context
        
        # Bonus for sentence length (moderate length preferred)
        length_bonus = 1.0
        if 50 <= len(sentence) <= 200:
            length_bonus = 1.2
        elif len(sentence) < 20 or len(sentence) > 300:
            length_bonus = 0.8
        
        return score * length_bonus


class StructureAnalyzer(ContentAnalyzer):
    """Analyze content structure and formatting."""
    
    def __init__(self):
        super().__init__("structure")
    
    def analyze(self, content: str) -> Optional[Dict[str, Any]]:
        """Analyze content structure."""
        if not self.can_analyze(content):
            return None
        
        # Analyze various structural elements
        structure = {
            'length': len(content),
            'word_count': len(re.findall(r'\b\w+\b', content)),
            'sentence_count': len(re.split(r'[.!?]+', content)),
            'paragraph_count': len([p for p in content.split('\n\n') if p.strip()]),
            'line_count': len(content.split('\n')),
            'has_lists': self._has_lists(content),
            'has_code': self._has_code_blocks(content),
            'has_links': self._has_links(content),
            'has_images': self._has_images(content),
            'formatting_elements': self._analyze_formatting(content),
            'analyzed_at': datetime.now().isoformat()
        }
        
        # Calculate readability metrics
        structure.update(self._calculate_readability(content, structure))
        
        return structure
    
    def _has_lists(self, content: str) -> bool:
        """Check if content contains lists."""
        # Check for bullet points or numbered lists
        list_patterns = [
            r'^\s*[-*+]\s',  # Bullet lists
            r'^\s*\d+\.\s',  # Numbered lists
        ]
        
        for pattern in list_patterns:
            if re.search(pattern, content, re.MULTILINE):
                return True
        
        return False
    
    def _has_code_blocks(self, content: str) -> bool:
        """Check if content contains code blocks."""
        # Check for code block markers
        code_patterns = [
            r'```',          # Markdown code blocks
            r'`[^`]+`',      # Inline code
            r'^    \w',      # Indented code (4 spaces)
        ]
        
        for pattern in code_patterns:
            if re.search(pattern, content, re.MULTILINE):
                return True
        
        return False
    
    def _has_links(self, content: str) -> bool:
        """Check if content contains links."""
        link_patterns = [
            r'https?://[^\s]+',       # URLs
            r'\[.*?\]\(.*?\)',        # Markdown links
            r'\[\[.*?\]\]',           # Wiki-style links
        ]
        
        for pattern in link_patterns:
            if re.search(pattern, content):
                return True
        
        return False
    
    def _has_images(self, content: str) -> bool:
        """Check if content contains images."""
        image_patterns = [
            r'!\[.*?\]\(.*?\)',       # Markdown images
            r'\.(jpg|jpeg|png|gif|svg)',  # Image file extensions
        ]
        
        for pattern in image_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                return True
        
        return False
    
    def _analyze_formatting(self, content: str) -> Dict[str, int]:
        """Analyze formatting elements."""
        elements = {
            'headers': len(re.findall(r'^#+\s', content, re.MULTILINE)),
            'bold_text': len(re.findall(r'\*\*.*?\*\*', content)),
            'italic_text': len(re.findall(r'\*.*?\*', content)),
            'blockquotes': len(re.findall(r'^>\s', content, re.MULTILINE)),
            'horizontal_rules': len(re.findall(r'^---+', content, re.MULTILINE)),
        }
        
        return elements
    
    def _calculate_readability(self, content: str, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate basic readability metrics."""
        word_count = structure['word_count']
        sentence_count = structure['sentence_count']
        
        if word_count == 0 or sentence_count == 0:
            return {'readability': {'words_per_sentence': 0, 'complexity': 'unknown'}}
        
        # Average words per sentence
        words_per_sentence = word_count / sentence_count
        
        # Simple complexity assessment
        if words_per_sentence < 10:
            complexity = 'simple'
        elif words_per_sentence < 20:
            complexity = 'moderate'
        else:
            complexity = 'complex'
        
        return {
            'readability': {
                'words_per_sentence': words_per_sentence,
                'complexity': complexity
            }
        }


class AnalyzerRegistry:
    """Registry for managing content analyzers."""
    
    def __init__(self):
        self.analyzers: Dict[str, ContentAnalyzer] = {}
        self.logger = logging.getLogger("analyzer.registry")
        
        # Register default analyzers
        self.register_defaults()
    
    def register(self, analyzer: ContentAnalyzer):
        """Register an analyzer."""
        self.analyzers[analyzer.name] = analyzer
        self.logger.info(f"Registered analyzer: {analyzer.name}")
    
    def get(self, name: str) -> Optional[ContentAnalyzer]:
        """Get analyzer by name."""
        return self.analyzers.get(name)
    
    def get_all(self) -> Dict[str, ContentAnalyzer]:
        """Get all registered analyzers."""
        return self.analyzers.copy()
    
    def analyze_content(self, content: str, analyzer_names: List[str] = None) -> Dict[str, Any]:
        """Analyze content using specified analyzers."""
        results = {}
        
        if analyzer_names:
            analyzers = [self.get(name) for name in analyzer_names]
            analyzers = [a for a in analyzers if a is not None]
        else:
            analyzers = list(self.analyzers.values())
        
        for analyzer in analyzers:
            try:
                if analyzer.can_analyze(content):
                    result = analyzer.analyze(content)
                    if result:
                        results[analyzer.name] = result
            except Exception as e:
                results[analyzer.name] = {'error': str(e)}
        
        return results
    
    def register_defaults(self):
        """Register default analyzers."""
        self.register(SentimentAnalyzer())
        self.register(TopicAnalyzer())
        self.register(SummaryAnalyzer())
        self.register(StructureAnalyzer())


# Global registry instance
analyzer_registry = AnalyzerRegistry()


# Convenience functions
def get_analyzer(name: str) -> Optional[ContentAnalyzer]:
    """Get analyzer by name from global registry."""
    return analyzer_registry.get(name)


def get_all_analyzers() -> Dict[str, ContentAnalyzer]:
    """Get all analyzers from global registry."""
    return analyzer_registry.get_all()


def analyze_content(content: str, analyzer_names: List[str] = None) -> Dict[str, Any]:
    """Analyze content using specified analyzers."""
    return analyzer_registry.analyze_content(content, analyzer_names)


def analyze_block(block: Block, analyzer_names: List[str] = None) -> Dict[str, Any]:
    """Analyze a block's content using specified analyzers."""
    if not block.content:
        return {}
    
    return analyze_content(block.content, analyzer_names)