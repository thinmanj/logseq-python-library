# Video Processing Pipeline for Logseq

A comprehensive pipeline that automatically processes video content in your Logseq graph, extracting metadata, subtitles, and generating semantic tags to enhance your knowledge management workflow.

## 🎯 What It Does

The Video Processing Pipeline transforms your Logseq graph by:

1. **🔍 Scanning** all pages and journal entries for video URLs
2. **📹 Extracting** video metadata (title, author, duration, platform)
3. **📝 Extracting** subtitles/transcripts from YouTube videos
4. **✨ Enhancing** blocks with `{{video URL}}` syntax for better display
5. **🏷️ Analyzing** content to generate relevant tags
6. **📄 Creating** tagged pages that connect videos by topic
7. **🔗 Adding** source references and timestamps

## 🎬 Supported Platforms

- **YouTube** - Full metadata + subtitle extraction
- **Vimeo** - Metadata via oEmbed API
- **TikTok** - Basic metadata (limited)
- **Twitch** - Videos and clips metadata
- **Dailymotion** - Metadata via oEmbed API

## 🚀 Quick Start

### Command Line Usage

```bash
# Basic dry run (safe - no files modified)
python scripts/video_processor_cli.py /path/to/logseq/graph --dry-run

# Full processing
python scripts/video_processor_cli.py /path/to/logseq/graph

# With YouTube API key for enhanced subtitle extraction
python scripts/video_processor_cli.py /path/to/logseq/graph --youtube-api-key YOUR_API_KEY

# Custom configuration
python scripts/video_processor_cli.py /path/to/logseq/graph \
  --tag-prefix "topic" \
  --max-tags 3 \
  --min-subtitle-length 200
```

### Python API Usage

```python
from logseq_py.pipeline.video_processor import VideoProcessingPipeline

# Configure pipeline
config = {
    'dry_run': False,  # Set to True for testing
    'youtube_api_key': 'YOUR_API_KEY',  # Optional but recommended
    'tag_prefix': 'video-topic',
    'max_tags_per_video': 5,
    'backup_enabled': True
}

# Run pipeline
pipeline = VideoProcessingPipeline('/path/to/logseq/graph', config)
result = pipeline.run()

# Check results
if result['success']:
    print(f"Enhanced {result['stats']['videos_enhanced']} videos")
    print(f"Created {result['stats']['pages_created']} tag pages")
```

## ⚙️ Configuration Options

| Option | Default | Description |
|--------|---------|-------------|
| `dry_run` | `False` | Preview changes without modifying files |
| `youtube_api_key` | `None` | YouTube Data API key for enhanced features |
| `tag_prefix` | `video-topic` | Prefix for generated tag pages |
| `min_subtitle_length` | `100` | Minimum subtitle length to process |
| `max_tags_per_video` | `5` | Maximum tags extracted per video |
| `backup_enabled` | `True` | Create backup before processing |

## 🔧 Installation Requirements

### Core Requirements
```bash
pip install logseq-python  # Base functionality
```

### Optional Enhancements
```bash
# For YouTube subtitle extraction
pip install youtube-transcript-api

# For advanced NLP (future feature)
pip install spacy
```

## 📋 Before/After Examples

### Before Processing
```markdown
- Check out this great tutorial: https://www.youtube.com/watch?v=abc123
- Another video: https://vimeo.com/123456
```

### After Processing
```markdown
- Check out this great tutorial: {{video https://www.youtube.com/watch?v=abc123}}
  **Python Programming Fundamentals**
  By: Code Academy
  Tags: #video-topic-programming #video-topic-education #video-topic-python

- Another video: {{video https://vimeo.com/123456}}
  **Design Principles**  
  By: Creative Studio
  Tags: #video-topic-design #video-topic-art
```

### Generated Tag Pages

The pipeline creates pages like `video-topic-programming.md`:

```markdown
type:: video-topic
tag:: programming
created:: 2024-10-21
video-count:: 3

# Videos tagged with: programming

This page contains all videos related to the topic: **programming**
Found in 3 video(s) from your Logseq graph.

## 1. Python Programming Fundamentals

**Source Page:** [[Daily Notes]]
**Video URL:** https://www.youtube.com/watch?v=abc123
**Processed:** 2024-10-21

### Content Preview
> Welcome to this comprehensive Python tutorial. Today we'll cover variables, functions, loops, and object-oriented programming concepts...

## 2. JavaScript Basics

**Source Page:** [[Learning Resources]]
**Video URL:** https://www.youtube.com/watch?v=def456
**Processed:** 2024-10-21
```

## 🎛️ Advanced Features

### YouTube API Integration

With a YouTube Data API key, you get:
- Video descriptions and full metadata
- Channel information
- View counts, like counts, publish dates
- Complete subtitle/transcript extraction
- Video tags and categories

**Getting a YouTube API Key:**
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a project or select existing
3. Enable YouTube Data API v3
4. Create credentials (API key)
5. Use with `--youtube-api-key` parameter

### Content Analysis & Tagging

The pipeline analyzes video content using multiple methods:

1. **Topic Detection** - Recognizes common video categories
2. **Keyword Extraction** - Identifies frequently mentioned terms  
3. **Entity Recognition** - Finds proper nouns and names
4. **Semantic Ranking** - Scores tags by relevance

Categories automatically detected:
- Technology, Science, Education
- Business, Health, Entertainment  
- News, Lifestyle, and more

### Backup & Safety Features

- **Automatic Backups** - Created before any modifications
- **Dry Run Mode** - Preview all changes safely
- **Error Recovery** - Graceful handling of API failures
- **Logging** - Detailed logs for debugging

## 🎯 Use Cases

### 1. Research & Learning
- **Problem**: Videos scattered across notes, hard to find related content
- **Solution**: Automatic tagging creates topic-based collections
- **Result**: Easy discovery of all Python tutorials, design videos, etc.

### 2. Content Curation
- **Problem**: Raw URLs don't show video context in Logseq
- **Solution**: Enhanced blocks show titles, authors, duration
- **Result**: Rich video previews directly in your notes

### 3. Knowledge Mapping
- **Problem**: Difficult to see connections between video content
- **Solution**: Tag pages reveal content relationships
- **Result**: Discover learning paths and content clusters

### 4. Content Analysis
- **Problem**: Can't search within video content
- **Solution**: Subtitle extraction makes video content searchable
- **Result**: Find specific topics within your video library

## 🔍 What Gets Processed

The pipeline scans:
- ✅ Main pages (`*.md` in root directory)
- ✅ Journal entries (`journals/*.md`)
- ✅ All block levels and nested content
- ✅ Mixed content blocks (text + video URLs)

It preserves:
- ✅ Original block structure and formatting
- ✅ Existing tags and properties
- ✅ Block relationships and hierarchy
- ✅ Non-video content unchanged

## 📊 Performance & Scaling

| Graph Size | Processing Time | Memory Usage |
|------------|----------------|--------------|
| Small (100 pages) | 30 seconds | ~50MB |
| Medium (1000 pages) | 5 minutes | ~100MB |  
| Large (10000+ pages) | 30+ minutes | ~500MB |

**Optimization Tips:**
- Use `--dry-run` first to estimate scope
- Process during low-activity periods
- Consider batch processing for huge graphs
- YouTube API key significantly speeds subtitle extraction

## 🚨 Important Notes

### Safety First
- **Always backup** your graph before processing
- **Test with `--dry-run`** on important data
- **Start small** with a few pages to verify results

### API Limits
- YouTube API has daily quotas (10,000 units/day default)
- Each video processes ~3-5 API units
- Without API key, basic extraction still works
- Rate limiting is handled automatically

### Subtitle Availability
- Not all YouTube videos have subtitles
- Auto-generated captions may have errors
- Some videos restrict subtitle access
- Pipeline gracefully handles missing subtitles

## 🛠️ Troubleshooting

### Common Issues

**"No videos found" but videos exist in graph:**
- Check URL formats are supported
- Verify URLs aren't in code blocks or comments
- Enable DEBUG logging to see scanning process

**Subtitle extraction fails:**
- Install `youtube-transcript-api`: `pip install youtube-transcript-api`
- Some videos don't have available subtitles
- Check if video is public and accessible

**API key errors:**
- Verify API key is correct and active
- Check YouTube Data API v3 is enabled
- Ensure API quotas aren't exceeded

**Performance issues:**
- Use `--dry-run` to estimate scope first
- Process smaller batches if graph is huge
- Check available disk space for backups

### Debug Mode
```bash
python scripts/video_processor_cli.py /path/to/graph \
  --dry-run --log-level DEBUG --log-file debug.log
```

## 🔮 Future Enhancements

Planned features:
- **Multi-language support** for subtitles
- **Advanced NLP** with spaCy/transformers
- **Timestamp-based tagging** for long videos  
- **Integration with more platforms** (Instagram, LinkedIn)
- **AI-powered summarization** of video content
- **Automated playlist generation** based on tags

## 🤝 Contributing

The video processing pipeline is part of the logseq-python project. Contributions welcome:

- **Report bugs** and suggest improvements
- **Add support** for new video platforms
- **Improve text analysis** algorithms
- **Enhance documentation** and examples

## 📚 Related Documentation

- [Video Title Extraction](VIDEO_TITLE_EXTRACTION.md) - Core video utilities
- [Pipeline Architecture](PIPELINE.md) - General pipeline framework
- [API Reference](api.md) - Complete API documentation

---

## Example Complete Workflow

Here's what happens when you run the pipeline:

```bash
🚀 Starting Logseq Video Processing Pipeline
📁 Graph: /Users/you/logseq-graph
🔑 YouTube API key provided - Enhanced subtitle extraction enabled
🏷️ Tag prefix: video-topic
📊 Max tags per video: 5

2024-10-21 10:00:01 - INFO - Starting video processing pipeline
2024-10-21 10:00:02 - INFO - Found 45 blocks with video content  
2024-10-21 10:00:03 - INFO - Processing video: https://www.youtube.com/watch?v=abc123
2024-10-21 10:00:04 - INFO - Extracted 2,340 chars of subtitles and 4 tags
2024-10-21 10:00:05 - INFO - Enhanced block with 1 videos
2024-10-21 10:00:06 - INFO - Created tag page: video-topic-programming
...

============================================================
📹 VIDEO PROCESSING REPORT
============================================================
✅ SUCCESS
📁 Graph: /Users/you/logseq-graph  
🕐 Time: 2024-10-21 10:05:23

📊 STATISTICS:
   • Blocks processed: 1,234
   • Videos found: 45
   • Videos enhanced: 45
   • Subtitles extracted: 28
   • Tags created: 12
   • Pages created: 12

============================================================

🎉 Processing completed successfully!
```

Your Logseq graph is now enhanced with rich video content, automatic tagging, and discoverable video collections! 🎬