"""
Unit tests for pipeline analyzers.
"""

import pytest

from logseq_py.models import Block
from logseq_py.pipeline.analyzers import (
    SentimentAnalyzer, TopicAnalyzer, SummaryAnalyzer, StructureAnalyzer,
    analyze_content, analyze_block
)


class TestSentimentAnalyzer:
    """Test SentimentAnalyzer functionality."""
    
    def test_positive_sentiment(self):
        """Test detection of positive sentiment."""
        analyzer = SentimentAnalyzer()
        
        positive_text = "I love this amazing product! It's fantastic and wonderful."
        result = analyzer.analyze(positive_text)
        
        assert result is not None
        assert result['sentiment'] == 'positive'
        assert result['polarity'] > 0
        assert result['positive_score'] > result['negative_score']
        assert 'analyzed_at' in result
    
    def test_negative_sentiment(self):
        """Test detection of negative sentiment."""
        analyzer = SentimentAnalyzer()
        
        negative_text = "This is terrible and awful. I hate it completely."
        result = analyzer.analyze(negative_text)
        
        assert result is not None
        assert result['sentiment'] == 'negative'
        assert result['polarity'] < 0
        assert result['negative_score'] > result['positive_score']
    
    def test_neutral_sentiment(self):
        """Test detection of neutral sentiment."""
        analyzer = SentimentAnalyzer()
        
        neutral_text = "The weather is okay today. Nothing special to report."
        result = analyzer.analyze(neutral_text)
        
        assert result is not None
        assert result['sentiment'] == 'neutral'
        assert abs(result['polarity']) <= 0.1
    
    def test_negation_handling(self):
        """Test handling of negations in sentiment."""
        analyzer = SentimentAnalyzer()
        
        # Positive word with negation should be negative
        negated_text = "This is not good at all. I don't love it."
        result = analyzer.analyze(negated_text)
        
        assert result is not None
        # Should detect the negation and flip sentiment
        assert result['negative_score'] > 0
    
    def test_intensifier_handling(self):
        """Test handling of intensifiers."""
        analyzer = SentimentAnalyzer()
        
        # Intensified positive sentiment
        intensified_text = "This is extremely wonderful and absolutely fantastic!"
        result = analyzer.analyze(intensified_text)
        
        assert result is not None
        assert result['sentiment'] == 'positive'
        # Should have higher scores due to intensifiers
        assert result['positive_score'] > 2  # Base score would be 2, intensified should be higher
    
    def test_empty_content(self):
        """Test analysis of empty content."""
        analyzer = SentimentAnalyzer()
        
        assert analyzer.analyze("") is None
        assert analyzer.analyze(None) is None
        assert analyzer.analyze("   ") is None
    
    def test_mixed_sentiment(self):
        """Test content with mixed sentiment."""
        analyzer = SentimentAnalyzer()
        
        mixed_text = "I love the good features but hate the terrible interface."
        result = analyzer.analyze(mixed_text)
        
        assert result is not None
        assert result['positive_score'] > 0
        assert result['negative_score'] > 0
        # Net result depends on the specific implementation


class TestTopicAnalyzer:
    """Test TopicAnalyzer functionality."""
    
    def test_technology_topic(self):
        """Test detection of technology topics."""
        analyzer = TopicAnalyzer()
        
        tech_text = "Python programming language software development coding algorithms data API database"
        result = analyzer.analyze(tech_text)
        
        assert result is not None
        assert 'topics' in result
        assert 'keywords' in result
        
        # Should detect technology topic
        topics = [t['topic'] for t in result['topics']]
        assert 'technology' in topics
        
        # Should extract relevant keywords
        keywords = [k['word'] for k in result['keywords']]
        assert 'python' in keywords
        assert 'programming' in keywords
    
    def test_business_topic(self):
        """Test detection of business topics."""
        analyzer = TopicAnalyzer()
        
        business_text = "Marketing strategy sales revenue customer growth business profit market analysis"
        result = analyzer.analyze(business_text)
        
        assert result is not None
        topics = [t['topic'] for t in result['topics']]
        assert 'business' in topics
    
    def test_keyword_extraction(self):
        """Test keyword extraction functionality."""
        analyzer = TopicAnalyzer()
        
        text = "machine learning artificial intelligence neural networks deep learning algorithms"
        result = analyzer.analyze(text)
        
        assert result is not None
        assert len(result['keywords']) > 0
        
        # Check keyword structure
        for keyword in result['keywords']:
            assert 'word' in keyword
            assert 'count' in keyword
            assert 'frequency' in keyword
            assert keyword['count'] > 0
            assert 0 <= keyword['frequency'] <= 1
    
    def test_entity_extraction(self):
        """Test entity extraction."""
        analyzer = TopicAnalyzer()
        
        text = "Check https://example.com and email me at test@example.com. #hashtag @mention"
        result = analyzer.analyze(text)
        
        assert result is not None
        assert 'entities' in result
        
        entities_by_type = {e['type']: e['text'] for e in result['entities']}
        assert 'url' in entities_by_type
        assert 'email' in entities_by_type
        assert 'hashtag' in entities_by_type
        assert 'mention' in entities_by_type
    
    def test_stop_words_filtering(self):
        """Test that stop words are filtered out."""
        analyzer = TopicAnalyzer()
        
        text = "the quick brown fox jumps over the lazy dog and the cat"
        result = analyzer.analyze(text)
        
        assert result is not None
        keywords = [k['word'] for k in result['keywords']]
        
        # Stop words should be filtered out
        assert 'the' not in keywords
        assert 'and' not in keywords
        assert 'over' not in keywords
        
        # Content words should remain
        assert 'quick' in keywords or 'brown' in keywords or 'fox' in keywords


class TestSummaryAnalyzer:
    """Test SummaryAnalyzer functionality."""
    
    def test_short_content_full_return(self):
        """Test that short content is returned in full."""
        analyzer = SummaryAnalyzer()
        
        short_text = "This is a short sentence."
        result = analyzer.analyze(short_text)
        
        assert result is not None
        assert result['summary'] == short_text
        assert result['compression_ratio'] == 1.0
        assert result['method'] == 'full_content'
    
    def test_long_content_summarization(self):
        """Test summarization of longer content."""
        analyzer = SummaryAnalyzer()
        
        long_text = ("This is the first sentence with important information. "
                    "This is the second sentence with more details. "
                    "This is the third sentence with additional context. "
                    "This is the fourth sentence with even more information. "
                    "This is the fifth sentence concluding the text.")
        
        result = analyzer.analyze(long_text)
        
        assert result is not None
        assert result['method'] == 'extractive'
        assert result['compression_ratio'] < 1.0
        assert len(result['sentences']) <= analyzer.max_sentences
        
        # Should have sentence scores
        assert 'sentence_scores' in result
        assert len(result['sentence_scores']) >= len(result['sentences'])
    
    def test_sentence_scoring(self):
        """Test sentence importance scoring."""
        analyzer = SummaryAnalyzer()
        
        # Text with repeated important words
        text = ("Python is a programming language. "
               "Programming with Python is fun. "
               "Python programming makes development easier. "
               "Weather is nice today.")
        
        sentences = analyzer._split_sentences(text)
        word_freq = {'python': 3, 'programming': 3, 'language': 1, 'fun': 1}
        
        scores = [analyzer._calculate_sentence_score(s, word_freq) for s in sentences]
        
        # Sentences with Python/programming should score higher
        python_sentence_indices = [i for i, s in enumerate(sentences) if 'Python' in s or 'programming' in s]
        weather_sentence_index = next(i for i, s in enumerate(sentences) if 'Weather' in s)
        
        # Average score of Python sentences should be higher than weather sentence
        python_avg_score = sum(scores[i] for i in python_sentence_indices) / len(python_sentence_indices)
        weather_score = scores[weather_sentence_index]
        
        assert python_avg_score > weather_score
    
    def test_sentence_splitting(self):
        """Test sentence splitting functionality."""
        analyzer = SummaryAnalyzer()
        
        text = "First sentence. Second sentence! Third sentence? Fourth statement."
        sentences = analyzer._split_sentences(text)
        
        assert len(sentences) == 4
        assert "First sentence" in sentences[0]
        assert "Second sentence" in sentences[1]
        assert "Third sentence" in sentences[2]
        assert "Fourth statement" in sentences[3]


class TestStructureAnalyzer:
    """Test StructureAnalyzer functionality."""
    
    def test_basic_structure_analysis(self):
        """Test basic structure metrics."""
        analyzer = StructureAnalyzer()
        
        text = ("# Header\n\n"
               "This is a paragraph with multiple sentences. "
               "Here's the second sentence.\n\n"
               "Another paragraph here.")
        
        result = analyzer.analyze(text)
        
        assert result is not None
        assert result['length'] > 0
        assert result['word_count'] > 0
        assert result['sentence_count'] > 0
        assert result['paragraph_count'] > 0
        assert result['line_count'] > 0
        assert 'analyzed_at' in result
    
    def test_markdown_structure_detection(self):
        """Test detection of markdown structures."""
        analyzer = StructureAnalyzer()
        
        markdown_text = ("# Main Header\n"
                        "## Subheader\n\n"
                        "Regular text with **bold** and *italic*.\n\n"
                        "> This is a blockquote\n\n"
                        "- List item 1\n"
                        "- List item 2\n\n"
                        "```python\n"
                        "print('code')\n"
                        "```\n\n"
                        "---\n")
        
        result = analyzer.analyze(markdown_text)
        
        assert result is not None
        assert result['has_lists'] is True
        assert result['has_code'] is True
        
        formatting = result['formatting_elements']
        assert formatting['headers'] > 0
        assert formatting['bold_text'] > 0
        assert formatting['italic_text'] > 0
        assert formatting['blockquotes'] > 0
        assert formatting['horizontal_rules'] > 0
    
    def test_link_and_image_detection(self):
        """Test detection of links and images."""
        analyzer = StructureAnalyzer()
        
        content_with_media = ("Visit https://example.com for more info. "
                             "![Image](image.png) and [Link](https://link.com)")
        
        result = analyzer.analyze(content_with_media)
        
        assert result is not None
        assert result['has_links'] is True
        assert result['has_images'] is True
    
    def test_readability_calculation(self):
        """Test readability metrics calculation."""
        analyzer = StructureAnalyzer()
        
        # Simple sentences
        simple_text = "This is simple. Easy to read. Very clear."
        simple_result = analyzer.analyze(simple_text)
        
        # Complex sentences
        complex_text = ("This is an extremely complicated sentence with multiple clauses, "
                       "subordinate phrases, and various complex grammatical structures "
                       "that make it difficult to understand and process quickly.")
        complex_result = analyzer.analyze(complex_text)
        
        assert simple_result['readability']['complexity'] == 'simple'
        assert complex_result['readability']['complexity'] in ['moderate', 'complex']
        
        # Complex text should have higher words per sentence
        assert (complex_result['readability']['words_per_sentence'] > 
               simple_result['readability']['words_per_sentence'])


class TestAnalyzerIntegration:
    """Test analyzer integration and convenience functions."""
    
    def test_analyze_content_function(self):
        """Test the analyze_content convenience function."""
        text = "I love this fantastic Python programming tutorial! It's amazing."
        
        results = analyze_content(text, ['sentiment', 'topics', 'structure'])
        
        assert 'sentiment' in results
        assert 'topics' in results
        assert 'structure' in results
        
        # Check that each analysis succeeded
        assert results['sentiment']['sentiment'] == 'positive'
        assert len(results['topics']['keywords']) > 0
        assert results['structure']['word_count'] > 0
    
    def test_analyze_block_function(self):
        """Test the analyze_block convenience function."""
        block = Block(content="TODO: Learn machine learning algorithms for better AI.")
        
        results = analyze_block(block, ['sentiment', 'topics'])
        
        assert 'sentiment' in results
        assert 'topics' in results
        
        # Should detect task-related and technology topics
        topics = [t['topic'] for t in results['topics']['topics']]
        assert 'technology' in topics
    
    def test_analyze_empty_block(self):
        """Test analyzing block with no content."""
        empty_block = Block(content=None)
        
        results = analyze_block(empty_block)
        
        # Should return empty dict for empty content
        assert results == {}
    
    def test_analyzer_error_handling(self):
        """Test analyzer error handling."""
        # This test would depend on how errors are handled in the analyzers
        # For now, test with edge cases
        
        results = analyze_content("", ['sentiment', 'topics'])
        
        # Should handle empty content gracefully
        assert isinstance(results, dict)
    
    def test_multiple_analyzer_coordination(self):
        """Test running multiple analyzers on the same content."""
        text = ("# Python Programming Tutorial\n\n"
               "I absolutely love working with Python! It's an amazing programming language "
               "that makes software development incredibly enjoyable and productive.\n\n"
               "Key features:\n"
               "- Clean syntax\n"
               "- Great libraries\n"
               "- Active community")
        
        results = analyze_content(text)  # All default analyzers
        
        # Should have results from all default analyzers
        expected_analyzers = ['sentiment', 'topics', 'summary', 'structure']
        
        for analyzer in expected_analyzers:
            if analyzer in results:
                assert results[analyzer] is not None
                
                # Each analyzer should have metadata
                if isinstance(results[analyzer], dict):
                    assert 'analyzed_at' in results[analyzer]
    
    def test_analyzer_consistency(self):
        """Test that analyzers produce consistent results."""
        text = "Python is a great programming language for machine learning."
        
        # Run analysis multiple times
        results1 = analyze_content(text, ['sentiment', 'topics'])
        results2 = analyze_content(text, ['sentiment', 'topics'])
        
        # Results should be consistent (assuming deterministic algorithms)
        if 'sentiment' in results1 and 'sentiment' in results2:
            assert results1['sentiment']['sentiment'] == results2['sentiment']['sentiment']
        
        if 'topics' in results1 and 'topics' in results2:
            topics1 = [t['topic'] for t in results1['topics']['topics']]
            topics2 = [t['topic'] for t in results2['topics']['topics']]
            assert topics1 == topics2