# Video Title Extraction

The logseq-python library provides easy-to-use utilities for extracting video titles and metadata from various video platforms. This feature leverages the existing comprehensive extractor system to provide simple, convenient functions.

## Supported Platforms

- **YouTube** - Full support with optional API key for enhanced data
- **Vimeo** - oEmbed API support
- **TikTok** - Basic HTML parsing (limited without API)
- **Twitch** - Videos and clips via HTML parsing 
- **Dailymotion** - oEmbed API support

## Quick Start

```python
from logseq_py import LogseqUtils

# Get a video title
title = LogseqUtils.get_video_title("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
print(f"Video title: {title}")
# Output: Video title: Rick Astley - Never Gonna Give You Up (Official Video)
```

## Core Functions

### `get_video_title(url, youtube_api_key=None)`

Extract just the title from a video URL.

**Parameters:**
- `url` (str): Video URL from supported platforms
- `youtube_api_key` (str, optional): YouTube Data API key for enhanced data

**Returns:**
- `str` or `None`: Video title if extraction successful, None otherwise

**Example:**
```python
# Basic usage
title = LogseqUtils.get_video_title("https://youtu.be/dQw4w9WgXcQ")

# With YouTube API key for enhanced data
title = LogseqUtils.get_video_title(
    "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    youtube_api_key="YOUR_API_KEY"
)
```

### `get_video_info(url, youtube_api_key=None)`

Extract comprehensive video information.

**Parameters:**
- `url` (str): Video URL from supported platforms
- `youtube_api_key` (str, optional): YouTube Data API key for enhanced data

**Returns:**
- `dict` or `None`: Dictionary with video metadata, None if extraction fails

**Example:**
```python
info = LogseqUtils.get_video_info("https://www.youtube.com/watch?v=dQw4w9WgXcQ")

if info:
    print(f"Title: {info.get('title')}")
    print(f"Author: {info.get('author_name')}")
    print(f"Duration: {info.get('duration')}")
    print(f"Views: {info.get('view_count', 'N/A')}")
    print(f"Published: {info.get('published_at', 'N/A')}")
```

### `extract_video_urls(text)`

Find all video URLs in a text string.

**Parameters:**
- `text` (str): Text containing potential video URLs

**Returns:**
- `list`: List of video URLs found

**Example:**
```python
text = """
Check out these videos:
- https://www.youtube.com/watch?v=dQw4w9WgXcQ
- https://vimeo.com/148751763
- Regular link: https://example.com (ignored)
"""

video_urls = LogseqUtils.extract_video_urls(text)
print(f"Found {len(video_urls)} video URLs")
for url in video_urls:
    print(f"  - {url}")
```

### `get_multiple_video_titles(urls, youtube_api_key=None)`

Get titles for multiple URLs at once.

**Parameters:**
- `urls` (list): List of video URLs
- `youtube_api_key` (str, optional): YouTube Data API key

**Returns:**
- `dict`: Dictionary mapping URLs to their titles (None for failed extractions)

**Example:**
```python
urls = [
    "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "https://vimeo.com/148751763",
    "https://www.dailymotion.com/video/x2jvvep"
]

titles = LogseqUtils.get_multiple_video_titles(urls)
for url, title in titles.items():
    if title:
        print(f"{title} - {url}")
    else:
        print(f"Could not extract title for: {url}")
```

## Platform-Specific Information

### YouTube

YouTube videos provide the richest metadata:

**Without API key (oEmbed):**
- Title
- Author name
- Author URL  
- Thumbnail URL
- Video dimensions

**With YouTube Data API key:**
- All oEmbed data plus:
- Description
- Channel information
- View count, like count, comment count
- Duration in seconds
- Publication date
- Tags
- Category

**Getting a YouTube API key:**
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable YouTube Data API v3
4. Create credentials (API key)
5. Use the API key in your calls

```python
# Enhanced YouTube data with API key
info = LogseqUtils.get_video_info(
    "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    youtube_api_key="YOUR_API_KEY_HERE"
)

if info:
    print(f"Description: {info.get('description', 'N/A')[:100]}...")
    print(f"Channel: {info.get('channel_title', 'N/A')}")
    print(f"Tags: {info.get('tags', [])}")
    print(f"Views: {info.get('view_count', 0):,}")
```

### Vimeo

Vimeo uses oEmbed API and provides:
- Title
- Description
- Author name and URL
- Thumbnail URL
- Duration
- Video dimensions
- Upload date

### TikTok

TikTok extraction is limited without official API access:
- Basic title extraction via HTML parsing
- Limited metadata
- May be unreliable due to dynamic content loading

### Twitch

Twitch supports both videos and clips:
- Basic title extraction via HTML parsing
- Automatic detection of videos vs clips
- Limited metadata without Twitch API

### Dailymotion  

Dailymotion uses oEmbed API:
- Title
- Author name and URL
- Thumbnail URL
- Video dimensions

## Error Handling

All functions handle errors gracefully:

```python
# Function returns None if extraction fails
title = LogseqUtils.get_video_title("https://invalid-url")
if title is None:
    print("Could not extract video title")

# Comprehensive info includes error details
info = LogseqUtils.get_video_info("https://private-video-url")
if info and info.get('status') == 'error':
    print(f"Extraction failed: {info.get('error')}")
```

## Integration with Logseq Workflows

### Auto-generating Video Block Titles

```python
from logseq_py import LogseqUtils, LogseqBuilder

def create_video_block(url):
    title = LogseqUtils.get_video_title(url)
    
    builder = LogseqBuilder()
    if title:
        builder.text(f"**{title}**")
    builder.text(url)
    
    return builder.build()

# Usage
block_content = create_video_block("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
print(block_content)
```

### Processing Pages with Video URLs

```python
def enhance_page_with_video_titles(page_content):
    # Find all video URLs in the page
    video_urls = LogseqUtils.extract_video_urls(page_content)
    
    if not video_urls:
        return page_content
    
    # Get titles for all videos
    titles = LogseqUtils.get_multiple_video_titles(video_urls)
    
    # Replace URLs with titled links
    enhanced_content = page_content
    for url, title in titles.items():
        if title:
            titled_link = f"[{title}]({url})"
            enhanced_content = enhanced_content.replace(url, titled_link)
    
    return enhanced_content
```

## Performance Considerations

- **Caching**: Consider caching results for frequently accessed videos
- **Rate Limiting**: Be mindful of API rate limits, especially for YouTube
- **Batch Processing**: Use `get_multiple_video_titles()` for efficiency
- **Timeouts**: Network requests have built-in timeouts
- **Error Handling**: Failed extractions return None rather than raising exceptions

## Complete Example

See `examples/video_title_example.py` for a comprehensive demonstration of all video title extraction features.

```bash
cd examples/
python video_title_example.py
```

This will demonstrate:
1. Individual video title extraction
2. Comprehensive video information
3. URL extraction from text
4. Batch title processing
5. API key usage (when configured)