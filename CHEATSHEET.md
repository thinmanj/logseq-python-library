# Logseq Python Library - IPython Cheat Sheet

## Quick Start
```bash
# Start the interactive session
./start_session.sh
# or
source .venv/bin/activate && ipython -i ipython_startup.py
```

## Context Manager Support (NEW!)

### Basic Usage with Auto-Save
```python
# Auto-saves all changes when context exits
with LogseqClient('/path/to/graph') as client:
    client.add_journal_entry('This will be auto-saved!')
    client.create_page('New Page', 'Content here #demo')
    # No need to call save - happens automatically
```

### With Backup Protection
```python
# Creates backup before making changes
with LogseqClient('/path/to/graph', backup_on_enter=True) as client:
    client.add_journal_entry('Changes are protected by backup')
    # If exception occurs, can rollback to backup
```

### Manual Save Control
```python
# Disable auto-save for manual control
with LogseqClient('/path/to/graph', auto_save=False) as client:
    client.add_journal_entry('Changes tracked but not auto-saved')
    
    # Check what's been modified
    session_info = client.get_session_info()
    print(f"Modified {session_info['modified_pages']} pages")
    
    # Save manually when ready
    saved_count = client.save_all()
```

### Session Information
```python
with LogseqClient('/path/to/graph') as client:
    info = client.get_session_info()
    # Returns: session_start, duration, modified_pages, backup info, etc.
```

### Exception Safety
```python
try:
    with LogseqClient('/path', backup_on_enter=True) as client:
        client.create_page('Test', 'Content')
        raise ValueError("Something went wrong!")  # Simulated error
except ValueError:
    # Context manager will offer rollback option if backup was created
    pass
```

## Basic Usage

### Connect to a Logseq Graph
```python
# Connect to your Logseq graph
client = LogseqClient('/path/to/your/logseq/graph')
graph = client.load_graph()

# Get basic statistics
stats = graph.get_statistics()
print(stats)
```

### Working with Pages
```python
# Access pages dictionary
pages = graph.pages

# Get a specific page
page = pages['page_name']

# Create a new page
new_page = client.create_page('New Page', 'Initial content here')

# Add journal entry
journal = client.add_journal_entry('Today I learned about Logseq Python! #learning')
```

### Working with Blocks
```python
# Create a new block
block = Block(content='This is a new block with #tags')

# Check what was extracted
print(f"Tags: {block.tags}")
print(f"Task state: {block.task_state}")

# Create task blocks
task_block = Block(content='TODO Finish the project [#A]')
print(f"Task: {task_block.task_state}")
print(f"Priority: {task_block.priority}")

# Work with sample data
for block in sample_blocks:
    print(f"Content: {block.content}")
    if block.is_task():
        print(f"  Task State: {block.task_state}")
    if block.tags:
        print(f"  Tags: {', '.join(block.tags)}")
```

### Search and Query
```python
# Search pages
project_pages = graph.search_pages('project')

# Search blocks
todo_blocks = graph.search_blocks('TODO')

# Advanced queries with QueryBuilder
query = QueryBuilder().blocks().with_content('meeting').with_task_state(TaskState.TODO)
results = graph.query(query)
```

### Available Enums
```python
# Task states
TaskState.TODO, TaskState.DOING, TaskState.DONE, TaskState.LATER
TaskState.NOW, TaskState.WAITING, TaskState.CANCELLED

# Priorities  
Priority.A, Priority.B, Priority.C

# Block types
BlockType.BULLET, BlockType.NUMBERED, BlockType.CODE, BlockType.HEADING
```

## Helpful Commands

### Exploration
```python
# Show welcome screen again
show_welcome()

# Show examples again  
show_examples()

# Get help on any component
help(LogseqClient)
help(Block)
help(Page)

# Explore sample data
sample_blocks[0].content
sample_pages[0].name

# Check what methods are available
dir(graph)
dir(client)
```

### Graph Analysis
```python
# Get statistics
stats = graph.get_statistics()

# Find all pages with tags
tagged_pages = [p for p in graph.pages.values() if p.tags]

# Find all task blocks
task_blocks = [b for b in graph.blocks.values() if b.is_task()]

# Find completed tasks
completed = [b for b in graph.blocks.values() if b.is_completed_task()]
```

### Block Analysis
```python
# Check block properties
block = sample_blocks[0]
print(f"Links: {block.get_links()}")
print(f"Block refs: {block.get_block_references()}")
print(f"Is scheduled: {block.is_scheduled()}")
print(f"Has deadline: {block.has_deadline()}")

# Convert to markdown
print(block.to_markdown())
```

## Advanced Features

### Working with Dates
```python
from datetime import date
from logseq_py.models import ScheduledDate

# Create scheduled date
scheduled = ScheduledDate(date=date.today(), time="10:00", repeater="+1w")

# Add to block
block = Block(content='Weekly meeting')
block.scheduled = scheduled
```

### Custom Properties
```python
# Add custom properties to blocks
block = Block(content='My block')
block.properties['priority'] = Priority.A
block.properties['custom_field'] = 'custom_value'
```

## Saving Changes to Filesystem

### Quick Save Methods
```python
# Save helper functions (from startup script)
show_save_methods()  # Show all save options

# Save all pages in the graph
save_graph(client)

# Quick add task to today's journal
task = quick_add_task(client, 'TODO Review the new features #work')

# Preview markdown before saving
preview_markdown(page)
preview_markdown(block)
```

### Direct Client Methods
```python
# Update existing block content (auto-saves)
updated_block = client.update_block(block_id, 'Updated content #new-tag')

# Add new blocks to existing pages (auto-saves)
new_block = client.add_block_to_page('Project Planning', 'New milestone achieved!')

# Create new pages (auto-saves)
new_page = client.create_page('Meeting Notes', 'Initial content here #meeting')

# Add journal entries (auto-saves)
journal = client.add_journal_entry('Today I made great progress! #success')

# Delete blocks (auto-saves)
success = client.delete_block(block_id)
```

### Manual Save Operations
```python
# Save individual pages
client._save_page(page)

# Save after modifying blocks manually
block.content = 'Modified content'
block.task_state = TaskState.DONE
page = client.get_page(block.page_name)
client._save_page(page)  # Save the page containing the block
```

### Working with File Paths
```python
# Check where pages will be saved
for page_name, page in graph.pages.items():
    if page.file_path:
        print(f'{page_name}: {page.file_path}')

# Create page with specific path
from pathlib import Path
file_path = client.graph_path / 'pages' / 'custom-page.md'
page = Page(name='Custom Page', file_path=file_path)
client._save_page(page)
```

### Batch Operations
```python
# Modify multiple blocks and save all affected pages
modified_pages = set()
for block in graph.blocks.values():
    if 'old-tag' in block.tags:
        block.content = block.content.replace('#old-tag', '#new-tag')
        if block.page_name:
            modified_pages.add(block.page_name)

# Save all modified pages
for page_name in modified_pages:
    page = graph.get_page(page_name)
    if page:
        client._save_page(page)
```

## Tips
- Use tab completion to explore available methods
- Check the `sample_blocks` and `sample_pages` variables for example data
- The library automatically parses tags, task states, priorities, and dates from content
- Most client methods (`add_journal_entry`, `create_page`, `update_block`) auto-save
- Use `preview_markdown()` to see how content will look before saving
- Changes to objects in memory need explicit saving with `client._save_page()`
- Use `save_graph(client)` to save all pages at once
- Use `graph.get_statistics()` to understand your graph structure
