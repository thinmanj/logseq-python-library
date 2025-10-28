#!/usr/bin/env python3
"""
Demo script to showcase the Logseq TUI.
Runs in demo mode with a temporary graph.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from logseq_py.tui import launch_tui

def main():
    """Launch TUI with demo graph."""
    demo_graph = "/tmp/logseq-demo-graph"
    
    print("=" * 60)
    print("         LOGSEQ TUI DEMO")
    print("=" * 60)
    print()
    print(f"Demo graph location: {demo_graph}")
    print()
    print("FEATURES:")
    print("  📅 Journals  - Browse and edit daily journals")
    print("  📄 Pages     - View and edit all pages")
    print("  📋 Templates - Manage templates with variables")
    print("  🔍 Search    - Full-text search across graph")
    print()
    print("KEYBOARD SHORTCUTS:")
    print("  Ctrl+J - Switch to Journals")
    print("  Ctrl+P - Switch to Pages")
    print("  Ctrl+T - Switch to Templates")
    print("  Ctrl+F - Search")
    print("  Ctrl+S - Save current page")
    print("  j/k    - Navigate lists (vim-style)")
    print("  q      - Quit")
    print()
    print("=" * 60)
    print("Launching TUI in 2 seconds...")
    print("=" * 60)
    print()
    
    import time
    time.sleep(2)
    
    try:
        launch_tui(demo_graph)
    except KeyboardInterrupt:
        print("\n\nTUI closed by user.")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
