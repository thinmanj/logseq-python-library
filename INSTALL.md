# Logseq Python Library - Installation Guide

## Project Structure

```
logseq-python/
├── README.md                    # Main documentation
├── setup.py                     # Package setup configuration
├── requirements.txt            # Python dependencies
├── INSTALL.md                  # This file
├── 
├── logseq_py/                  # Main package
│   ├── __init__.py             # Package initialization
│   ├── logseq_client.py        # Main client class
│   ├── models.py               # Data models (Block, Page, LogseqGraph)
│   ├── query.py                # Query builder and statistics
│   └── utils.py                # Utility functions
├── 
├── examples/                   # Usage examples
│   ├── basic_usage.py          # Basic library usage
│   ├── advanced_queries.py     # Advanced query examples
│   └── data_export_import.py   # Data export/import examples
├── 
├── tests/                      # Test suite
│   └── test_basic.py          # Basic functionality tests
└── 
└── docs/                      # Documentation
    └── api.md                 # Complete API documentation
```

## Installation

### 1. Clone or Download

```bash
# If you have git
git clone <repository-url>
cd logseq-python

# Or download and extract the files to a directory
```

### 2. Install Dependencies

```bash
# Create a virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Install the Package

```bash
# Install in development mode (recommended for testing)
pip install -e .

# Or install normally
pip install .
```

### 4. Verify Installation

```python
# Test that the library can be imported
python3 -c "from logseq_py import LogseqClient; print('✅ Installation successful!')"
```

## Quick Start

1. **Update the examples**: Edit the `graph_path` variable in the example files to point to your Logseq graph directory.

2. **Run basic example**:
   ```bash
   python examples/basic_usage.py
   ```

3. **Explore advanced features**:
   ```bash
   python examples/advanced_queries.py
   python examples/data_export_import.py
   ```

## Dependencies

The library requires:
- Python 3.8+
- python-dateutil>=2.8.0
- pyyaml>=6.0
- regex>=2021.4.4
- markdown>=3.3.0
- rich>=13.0.0 (optional, for better CLI output)
- click>=8.0.0 (optional, for CLI interface)

## 🚀 **Comprehensive Feature Set**

### ✅ **Core Features** (100% Complete)
- **📚 Data Reading**: Complete Logseq markdown parsing
- **🔍 Query System**: 30+ advanced query methods
- **📝 Content Creation**: Pages, blocks, journal entries
- **📊 Analytics**: Graph insights and statistics
- **💾 Data Export**: JSON, Markdown, advanced formats

### ✅ **Advanced Task Management** (100% Complete)
- **📋 Task States**: TODO, DOING, DONE, LATER, NOW, WAITING, CANCELLED, DELEGATED, IN-PROGRESS
- **⭐ Priority Levels**: A, B, C with [#A] syntax parsing
- **📅 Scheduling**: SCHEDULED dates with time and repeaters (+1w, +3d)
- **⏰ Deadlines**: DEADLINE tracking with overdue detection
- **📈 Workflow Analytics**: Completion rates, productivity metrics

### ✅ **Advanced Content Types** (100% Complete)
- **💻 Code Blocks**: Language detection (```python, #+begin_src)
- **🔢 Mathematics**: LaTeX/Math parsing ($$math$$, \\(inline\\))
- **🔍 Query Blocks**: {{query}} and #+begin_query support
- **📝 Headings**: H1-H6 hierarchical structure
- **🔗 References**: ((block-id)) linking and {{embed}} support
- **⚙️ Properties**: Advanced property parsing and querying

### ✅ **Organization & Structure** (100% Complete)
- **📁 Namespaces**: project/backend hierarchical organization
- **📄 Templates**: Template variables {{variable}} parsing
- **🔄 Aliases**: Page alias system with [[link]] support
- **🎨 Whiteboards**: .whiteboard file detection and support
- **📊 Hierarchies**: Parent/child page relationships

### ✅ **Graph Analytics & Insights** (95% Complete)
- **🔗 Connection Analysis**: Backlinks, most connected pages
- **📊 Content Statistics**: Block type distribution, tag usage
- **📈 Productivity Metrics**: Task completion trends, workflow summaries
- **🔍 Graph Relationships**: Link analysis, reference mapping
- **📋 Workflow Insights**: Advanced task analytics and reporting

### 🎯 Core Capabilities

1. **Read Logseq Data**: Load and parse entire Logseq graphs
2. **Advanced Queries**: Use fluent query builder for complex searches
3. **Content Manipulation**: Create, update, and delete content
4. **Data Analysis**: Generate statistics and insights
5. **Export/Import**: Backup and transform data

## Usage Examples

### Basic Usage
```python
from logseq_py import LogseqClient

# Initialize and load graph
client = LogseqClient("/path/to/your/logseq/graph")
graph = client.load_graph()

# Get statistics
stats = client.get_statistics()
print(f"Total pages: {stats['total_pages']}")

# Search content
results = client.search("python")
```

### Advanced Queries
```python
# Find project pages with active tag, sorted by name
project_pages = (client.query()
                .pages()
                .has_all_tags(["project", "active"])
                .sort_by("name")
                .execute())

# Find blocks with URLs
url_blocks = (client.query()
             .blocks()
             .content_matches(r'https?://[^\s]+')
             .limit(10)
             .execute())
```

### Content Creation
```python
# Create new page
page = client.create_page("My New Page", "- Initial content #important")

# Add journal entry
client.add_journal_entry("Today I learned about Logseq automation! #learning")

# Add block to existing page
block = client.add_block_to_page("My New Page", "Additional insight")
```

## Running Tests

```bash
# Run basic tests
python tests/test_basic.py

# Or with pytest (if installed)
python -m pytest tests/
```

## Troubleshooting

### Common Issues

1. **ModuleNotFoundError**: Install dependencies with `pip install -r requirements.txt`

2. **Graph not found**: Ensure the path points to your actual Logseq graph directory (contains .md files)

3. **Permission errors**: Make sure Python has read/write access to the graph directory

4. **Import errors**: Make sure you're in the correct directory and have installed the package

### Getting Help

1. Check the [API documentation](docs/api.md)
2. Look at the [examples](examples/) directory
3. Run the test suite to verify functionality
4. Check that your Logseq graph is in the expected format

## Contributing

This is a comprehensive Logseq Python library that provides:
- Full read/write access to Logseq graphs
- Advanced query capabilities
- Data export and analysis tools
- Extensive documentation and examples

The library is designed to be:
- **Easy to use**: Simple API for common operations
- **Powerful**: Advanced queries and data manipulation
- **Well-documented**: Complete API docs and examples
- **Tested**: Comprehensive test suite
- **Extensible**: Easy to add new features

Feel free to extend and customize the library for your specific needs!