# Video Extraction Improvements

## Problem

Users reported "all methods failed" errors when extracting video information, particularly for YouTube videos. The extraction was failing silently without providing enough detail about which method failed and why.

## Root Causes

1. **Insufficient fallback methods**: Only 2 extraction methods (YouTube API and oEmbed)
2. **Poor error reporting**: Generic failures without detailed error messages
3. **No HTML scraping**: When APIs failed, there was no fallback to parse HTML
4. **Silent failures**: Errors were logged but not tracked or reported comprehensively

## Solutions Implemented

### 1. Three-Tier Extraction Strategy

Implemented a comprehensive 3-method fallback system:

```python
# Method 1: YouTube Data API (if API key provided)
# - Most comprehensive data
# - Requires API key
# - Rate limited

# Method 2: YouTube oEmbed API
# - Good basic metadata
# - No API key required
# - Publicly available

# Method 3: HTML Scraping
# - Last resort fallback
# - Parses YouTube HTML directly
# - Always available but less reliable
```

### 2. Enhanced HTML Scraping Method

Added `_extract_from_html()` method with multiple extraction strategies:

```python
def _extract_from_html(self, video_id: str) -> Optional[Dict[str, Any]]:
    # Try multiple HTML parsing methods:
    
    # 1. Extract from <title> tag
    # 2. Extract from og:title meta tag
    # 3. Extract from JSON-LD structured data
    # 4. Extract author from itemprop='name'
    # 5. Extract thumbnail from og:image
```

### 3. Comprehensive Error Tracking

Track errors from each method and report them:

```python
errors = []

# Try method 1
try:
    ...
except Exception as e:
    errors.append(f"YouTube API: {str(e)}")

# Try method 2
try:
    ...
except Exception as e:
    errors.append(f"oEmbed: {str(e)}")

# Try method 3
try:
    ...
except Exception as e:
    errors.append(f"HTML scraping: {str(e)}")

# Report all errors if all methods fail
if all_failed:
    error_msg = 'All extraction methods failed: ' + '; '.join(errors)
```

### 4. Better Logging

Added detailed debug logging for each step:

```python
self.logger.debug(f"Successfully extracted via YouTube API: {video_id}")
self.logger.debug(f"Successfully extracted via oEmbed: {video_id}")
self.logger.debug(f"Successfully extracted via HTML scraping: {video_id}")
self.logger.warning(f"All extraction methods failed for {video_id}: {errors}")
```

### 5. Graceful Degradation

Even when all methods fail, return basic video information:

```python
# Return minimal info with clear error message
return {
    'video_id': video_id,
    'url': f"https://www.youtube.com/watch?v={video_id}",
    'title': f"YouTube Video {video_id}",
    'status': 'failed',
    'error': 'All extraction methods failed: ...',
    'data_source': 'none',
    'author_name': None,
    'platform': 'youtube'
}
```

## Impact

### Before
```
WARNING: Could not extract video info for: https://youtube.com/watch?v=ABC123
```
- No video info returned
- No details about what failed
- Processing stopped

### After
```
DEBUG: YouTube API: 403 Quota exceeded
DEBUG: oEmbed: HTTP 429 Too Many Requests
DEBUG: Successfully extracted via HTML scraping: ABC123
```
- Video info extracted successfully
- Detailed error messages for debugging
- Processing continues with fallback method

### Error Reporting Example

When all methods fail:
```json
{
  "video_id": "ABC123",
  "title": "YouTube Video ABC123",
  "status": "failed",
  "error": "All extraction methods failed: YouTube API: 403 Quota exceeded; oEmbed: HTTP 429; HTML scraping: No title found",
  "data_source": "none"
}
```

## HTML Scraping Details

The HTML scraping method extracts data from multiple sources in the YouTube HTML:

### Title Extraction (3 methods)
1. **`<title>` tag**: Basic page title (e.g., "Video Title - YouTube")
2. **Open Graph meta tag**: `<meta property="og:title" content="...">`
3. **JSON-LD structured data**: `<script type="application/ld+json">`

### Author/Channel Extraction
- **Link itemprop**: `<link itemprop="name" content="Channel Name">`

### Thumbnail Extraction
- **Open Graph image**: `<meta property="og:image" content="...">`

## Rate Limiting Considerations

YouTube APIs have rate limits:

### YouTube Data API
- **Quota**: 10,000 units per day (default)
- **Per video**: 1 unit
- **Solution**: Use HTML scraping as fallback when quota exhausted

### oEmbed API
- **Rate limit**: ~100 requests per minute
- **HTTP 429**: Too Many Requests
- **Solution**: Automatic fallback to HTML scraping

### HTML Scraping
- **Rate limit**: Subject to YouTube's general rate limiting
- **Advantage**: No API key required
- **Disadvantage**: Less stable, may break if YouTube changes HTML structure

## Best Practices

### For API Users
1. Provide YouTube API key for best results
2. Monitor quota usage
3. Implement request batching

### For Non-API Users
1. HTML scraping works without API key
2. May be slower (needs full page fetch)
3. Subject to HTML structure changes

### Error Handling
1. Always check `status` field
2. Parse `error` field for debugging
3. Log `data_source` to understand which method succeeded

## Testing

Test the improved extraction:

```python
from logseq_py.utils import LogseqUtils

# Test with API key
video_info = LogseqUtils.get_video_info(
    "https://youtube.com/watch?v=ABC123",
    youtube_api_key="YOUR_API_KEY"
)

# Test without API key (uses oEmbed + HTML fallback)
video_info = LogseqUtils.get_video_info(
    "https://youtube.com/watch?v=ABC123"
)

# Check result
print(f"Status: {video_info['status']}")
print(f"Source: {video_info['data_source']}")
print(f"Title: {video_info['title']}")
if video_info['status'] == 'failed':
    print(f"Error: {video_info['error']}")
```

## Future Enhancements

Potential improvements:

1. **Cache extraction results** to reduce API calls
2. **Batch API requests** for multiple videos
3. **Add more platforms** (Vimeo, TikTok HTML scraping)
4. **Implement retry logic** with exponential backoff
5. **Parse more metadata** from HTML (views, upload date, etc.)

## Related Files

- `logseq_py/pipeline/extractors.py` - Main implementation
- `logseq_py/utils.py` - Utility wrapper for extraction
- `SUBTITLE_EXTRACTION.md` - Related subtitle extraction documentation
