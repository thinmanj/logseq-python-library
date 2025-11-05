# Logseq-Python Warp Workflows - Quick Reference

## 🚀 Access Workflows
- **Command Palette**: `Cmd+P` → type "Logseq"
- **Workflow Menu**: Click workflows icon (top-right)

## 📋 Available Workflows

| Workflow | Description | Use Case |
|----------|-------------|----------|
| **Daily Task Summary** 📊 | Count tasks by state, show completion rate | Morning routine check-in |
| **Extract Content** 🔗 | Process URLs (YouTube, Twitter, PDFs) | Enrich notes with metadata |
| **Graph Insights** 🔍 | Analyze graph structure and connections | Understand knowledge patterns |
| **Code Statistics** 💻 | Language distribution in code blocks | Track learning/projects |
| **Create Daily Template** 📅 | Generate structured journal entry | Start new day with template |
| **High Priority Tasks** 🚨 | List all [#A] priority items | Focus on urgent work |
| **Backup Metadata** 💾 | Export graph structure to JSON | Regular backups |

## ⚡ Quick Commands

### From Terminal (in graph directory)
```bash
# Task summary
python3 -c "from logseq_py import LogseqClient; client = LogseqClient('.'); print(client.graph.get_workflow_summary())"

# Graph stats
python3 -c "from logseq_py import LogseqClient; client = LogseqClient('.'); print(client.graph.get_graph_insights())"
```

### Set Graph Environment Variable
```bash
# Add to ~/.zshrc
export LOGSEQ_GRAPH="/path/to/your/graph"
```

## 🎯 Common Use Cases

### Morning Routine
1. **Daily Task Summary** - Check what's pending
2. **High Priority Tasks** - Focus on urgent items
3. **Create Daily Template** - Start fresh journal entry

### Weekly Review
1. **Graph Insights** - See knowledge growth
2. **Code Statistics** - Track learning progress
3. **Backup Metadata** - Save snapshot

### Content Enrichment
1. **Extract Content** - Process pasted URLs
2. Run with `max_blocks=50` for quick batch
3. Review enhanced blocks in Logseq

## ⚙️ Customization

### Modify Workflow
Edit `.warp/workflows/logseq-automation.yaml` in your graph directory.

### Example: Change Daily Template
```yaml
- name: "Logseq: Create Daily Template"
  command: |
    python3 << 'EOF'
    from logseq_py import LogseqClient
    client = LogseqClient('.')
    
    # Your custom template
    template = """## My Custom Template
    - TODO First task
    - Goals: """
    
    client.add_journal_entry(template)
    EOF
```

## 🔧 Troubleshooting

| Issue | Solution |
|-------|----------|
| Workflows not showing | Check `.warp/workflows/` exists, restart Warp |
| Import errors | Run `pip install logseq-py` or set `PYTHONPATH` |
| Rate limiting (YouTube) | Use async processor, smaller batches |
| Wrong graph directory | Run workflows from graph root or set `LOGSEQ_GRAPH` |

## 📚 More Info

- [Full Integration Guide](../WARP_INTEGRATION.md)
- [Main README](../README.md)
- [Async Processing Guide](../ASYNC_RATE_LIMIT_HANDLING.md)

---

**Tip**: Use `Cmd+P` frequently to quickly access workflows without leaving your terminal context!
