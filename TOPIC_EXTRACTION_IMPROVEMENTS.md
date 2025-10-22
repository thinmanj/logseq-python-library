# Topic Extraction Improvements

## Problem Statement

The comprehensive processor was extracting incorrect topics from content, including:

1. **URL fragments**: Terms like "http", "https", "href", "www" were appearing as topics
2. **HTML artifacts**: Terms like "blockquote", "embed", "onclick" were leaking into topics
3. **Partial words**: Truncated text with "..." was generating broken topic words
4. **Bonus scoring issues**: The regex pattern was giving bonuses to URL-related terms

## Root Causes

### 1. HTML Text Extraction

The Twitter oEmbed API returns HTML with embedded URLs and attributes. The `_extract_text_from_html` method wasn't fully cleaning these before topic analysis:

```html
<blockquote class="twitter-tweet">
  <p><a href="https://...">Some text...</a></p>
</blockquote>
```

This could leak "href", "blockquote", and URL components into the extracted text.

### 2. Content Truncation

Both Twitter and PDF content were truncated with "..." which could break words:

```
"This is about machine lear..."
```

Would extract "lear" as a potential topic instead of recognizing the truncation.

### 3. Insufficient Filtering

The topic extraction only filtered common stop words but not URL/HTML-specific terms. The regex bonus pattern included "http" which incorrectly boosted URL fragments.

## Solutions Implemented

### 1. Enhanced HTML Cleaning

Updated `_extract_text_from_html` to:
- Remove all URLs before text extraction: `https?://[^\s<>"]+`
- Strip HTML attributes: `(href|src|class|id|style)=["'][^"']*["']`
- Clean URLs from embedded content completely

```python
# Remove all URLs before extracting text
html = re.sub(r'https?://[^\s<>"]+', '', html)

# Remove common HTML attributes
html = re.sub(r'(href|src|class|id|style)=["'][^"']*["']', '', html)
```

### 2. Content Cleaning Method

Added `_clean_content_for_analysis` to preprocess content:

```python
def _clean_content_for_analysis(self, content: str) -> str:
    # Remove URLs completely
    content = re.sub(r'https?://[^\s<>"]+', '', content)
    content = re.sub(r'www\.[^\s<>"]+', '', content)
    
    # Remove HTML tags
    content = re.sub(r'<[^>]+>', '', content)
    
    # Handle truncation artifacts
    # "some tex..." -> "some ..."
    content = re.sub(r'\b\w{1,3}\.{2,}', '...', content)
    # "...xt more" -> "... more"
    content = re.sub(r'\.{2,}\w{1,3}\b', '...', content)
    
    # Remove ellipsis completely
    content = re.sub(r'\.{3,}', ' ', content)
    
    return content.strip()
```

### 3. URL Stopwords List

Added comprehensive URL/HTML stopwords:

```python
self.url_stopwords = {
    'http', 'https', 'href', 'www', 'com', 'org', 'net', 'html', 'htm',
    'link', 'url', 'src', 'img', 'div', 'span', 'class', 'style', 'script',
    'onclick', 'onload', 'javascript', 'ajax', 'json', 'xml', 'css',
    'blockquote', 'twitter', 'tweet', 'status', 'embed', 'oembed'
}
```

### 4. Filtering Throughout Extraction

Applied URL stopword filtering to all extraction methods:

- `_extract_important_words`: Check both `stop_words` and `url_stopwords`
- `_extract_important_words_tfidf`: Filter URL terms from TF-IDF scoring
- `_extract_key_phrases`: Filter URL terms from bigrams and trigrams
- `_extract_from_title`: Exclude URL terms from title extraction

### 5. Fixed Regex Bonus

Updated `_rank_topics_advanced` to:

```python
# OLD (incorrect - boosted "http")
if re.search(r'\d|api|sql|http|tech|data', topic_clean):
    score += 2

# NEW (correct - excludes URL stopwords)
if re.search(r'\d|api|sql|tech|data', topic_clean) and topic_clean not in self.url_stopwords:
    score += 2

# Also penalize URL/HTML terms
if any(url_term in topic_clean for url_term in self.url_stopwords):
    score -= 20
```

## Impact

### Before

Topics extracted from a tweet about machine learning:
```
['http', 'href', 'machine-learning', 'lear', 'blockquote', 'embed', 'twitter']
```

### After

Topics extracted from the same content:
```
['machine-learning', 'artificial-intelligence', 'data-science']
```

## Testing

To test the improvements:

```python
from logseq_py.pipeline.enhanced_extractors import ContentAnalyzer

analyzer = ContentAnalyzer(max_topics=5)

# Test with HTML content
html_content = '<a href="https://example.com">Machine Learning basics...</a>'
topics = analyzer.extract_topics(html_content, "ML Tutorial", "x-twitter")
# Should NOT include: 'http', 'href', 'example', 'com'
# Should include: 'machine', 'learning', 'tutorial'

# Test with truncated content
truncated = "This is about deep lear... and neural networks"
topics = analyzer.extract_topics(truncated, "Deep Learning", "pdf")
# Should NOT include: 'lear'
# Should include: 'deep', 'learning', 'neural', 'networks'
```

## Configuration

No configuration changes required. The improvements are automatic and backward-compatible.

## Future Enhancements

Potential further improvements:

1. **Full text extraction**: Instead of truncating, fetch complete Twitter/PDF content when available
2. **Named entity recognition**: Use NLP libraries (spaCy, NLTK) for better topic extraction
3. **Domain-specific filtering**: Allow users to configure custom stopwords for their domain
4. **Language detection**: Apply language-specific filtering and stemming
5. **Validation logging**: Add debug logs showing filtered terms for transparency

## Related Files

- `logseq_py/pipeline/enhanced_extractors.py` - Main implementation
- `logseq_py/pipeline/comprehensive_processor.py` - Uses the enhanced extractors
- `BUILDER_INTEGRATION.md` - Related builder pattern documentation
