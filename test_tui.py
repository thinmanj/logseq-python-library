#!/usr/bin/env python3
"""
Test script for Logseq TUI.

Usage:
    python test_tui.py [graph_path]
    
If no graph_path is provided, uses the Test graph by default.
"""

import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

def main():
    """Launch the TUI with the specified or default graph."""
    
    # Get graph path from command line or use default
    if len(sys.argv) > 1:
        graph_path = Path(sys.argv[1])
    else:
        # Default to Test graph
        graph_path = Path.home() / "Documents" / "Logseq" / "Test"
        
        # If that doesn't exist, look for environment variable
        if not graph_path.exists():
            env_graph = os.environ.get("LOGSEQ_GRAPH_PATH")
            if env_graph:
                graph_path = Path(env_graph)
            else:
                print(f"Error: Default graph not found at {graph_path}")
                print(f"Usage: {sys.argv[0]} <graph_path>")
                print(f"Or set LOGSEQ_GRAPH_PATH environment variable")
                sys.exit(1)
    
    # Verify graph exists
    if not graph_path.exists():
        print(f"Error: Graph path does not exist: {graph_path}")
        sys.exit(1)
    
    if not graph_path.is_dir():
        print(f"Error: Graph path is not a directory: {graph_path}")
        sys.exit(1)
    
    print(f"Launching Logseq TUI for graph: {graph_path}")
    print("Loading...")
    print()
    print("Keyboard shortcuts:")
    print("  Ctrl+J - Journals view")
    print("  Ctrl+P - Pages view")
    print("  Ctrl+T - Templates view")
    print("  Ctrl+F - Search")
    print("  Ctrl+S - Save")
    print("  q      - Quit")
    print()
    
    # Import and launch TUI
    try:
        from logseq_py.tui import launch_tui
        launch_tui(str(graph_path))
    except ImportError as e:
        print(f"Error: Missing dependency - {e}")
        print()
        print("Install TUI dependencies with:")
        print("  pip install textual")
        sys.exit(1)
    except Exception as e:
        print(f"Error launching TUI: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
