# 🐍 Logseq Python Library

**The most comprehensive Python library for Logseq knowledge graph interaction**

Transform your Logseq workflow with programmatic access to every major feature. From basic note-taking to advanced task management, academic research, and knowledge graph analytics - this library supports it all.

[![Python 3.8+](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](https://github.com/thinmanj/logseq-python-library/blob/main/LICENSE)
[![GitHub Stars](https://img.shields.io/github/stars/thinmanj/logseq-python-library.svg)](https://github.com/thinmanj/logseq-python-library/stargazers)

## ✨ **Comprehensive Feature Support**

### 🎯 **Task Management & Workflows**
- ✅ **Complete Task System**: TODO, DOING, DONE, LATER, NOW, WAITING, CANCELLED, DELEGATED, IN-PROGRESS
- ✅ **Priority Levels**: A, B, C with full parsing and filtering
- ✅ **Scheduling**: SCHEDULED dates with time and repeaters (+1w, +3d)
- ✅ **Deadlines**: DEADLINE tracking with overdue detection
- ✅ **Workflow Analytics**: Completion rates, productivity metrics

### 📝 **Advanced Content Types**
- ✅ **Code Blocks**: Language detection, syntax highlighting support
- ✅ **Mathematics**: LaTeX/Math parsing ($$math$$, \\(inline\\))
- ✅ **Queries**: {{query}} and #+begin_query support
- ✅ **Headings**: H1-H6 hierarchical structure
- ✅ **References**: ((block-id)) linking and {{embed}} support
- ✅ **Properties**: Advanced property parsing and querying

### 🗂️ **Organization & Structure**
- ✅ **Namespaces**: project/backend hierarchical organization
- ✅ **Templates**: Template variables {{variable}} parsing
- ✅ **Aliases**: Page alias system with [[link]] support
- ✅ **Whiteboards**: .whiteboard file detection
- ✅ **Hierarchies**: Parent/child page relationships

### 📊 **Knowledge Graph Analytics**
- ✅ **Graph Insights**: Connection analysis, relationship mapping
- ✅ **Content Statistics**: Block type distribution, tag usage
- ✅ **Productivity Metrics**: Task completion trends
- ✅ **Workflow Summaries**: Advanced task analytics

### 🔍 **Powerful Query System**
- ✅ **25+ Query Methods**: Task states, priorities, content types
- ✅ **Date Filtering**: Scheduled, deadline, creation date queries
- ✅ **Content Filtering**: Code language, math content, headings
- ✅ **Relationship Queries**: Block references, embeds, backlinks
- ✅ **Advanced Combinations**: Chain multiple filters fluently

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

## 🚀 **Quick Start**

### Basic Setup
```python
from logseq_py import LogseqClient, TaskState, Priority

# Initialize client with your Logseq graph directory
client = LogseqClient("/path/to/your/logseq/graph")
graph = client.load_graph()
```

### 📋 **Task Management**
```python
# Find all high-priority tasks
urgent_tasks = client.query().blocks().has_priority(Priority.A).execute()

# Get overdue tasks
from datetime import date
overdue = client.query().blocks().has_deadline().custom_filter(
    lambda block: block.deadline.date < date.today()
).execute()

# Find completed tasks
completed = client.query().blocks().has_task_state(TaskState.DONE).execute()

# Get workflow summary
workflow = client.graph.get_workflow_summary()
print(f"Completion rate: {workflow['completed_tasks']}/{workflow['total_tasks']}")
```

### 💻 **Code & Content Analysis**
```python
# Find all Python code blocks
python_code = client.query().blocks().is_code_block(language="python").execute()

# Get math/LaTeX content
math_blocks = client.query().blocks().has_math_content().execute()

# Find all headings
headings = client.query().blocks().is_heading().execute()

# Get blocks with references
linked_blocks = client.query().blocks().has_block_references().execute()
```

### 📊 **Advanced Analytics**
```python
# Get comprehensive graph insights
insights = client.graph.get_graph_insights()

# Analyze namespaces
for namespace in client.graph.get_all_namespaces():
    pages = client.graph.get_pages_by_namespace(namespace)
    print(f"{namespace}/: {len(pages)} pages")

# Find most connected pages
for page_name, connections in insights['most_connected_pages'][:5]:
    print(f"{page_name}: {connections} backlinks")
```

### ✍️ **Content Creation**
```python
# Add journal entry with task
client.add_journal_entry("TODO Review project documentation #urgent")

# Create a structured page
content = """# Project Planning
- TODO Set up initial framework [#A]
  SCHEDULED: <2024-01-15 Mon>
- Code review checklist
  - [ ] Security audit
  - [ ] Performance testing"""

client.create_page("Project Alpha", content)
```

## 🎯 **Real-World Use Cases**

### 📈 **Project Management**
- Track tasks across multiple projects with priorities and deadlines
- Generate productivity reports and completion metrics
- Automate workflow status updates and notifications
- Analyze team performance and bottlenecks

### 🔬 **Academic Research**
- Parse and analyze LaTeX mathematical content
- Extract and organize research notes with citations
- Track paper progress and review status
- Generate bibliographies and reference networks

### 💻 **Software Development**
- Document code examples with syntax highlighting
- Track bugs and feature requests with priority levels
- Organize documentation by namespace (frontend/backend)
- Generate code statistics and language usage reports

### 📚 **Knowledge Management**
- Build comprehensive knowledge graphs with relationships
- Track learning progress with spaced repetition
- Organize information hierarchically with namespaces
- Generate insights about information consumption patterns

### 🎨 **Creative Work**
- Organize creative projects with visual whiteboards
- Track inspiration and reference materials
- Manage creative workflows with custom task states
- Analyze creative output patterns and productivity

## 🛠️ **Advanced Examples**

### Task Automation
```python
# Find all overdue high-priority tasks and generate a report
from datetime import date, timedelta

overdue_urgent = (client.query()
    .blocks()
    .is_task()
    .has_priority(Priority.A)
    .has_deadline()
    .custom_filter(lambda b: b.deadline.date < date.today())
    .execute())

for task in overdue_urgent:
    days_overdue = (date.today() - task.deadline.date).days
    print(f"⚠️ OVERDUE {days_overdue} days: {task.content}")
```

### Content Analysis
```python
# Analyze your coding activity across languages
code_stats = {}
for block in client.query().blocks().is_code_block().execute():
    lang = block.code_language or 'unknown'
    code_stats[lang] = code_stats.get(lang, 0) + 1

print("📊 Code block distribution:")
for lang, count in sorted(code_stats.items(), key=lambda x: x[1], reverse=True):
    print(f"  {lang}: {count} blocks")
```

### Knowledge Graph Analysis
```python
# Find your most referenced pages (knowledge hubs)
page_refs = {}
for block in client.query().blocks().has_block_references().execute():
    for ref in block.referenced_blocks:
        page_refs[ref] = page_refs.get(ref, 0) + 1

print("🔗 Most referenced content:")
for ref, count in sorted(page_refs.items(), key=lambda x: x[1], reverse=True)[:10]:
    print(f"  {ref}: {count} references")
```

## 🚀 **Warp Terminal Integration**

**NEW!** Seamlessly integrate logseq-python into your Warp terminal workflows:

- ✅ **7 Pre-built Workflows**: Task summaries, graph insights, content extraction, code stats
- ✅ **One-Command Access**: `Cmd+P` → type "Logseq" to run any workflow
- ✅ **Customizable**: Easy YAML configuration for your own workflows
- ✅ **Powerful Automation**: Daily routines, batch processing, scheduled tasks

### Quick Setup
```bash
# Copy workflow file to your Logseq graph
cd /path/to/your/logseq/graph
mkdir -p .warp/workflows
cp /path/to/logseq-python/.warp/workflows/logseq-automation.yaml .warp/workflows/

# Use in Warp: Cmd+P → "Logseq: Daily Task Summary"
```

📚 **[Full Warp Integration Guide](WARP_INTEGRATION.md)**

---

## 📖 **Documentation**

- 📘 [Complete API Reference](docs/api.md) - Comprehensive API documentation
- 🚀 [Warp Integration Guide](WARP_INTEGRATION.md) - **NEW!** Terminal workflow automation
- 🎯 [Basic Usage Examples](examples/basic_usage.py) - Get started quickly
- 🔍 [Advanced Queries](examples/advanced_queries.py) - Complex search examples
- 🎨 [Advanced Features](examples/advanced_logseq_features.py) - All new features showcase
- 📤 [Data Export/Import](examples/data_export_import.py) - Backup and analysis
- 🧪 [Test Suite](tests/) - Comprehensive testing examples

## Requirements

- Python 3.8+
- Logseq graph (local directory)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

The MIT License is a permissive license that allows for commercial use, modification, distribution, and private use, with the only requirement being that the license and copyright notice must be included with any substantial portions of the software.
