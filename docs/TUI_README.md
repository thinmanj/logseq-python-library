# Logseq TUI - Quick Start

The Logseq Python library now includes a powerful Terminal User Interface (TUI) for interacting with your Logseq graphs directly from the command line!

## Installation

```bash
pip install logseq-python[tui]
```

Or if you already have logseq-python installed:

```bash
pip install textual
```

## Quick Start

Launch the TUI:

```bash
logseq tui /path/to/your/graph
```

Or use the test script:

```bash
python test_tui.py /path/to/your/graph
```

## Features at a Glance

### 📅 Journals
- Navigate through daily journals with arrow buttons
- Edit journal entries with full markdown support
- Jump to today or any date quickly

### 📄 Pages
- Browse all pages in a tree view organized by namespace
- Search and filter pages
- Edit pages with markdown syntax highlighting
- Create new pages on the fly

### 📋 Templates
- View and manage all your templates
- Create new templates with variable substitution
- Edit existing templates
- Auto-detect template variables

### 🔍 Search
- Full-text search across all pages and blocks
- View results with context
- Navigate to matching pages

## Keyboard Shortcuts

Essential shortcuts to get started:

- **`Ctrl+J`** - Switch to Journals
- **`Ctrl+P`** - Switch to Pages  
- **`Ctrl+T`** - Switch to Templates
- **`Ctrl+F`** - Search
- **`Ctrl+S`** - Save current page
- **`q`** - Quit

Vim-style navigation:
- **`j`** / **`k`** - Move up/down in lists
- **`Enter`** - Select/open item

## Use Cases

### Daily Journaling
Perfect for maintaining your daily notes:
```bash
logseq tui ~/Documents/Logseq/Personal
# Press Ctrl+J, edit today's journal, Ctrl+S to save
```

### Quick Page Edits
Edit pages without opening Logseq desktop:
```bash
logseq tui ~/Documents/Logseq/Work
# Press Ctrl+P, select page, edit, Ctrl+S to save
```

### Template Management
Organize and edit your templates:
```bash
logseq tui ~/Documents/Logseq/Templates
# Press Ctrl+T, create/edit templates
```

### Content Search
Find information across your knowledge base:
```bash
logseq tui ~/Documents/Logseq/Research
# Press Ctrl+F, search for keywords
```

## Why Use the TUI?

✅ **Fast**: Launch instantly without waiting for desktop app  
✅ **Lightweight**: Minimal resource usage  
✅ **Remote-friendly**: Works over SSH  
✅ **Keyboard-first**: Efficient navigation with shortcuts  
✅ **Scriptable**: Integrate into workflows and automation  
✅ **Safe**: Direct markdown editing with no sync conflicts  

## Example Workflow

```bash
# Morning routine: check yesterday's notes and start today
logseq tui ~/Documents/Logseq/Personal

# In the TUI:
# 1. Press Ctrl+J (Journals)
# 2. Click "◀ Prev" to review yesterday
# 3. Click "Today" to start today's entry
# 4. Write your thoughts
# 5. Press Ctrl+S to save
# 6. Press q to quit

# Quick page edit during the day
logseq tui ~/Documents/Logseq/Work
# Ctrl+P → select page → edit → Ctrl+S → q

# Evening: review and organize with templates
logseq tui ~/Documents/Logseq/Personal
# Ctrl+T → review templates → create weekly review template
```

## Screenshots

```
┌─ Logseq TUI ─────────────────────────────────────────┐
│ Journals │ Pages │ Templates │ Search               │
├──────────────────────────────────────────────────────┤
│                                                      │
│  ◀ Prev    2025-10-28 (Monday)    Next ▶   Today    │
│                                                      │
│  📄 2025-10-28                                       │
│  ┌────────────────────────────────────────────────┐ │
│  │ - Morning review                               │ │
│  │   - Completed yesterday's tasks                │ │
│  │   - Started new project proposal               │ │
│  │                                                │ │
│  │ - Goals for today                              │ │
│  │   - [ ] Review PRs                             │ │
│  │   - [ ] Write documentation                    │ │
│  │   - [ ] Team meeting at 2pm                    │ │
│  └────────────────────────────────────────────────┘ │
│                                                      │
│          [Save]              [Cancel]                │
│                                                      │
├──────────────────────────────────────────────────────┤
│ q: Quit │ ^S: Save │ ^J: Journals │ ^P: Pages       │
└──────────────────────────────────────────────────────┘
```

## Full Documentation

For complete documentation, see [docs/TUI.md](docs/TUI.md)

Topics covered:
- Complete feature reference
- All keyboard shortcuts
- Template creation guide
- Search syntax
- Troubleshooting
- Advanced usage examples

## Requirements

- Python 3.8+
- textual >= 0.41.0
- logseq-python

## Platform Support

The TUI works on:
- ✅ macOS
- ✅ Linux
- ✅ Windows (Windows Terminal recommended)
- ✅ SSH sessions

## Coming Soon

Future enhancements planned:
- Template application to pages
- Block-level editing
- Task management view
- Graph visualization
- Custom themes
- Vim mode

## Feedback

Love the TUI? Have suggestions? [Open an issue](https://github.com/thinmanj/logseq-python-library/issues) or contribute!
