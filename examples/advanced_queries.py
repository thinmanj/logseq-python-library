#!/usr/bin/env python3
"""
Advanced queries example for the Logseq Python library.

This example demonstrates advanced query capabilities:
1. Complex filtering
2. Query statistics
3. Custom filters
4. Chained operations
"""

import sys
import os
import re
from datetime import date, datetime, timedelta

# Add the parent directory to Python path so we can import logseq_py
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from logseq_py import LogseqClient
from logseq_py.query import QueryStats


def main():
    # Replace with your actual Logseq graph path
    graph_path = "/path/to/your/logseq/graph"
    
    if not os.path.exists(graph_path):
        print(f"Graph path '{graph_path}' not found.")
        print("Please update the graph_path variable with your actual Logseq graph directory.")
        return
    
    print("🔍 Logseq Python Library - Advanced Queries Example")
    print("=" * 60)
    
    client = LogseqClient(graph_path)
    client.load_graph()
    
    print("1️⃣  Complex Content Filtering")
    print("-" * 30)
    
    # Find blocks with URLs
    url_blocks = client.query().content_matches(r'https?://[^\s]+').execute()
    print(f"📎 Found {len(url_blocks)} blocks containing URLs")
    
    # Show some examples
    for block in url_blocks[:3]:
        urls = re.findall(r'https?://[^\s]+', block.content)
        print(f"   📄 {block.page_name}: {urls[0]}")
    print()
    
    # Find blocks with code (surrounded by backticks)
    code_blocks = client.query().content_matches(r'`[^`]+`').execute()
    print(f"💻 Found {len(code_blocks)} blocks with inline code")
    
    # Find blocks with block references
    ref_blocks = client.query().content_matches(r'\(\([^)]+\)\)').execute()
    print(f"🔗 Found {len(ref_blocks)} blocks with block references")
    print()
    
    print("2️⃣  Tag-based Queries")
    print("-" * 30)
    
    # Find pages with multiple specific tags
    multi_tag_pages = client.query().pages().has_all_tags(["project", "active"]).execute()
    print(f"🏷️  Found {len(multi_tag_pages)} pages with both 'project' and 'active' tags")
    
    # Find blocks with any programming-related tags
    programming_tags = ["python", "javascript", "coding", "programming", "development"]
    programming_blocks = client.query().blocks().has_any_tag(programming_tags).execute()
    print(f"👨‍💻 Found {len(programming_blocks)} blocks with programming-related tags")
    print()
    
    print("3️⃣  Property-based Queries")
    print("-" * 30)
    
    # Find pages with specific properties
    todo_pages = client.query().pages().has_property("type", "todo").execute()
    print(f"✅ Found {len(todo_pages)} pages with type=todo")
    
    # Find blocks with any property
    property_blocks = client.query().blocks().custom_filter(
        lambda block: len(block.properties) > 0
    ).execute()
    print(f"⚙️  Found {len(property_blocks)} blocks with properties")
    print()
    
    print("4️⃣  Date-based Queries")
    print("-" * 30)
    
    # Find recent journal entries (last 7 days)
    week_ago = date.today() - timedelta(days=7)
    recent_journals = client.query().pages().is_journal().created_after(week_ago).execute()
    print(f"📅 Found {len(recent_journals)} journal entries from the last 7 days")
    
    # Find pages created in the last month
    month_ago = datetime.now() - timedelta(days=30)
    recent_pages = client.query().pages().created_after(month_ago).limit(10).execute()
    print(f"🆕 Found {len(recent_pages)} pages created in the last month")
    print()
    
    print("5️⃣  Structure-based Queries")
    print("-" * 30)
    
    # Find blocks with children (parent blocks)
    parent_blocks = client.query().blocks().has_children().limit(5).execute()
    print(f"👨‍👩‍👧‍👦 Found {len(parent_blocks)} blocks with children")
    
    for block in parent_blocks:
        print(f"   📄 {block.page_name}: '{block.content[:50]}...' ({len(block.children_ids)} children)")
    print()
    
    # Find deeply nested blocks (level 3 or higher)
    deep_blocks = client.query().blocks().min_level(3).limit(10).execute()
    print(f"🏗️  Found {len(deep_blocks)} deeply nested blocks (level 3+)")
    print()
    
    print("6️⃣  Custom Filters")
    print("-" * 30)
    
    # Find blocks with questions (containing "?")
    question_blocks = client.query().blocks().custom_filter(
        lambda block: "?" in block.content and len(block.content.strip()) > 10
    ).limit(5).execute()
    print(f"❓ Found {len(question_blocks)} blocks that seem to contain questions")
    
    for block in question_blocks:
        print(f"   📄 {block.page_name}: {block.content[:80]}...")
    print()
    
    # Find long blocks (more than 200 characters)
    long_blocks = client.query().blocks().custom_filter(
        lambda block: len(block.content) > 200
    ).sort_by("content", desc=True).limit(5).execute()
    print(f"📜 Found {len(long_blocks)} long blocks (>200 characters)")
    print()
    
    print("7️⃣  Query Statistics")
    print("-" * 30)
    
    # Get all blocks with tags
    tagged_blocks = client.query().blocks().custom_filter(
        lambda block: len(block.tags) > 0
    ).execute()
    
    if tagged_blocks:
        # Analyze tag frequency
        tag_freq = QueryStats.tag_frequency(tagged_blocks)
        print(f"🏷️  Tag frequency analysis (top 10 tags):")
        for tag, count in list(tag_freq.items())[:10]:
            print(f"   #{tag}: {count} occurrences")
        print()
        
        # Analyze page distribution
        page_dist = QueryStats.page_distribution(tagged_blocks)
        print(f"📄 Page distribution (top 5 pages with most tagged blocks):")
        for page_name, count in list(page_dist.items())[:5]:
            print(f"   {page_name}: {count} tagged blocks")
        print()
        
        # Analyze level distribution
        level_dist = QueryStats.level_distribution(tagged_blocks)
        print(f"🔢 Level distribution of tagged blocks:")
        for level, count in level_dist.items():
            indent = "  " * level
            print(f"   {indent}Level {level}: {count} blocks")
        print()
    
    print("8️⃣  Chained Complex Queries")
    print("-" * 30)
    
    # Complex query: Find top-level blocks in journal pages that contain links
    # and were created in the last 30 days
    complex_query = (client.query()
                    .blocks()
                    .level(0)  # Top-level blocks
                    .custom_filter(lambda block: 
                        # Block is in a journal page
                        client.get_page(block.page_name).is_journal if block.page_name else False
                    )
                    .custom_filter(lambda block: 
                        # Block contains links
                        len(block.get_links()) > 0
                    )
                    .created_after(month_ago)
                    .sort_by("content")
                    .limit(10))
    
    complex_results = complex_query.execute()
    print(f"🎯 Complex query result: {len(complex_results)} blocks")
    print("   (Top-level blocks in journal pages with links from last 30 days)")
    
    for block in complex_results:
        links = list(block.get_links())[:2]  # Show first 2 links
        print(f"   📄 {block.page_name}: {links}")
    print()
    
    print("🎉 Advanced queries example completed!")


if __name__ == "__main__":
    main()