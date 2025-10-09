# 🐍 Logseq Python Library API Documentation

## Overview

The Logseq Python Library provides the most comprehensive interface available for reading, querying, and modifying Logseq knowledge graphs programmatically. With support for virtually every Logseq feature, this library transforms your knowledge management workflow.

## 🆕 What's New in Advanced Version

- ✅ **Complete Task Management**: All task states, priorities, scheduling, deadlines
- ✅ **Advanced Content Types**: Code blocks, LaTeX/Math, queries, headings
- ✅ **Organization Features**: Namespaces, templates, aliases, hierarchies
- ✅ **Block Relationships**: References, embeds, annotations
- ✅ **25+ Query Methods**: Advanced filtering and search capabilities
- ✅ **Graph Analytics**: Workflow insights, productivity metrics
- ✅ **Real-time Parsing**: Automatic content type detection

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

## 🔥 **Advanced Data Models**

### TaskState (Enum)

Represents task states in Logseq.

**Values:**
- `TODO` - Task to be done
- `DOING` - Currently in progress
- `DONE` - Completed task
- `LATER` - Deferred task
- `NOW` - High priority current task
- `WAITING` - Waiting for external dependency
- `CANCELLED` - Task cancelled
- `DELEGATED` - Task assigned to someone else
- `IN_PROGRESS` - Alternative for DOING

### Priority (Enum)

Represents priority levels in Logseq.

**Values:**
- `A` - High priority [#A]
- `B` - Medium priority [#B] 
- `C` - Low priority [#C]

### BlockType (Enum)

Represents different types of blocks in Logseq.

**Values:**
- `BULLET` - Regular bullet point
- `NUMBERED` - Numbered list item
- `QUOTE` - Quote block
- `HEADING` - Heading block (H1-H6)
- `CODE` - Code block
- `MATH` - Mathematical content
- `EXAMPLE` - Example block
- `EXPORT` - Export block
- `VERSE` - Verse block
- `DRAWER` - Drawer block

### ScheduledDate

Represents scheduled/deadline dates with advanced features.

**Attributes:**
- `date` (date): The scheduled date
- `time` (Optional[str]): Time component (e.g., "10:00")
- `repeater` (Optional[str]): Repeater pattern (e.g., "+1w", "+3d")
- `delay` (Optional[str]): Delay pattern

### LogseqQuery

Represents a Logseq query block.

**Attributes:**
- `query_string` (str): The query content
- `query_type` (str): Type - "simple", "advanced", or "custom"
- `results` (List[Dict]): Query results (when executed)
- `live` (bool): Whether query is live-updating
- `collapsed` (bool): Whether query block is collapsed

### Template

Represents a Logseq template.

**Attributes:**
- `name` (str): Template name
- `content` (str): Template content
- `variables` (List[str]): Template variables ({{variable}})
- `usage_count` (int): How often template is used
- `template_type` (str): "block" or "page"

### Annotation

Represents PDF annotations or highlights.

**Attributes:**
- `id` (str): Unique annotation identifier
- `content` (str): Annotation content/note
- `page_number` (Optional[int]): PDF page number
- `highlight_text` (Optional[str]): Highlighted text
- `annotation_type` (str): "highlight", "note", "underline"
- `color` (Optional[str]): Highlight color
- `pdf_path` (Optional[str]): Path to PDF file
- `coordinates` (Optional[Dict]): Position coordinates

### WhiteboardElement

Represents elements on a Logseq whiteboard.

**Attributes:**
- `id` (str): Unique element identifier
- `element_type` (str): "shape", "text", "block", "page", "image"
- `content` (str): Element content
- `position` (Dict): x, y coordinates
- `size` (Dict): width, height dimensions
- `style` (Dict): color, stroke, and other styling
- `block_id` (Optional[str]): Linked block ID

---

### Block (Enhanced)

Represents a single block in Logseq with full feature support.

#### Attributes

**Core Attributes:**
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

**🆕 Advanced Task Features:**
- **task_state**: TaskState enum (TODO, DOING, DONE, etc.)
- **priority**: Priority enum (A, B, C)
- **scheduled**: ScheduledDate for SCHEDULED dates
- **deadline**: ScheduledDate for DEADLINE dates

**🆕 Content Type Features:**
- **block_type**: BlockType enum (BULLET, CODE, HEADING, etc.)
- **collapsed**: Boolean indicating if block is collapsed
- **heading_level**: Integer 1-6 for heading blocks
- **code_language**: Programming language for code blocks
- **latex_content**: Extracted LaTeX/math content
- **query**: LogseqQuery object for query blocks

**🆕 Relationship Features:**
- **referenced_blocks**: Set of block IDs this block references
- **embedded_blocks**: List of BlockEmbed objects
- **annotations**: List of Annotation objects

**🆕 Advanced Features:**
- **drawing_data**: Dictionary containing drawing information
- **whiteboard_elements**: List of WhiteboardElement objects
- **plugin_data**: Dictionary for plugin-specific data

#### Methods

##### `get_links() -> Set[str]`

Extract page links from content.

- **Returns**: Set of linked page names

##### `get_block_references() -> Set[str]`

Extract block references from content.

- **Returns**: Set of referenced block IDs

##### `is_task() -> bool`

Check if this block is a task.

- **Returns**: True if block has a task state

##### `is_completed_task() -> bool`

Check if this is a completed task.

- **Returns**: True if task state is DONE

##### `is_scheduled() -> bool`

Check if this block is scheduled.

- **Returns**: True if block has a scheduled date

##### `has_deadline() -> bool`

Check if this block has a deadline.

- **Returns**: True if block has a deadline date

##### `get_all_dates() -> List[date]`

Get all dates associated with this block.

- **Returns**: List of scheduled and deadline dates

##### `to_markdown() -> str`

Convert block to Logseq markdown format with task states and priorities.

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

#### 🆕 Advanced Logseq Query Methods

##### `has_task_state(state: TaskState) -> QueryBuilder`

Filter by task state.

- **state**: TaskState to filter by (TODO, DOING, DONE, etc.)

##### `is_task() -> QueryBuilder`

Filter items that are tasks.

##### `is_completed_task() -> QueryBuilder`

Filter completed tasks.

##### `has_priority(priority: Priority) -> QueryBuilder`

Filter by priority level.

- **priority**: Priority level (A, B, C)

##### `has_scheduled_date(date_obj: Optional[date] = None) -> QueryBuilder`

Filter items that are scheduled.

- **date_obj**: Specific date to filter by (None for any scheduled item)

##### `has_deadline(date_obj: Optional[date] = None) -> QueryBuilder`

Filter items that have deadlines.

- **date_obj**: Specific date to filter by (None for any deadline)

##### `has_block_type(block_type: BlockType) -> QueryBuilder`

Filter by block type.

- **block_type**: BlockType to filter by

##### `is_heading(level: Optional[int] = None) -> QueryBuilder`

Filter heading blocks.

- **level**: Specific heading level (1-6), None for any heading

##### `is_code_block(language: Optional[str] = None) -> QueryBuilder`

Filter code blocks.

- **language**: Programming language to filter by

##### `has_math_content() -> QueryBuilder`

Filter blocks with LaTeX/mathematical content.

##### `has_query() -> QueryBuilder`

Filter blocks that contain queries.

##### `has_block_references() -> QueryBuilder`

Filter blocks that reference other blocks.

##### `has_embeds() -> QueryBuilder`

Filter blocks that embed other content.

##### `in_namespace(namespace: str) -> QueryBuilder`

Filter pages in a specific namespace.

- **namespace**: Namespace to filter by

##### `is_template() -> QueryBuilder`

Filter template pages.

##### `is_whiteboard() -> QueryBuilder`

Filter whiteboard pages.

##### `has_annotations() -> QueryBuilder`

Filter items with PDF annotations.

##### `is_collapsed() -> QueryBuilder`

Filter collapsed blocks.

##### `has_alias(alias: str) -> QueryBuilder`

Filter pages that have a specific alias.

- **alias**: Alias to search for

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

### 🆕 Advanced Task Management

```python
from logseq_py import TaskState, Priority
from datetime import date, timedelta

# Find high-priority tasks due this week
urgent_tasks = (client.query()
               .blocks()
               .is_task()
               .has_priority(Priority.A)
               .has_deadline()
               .custom_filter(lambda b: b.deadline.date <= date.today() + timedelta(days=7))
               .execute())

# Get overdue tasks
overdue = (client.query()
          .blocks()
          .has_deadline()
          .custom_filter(lambda b: b.deadline.date < date.today())
          .execute())

# Find all TODO tasks in project namespace
project_todos = (client.query()
                .blocks()
                .has_task_state(TaskState.TODO)
                .in_page("project/")
                .execute())

# Get workflow summary
workflow = client.graph.get_workflow_summary()
print(f"Tasks: {workflow['total_tasks']} ({workflow['completed_tasks']} done)")
```

### 💻 Advanced Content Analysis

```python
# Find Python code blocks
python_code = (client.query()
              .blocks()
              .is_code_block(language="python")
              .execute())

# Get math content
math_blocks = (client.query()
              .blocks()
              .has_math_content()
              .execute())

# Find all H2 headings
headings = (client.query()
           .blocks()
           .is_heading(level=2)
           .execute())

# Get blocks with references
linked_blocks = (client.query()
                .blocks()
                .has_block_references()
                .execute())
```

### 🗂️ Organization & Structure

```python
# Find template pages
templates = client.query().pages().is_template().execute()

# Get pages in specific namespace
project_pages = client.query().pages().in_namespace("project").execute()

# Find whiteboard pages
whiteboards = client.query().pages().is_whiteboard().execute()

# Get pages with aliases
aliased_pages = (client.query()
                .pages()
                .custom_filter(lambda p: len(p.aliases) > 0)
                .execute())
```

### 📊 Graph Analytics

```python
# Get comprehensive insights
insights = client.graph.get_graph_insights()

# Most connected pages
for page, connections in insights['most_connected_pages'][:5]:
    print(f"{page}: {connections} backlinks")

# Most used tags
for tag, usage in insights['most_used_tags'][:10]:
    print(f"#{tag}: {usage} pages")

# Namespace analysis
for namespace in client.graph.get_all_namespaces():
    pages = client.graph.get_pages_by_namespace(namespace)
    print(f"{namespace}/: {len(pages)} pages")
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