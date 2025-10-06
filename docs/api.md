# Logseq Python Library API Documentation

## Overview

The Logseq Python Library provides a comprehensive interface for reading, querying, and modifying Logseq knowledge graphs programmatically.

## Core Components

### LogseqClient

The main entry point for interacting with Logseq graphs.

#### Constructor

```python
LogseqClient(graph_path: Union[str, Path])
```

- **graph_path**: Path to your Logseq graph directory

#### Methods

##### `load_graph(force_reload: bool = False) -> LogseqGraph`

Load the Logseq graph from disk.

- **force_reload**: Force reload even if graph is already loaded
- **Returns**: LogseqGraph object containing all pages and blocks

##### `get_page(page_name: str) -> Optional[Page]`

Retrieve a specific page by name.

- **page_name**: Name of the page to retrieve
- **Returns**: Page object or None if not found

##### `get_block(block_id: str) -> Optional[Block]`

Retrieve a specific block by ID.

- **block_id**: ID of the block to retrieve
- **Returns**: Block object or None if not found

##### `query() -> QueryBuilder`

Create a new query builder for advanced searches.

- **Returns**: QueryBuilder instance for constructing queries

##### `search(query: str, case_sensitive: bool = False) -> Dict[str, List[Block]]`

Search for text across all pages.

- **query**: Text to search for
- **case_sensitive**: Whether to perform case-sensitive search
- **Returns**: Dictionary mapping page names to matching blocks

##### `create_page(name: str, content: str = "", properties: Dict[str, Any] = None) -> Page`

Create a new page.

- **name**: Name of the new page
- **content**: Initial content for the page
- **properties**: Page properties
- **Returns**: Created Page object

##### `add_journal_entry(content: str, date_obj: Optional[date] = None) -> Page`

Add a journal entry.

- **content**: Content of the journal entry
- **date_obj**: Date for the journal entry (defaults to today)
- **Returns**: Journal page object

##### `add_block_to_page(page_name: str, content: str, parent_block_id: Optional[str] = None) -> Block`

Add a new block to a page.

- **page_name**: Name of the target page
- **content**: Block content
- **parent_block_id**: ID of parent block (for nested blocks)
- **Returns**: Created Block object

##### `update_block(block_id: str, content: str) -> Optional[Block]`

Update the content of an existing block.

- **block_id**: ID of the block to update
- **content**: New content for the block
- **Returns**: Updated Block object or None if not found

##### `delete_block(block_id: str) -> bool`

Delete a block.

- **block_id**: ID of the block to delete
- **Returns**: True if deleted successfully, False if not found

##### `get_statistics() -> Dict[str, Any]`

Get graph statistics.

- **Returns**: Dictionary containing various graph statistics

##### `export_to_json(output_path: Union[str, Path]) -> None`

Export the graph to JSON format.

- **output_path**: Path where to save the JSON file

---

### Block

Represents a single block in Logseq.

#### Attributes

- **id**: Unique block identifier
- **content**: Block content text
- **level**: Indentation level (0 = top-level)
- **parent_id**: ID of parent block (if any)
- **children_ids**: List of child block IDs
- **properties**: Dictionary of block properties
- **tags**: Set of tags in the block
- **page_name**: Name of the page containing this block
- **created_at**: Creation timestamp
- **updated_at**: Last modification timestamp

#### Methods

##### `get_links() -> Set[str]`

Extract page links from content.

- **Returns**: Set of linked page names

##### `get_block_references() -> Set[str]`

Extract block references from content.

- **Returns**: Set of referenced block IDs

##### `to_markdown() -> str`

Convert block to Logseq markdown format.

- **Returns**: Markdown representation of the block

---

### Page

Represents a page in Logseq.

#### Attributes

- **name**: Page name
- **title**: Page title
- **file_path**: Path to the source file
- **blocks**: List of blocks in the page
- **properties**: Dictionary of page properties
- **tags**: Set of all tags in the page
- **links**: Set of pages this page links to
- **backlinks**: Set of pages that link to this page
- **is_journal**: Whether this is a journal page
- **journal_date**: Date for journal pages
- **created_at**: Creation timestamp
- **updated_at**: Last modification timestamp

#### Methods

##### `add_block(block: Block)`

Add a block to the page.

- **block**: Block to add

##### `get_block_by_id(block_id: str) -> Optional[Block]`

Get a block by its ID.

- **block_id**: ID of the block to find
- **Returns**: Block object or None if not found

##### `get_blocks_by_content(search_text: str, case_sensitive: bool = False) -> List[Block]`

Find blocks containing specific text.

- **search_text**: Text to search for
- **case_sensitive**: Whether search should be case-sensitive
- **Returns**: List of matching blocks

##### `get_blocks_by_tag(tag: str) -> List[Block]`

Find blocks with a specific tag.

- **tag**: Tag to search for
- **Returns**: List of blocks with the tag

##### `to_markdown() -> str`

Convert page to Logseq markdown format.

- **Returns**: Markdown representation of the page

---

### QueryBuilder

Fluent interface for constructing complex queries.

#### Target Selection

##### `pages() -> QueryBuilder`

Query pages instead of blocks.

##### `blocks() -> QueryBuilder`

Query blocks (default behavior).

#### Content Filters

##### `content_contains(text: str, case_sensitive: bool = False) -> QueryBuilder`

Filter by content containing specific text.

##### `content_matches(pattern: str, flags: int = 0) -> QueryBuilder`

Filter by content matching a regex pattern.

#### Tag Filters

##### `has_tag(tag: str) -> QueryBuilder`

Filter by items containing a specific tag.

##### `has_any_tag(tags: List[str]) -> QueryBuilder`

Filter by items containing any of the specified tags.

##### `has_all_tags(tags: List[str]) -> QueryBuilder`

Filter by items containing all of the specified tags.

#### Property Filters

##### `has_property(key: str, value: Optional[str] = None) -> QueryBuilder`

Filter by items having a specific property.

#### Link Filters

##### `links_to(page_name: str) -> QueryBuilder`

Filter by items that link to a specific page.

##### `in_page(page_name: str) -> QueryBuilder`

Filter blocks that are in a specific page.

#### Type Filters

##### `is_journal(is_journal: bool = True) -> QueryBuilder`

Filter by journal pages (only works when querying pages).

#### Date Filters

##### `created_after(date_obj: Union[datetime, date]) -> QueryBuilder`

Filter by items created after a specific date.

##### `created_before(date_obj: Union[datetime, date]) -> QueryBuilder`

Filter by items created before a specific date.

##### `updated_after(date_obj: Union[datetime, date]) -> QueryBuilder`

Filter by items updated after a specific date.

#### Structure Filters

##### `level(level: int) -> QueryBuilder`

Filter blocks by indentation level.

##### `min_level(level: int) -> QueryBuilder`

Filter blocks by minimum indentation level.

##### `max_level(level: int) -> QueryBuilder`

Filter blocks by maximum indentation level.

##### `has_children() -> QueryBuilder`

Filter blocks that have child blocks.

##### `is_orphan() -> QueryBuilder`

Filter blocks that have no parent (top-level blocks).

#### Custom Filters

##### `custom_filter(filter_func: Callable) -> QueryBuilder`

Add a custom filter function.

- **filter_func**: Function that takes an item and returns bool

#### Sorting and Limiting

##### `sort_by(field: str, desc: bool = False) -> QueryBuilder`

Sort results by a field.

##### `limit(count: int) -> QueryBuilder`

Limit the number of results.

#### Execution

##### `execute() -> Union[List[Block], List[Page]]`

Execute the query and return results.

##### `count() -> int`

Count the number of matching items without returning them.

##### `first() -> Optional[Union[Block, Page]]`

Get the first matching item.

##### `exists() -> bool`

Check if any items match the query.

---

### LogseqUtils

Utility class for Logseq operations.

#### Static Methods

##### `is_journal_page(page_name: str) -> bool`

Check if a page name represents a journal entry.

##### `parse_journal_date(page_name: str) -> Optional[datetime]`

Parse journal date from page name.

##### `parse_markdown_file(file_path: Path) -> Page`

Parse a Logseq markdown file into a Page object.

##### `ensure_valid_page_name(name: str) -> str`

Ensure a page name is valid for Logseq.

##### `format_date_for_journal(date_obj: date) -> str`

Format a date object for Logseq journal page naming.

---

### QueryStats

Helper class for computing statistics on query results.

#### Static Methods

##### `tag_frequency(items: List[Union[Block, Page]]) -> Dict[str, int]`

Compute tag frequency from a list of items.

##### `page_distribution(blocks: List[Block]) -> Dict[str, int]`

Compute page distribution for a list of blocks.

##### `level_distribution(blocks: List[Block]) -> Dict[int, int]`

Compute level distribution for a list of blocks.

##### `property_frequency(items: List[Union[Block, Page]]) -> Dict[str, int]`

Compute property frequency from a list of items.

---

## Usage Examples

### Basic Usage

```python
from logseq_py import LogseqClient

# Initialize client
client = LogseqClient("/path/to/your/logseq/graph")

# Load graph
graph = client.load_graph()

# Get statistics
stats = client.get_statistics()
print(f"Total pages: {stats['total_pages']}")

# Search for content
results = client.search("python")
```

### Advanced Queries

```python
# Find all project pages with active tag
project_pages = (client.query()
                 .pages()
                 .has_all_tags(["project", "active"])
                 .sort_by("name")
                 .execute())

# Find recent journal entries
from datetime import date, timedelta
week_ago = date.today() - timedelta(days=7)
recent_journals = (client.query()
                   .pages()
                   .is_journal()
                   .created_after(week_ago)
                   .execute())

# Find blocks with URLs
url_blocks = (client.query()
              .blocks()
              .content_matches(r'https?://[^\s]+')
              .limit(10)
              .execute())
```

### Creating Content

```python
# Create a new page
page = client.create_page("My New Page", "- Initial content")

# Add journal entry
client.add_journal_entry("Today I learned about Logseq Python integration!")

# Add block to existing page
block = client.add_block_to_page("My New Page", "Additional content")
```

### Data Export

```python
# Export to JSON
client.export_to_json("graph_backup.json")

# Query statistics
from logseq_py.query import QueryStats

tagged_blocks = client.query().blocks().custom_filter(
    lambda block: len(block.tags) > 0
).execute()

tag_freq = QueryStats.tag_frequency(tagged_blocks)
print("Most common tags:", list(tag_freq.keys())[:10])
```