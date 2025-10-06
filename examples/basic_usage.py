#!/usr/bin/env python3
"""
Basic usage example for the Logseq Python library.

This example demonstrates how to:
1. Initialize the client
2. Load a graph
3. Perform basic queries
4. Create new content
"""

import sys
import os
from datetime import date, timedelta

# Add the parent directory to Python path so we can import logseq_py
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from logseq_py import LogseqClient


def main():
    # Replace with your actual Logseq graph path
    graph_path = "/path/to/your/logseq/graph"
    
    # Note: For this example to work, you need to provide a real Logseq graph path
    if not os.path.exists(graph_path):
        print(f"Graph path '{graph_path}' not found.")
        print("Please update the graph_path variable with your actual Logseq graph directory.")
        return
    
    print("🚀 Logseq Python Library - Basic Usage Example")
    print("=" * 50)
    
    # Initialize the client
    client = LogseqClient(graph_path)
    
    # Load the graph
    print("📚 Loading graph...")
    graph = client.load_graph()
    
    # Get basic statistics
    stats = client.get_statistics()
    print(f"📊 Graph Statistics:")
    print(f"   Total pages: {stats['total_pages']}")
    print(f"   Journal pages: {stats['journal_pages']}")
    print(f"   Regular pages: {stats['regular_pages']}")
    print(f"   Total blocks: {stats['total_blocks']}")
    print(f"   Unique tags: {stats['total_tags']}")
    print()
    
    # Search for content
    print("🔍 Searching for blocks containing 'python'...")
    python_blocks = client.search("python", case_sensitive=False)
    print(f"Found {len(python_blocks)} pages with blocks containing 'python':")
    for page_name, blocks in list(python_blocks.items())[:3]:  # Show first 3 results
        print(f"   📄 {page_name}: {len(blocks)} blocks")
        for block in blocks[:2]:  # Show first 2 blocks per page
            content_preview = block.content[:100] + "..." if len(block.content) > 100 else block.content
            print(f"      - {content_preview}")
    print()
    
    # Query with advanced filters
    print("🔎 Advanced Query: Pages with 'project' tag...")
    project_pages = client.query().pages().has_tag("project").execute()
    print(f"Found {len(project_pages)} pages with 'project' tag:")
    for page in project_pages[:5]:  # Show first 5
        print(f"   📄 {page.name}")
    print()
    
    # Query journal entries
    print("📅 Recent journal entries...")
    recent_journals = client.query().pages().is_journal().sort_by("journal_date", desc=True).limit(5).execute()
    print(f"Found {len(recent_journals)} recent journal entries:")
    for page in recent_journals:
        date_str = page.journal_date.strftime("%Y-%m-%d") if page.journal_date else "Unknown"
        print(f"   📅 {page.name} ({date_str}) - {len(page.blocks)} blocks")
    print()
    
    # Query blocks by level
    print("🔢 Top-level blocks (level 0)...")
    top_level_blocks = client.query().blocks().level(0).limit(10).execute()
    print(f"Found {len(top_level_blocks)} top-level blocks (showing first 10):")
    for block in top_level_blocks:
        content_preview = block.content[:80] + "..." if len(block.content) > 80 else block.content
        print(f"   - {content_preview} (in {block.page_name})")
    print()
    
    # Create new content (be careful - this will modify your graph!)
    print("✏️  Creating new content...")
    print("⚠️  WARNING: This will create new files in your Logseq graph!")
    response = input("Do you want to proceed? (y/N): ")
    
    if response.lower() == 'y':
        # Create a new page
        try:
            new_page = client.create_page(
                "Python Library Test", 
                "- This page was created by the Logseq Python library!\n- It demonstrates basic functionality\n\t- Creating pages\n\t- Adding blocks\n\t- Setting properties"
            )
            print(f"✅ Created new page: {new_page.name}")
            
            # Add a journal entry
            today = date.today()
            journal_page = client.add_journal_entry(
                f"Today I tested the Logseq Python library! It can read and write to my graph programmatically. #python #logseq"
            )
            print(f"✅ Added journal entry for {today}")
            
            # Add a block to the new page
            block = client.add_block_to_page(
                "Python Library Test",
                "This block was added after the page was created!"
            )
            print(f"✅ Added block to page: {block.content[:50]}...")
            
        except Exception as e:
            print(f"❌ Error creating content: {e}")
    else:
        print("🛑 Skipped content creation")
    
    print()
    print("🎉 Example completed successfully!")
    print("Check your Logseq graph to see any new content that was created.")


if __name__ == "__main__":
    main()