# Logseq Python Library

A Python library for interacting with Logseq knowledge graphs. This library allows you to programmatically read, query, and modify your Logseq data.

## Features

- **Read Logseq Data**: Parse pages, blocks, and metadata from your Logseq graph
- **Query System**: Search for blocks, pages, and content using various criteria
- **Data Manipulation**: Add new pages, blocks, and journal entries
- **Graph Operations**: Work with links, references, and relationships
- **Preserve Format**: Maintain Logseq's markdown format when making changes

## Installation

```bash
pip install logseq-py
```

Or for development:

```bash
git clone https://github.com/yourusername/logseq-python.git
cd logseq-python
pip install -e .
```

## Quick Start

```python
from logseq_py import LogseqClient

# Initialize client with your Logseq graph directory
client = LogseqClient("/path/to/your/logseq/graph")

# Load the graph
graph = client.load_graph()

# Query for blocks containing specific text
blocks = client.query().content_contains("python").execute()

# Get all pages with a specific tag
pages = client.query().has_tag("project").execute()

# Add a new journal entry
client.add_journal_entry("Today I learned about Logseq Python integration!")

# Create a new page
client.create_page("My New Page", "This is the content of my new page.")
```

## Documentation

- [API Reference](docs/api.md)
- [Examples](examples/)
- [Contributing](CONTRIBUTING.md)

## Requirements

- Python 3.8+
- Logseq graph (local directory)

## License

MIT License - see [LICENSE](LICENSE) file for details.