#!/usr/bin/env python3
"""
Demo script showing how to push changes and updates to the Logseq filesystem.
Run this script to see various save operations in action.
"""

import sys
from pathlib import Path
from datetime import date, datetime
from logseq_py import LogseqClient, Block, Page, TaskState, Priority

def main():
    """Demonstrate various save operations."""
    
    # Connect to the Logseq graph
    graph_path = input("Enter path to your Logseq graph (or press Enter for '/Volumes/Projects/logseq'): ").strip()
    if not graph_path:
        graph_path = '/Volumes/Projects/logseq'
    
    try:
        client = LogseqClient(graph_path)
        graph = client.load_graph()
        print(f"✓ Connected to Logseq graph at: {graph_path}")
    except Exception as e:
        print(f"❌ Failed to connect to graph: {e}")
        return
    
    print(f"\n📊 Current graph stats: {graph.get_statistics()}")
    
    # Demo 1: Add a journal entry (auto-saves)
    print("\n🗓️  Demo 1: Adding journal entry...")
    journal_content = f"Demo: Testing Logseq Python save operations at {datetime.now().strftime('%H:%M:%S')} #demo #python"
    journal_page = client.add_journal_entry(journal_content)
    print(f"✓ Added journal entry to: {journal_page.file_path}")
    
    # Demo 2: Create a new page (auto-saves)
    print("\n📄 Demo 2: Creating new page...")
    page_name = f"Demo Page {datetime.now().strftime('%Y%m%d_%H%M%S')}"
    new_page = client.create_page(
        page_name, 
        "This is a demo page created by the Logseq Python library! #demo #created-by-python"
    )
    print(f"✓ Created new page: {new_page.file_path}")
    
    # Demo 3: Add blocks to existing page (auto-saves)
    print("\n🔲 Demo 3: Adding blocks to existing page...")
    block1 = client.add_block_to_page(page_name, "TODO First demo task #task #demo")
    block2 = client.add_block_to_page(page_name, "DOING Second demo task with [#A] priority")
    block3 = client.add_block_to_page(page_name, "```python\nprint('Hello from Logseq Python!')\n```")
    print(f"✓ Added {len([block1, block2, block3])} blocks to '{page_name}'")
    
    # Demo 4: Update existing block content (auto-saves)
    print("\n✏️  Demo 4: Updating block content...")
    original_content = block1.content
    updated_content = f"DONE {original_content.replace('TODO ', '')} (completed via Python API!)"
    client.update_block(block1.id, updated_content)
    print(f"✓ Updated block from: {original_content}")
    print(f"   to: {updated_content}")
    
    # Demo 5: Manual modifications with explicit save
    print("\n🔧 Demo 5: Manual modifications with explicit save...")
    
    # Create a new block manually and add it to a page
    manual_block = Block(content="This block was created and saved manually #manual #demo")
    new_page.add_block(manual_block)
    graph.blocks[manual_block.id] = manual_block
    
    # Save the page explicitly
    client._save_page(new_page)
    print(f"✓ Manually added block and saved page")
    
    # Demo 6: Batch operations
    print("\n📦 Demo 6: Batch modifications...")
    modified_pages = set()
    
    # Find all blocks with #demo tag and add completion timestamp
    for block in graph.blocks.values():
        if 'demo' in block.tags and 'timestamp' not in block.content:
            block.content += f" (processed at {datetime.now().strftime('%H:%M:%S')})"
            if block.page_name:
                modified_pages.add(block.page_name)
    
    # Save all modified pages
    for page_name in modified_pages:
        page = graph.get_page(page_name)
        if page:
            client._save_page(page)
    
    print(f"✓ Batch updated {len(modified_pages)} pages")
    
    # Demo 7: Create structured content
    print("\n🏗️  Demo 7: Creating structured content...")
    project_page = client.create_page("Demo Project Structure", "")
    
    # Add hierarchical blocks
    main_block = client.add_block_to_page("Demo Project Structure", "## Project Overview #project")
    sub_block1 = client.add_block_to_page("Demo Project Structure", "TODO Set up project structure")
    sub_block2 = client.add_block_to_page("Demo Project Structure", "DOING Research best practices")
    sub_block3 = client.add_block_to_page("Demo Project Structure", "### Resources")
    
    print(f"✓ Created structured project page with multiple sections")
    
    # Final stats
    print("\n📊 Final graph statistics:")
    final_stats = client.get_statistics()
    for key, value in final_stats.items():
        print(f"   {key}: {value}")
    
    print(f"\n✅ Demo completed! All changes have been saved to {graph_path}")
    print(f"💡 You can now check your Logseq app to see the changes!")
    
    # Show file locations
    print(f"\n📁 Files created/modified:")
    for page_name, page in graph.pages.items():
        if page.file_path and page.file_path.exists():
            # Check if file was modified recently (last 5 minutes)
            mtime = datetime.fromtimestamp(page.file_path.stat().st_mtime)
            if (datetime.now() - mtime).seconds < 300:
                print(f"   📝 {page.file_path}")

if __name__ == "__main__":
    main()