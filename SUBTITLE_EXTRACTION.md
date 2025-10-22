# YouTube Subtitle Extraction

## Overview
The comprehensive processor can extract YouTube video subtitles/transcripts for better topic analysis.

## How It Works

The `YouTubeSubtitleExtractor` tries multiple methods to get subtitles:

1. **youtube-transcript-api** (Primary method)
   - Uses the community API to fetch transcripts
   - Works with auto-generated and manual captions
   - Supports multiple languages (prefers English)
   - No API key required

2. **YouTube Data API** (If API key provided)
   - Official Google API
   - More reliable but requires API key
   - Subject to quota limits

3. **Page parsing** (Fallback)
   - Parses YouTube page HTML
   - Limited implementation
   - Last resort method

## Rate Limiting

⚠️ **Important**: YouTube rate-limits transcript requests from the same IP.

### Common Issues:

**HTTP 429 Error**: Too many requests
- YouTube blocks IPs that make too many requests
- Cloud provider IPs (AWS, GCP, Azure) are often blocked by default
- Wait 10-60 minutes before retrying
- Consider using a YouTube API key for better reliability

### Solutions:

1. **Use YouTube Data API Key**:
   ```bash
   python scripts/comprehensive_processor_cli.py /path/to/graph \
     --youtube-api-key YOUR_API_KEY
   ```

2. **Process in batches**:
   - Don't process your entire library at once
   - Process 10-20 videos at a time
   - Wait between batches

3. **Working around IP bans**:
   - Use a residential IP (not cloud/datacenter)
   - Use a VPN to change IP address
   - Add delays between requests
   - See: https://github.com/jdepoix/youtube-transcript-api#working-around-ip-bans

## Configuration

### Minimum Subtitle Length
Only subtitles longer than this will be used for analysis:
```bash
--min-subtitle-length 100  # Default: 100 characters
```

### Without Subtitles
If subtitles aren't available or fail to extract:
- Topic analysis falls back to video title only
- Still creates useful topics based on title keywords
- Less comprehensive than with full transcripts

## Statistics

Check processing statistics to see subtitle extraction success:
```python
stats = processor.run()
print(f"Subtitles extracted: {stats['stats']['subtitles_extracted']}")
print(f"Videos processed: {stats['stats']['videos_enhanced']}")
```

## API Version

Currently uses `youtube-transcript-api` v1.2.3:
- Instance-based API (not class methods)
- Uses `api.list(video_id)` and `transcript.fetch()`
- Returns `FetchedTranscriptSnippet` objects with `.text` attribute

## Best Practices

1. **Start small**: Test with a few videos first
2. **Use API key**: More reliable for large batches
3. **Monitor logs**: Watch for rate limit warnings
4. **Be patient**: Wait if you hit rate limits
5. **Process incrementally**: The processor skips already-processed videos

## Example Logs

**Successful extraction**:
```
INFO - Successfully extracted 23942 chars from transcript API
INFO - Extracted 23942 chars of subtitles
```

**Rate limited**:
```
WARNING - All subtitle extraction methods failed for video: QdnxjYj1pS0
DEBUG - Could not get transcripts: YouTube is blocking requests from your IP
```

**No subtitles available**:
```
DEBUG - No transcripts available for video abc123
```

## Testing

Test subtitle extraction on a single video:
```bash
python test_subtitle_extraction.py
```

Note: If you've been testing multiple times, you may be temporarily rate-limited.
