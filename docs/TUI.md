# Logseq Terminal User Interface (TUI)

An interactive terminal-based interface for viewing and editing Logseq pages, journals, and templates.

## Features

- **Journal Navigation**: Browse and edit daily journal entries with date navigation
- **Page Management**: View, edit, and create pages with full markdown support
- **Template System**: Create, edit, and manage templates with variable substitution
- **Full-text Search**: Search across all pages and blocks
- **Keyboard Shortcuts**: Efficient navigation with vim-style keybindings
- **Live Updates**: Changes are saved directly to your Logseq graph

## Installation

The TUI requires the `textual` library:

```bash
pip install logseq-python[tui]
```

Or install textual separately:

```bash
pip install textual
```

## Usage

### Command Line

Launch the TUI using the CLI:

```bash
logseq tui /path/to/your/graph
```

Or use the test script:

```bash
python test_tui.py /path/to/your/graph
```

### Programmatic

Launch from Python code:

```python
from logseq_py.tui import launch_tui

launch_tui("/path/to/your/graph")
```

## Interface Overview

The TUI is organized into four main tabs:

### 1. Journals Tab (Ctrl+J)

Navigate and edit daily journal entries.

**Features:**
- Date navigation with Previous/Next buttons
- Quick jump to today
- Full markdown editor for journal content
- Automatic journal page creation for new dates

**Navigation:**
- `◀ Prev` - Go to previous day
- `Next ▶` - Go to next day  
- `Today` - Jump to today's journal
- `Ctrl+S` - Save current journal entry

### 2. Pages Tab (Ctrl+P)

Browse and edit regular Logseq pages.

**Features:**
- Sidebar with page tree (organized by namespaces)
- Page list with search
- Full markdown editor
- Support for all Logseq page types

**Navigation:**
- Click pages in sidebar or list to open
- `j/k` - Navigate page list (vim-style)
- `Enter` - Open selected page
- `Ctrl+S` - Save current page
- `Ctrl+N` - Create new page

### 3. Templates Tab (Ctrl+T)

Manage Logseq templates.

**Features:**
- List all templates in your graph
- Create new templates
- Edit existing templates
- Variable detection ({{variable}} syntax)
- Delete templates

**Template Format:**
```markdown
- Template content here
  - Use {{variable_name}} for placeholders
  - Use {{date}} for current date
  - Use {{time}} for current time
```

**Navigation:**
- Click template in list to edit
- `+ New Template` - Create a new template
- `Save Template` - Save changes
- `Delete Template` - Remove template

### 4. Search Tab (Ctrl+F)

Search across all pages and blocks.

**Features:**
- Full-text search
- Results table with page name, block content, and tags
- Search result count

**Usage:**
1. Type your search query
2. Press `Enter` to search
3. View results in the table

## Keyboard Shortcuts

### Global Shortcuts

| Key | Action |
|-----|--------|
| `q` | Quit application |
| `Ctrl+S` | Save current page/journal |
| `Ctrl+J` | Switch to Journals view |
| `Ctrl+P` | Switch to Pages view |
| `Ctrl+T` | Switch to Templates view |
| `Ctrl+F` | Switch to Search view |
| `Ctrl+N` | Create new page |

### Navigation Shortcuts

| Key | Action |
|-----|--------|
| `j` | Move down in lists (vim-style) |
| `k` | Move up in lists (vim-style) |
| `Enter` | Select/open item |
| `Tab` | Move between UI elements |
| `Shift+Tab` | Move backward between elements |

### Editor Shortcuts

Standard text editor shortcuts work in the markdown editor:
- `Ctrl+A` - Select all
- `Ctrl+C` - Copy
- `Ctrl+V` - Paste
- `Ctrl+X` - Cut
- `Ctrl+Z` - Undo
- `Ctrl+Y` - Redo

## Template Management

### Creating Templates

1. Switch to Templates tab (`Ctrl+T`)
2. Click `+ New Template`
3. Enter template name
4. Add template content with variables
5. Click `Save Template`

### Using Variables

Templates support variable substitution using `{{variable}}` syntax:

```markdown
- Meeting notes for {{topic}}
  - Date: {{date}}
  - Time: {{time}}
  - Attendees:
    - {{attendee1}}
    - {{attendee2}}
  - Notes:
    - {{notes}}
```

When the template is detected, all `{{variable}}` placeholders are identified and shown in the UI.

### Template Storage

Templates are stored as pages in your graph under the `template/` namespace with the `template:: true` property.

Example: A template named "Meeting Notes" is stored as `template/Meeting Notes.md`.

## Page Tree Organization

The sidebar shows pages organized by:

1. **Journals** - Most recent 10 journal entries
2. **Pages** - Regular pages grouped by namespace
   - **Namespaced pages** - Under folder icons (📁)
   - **Root pages** - Without namespace

Example structure:
```
📚 Logseq
├─ 📅 Journals
│  ├─ 2025-10-28
│  ├─ 2025-10-27
│  └─ ...
└─ 📄 Pages
   ├─ 📁 project
   │  ├─ project/backend
   │  └─ project/frontend
   ├─ 📋 template/Meeting Notes
   └─ 📄 Quick Notes
```

## Search Features

The search function finds matches across:
- Page names
- Block content
- Block properties
- Tags

Search is case-insensitive and searches all loaded pages.

## Tips and Best Practices

### Performance

- The TUI loads your entire graph on startup
- For large graphs (1000+ pages), initial load may take a few seconds
- Page tree is limited to first 50 pages for performance
- Journal list shows last 10 entries

### Editing

- Changes are saved directly to markdown files
- No auto-save - use `Ctrl+S` to save explicitly
- The editor supports full markdown syntax
- Properties are preserved when editing

### Templates

- Store reusable content as templates
- Use descriptive variable names
- Organize templates with the `template/` namespace
- Templates can include block structure and properties

### Navigation

- Use keyboard shortcuts for speed
- Tree view for quick access to frequent pages
- List view for browsing all pages
- Search for finding specific content

## Troubleshooting

### TUI won't start

Check that textual is installed:
```bash
pip install textual
```

### Graph not loading

Verify the graph path is correct and contains markdown files:
```bash
ls /path/to/your/graph
```

### Changes not saving

- Ensure you press `Ctrl+S` to save
- Check file permissions on graph directory
- Verify Logseq is not running (file locks)

### Display issues

If the TUI displays incorrectly:
- Ensure terminal supports Unicode
- Try resizing terminal window
- Use a modern terminal emulator (iTerm2, Alacritty, etc.)

## Advanced Usage

### Custom Graph Location

Set environment variable for default graph:

```bash
export LOGSEQ_GRAPH_PATH="/path/to/your/graph"
python test_tui.py
```

### Multiple Graphs

Launch TUI with different graphs:

```bash
logseq tui ~/Documents/Logseq/Work
logseq tui ~/Documents/Logseq/Personal
```

### Integration with Scripts

Use the TUI programmatically:

```python
from pathlib import Path
from logseq_py.tui import LogseqTUI

# Create TUI instance
app = LogseqTUI(Path("/path/to/graph"))

# Run the app
app.run()
```

## Related Features

- **Async Processor**: Process content in bulk - see [Async Processing](async_processing.md)
- **Builder System**: Construct complex content - see [Builders](builders.md)
- **CLI**: Command-line tools - see [CLI Reference](cli.md)

## Future Enhancements

Planned features for future versions:

- [ ] Template application to pages/journals
- [ ] Block-level editing
- [ ] Task management view
- [ ] Graph visualization
- [ ] Custom themes
- [ ] Plugin system
- [ ] Multi-graph workspace
- [ ] Vim mode
- [ ] Preview mode for markdown
- [ ] Diff view for changes

## Feedback

Found a bug or have a feature request? Please open an issue on GitHub.
