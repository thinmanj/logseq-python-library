# 🚀 Warp Integration Guide

**Seamlessly integrate logseq-python into your Warp terminal workflows**

This guide shows you how to leverage Warp's workflow system to automate your Logseq knowledge graph management directly from your terminal.

## 📋 Table of Contents

- [Quick Setup](#quick-setup)
- [Available Workflows](#available-workflows)
- [Custom Workflows](#custom-workflows)
- [Best Practices](#best-practices)
- [Advanced Usage](#advanced-usage)

---

## 🎯 Quick Setup

### 1. Install logseq-python

```bash
pip install logseq-py
```

### 2. Copy Workflow File

Copy `.warp/workflows/logseq-automation.yaml` to your Logseq graph directory:

```bash
cd /path/to/your/logseq/graph
mkdir -p .warp/workflows
cp /path/to/logseq-python/.warp/workflows/logseq-automation.yaml .warp/workflows/
```

### 3. Set Environment Variable (Optional)

For global access, add to your `~/.zshrc`:

```bash
export LOGSEQ_GRAPH="/path/to/your/logseq/graph"
```

### 4. Use in Warp

Open Warp in your Logseq graph directory and access workflows via:
- **Command Palette**: `Cmd+P` → type "Logseq"
- **Workflow Menu**: Top-right workflows icon

---

## 📦 Available Workflows

### 1. **Daily Task Summary** 📊

Get a quick overview of your tasks for today.

**What it does:**
- Counts TODO, DOING, and DONE tasks
- Calculates completion rate
- Shows workflow summary

**Usage:**
```bash
# Via Warp: Select "Logseq: Daily Task Summary"
# Or run directly:
cd /path/to/graph && python3 -c "from logseq_py import LogseqClient, TaskState; ..."
```

**Output:**
```
📊 Today's Task Summary

TODO: 12
DOING: 3
DONE: 8

✅ Completion Rate: 34.8%
```

---

### 2. **Extract Content** 🔗

Async extraction of video, Twitter, and PDF content from URLs in your graph.

**What it does:**
- Finds all URLs in blocks
- Extracts metadata (titles, authors, descriptions)
- Adds structured content back to graph
- Handles rate limiting intelligently

**Usage:**
```bash
# Via Warp: Select "Logseq: Extract Content"
# Processes up to 100 blocks by default
```

**Features:**
- YouTube video metadata + subtitles
- Twitter/X post content
- PDF previews
- Topic extraction
- Rate limit handling with retry

---

### 3. **Graph Insights** 🔍

Analyze your knowledge graph structure and connections.

**What it does:**
- Total pages and blocks count
- Most connected pages
- Tag usage statistics
- Namespace distribution

**Output:**
```
🔍 Graph Insights

📄 Total Pages: 342
🔗 Total Blocks: 5,621
🏷️  Total Tags: 87

📊 Top Connected Pages:
  Index: 142 connections
  Projects: 89 connections
  Resources: 76 connections

🏷️  Top Tags:
  #project: 234 uses
  #learning: 156 uses
  #reference: 98 uses
```

---

### 4. **Code Statistics** 💻

Analyze programming language usage in your graph.

**Output:**
```
💻 Code Statistics

Total code blocks: 387

python          ████████████████ 45
javascript      ████████████ 32
bash            ████████ 28
sql             ██████ 19
go              ████ 12
```

---

### 5. **Create Daily Template** 📅

Generate structured daily journal entries.

**Template:**
- Today's Goals
- Notes section
- Completed items
- Insights

**Customization:**
Edit the template in the workflow file to match your preferred structure.

---

### 6. **High Priority Tasks** 🚨

List all [#A] priority tasks across your graph.

**Features:**
- Shows task state (TODO/DOING)
- Displays deadlines
- Numbered list for easy reference

**Output:**
```
🚨 High Priority Tasks

1. [TODO] Complete project proposal 📅 2024-01-20
2. [DOING] Review PR #234
3. [TODO] Client meeting prep 📅 2024-01-18

Total: 3 tasks
```

---

### 7. **Backup Metadata** 💾

Export your graph structure to JSON for backup or analysis.

**Includes:**
- Timestamp
- Graph statistics
- All page names
- Namespace structure

**Output File:**
```
logseq_backup_20240115_143022.json
```

---

## 🛠️ Custom Workflows

### Create Your Own Workflow

Add to `.warp/workflows/logseq-automation.yaml`:

```yaml
- name: "Logseq: Your Custom Workflow"
  description: "What your workflow does"
  command: |
    python3 << 'EOF'
    from logseq_py import LogseqClient
    
    client = LogseqClient('.')
    graph = client.load_graph()
    
    # Your custom logic here
    pages = client.query().pages().has_tag("important").execute()
    print(f"Found {len(pages)} important pages")
    EOF
```

### Example: Weekly Review

```yaml
- name: "Logseq: Weekly Review"
  description: "Summarize last week's activity"
  command: |
    python3 << 'EOF'
    from logseq_py import LogseqClient, TaskState
    from datetime import datetime, timedelta
    
    client = LogseqClient('.')
    graph = client.load_graph()
    
    # Get last week's date range
    today = datetime.now()
    week_ago = today - timedelta(days=7)
    
    # Count completed tasks
    completed = client.query().blocks().has_task_state(TaskState.DONE).execute()
    
    # Filter by date (you'd need to add date filtering)
    print(f"📊 Weekly Review")
    print(f"Completed Tasks: {len(completed)}")
    
    # Add more analytics...
    EOF
```

---

## 🎯 Best Practices

### 1. **Run in Graph Directory**

Always execute workflows from your Logseq graph root:

```bash
cd /path/to/logseq/graph
# Then use Warp workflows
```

### 2. **Use Dry Run First**

For content extraction, test with dry run:

```python
processor = AsyncComprehensiveProcessor(
    graph_dir='.',
    dry_run=True,  # Won't modify files
    max_blocks=10   # Test with small batch
)
```

### 3. **Batch Processing**

For large graphs (>1000 pages), use batch parameters:

```python
processor = AsyncComprehensiveProcessor(
    graph_dir='.',
    batch_size=100,      # Process 100 blocks at a time
    batch_offset=0,      # Start from beginning
    max_blocks=500       # Limit total processing
)
```

### 4. **Scheduling**

Combine with cron or Warp's scheduling features:

```bash
# Run daily task summary every morning at 9am
0 9 * * * cd /path/to/graph && python3 -c "from logseq_py import ..."
```

---

## 🚀 Advanced Usage

### Chaining Workflows

Create a "mega workflow" that runs multiple operations:

```yaml
- name: "Logseq: Full Daily Routine"
  description: "Complete morning workflow"
  command: |
    python3 << 'EOF'
    from logseq_py import LogseqClient, TaskState
    import asyncio
    
    def main():
        client = LogseqClient('.')
        
        # 1. Create daily template
        client.add_journal_entry("## Morning Review\n- TODO Review tasks")
        
        # 2. Show task summary
        workflow = client.graph.get_workflow_summary()
        print(f"Tasks: {workflow['total_tasks']}")
        
        # 3. Extract new content
        # asyncio.run(extract_content())
    
    main()
    EOF
```

### Integration with Other Tools

Use logseq-python output in other commands:

```bash
# Export high-priority tasks to file
python3 << 'EOF' > urgent_tasks.txt
from logseq_py import LogseqClient, Priority
client = LogseqClient('.')
for task in client.query().blocks().has_priority(Priority.A).execute():
    print(task.content)
EOF

# Then use with other tools
cat urgent_tasks.txt | pbcopy  # Copy to clipboard
```

### API Integration

Combine with external APIs:

```python
from logseq_py import LogseqClient
import requests

client = LogseqClient('.')

# Get incomplete tasks
tasks = client.query().blocks().has_task_state(TaskState.TODO).execute()

# Send to external system
for task in tasks:
    requests.post('https://your-api.com/tasks', json={
        'content': task.content,
        'priority': task.priority.value if task.priority else None
    })
```

---

## 🔧 Troubleshooting

### Workflow Not Showing in Warp

1. Ensure `.warp/workflows/` directory exists in your graph
2. Check YAML syntax is valid
3. Restart Warp terminal
4. Verify you're in the graph directory

### Python Import Errors

```bash
# Ensure logseq-py is installed
pip show logseq-py

# Or use local development version
export PYTHONPATH="/path/to/logseq-python:$PYTHONPATH"
```

### Content Extraction Issues

- **Rate Limiting**: Use async processor with rate limit handling
- **Missing Content**: Check URL formats and network connectivity
- **Large Graphs**: Use batch processing with smaller chunks

---

## 📚 Additional Resources

- [Full Documentation](README.md)
- [Pipeline Guide](PIPELINE_GUIDE.md)
- [Async Processing](ASYNC_RATE_LIMIT_HANDLING.md)
- [Content Extraction](README_COMPREHENSIVE_PROCESSOR.md)
- [Builder System](BUILDER_DSL_SUMMARY.md)

---

## 🤝 Contributing

Have a useful workflow? Share it!

1. Add to `.warp/workflows/logseq-automation.yaml`
2. Test thoroughly
3. Submit PR with description

---

## 📝 License

MIT License - same as logseq-python library
