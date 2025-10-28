# Logseq Python: Complete Tutorial

🎉 **Your all-in-one guide to library usage, pipelines, TUI, and ETL automation**

## Quick Links

- [Installation](#installation)
- [Part 1: Library Basics](#part-1-library-basics-logseqclient)
- [Part 2: Processing Pipelines](#part-2-processing-pipelines)
- [Part 3: Terminal UI](#part-3-terminal-ui-tui)
- [Part 4: ETL & Automation](#part-4-etl--automation)
- [Part 5: Real-World Examples](#part-5-real-world-examples)

---

## Installation

```bash
# Core library
pip install logseq-python

# With all features
pip install "logseq-python[cli,tui,pipeline,ml]"

# Or individually
pip install "logseq-python[cli]"    # CLI tools
pip install "logseq-python[tui]"    # Terminal UI
pip install "logseq-python[pipeline]"  # Processing pipelines
pip install "logseq-python[ml]"     # ML/NLP features
```

---

## Part 1: Library Basics (LogseqClient)

### Quick Start

```python path=null start=null
from logseq_py.logseq_client import LogseqClient

# Context manager - auto-saves on exit
with LogseqClient("/path/to/graph") as client:
    # Read
    page = client.get_page("Quick Notes")
    print(page.blocks[0].content)
    
    # Write
    client.add_journal_entry("- TUI tutorial completed!")
    
    # Search
    results = client.search("TUI")
    print(f"Found in {len(results)} pages")
    
    # Create page
    client.create_page("Meeting Notes", """
- Attendees: Alice, Bob
- Date: 2025-10-28
- Topics:
  - Project kickoff
  - Timeline discussion
    """)
```

### Key Features

- **Pages**: Create, read, update, delete
- **Journals**: Daily entries with date navigation
- **Blocks**: Hierarchical content with properties
- **Tasks**: TODO/DOING/DONE with priorities
- **Search**: Full-text across all content
- **Export**: JSON snapshots

### Example: Task Dashboard

```python path=null start=null
with LogseqClient("/path/to/graph") as client:
    graph = client.load_graph()
    
    # Get all tasks
    tasks = graph.get_task_blocks()
    
    # By status
    todo = [t for t in tasks if t.task_state.value == "TODO"]
    doing = [t for t in tasks if t.task_state.value == "DOING"]
    done = [t for t in tasks if t.is_completed_task()]
    
    # By priority
    high = graph.get_blocks_by_priority(Priority.A)
    
    print(f"TODO: {len(todo)}, DOING: {len(doing)}, DONE: {len(done)}")
    print(f"High priority: {len(high)}")
```

---

## Part 2: Processing Pipelines

### CLI Pipelines

Extract, analyze, and generate content from your graph:

```bash
# Basic pipeline
logseq pipeline run /path/to/graph \
  --extractors youtube url pdf \
  --analyzers sentiment topics \
  --generators summary_page

# View templates
logseq pipeline templates --list-templates

# Graph info
logseq pipeline info /path/to/graph
```

### Async Processor (for large graphs)

```bash
# Process with concurrency & rate-limit handling
python run_async_processor.py /path/to/graph

# Generates:
# - Enhanced blocks with metadata
# - Topic pages
# - Content summaries
```

**Features:**
- Concurrent processing
- YouTube subtitle extraction
- Twitter/X post parsing
- PDF metadata extraction
- Topic detection & tagging
- Automatic rate-limit handling

### Custom Pipeline

```python path=null start=null
from logseq_py.pipeline import create_pipeline, ProcessingContext

# Build custom pipeline
context = ProcessingContext(graph_path="/path/to/graph")

pipeline = create_pipeline("my_pipeline", "Custom processing")
pipeline.step(LoadContentStep())
pipeline.step(FilterBlocksStep(lambda b: "important" in b.tags))
pipeline.step(AnalyzeContentStep(["sentiment", "topics"]))
pipeline.step(GenerateContentStep(["summary_page"]))

result = pipeline.build().execute(context)
print(f"Processed {result.processed_items} items")
```

---

## Part 3: Terminal UI (TUI)

### Launch TUI

```bash
# Via CLI
logseq tui /path/to/graph

# Or test script
python demo_tui.py
python test_tui.py /path/to/graph
```

### Features

**4 Main Views:**

1. **Journals** (Ctrl+J)
   - Navigate by date (Prev/Next/Today)
   - Edit daily entries
   - Markdown support

2. **Pages** (Ctrl+P)
   - Tree view (organized by namespace)
   - List view with search
   - Full editor

3. **Templates** (Ctrl+T)
   - Create/edit templates
   - Variable detection `{{variable}}`
   - Apply to pages

4. **Search** (Ctrl+F)
   - Full-text search
   - Results table
   - Quick navigation

### Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `Ctrl+J` | Journals |
| `Ctrl+P` | Pages |
| `Ctrl+T` | Templates |
| `Ctrl+F` | Search |
| `Ctrl+S` | Save |
| `Ctrl+N` | New page |
| `j`/`k` | Navigate (vim-style) |
| `q` | Quit |

### Use Cases

```bash
# Morning routine
logseq tui ~/Documents/Logseq/Personal
# Edit today's journal, review tasks

# Quick edit
logseq tui ~/Documents/Logseq/Work
# Ctrl+P → select page → edit → Ctrl+S → q

# Template management
logseq tui ~/Documents/Logseq/Templates
# Ctrl+T → create weekly review template
```

---

## Part 4: ETL & Automation

### ETL Script

All-in-one ETL tool: `scripts/etl_examples.py`

```bash
# 1. Export to JSON
python scripts/etl_examples.py export-json /path/to/graph \
  --out graph_backup.json

# 2. Export tasks to CSV
python scripts/etl_examples.py tasks-csv /path/to/graph \
  --out tasks.csv \
  --state TODO DOING

# 3. Weekly report
python scripts/etl_examples.py weekly-report /path/to/graph \
  --start 2025-10-20 --end 2025-10-26 \
  --out weekly.md \
  --page "Weekly Review 2025-10-26"

# 4. Convert to PDF
python scripts/etl_examples.py to-pdf weekly.md \
  --out weekly.pdf

# 5. Apply template
python scripts/etl_examples.py apply-template /path/to/graph \
  --template "template/Meeting Notes" \
  --page "Meeting 2025-10-28" \
  --var topic="Sprint Planning" \
  --var attendee1="Alice"

# 6. Topic index
python scripts/etl_examples.py topic-report /path/to/graph \
  --out topics.md \
  --page "Topic Index"

# 7. Graph stats
python scripts/etl_examples.py stats /path/to/graph
```

### Automation with Cron

```bash
# Edit crontab
crontab -e

# Daily brief (6 AM)
0 6 * * * cd /path/to/logseq-python && python3 daily_brief.py

# Weekly review (Sunday 8 PM)
0 20 * * 0 cd /path/to/logseq-python && python3 weekly_review.py

# Nightly backup (midnight)
0 0 * * * /path/to/backup_logseq.sh

# Task sync (every 4 hours)
0 */4 * * * python3 sync_tasks.py
```

---

## Part 5: Real-World Examples

### 1. Morning Brief Generator

```python path=null start=null
#!/usr/bin/env python3
"""Generate daily brief with tasks and schedule."""

from datetime import date
from logseq_py.logseq_client import LogseqClient

def morning_brief():
    with LogseqClient("/path/to/graph") as client:
        graph = client.load_graph()
        
        # Get today's tasks
        tasks = [t for t in graph.get_task_blocks() 
                if not t.is_completed_task()]
        
        # Get scheduled
        scheduled = graph.get_scheduled_blocks(date.today())
        
        # Build brief
        brief = f"# Daily Brief: {date.today()}\n\n"
        brief += f"## Tasks ({len(tasks)})\n"
        for task in tasks[:10]:
            brief += f"- {task.content}\n"
        
        brief += f"\n## Schedule ({len(scheduled)})\n"
        for item in scheduled:
            brief += f"- {item.content}\n"
        
        client.create_page(f"Daily Brief {date.today()}", brief)

if __name__ == "__main__":
    morning_brief()
```

### 2. Research Digest

```python path=null start=null
"""Collect research content weekly."""

def research_digest():
    with LogseqClient("/path/to/graph") as client:
        graph = client.load_graph()
        
        # Find research pages
        research = [p for p in graph.pages.values() 
                   if 'research' in p.tags or 'paper' in p.tags]
        
        # Extract URLs
        urls = []
        for page in research:
            for block in page.blocks:
                if 'http' in block.content:
                    urls.append((page.name, block.content))
        
        # Generate digest
        digest = "# Research Digest\n\n"
        for page_name, url in urls[:20]:
            digest += f"- [[{page_name}]]: {url}\n"
        
        client.create_page(f"Research Digest {date.today()}", digest)
```

### 3. Personal CRM

```python path=null start=null
"""Track when you last talked to people."""

import re
from datetime import date

def crm_tracker():
    with LogseqClient("/path/to/graph") as client:
        graph = client.load_graph()
        
        # Extract @mentions from journals
        people = {}
        for journal in graph.get_journal_pages():
            if not journal.journal_date:
                continue
            
            for block in journal.blocks:
                mentions = re.findall(r'@(\w+)', block.content)
                for person in mentions:
                    people[person] = journal.journal_date.date()
        
        # Find who to follow up with
        today = date.today()
        overdue = [(p, (today - d).days) for p, d in people.items() 
                  if (today - d).days > 30]
        
        # Generate report
        report = "# Follow-Up Tracker\n\n"
        for person, days in sorted(overdue, key=lambda x: x[1], reverse=True):
            report += f"- [[{person}]] - {days} days ago\n"
        
        client.create_page("Follow-Up Tracker", report)
```

### 4. Meeting Prep

```python path=null start=null
"""Prepare meeting page from template."""

from datetime import datetime

def prepare_meeting(topic, attendees):
    with LogseqClient("/path/to/graph") as client:
        # Get template
        template = client.get_page("template/Meeting Notes")
        content = template.to_markdown()
        
        # Substitute variables
        content = content.replace("{{topic}}", topic)
        content = content.replace("{{date}}", datetime.now().strftime("%Y-%m-%d"))
        
        for i, name in enumerate(attendees, 1):
            content = content.replace(f"{{{{attendee{i}}}}}", name)
        
        # Create page
        page_name = f"Meetings/{topic} - {datetime.now().strftime('%Y-%m-%d')}"
        client.create_page(page_name, content)
        print(f"✓ Created {page_name}")

# Usage
prepare_meeting("Sprint Planning", ["Alice", "Bob", "Charlie"])
```

### 5. Learning Tracker

```python path=null start=null
"""Track learning progress."""

def learning_tracker():
    with LogseqClient("/path/to/graph") as client:
        graph = client.load_graph()
        
        # Find learning pages
        learning = [p for p in graph.pages.values() if 'learning' in p.tags]
        
        # Categorize by status
        in_progress = [p for p in learning 
                      if 'progress' in p.properties.get('status', '').lower()]
        completed = [p for p in learning 
                    if 'complete' in p.properties.get('status', '').lower()]
        
        # Generate report
        report = "# Learning Progress\n\n"
        report += f"## In Progress ({len(in_progress)})\n"
        for page in in_progress:
            report += f"- [[{page.name}]]\n"
        
        report += f"\n## Completed ({len(completed)})\n"
        for page in completed:
            report += f"- ✓ [[{page.name}]]\n"
        
        client.create_page("Learning Progress", report)
```

---

## Combining All Components

### Complete Workflow Example

```bash
#!/bin/bash
# complete_workflow.sh - Daily automation workflow

GRAPH="$HOME/Documents/Logseq/Personal"

echo "=== Daily Logseq Workflow ==="

# 1. Generate morning brief
echo "Generating morning brief..."
python3 daily_brief.py

# 2. Process new content with pipeline
echo "Processing content..."
python3 run_async_processor.py "$GRAPH" --batch-size 50

# 3. Export tasks
echo "Exporting tasks..."
python3 scripts/etl_examples.py tasks-csv "$GRAPH" --out ~/tasks.csv

# 4. Update CRM tracker
echo "Updating CRM..."
python3 crm_tracker.py

# 5. Backup
echo "Creating backup..."
python3 scripts/etl_examples.py export-json "$GRAPH" --out ~/backups/graph-$(date +%Y%m%d).json

echo "✓ Workflow complete!"
```

---

## Best Practices

### 1. Safety

- **Close Logseq** before running ETL scripts
- **Use git** to version control your graph
- **Test scripts** on a copy first
- **Backup regularly** before automation

### 2. Performance

- Use **async processor** for large graphs (>500 pages)
- **Batch operations** when possible
- **Filter early** in pipelines
- **Limit results** in queries

### 3. Organization

- **Template everything** - meetings, reviews, briefs
- **Tag consistently** - use standard tags
- **Namespace pages** - project/page, area/topic
- **Properties for metadata** - status, priority, dates

### 4. Automation

- **Start simple** - one script at a time
- **Log everything** - redirect output to files
- **Monitor failures** - set up notifications
- **Iterate gradually** - add features over time

---

## Troubleshooting

### Common Issues

**1. Import errors**
```bash
pip install "logseq-python[cli,tui]"
```

**2. Graph not found**
```bash
ls /path/to/graph  # Verify path
```

**3. TUI won't start**
```bash
pip install textual
```

**4. PDF conversion fails**
```bash
# Install pandoc
brew install pandoc  # macOS
```

**5. Cron job doesn't run**
```bash
# Use absolute paths
which python3  # Get full path
```

---

## Next Steps

1. **Start with basics**: Load graph, read pages
2. **Try TUI**: Quick edits and navigation
3. **Run pipeline**: Process your content
4. **Create one ETL script**: e.g., daily brief
5. **Automate gradually**: Add cron jobs as needed
6. **Customize**: Adapt examples to your workflow

---

## Documentation

- **Tutorial**: `docs/TUTORIAL.md` - Step-by-step guide
- **TUI Guide**: `docs/TUI.md` - Complete TUI reference
- **TUI Demo**: `TUI_VISUAL_DEMO.md` - Visual walkthrough
- **ETL Examples**: `docs/ETL_EXAMPLES.md` - Practical automation
- **API Docs**: `docs/` - Full API documentation

---

## Support

- **Examples**: `examples/` directory
- **Scripts**: `scripts/` directory
- **Issues**: GitHub issues
- **Discussions**: GitHub discussions

Happy automating! 🚀
