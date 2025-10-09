# 🚀 Advanced Features Guide

This guide covers all the advanced Logseq features supported by the Python library. These features transform the library from a simple note reader into a comprehensive knowledge management and workflow automation toolkit.

## 📋 Task Management System

### Task States

The library supports all Logseq task states with automatic parsing:

```python
from logseq_py import TaskState

# Available task states
TaskState.TODO      # Standard task
TaskState.DOING     # In progress
TaskState.DONE      # Completed
TaskState.LATER     # Deferred
TaskState.NOW       # High priority current
TaskState.WAITING   # Waiting for external dependency
TaskState.CANCELLED # Cancelled task
TaskState.DELEGATED # Assigned to someone else
TaskState.IN_PROGRESS  # Alternative for DOING
```

### Priority Levels

Priority parsing with `[#A]`, `[#B]`, `[#C]` syntax:

```python
from logseq_py import Priority

# Find high-priority tasks
urgent = client.query().blocks().has_priority(Priority.A).execute()

# Priority levels
Priority.A  # High priority [#A]
Priority.B  # Medium priority [#B] 
Priority.C  # Low priority [#C]
```

### Scheduling & Deadlines

Full support for Org-mode style scheduling:

```python
# Scheduled dates with repeaters
# SCHEDULED: <2024-01-15 Mon 10:00 +1w>
scheduled_blocks = client.query().blocks().has_scheduled_date().execute()

# Deadline tracking
# DEADLINE: <2024-01-20 Sat>
deadline_blocks = client.query().blocks().has_deadline().execute()

# Check individual block
if block.is_scheduled():
    print(f"Scheduled for: {block.scheduled.date}")
    if block.scheduled.repeater:
        print(f"Repeats: {block.scheduled.repeater}")
```

### Workflow Analytics

Comprehensive task analytics:

```python
# Get workflow summary
summary = client.graph.get_workflow_summary()

print(f"Total tasks: {summary['total_tasks']}")
print(f"Completed: {summary['task_states']['DONE']}")
print(f"In progress: {summary['task_states']['DOING']}")
print(f"Scheduled: {summary['scheduled_tasks']}")
print(f"With deadlines: {summary['tasks_with_deadline']}")

# Task state breakdown
for state, count in summary['task_states'].items():
    if count > 0:
        print(f"{state}: {count} tasks")
```

## 💻 Advanced Content Types

### Code Blocks

Automatic language detection and filtering:

```python
# Find all code blocks
all_code = client.query().blocks().is_code_block().execute()

# Filter by language
python_code = client.query().blocks().is_code_block("python").execute()
js_code = client.query().blocks().is_code_block("javascript").execute()

# Analyze code distribution
languages = {}
for block in all_code:
    lang = block.code_language or 'unknown'
    languages[lang] = languages.get(lang, 0) + 1

print("📊 Code distribution:")
for lang, count in sorted(languages.items(), key=lambda x: x[1], reverse=True):
    print(f"  {lang}: {count} blocks")
```

### Mathematics & LaTeX

Parse and work with mathematical content:

```python
# Find all math content
math_blocks = client.query().blocks().has_math_content().execute()

for block in math_blocks:
    print(f"Math content: {block.latex_content}")
    
# Examples of supported formats:
# $$\\sum_{i=1}^{n} x_i$$
# \\(E = mc^2\\)
```

### Query Blocks

Support for Logseq's query system:

```python
# Find all query blocks
query_blocks = client.query().blocks().has_query().execute()

for block in query_blocks:
    if block.query:
        print(f"Query type: {block.query.query_type}")
        print(f"Query: {block.query.query_string}")
        
# Supported formats:
# {{query "search term"}}
# #+begin_query
# advanced query here
# #+end_query
```

### Headings & Structure

Hierarchical heading support:

```python
# Find all headings
all_headings = client.query().blocks().is_heading().execute()

# Filter by level
h1_headings = client.query().blocks().is_heading(1).execute()
h2_headings = client.query().blocks().is_heading(2).execute()

# Analyze heading structure
heading_levels = {}
for block in all_headings:
    level = block.heading_level
    heading_levels[level] = heading_levels.get(level, 0) + 1

print("📝 Heading distribution:")
for level in sorted(heading_levels.keys()):
    count = heading_levels[level]
    print(f"  H{level}: {count} headings")
```

## 🔗 Block Relationships

### Block References

Parse `((block-id))` references:

```python
# Find blocks with references
ref_blocks = client.query().blocks().has_block_references().execute()

for block in ref_blocks:
    refs = list(block.referenced_blocks)
    print(f"Block references: {refs}")
    print(f"Content: {block.content}")
```

### Block Embeds

Parse `{{embed ((block-id))}}` embeds:

```python
# Find blocks with embeds
embed_blocks = client.query().blocks().has_embeds().execute()

for block in embed_blocks:
    for embed in block.embedded_blocks:
        print(f"Embed type: {embed.embed_type}")
        print(f"Target: {embed.block_id}")
```

## 🗂️ Organization Features

### Namespaces

Hierarchical page organization:

```python
# Get all namespaces
namespaces = client.graph.get_all_namespaces()
print(f"📁 Found {len(namespaces)} namespaces")

for namespace in namespaces:
    pages = client.graph.get_pages_by_namespace(namespace)
    print(f"  {namespace}/: {len(pages)} pages")

# Query by namespace
project_pages = client.query().pages().in_namespace("project").execute()
frontend_pages = client.query().pages().in_namespace("frontend").execute()
```

### Templates

Template system with variable parsing:

```python
# Find template pages
templates = client.query().pages().is_template().execute()

for page in templates:
    for template in page.templates:
        print(f"Template: {template.name}")
        print(f"Variables: {template.variables}")
        print(f"Usage count: {template.usage_count}")

# Get specific template
template = client.graph.get_template("Daily Template")
if template:
    print(f"Variables: {template.variables}")
```

### Aliases

Page alias system:

```python
# Find pages with aliases
aliased_pages = client.query().pages().custom_filter(
    lambda p: len(p.aliases) > 0
).execute()

for page in aliased_pages:
    print(f"Page: {page.name}")
    print(f"Aliases: {list(page.aliases)}")

# Find page by alias
page = client.graph.get_page_by_alias("alias-name")
if page:
    print(f"Found page: {page.name}")
```

### Whiteboards

Visual thinking support:

```python
# Find whiteboard pages
whiteboards = client.query().pages().is_whiteboard().execute()

print(f"🎨 Found {len(whiteboards)} whiteboards")

for whiteboard in whiteboards:
    print(f"Whiteboard: {whiteboard.name}")
    if whiteboard.whiteboard_elements:
        print(f"Elements: {len(whiteboard.whiteboard_elements)}")
```

## 📊 Graph Analytics

### Connection Analysis

Find the most connected content:

```python
insights = client.graph.get_graph_insights()

# Most connected pages
print("🔗 Most connected pages:")
for page_name, connections in insights['most_connected_pages'][:10]:
    print(f"  {page_name}: {connections} backlinks")

# Most used tags
print("\n🏷️ Most used tags:")
for tag, usage in insights['most_used_tags'][:15]:
    print(f"  #{tag}: {usage} pages")
```

### Content Distribution

Analyze your knowledge graph:

```python
stats = client.graph.get_statistics()

print("📊 Graph Overview:")
print(f"  Pages: {stats['total_pages']}")
print(f"  Blocks: {stats['total_blocks']}")
print(f"  Namespaces: {stats['namespaces']}")
print(f"  Templates: {stats['templates']}")
print(f"  Whiteboards: {stats['whiteboards']}")
print(f"  Task blocks: {stats['task_blocks']}")
print(f"  Code blocks: {stats['code_blocks']}")
print(f"  Query blocks: {stats['query_blocks']}")
```

### Productivity Metrics

Track your productivity:

```python
# Calculate task completion rate
all_tasks = client.query().blocks().is_task().execute()
completed_tasks = client.query().blocks().is_completed_task().execute()

if all_tasks:
    completion_rate = len(completed_tasks) / len(all_tasks) * 100
    print(f"📈 Task completion rate: {completion_rate:.1f}%")

# Recent activity
from datetime import date, timedelta

week_ago = date.today() - timedelta(days=7)
recent_tasks = client.query().blocks().is_task().created_after(week_ago).execute()

print(f"📋 New tasks this week: {len(recent_tasks)}")
```

## 🔍 Advanced Query Patterns

### Complex Filtering

Chain multiple conditions:

```python
# Overdue high-priority tasks
overdue_urgent = (client.query()
    .blocks()
    .is_task()
    .has_priority(Priority.A)
    .has_deadline()
    .custom_filter(lambda b: b.deadline.date < date.today())
    .sort_by('deadline')
    .execute())

# Code blocks in project namespace
project_code = (client.query()
    .blocks()
    .is_code_block()
    .custom_filter(lambda b: 
        client.get_page(b.page_name).namespace == "project")
    .execute())

# Math content with references
linked_math = (client.query()
    .blocks()
    .has_math_content()
    .has_block_references()
    .execute())
```

### Statistical Queries

Analyze patterns in your data:

```python
from logseq_py.query import QueryStats

# Get all tagged blocks
tagged_blocks = client.query().blocks().custom_filter(
    lambda b: len(b.tags) > 0
).execute()

# Analyze tag frequency
tag_freq = QueryStats.tag_frequency(tagged_blocks)
print("Most common tags:")
for tag, count in list(tag_freq.items())[:10]:
    print(f"  #{tag}: {count} occurrences")

# Page distribution of tasks
task_blocks = client.query().blocks().is_task().execute()
page_dist = QueryStats.page_distribution(task_blocks)
print("\nPages with most tasks:")
for page, count in list(page_dist.items())[:10]:
    print(f"  {page}: {count} tasks")
```

## 🛠️ Workflow Automation

### Daily Reports

Generate daily productivity reports:

```python
def daily_report():
    today = date.today()
    
    # Today's scheduled tasks
    today_tasks = client.query().blocks().has_scheduled_date(today).execute()
    
    # Overdue tasks
    overdue = client.query().blocks().has_deadline().custom_filter(
        lambda b: b.deadline.date < today
    ).execute()
    
    # Recently completed
    completed_today = client.query().blocks().is_completed_task().updated_after(today).execute()
    
    print(f"📅 Daily Report - {today}")
    print(f"  Scheduled today: {len(today_tasks)}")
    print(f"  Overdue: {len(overdue)}")
    print(f"  Completed today: {len(completed_today)}")
    
    return {
        'scheduled': today_tasks,
        'overdue': overdue,
        'completed': completed_today
    }
```

### Project Analysis

Analyze project progress:

```python
def analyze_project(project_name):
    # Get project namespace pages
    project_pages = client.query().pages().in_namespace(project_name).execute()
    
    # Collect all project tasks
    project_tasks = []
    for page in project_pages:
        tasks = page.get_task_blocks()
        project_tasks.extend(tasks)
    
    # Analyze task distribution
    task_states = {}
    for task in project_tasks:
        state = task.task_state.value if task.task_state else 'NO_STATE'
        task_states[state] = task_states.get(state, 0) + 1
    
    print(f"📊 Project: {project_name}")
    print(f"  Pages: {len(project_pages)}")
    print(f"  Total tasks: {len(project_tasks)}")
    
    for state, count in task_states.items():
        print(f"  {state}: {count}")
    
    return {
        'pages': project_pages,
        'tasks': project_tasks,
        'states': task_states
    }
```

## 🎨 Advanced Use Cases

### Academic Research

Track research progress:

```python
# Find all papers and citations
papers = client.query().pages().has_tag("paper").execute()
citations = client.query().blocks().content_matches(r'@\w+').execute()

# Math-heavy pages
math_pages = client.query().pages().custom_filter(
    lambda p: len(p.get_math_blocks()) > 0
).execute()

print(f"📚 Research Summary:")
print(f"  Papers: {len(papers)}")
print(f"  Citations: {len(citations)}")
print(f"  Math-heavy pages: {len(math_pages)}")
```

### Software Development

Code documentation analysis:

```python
# Code blocks by language
code_blocks = client.query().blocks().is_code_block().execute()
languages = {}
for block in code_blocks:
    lang = block.code_language or 'unknown'
    languages[lang] = languages.get(lang, 0) + 1

# Documentation coverage
docs_pages = client.query().pages().in_namespace("docs").execute()
api_pages = client.query().pages().has_tag("api").execute()

print(f"💻 Development Summary:")
print(f"  Code blocks: {len(code_blocks)}")
print(f"  Languages: {len(languages)}")
print(f"  Documentation pages: {len(docs_pages)}")
print(f"  API documentation: {len(api_pages)}")
```

This advanced features guide showcases the comprehensive capabilities of the Logseq Python library. With these features, you can build sophisticated knowledge management workflows, automate productivity tracking, and create powerful analysis tools for your Logseq data.