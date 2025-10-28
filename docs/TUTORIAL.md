# Logseq Python: Library, Pipeline, TUI, and ETL Tutorial

This tutorial walks you through practical ways to use the library (LogseqClient), the processing pipelines (sync and async), the TUI, and how to build automated ETL scripts to extract, transform, and load data from your Logseq graph.

Sections:
- 1) Library Quickstart (LogseqClient)
- 2) Pipelines (sync CLI and async processor)
- 3) TUI (Terminal User Interface)
- 4) ETL Automation (scripts to export, report, and publish)
- 5) Innovative ideas and recipes

---

## 1) Library Quickstart (LogseqClient)

Install the core library (if you haven’t yet):

```bash
pip install logseq-python
```

Basic usage to load a graph and read/update pages:

```python path=null start=null
from pathlib import Path
from logseq_py.logseq_client import LogseqClient

GRAPH = "/path/to/your/logseq/graph"

with LogseqClient(GRAPH) as client:
    graph = client.load_graph()

    # Get a page
    page = client.get_page("Quick Notes")
    if page:
        print("Blocks:")
        for b in page.blocks[:5]:
            print("-", b.content)

    # Create or update a page
    report_md = """
- Weekly Review
  - Wins: Great progress on the TUI
  - Risks: None
  - Next: Add template application
"""
    client.create_page("Weekly Review", report_md)

    # Add a journal entry (today by default)
    client.add_journal_entry("- TUI tutorial created and documented")

    # Search across blocks
    matches = client.search("TUI")
    for page_name, blocks in matches.items():
        print(page_name, len(blocks))
```

Notes:
- Pages are written as Markdown in your graph folder.
- Use `client.export_to_json(path)` to export a JSON snapshot of your graph.

---

## 2) Pipelines

The library includes a flexible processing framework (extractors, analyzers, generators).

### 2.1 Sync pipeline via CLI

Install CLI extras:

```bash
pip install "logseq-python[cli]"
```

Run pipeline:

```bash
logseq pipeline run /path/to/graph \
  --extractors youtube twitter url \
  --analyzers sentiment topics summary \
  --generators summary_page insights_blocks \
  --output ./pipeline_output
```

- `extractors`: external content handling (e.g. YouTube, Twitter, PDFs).
- `analyzers`: NLP/text analysis.
- `generators`: produce new blocks/pages (e.g., summaries).

List pipeline templates:

```bash
logseq pipeline templates --list-templates
```

Get graph info:

```bash
logseq pipeline info /path/to/graph -o graph_info.json
```

### 2.2 Async comprehensive processor

For large graphs and rate limit resilience, use the async processor script:

```bash
python run_async_processor.py /path/to/graph
```

Features:
- Concurrency & rate-limit handling
- Queue-based processing
- Topic index page generation
- Streaming/batch modes

See examples in `examples/async_cached_pipeline.py` and `scripts/comprehensive_processor_cli.py`.

---

## 3) TUI (Terminal User Interface)

Install TUI extra:

```bash
pip install "logseq-python[tui]"
```

Launch TUI with CLI:

```bash
logseq tui /path/to/graph
```

Or run the included demo/test:

```bash
python demo_tui.py
# or
python test_tui.py /path/to/graph
```

Highlights:
- Journals: date navigation + editor
- Pages: namespace tree + editor
- Templates: create/edit (variables detected)
- Search: full-text search in blocks

Shortcuts: Ctrl+J/P/T/F, Ctrl+S, q, j/k

See full docs: `docs/TUI.md` and `TUI_VISUAL_DEMO.md`.

---

## 4) ETL Automation

This section shows how to build automated scripts to:
- Export snapshots (JSON/CSV)
- Generate reports (Markdown) and publish as pages
- Create PDFs (via Pandoc if available)
- Apply templates programmatically

We provide a ready-made CLI script: `scripts/etl_examples.py`.

Install CLI extras (for Click):

```bash
pip install "logseq-python[cli]"
```

Usage examples:

```bash
# 4.1 Export entire graph to JSON
python scripts/etl_examples.py export-json /path/to/graph --out graph.json

# 4.2 Export tasks across graph to CSV
python scripts/etl_examples.py tasks-csv /path/to/graph --out tasks.csv

# 4.3 Generate a weekly review Markdown and also create/update a page
python scripts/etl_examples.py weekly-report /path/to/graph \
  --start 2025-10-20 --end 2025-10-26 \
  --out weekly_2025-10-26.md \
  --page "Weekly Review 2025-10-26"

# 4.4 Convert Markdown to PDF (requires pandoc installed)
python scripts/etl_examples.py to-pdf weekly_2025-10-26.md --out weekly_2025-10-26.pdf

# 4.5 Apply a template to a target page with variable substitutions
python scripts/etl_examples.py apply-template /path/to/graph \
  --template "template/Meeting Notes" \
  --page "Meetings/2025-10-28" \
  --var topic="TUI Launch" --var attendee1="Alex" --var attendee2="Riley"

# 4.6 Topic report (collect top tags/topics and publish to page + md)
python scripts/etl_examples.py topic-report /path/to/graph \
  --out topics.md --page "Topic Index"
```

What these do:
- `export-json`: snapshot of graph pages/blocks
- `tasks-csv`: extract tasks (TODO/DOING/DONE) into CSV
- `weekly-report`: aggregated report for a date range (journals + tasks)
- `to-pdf`: converts any Markdown file to PDF (via Pandoc)
- `apply-template`: variable substitution from a template page into a target page
- `topic-report`: builds an index of tags/topics (simple), writes Markdown + optional page

All operations are safe and operate directly on your Markdown files.

---

## 5) Innovative ideas and recipes

Here are additional patterns you can adopt/adapt:

- Meeting pipelines: automatically collect all “Meeting” pages in a date range, extract decisions and action items, and generate a single-page Brief + PDF.
- Research digest: run the pipeline on YouTube/Twitter/PDF URLs you’ve clipped, summarize findings, and publish a curated digest page weekly.
- Personal CRM: extract people-tagged pages (e.g., `#person`), roll up last-contact dates from journals, and produce a follow-up plan page.
- Learning tracker: collect all pages tagged `#learning`, list progress and top topics, and export a PDF progress report monthly.
- OKR rollups: aggregate blocks tagged `#okr` and compute progress per objective with links to supporting notes.

Combine the TUI (fast edits), the pipeline (heavy lifting), and ETL scripts (automation) to build a robust personal knowledge ops system.

---

## Troubleshooting & Tips

- Keep Logseq desktop closed during ETL runs to avoid file lock conflicts.
- Use git to version-control your graph for safe experimentation and diffs.
- For Pandoc PDF export, install Pandoc: https://pandoc.org/installing.html
- For large graphs, prefer the async processor (`run_async_processor.py`).
- Templates are stored as pages with `template:: true`—you can manage them via TUI or ETL.

Happy building!