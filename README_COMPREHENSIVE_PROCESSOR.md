# Comprehensive Content Processor for Logseq

A powerful pipeline for automatically processing and organizing videos, X/Twitter posts, and PDFs in your Logseq knowledge graph with intelligent topic extraction and semantic organization.

## Features

### 🎥 Multi-Platform Content Support
- **YouTube Videos**: Extract metadata, titles, authors, duration, and subtitles
- **X/Twitter Posts**: Extract tweets with author info and content previews
- **PDF Documents**: Extract titles, authors, page counts, and content previews

### 🏷️ Advanced Topic Extraction
- **Multi-word phrases**: "machine-learning", "data-science", "deep-learning"
- **TF-IDF scoring**: Intelligent keyword importance ranking
- **Title weighting**: 10x bonus for topics found in titles
- **Domain recognition**: 20+ technical term patterns
- **Smart ranking**: 7-criteria scoring algorithm

### 📊 Smart Organization
- **Topic pages**: Automatically creates pages for each topic
- **Cross-references**: Links content back to source pages
- **Statistics**: Tracks content types, counts, and processing dates
- **Hierarchical structure**: Main blocks with properties, sub-blocks with details

### 🚀 Intelligent Processing
- **Skip processed**: Avoids re-processing already enhanced content
- **Fallback logic**: Multiple extraction methods for reliability
- **Error handling**: Graceful degradation when APIs unavailable
- **Progress tracking**: Detailed logging and statistics

## Installation

### Prerequisites
```bash
pip install -r requirements.txt
```

### Required Dependencies
- `youtube_transcript_api>=1.2.3` - Video subtitle extraction
- `requests>=2.28.0` - HTTP requests
- `PyPDF2>=3.0.0` - PDF content extraction
- `textblob>=0.17.0` - Content analysis

## Usage

### Basic Usage
```bash
python scripts/comprehensive_processor_cli.py /path/to/logseq/graph
```

### With Options
```bash
python scripts/comprehensive_processor_cli.py /path/to/logseq/graph \
  --max-topics 3 \
  --log-level INFO \
  --youtube-api-key YOUR_KEY
```

### Command Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `--dry-run` | Preview changes without modifying files | False |
| `--max-topics N` | Maximum topics per content item | 3 |
| `--youtube-api-key KEY` | YouTube API key for enhanced features | None |
| `--twitter-bearer-token TOKEN` | Twitter API bearer token | None |
| `--no-videos` | Skip video processing | Process all |
| `--no-twitter` | Skip X/Twitter processing | Process all |
| `--no-pdfs` | Skip PDF processing | Process all |
| `--property-prefix PREFIX` | Property prefix for topics | "topic" |
| `--min-subtitle-length N` | Minimum subtitle length | 100 |
| `--no-backup` | Disable automatic backups | Enabled |
| `--log-level LEVEL` | Logging level | INFO |
| `--log-file FILE` | Write logs to file | Console only |
| `--report-file FILE` | Save JSON report | No report |

## Output Format

### Block Structure
The processor creates a hierarchical block structure:

```markdown
topic-1:: machine-learning
topic-2:: python
topic-3:: tutorial
- {{video https://youtube.com/watch?v=...}}
  **Learn Python - Full Course for Beginners**
  By: freeCodeCamp.org
  Duration: 4:26:52
```

### Topic Pages
Each topic gets its own page with:

```markdown
type:: content-topic
topic:: machine-learning
created:: 2025-10-21
item-count:: 25
video-count:: 6
twitter-count:: 19

# Content tagged with: machine-learning
This page contains all content related to the topic: **machine-learning**
Found in 25 item(s) from your Logseq graph.

## Video Content (6 items)
### 1. Machine Learning Basics
**Source Page:** [[2024_01_15]]
**URL:** https://youtube.com/watch?v=...
**Author:** Author Name
**Processed:** 2025-10-21
```

## Topic Extraction Algorithm

### Methods Used
1. **Multi-word Phrase Extraction**
   - Bigrams: "machine-learning", "data-science"
   - Trigrams: "deep-learning-neural"
   - Domain terms: 20+ recognized patterns

2. **TF-IDF Scoring**
   - Term frequency with normalization
   - Sublinear scaling
   - Variation detection

3. **Title Analysis**
   - Capitalized word extraction
   - Special formatting detection
   - 2x weight multiplier

4. **Context-Aware Ranking**
   - Frequency score (2x weight)
   - Title presence (10x bonus)
   - Category matching (5x bonus)
   - Multi-word specificity (2x per word)
   - Domain recognition (8x bonus)
   - Technical patterns (+2 bonus)

### Example Results

**Input Title**: "Learn Python - Full Course for Beginners [Tutorial]"

**Extracted Topics**:
1. `python` (from title + content)
2. `full-course` (bigram from title)
3. `learn-python` (bigram from title)
4. `tutorial` (from title)
5. `programming` (from content)

## Architecture

### Pipeline Components

```
┌─────────────────────────────────────┐
│  Comprehensive Content Processor    │
├─────────────────────────────────────┤
│                                     │
│  ┌──────────────────────────────┐  │
│  │   Content Scanners           │  │
│  │   - Video URL Detection      │  │
│  │   - Twitter URL Detection    │  │
│  │   - PDF URL Detection        │  │
│  └──────────────────────────────┘  │
│                                     │
│  ┌──────────────────────────────┐  │
│  │   Content Extractors         │  │
│  │   - YouTube Metadata         │  │
│  │   - Subtitle Extraction      │  │
│  │   - Tweet Data               │  │
│  │   - PDF Metadata             │  │
│  └──────────────────────────────┘  │
│                                     │
│  ┌──────────────────────────────┐  │
│  │   Content Analyzer           │  │
│  │   - Topic Extraction         │  │
│  │   - TF-IDF Scoring           │  │
│  │   - Phrase Detection         │  │
│  │   - Smart Ranking            │  │
│  └──────────────────────────────┘  │
│                                     │
│  ┌──────────────────────────────┐  │
│  │   Block Enhancement          │  │
│  │   - Hierarchical Structure   │  │
│  │   - Property Assignment      │  │
│  │   - Metadata Formatting      │  │
│  └──────────────────────────────┘  │
│                                     │
│  ┌──────────────────────────────┐  │
│  │   Topic Page Generation      │  │
│  │   - Content Aggregation      │  │
│  │   - Cross-referencing        │  │
│  │   - Statistics               │  │
│  └──────────────────────────────┘  │
│                                     │
└─────────────────────────────────────┘
```

### Key Classes

- `ComprehensiveContentProcessor`: Main orchestrator
- `YouTubeSubtitleExtractor`: Video subtitle extraction
- `XTwitterExtractor`: Twitter/X content extraction
- `PDFExtractor`: PDF metadata and content extraction
- `ContentAnalyzer`: Advanced topic extraction

## Examples

### Test Topic Extraction
```bash
python test_improvements.py
```

### Process Specific Content Types
```bash
# Videos only
python scripts/comprehensive_processor_cli.py /path/to/graph --no-twitter --no-pdfs

# Twitter only
python scripts/comprehensive_processor_cli.py /path/to/graph --no-videos --no-pdfs

# PDFs only
python scripts/comprehensive_processor_cli.py /path/to/graph --no-videos --no-twitter
```

### Dry Run (Preview)
```bash
python scripts/comprehensive_processor_cli.py /path/to/graph --dry-run --log-level DEBUG
```

## Best Practices

1. **Backup First**: Always enabled by default, but verify backups exist
2. **Start Small**: Test on a small subset of pages first
3. **Review Topics**: Check generated topic pages for quality
4. **Iterate**: Adjust `--max-topics` based on your needs
5. **Use APIs**: YouTube and Twitter APIs provide better data
6. **Monitor Logs**: Use `--log-level DEBUG` for troubleshooting

## Troubleshooting

### No Subtitles Extracted
- Install `youtube_transcript_api`: `pip install youtube_transcript_api`
- Some videos don't have transcripts available
- Try providing `--youtube-api-key` for better results

### Topics Too Generic
- Increase `--max-topics` to get more specific topics
- Check that subtitles are being extracted (they provide better context)
- Review title formatting (capitalization helps)

### Already Processed Content
- The processor automatically skips processed blocks
- Look for "Block already processed, skipping" in logs
- Delete topic properties to reprocess specific blocks

### Memory Issues
- Process journals separately from main pages
- Use `--no-backup` to save disk space
- Clear old backup directories

## Performance

- **Processing Speed**: ~10-50 blocks/second (depending on network)
- **Memory Usage**: ~50-200MB (scales with graph size)
- **Topic Generation**: ~1000 topics for 1500 blocks
- **Backup Size**: Same as original graph

## License

See main project LICENSE file.

## Contributing

Contributions welcome! Please:
1. Add tests for new features
2. Update documentation
3. Follow existing code style
4. Test on sample graphs first

## Support

For issues, questions, or feature requests, please see the main project repository.
