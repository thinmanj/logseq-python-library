#!/bin/bash
# Quick launcher for Personal Logseq graph TUI

GRAPH="/Volumes/Projects/logseq/Personal"

echo "=========================================="
echo "  Logseq TUI - Personal Graph"
echo "=========================================="
echo
echo "Graph: $GRAPH"
echo
echo "Loading TUI..."
echo
echo "Keyboard Shortcuts:"
echo "  Ctrl+J - Journals"
echo "  Ctrl+P - Pages"
echo "  Ctrl+T - Templates"
echo "  Ctrl+F - Search"
echo "  Ctrl+S - Save"
echo "  q      - Quit"
echo
echo "=========================================="
echo

# Launch TUI
cd /Volumes/Projects/logseq-python
python3 test_tui.py "$GRAPH"
