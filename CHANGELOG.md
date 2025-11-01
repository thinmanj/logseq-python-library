# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.4.0] - 2025-11-01

### ✨ Features
- **DiagramBuilder for visual diagrams** - Full support for diagram code blocks in Logseq
  - **Mermaid diagrams:** flowchart, sequence, gantt, class, state, ER, pie charts
  - **Graphviz:** directed and undirected graphs with helper methods
  - **PlantUML:** sequence diagrams, class diagrams, and more
  - **Additional formats:** Ditaa, Vega, Vega-Lite, Excalidraw support
  - Convenience method `page.diagram('mermaid')` for easy integration
  - Diagrams work seamlessly in pages and as sub-blocks
  - Helper methods for common diagram types (e.g., `mermaid_flowchart()`, `graphviz_digraph()`)

### ✅ Testing
- **14 new diagram tests** - Complete coverage of all diagram types
  - Tests for all Mermaid diagram types (7 types)
  - Graphviz directed and undirected graphs
  - PlantUML start/end tags
  - Diagrams in blocks and pages
  - Multiple diagrams in single page
  - **Total: 68 passing builder tests**

### 📚 Examples
```python
# Mermaid flowchart
page.diagram('mermaid').mermaid_flowchart('LR').line('A --> B')

# Graphviz
diagram = DiagramBuilder('graphviz')
diagram.graphviz_digraph().line('  A -> B;').close_block()

# PlantUML
diagram = DiagramBuilder('plantuml')
diagram.plantuml_start().line('Alice -> Bob').plantuml_end()
```

## [0.3.3] - 2025-11-01

### ✅ Testing
- **Added comprehensive builder test suite** - 54 new tests preventing regressions
  - Regression tests for v0.3.1 newline handling fix
  - Regression tests for v0.3.2 multi-line content fix
  - Complete coverage of BlockBuilder, CodeBlockBuilder, and all content type builders
  - Tests for tasks, tables, quotes, media embeds, queries, and journal entries
  - Edge case tests: unicode, special characters, deep nesting (10 levels)
  - Integration scenarios: meeting notes, code documentation, project pages
  - All 54 tests passing, preventing future bugs in builder functionality

## [0.3.2] - 2025-11-01

### 🐛 Bug Fixes
- **Fixed BlockBuilder multi-line content handling** - Code blocks and other multi-line content now render correctly within blocks
  - When a code block (or any multi-line content) is added to a block, all lines are now properly indented
  - First line gets the bullet point (`- `), subsequent lines get proper continuation indentation
  - Fixes code blocks being split incorrectly across multiple unindented lines

## [0.3.1] - 2025-11-01

### 🐛 Bug Fixes
- **Fixed BlockBuilder newline rendering** - Blocks and sub-blocks now properly render on separate lines with correct indentation
  - Changed `"\\n".join()` to `"\n".join()` in `BlockBuilder.build()` and `LogseqBuilder.build()`
  - Sub-blocks now correctly nest under parent blocks instead of appearing on the same line
  - This fix affects all content generated using the builder pattern (comprehensive processor, media embeds, etc.)

## [0.3.0] - 2025-10-29

### ✨ Added
- **Terminal User Interface (TUI)**
  - Interactive graph browser with search and navigation
  - Real-time page editing and block management
  - Graph statistics and metrics dashboard
  - Keyboard shortcuts for efficient workflow
  - Built with Textual for rich terminal experience

- **ETL Scripts and Automation**
  - JSON and CSV export functionality
  - Weekly report generation from journal entries
  - Markdown to PDF conversion utilities
  - Template application with variable substitution
  - Topic and tag indexing automation
  - Complete CLI interface for all ETL operations

- **Comprehensive Documentation**
  - Complete tutorial system (TUTORIAL.md)
  - ETL automation guide (AUTOMATION.md)
  - Test coverage roadmap (TEST_COVERAGE.md)
  - Pipeline usage guide updates
  - Real-world automation examples

- **Testing Infrastructure**
  - 67 new tests for TUI and ETL functionality
  - Coverage reporting with strategic exclusions
  - Test fixtures for isolated graph testing
  - Performance and integration test suites

### 🔧 Improvements
- Enhanced LogseqClient with context manager support
- Better error handling in content processors
- Improved template variable detection
- Optimized graph loading for large datasets

### 📦 Package Updates
- Added `textual>=0.41.0` for TUI support
- Updated test dependencies (pytest, pytest-cov)
- New optional dependencies for CLI and TUI features

### 📊 Test Coverage
- Current coverage: 35% (178 passing tests)
- TUI: 32 tests covering widgets and navigation
- ETL: 42 tests covering all export formats
- Roadmap to 80% core module coverage

### 🎯 Use Cases Enabled
- Knowledge graph automation and scheduling
- Batch export and backup workflows
- Meeting preparation and note synthesis
- Research digest generation
- Personal CRM and task management
- Learning and progress tracking

### 🚀 Breaking Changes
None - this release is fully backward compatible with 0.2.x

### 📚 Migration Guide
No migration needed. New TUI and ETL features are opt-in:
```bash
# Install with TUI support
pip install logseq-python[tui]

# Launch TUI
logseq tui /path/to/graph

# Run ETL commands
logseq etl export --format json /path/to/graph output.json
```

## [1.0.0a1] - 2024-10-15 - Alpha Release

### ✨ Added
- **Complete Analysis Engine Implementation**
  - 4 Advanced Content Analyzers: Sentiment, Topics, Summary, Structure
  - AI-powered content analysis with comprehensive insights
  - Lexicon-based sentiment analysis with negation handling
  - Topic extraction with keyword analysis and entity recognition
  - Extractive summarization with sentence scoring
  - Content structure analysis and readability metrics

- **8 Specialized Content Extractors**
  - URL Content Extractor with metadata extraction
  - YouTube Video Extractor with API integration
  - Twitter Thread Extractor with engagement metrics
  - Academic Paper Extractor for research content
  - GitHub Repository Extractor with code analysis
  - PDF Document Extractor with text extraction
  - RSS/News Feed Extractor for articles
  - Video Platform Extractor (Vimeo, TikTok, Twitch, Dailymotion)

- **3 Intelligent Content Generators**
  - Summary Page Generator for comprehensive reports
  - Insights Block Generator for analytical findings
  - Task Analysis Generator for productivity insights

- **Flexible Pipeline Framework**
  - Step-by-step processing with state management
  - Error handling and recovery mechanisms
  - Progress tracking and reporting
  - Resumable pipeline execution
  - Performance optimization features

- **Rich CLI Interface**
  - Complete command-line tools for all operations
  - Pipeline templates and configuration management
  - Real-world example workflows
  - Interactive progress reporting
  - Batch processing capabilities

- **Real-World Examples**
  - Research paper processing workflow
  - Social media content curation pipeline
  - News article summarization system

- **Comprehensive Testing**
  - Full integration test suite
  - End-to-end workflow testing
  - Performance and scalability tests
  - Mock integration testing

- **Complete Documentation**
  - 600+ line comprehensive guide
  - API reference documentation
  - Logseq-formatted documentation
  - Tutorials and usage examples
  - Advanced customization guides

### 🔧 Technical Features
- Python 3.8+ compatibility
- Async/await support for performance
- Type hints throughout codebase
- Comprehensive error handling
- Logging and debugging support
- Memory optimization for large datasets
- Parallel processing capabilities
- Result caching system

### 📦 Package Features
- PyPI-ready package configuration
- Optional dependencies for different use cases
- CLI entry points
- Development tools integration
- Comprehensive test coverage

### 🚀 Release Notes
This is the first alpha release of logseq-python with complete Analysis Engine functionality. 
The package is feature-complete and ready for testing and feedback from the community.

**Breaking Changes**: None (initial release)

**Migration Guide**: None (initial release)

**Known Issues**: 
- Some extractors require API keys for full functionality
- Large graph processing may require memory optimization settings

**Next Release Planning**: 
- Beta release planned after community feedback
- Additional extractor integrations
- Performance optimizations
- Extended documentation

---

## How to Upgrade

For alpha users:
```bash
pip install --upgrade logseq-python==1.0.0a1
```

## Support

- **Documentation**: See README.md and PIPELINE_GUIDE.md
- **Issues**: https://github.com/thinmanj/logseq-python-library/issues
- **Discussions**: https://github.com/thinmanj/logseq-python-library/discussions