#!/usr/bin/env python3
"""
IPython startup script for Logseq Python Library
This script sets up a convenient interactive environment for exploring the Logseq library.
"""

import os
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import print as rprint

# Import the main Logseq library components
from logseq_py import (
    LogseqClient, Block, Page, LogseqGraph,
    QueryBuilder, LogseqUtils, TaskState, Priority,
    BlockType, BlockEmbed, ScheduledDate, LogseqQuery,
    Template, Annotation, WhiteboardElement
)

console = Console()

def show_welcome():
    """Display a welcome message with library overview."""
    
    # Create a welcome panel
    welcome_text = """
[bold cyan]Welcome to Logseq Python Library Interactive Session![/bold cyan]

This library provides comprehensive access to Logseq knowledge graphs.
All main components have been imported and are ready to use.
    """
    
    console.print(Panel(welcome_text, title="🧠 Logseq Python Library", border_style="cyan"))
    
    # Create a table of available components
    table = Table(title="Available Components", show_header=True, header_style="bold magenta")
    table.add_column("Component", style="cyan", no_wrap=True)
    table.add_column("Description", style="white")
    
    components = [
        ("LogseqClient", "Main client for interacting with Logseq graphs"),
        ("Block", "Represents a Logseq block with content, metadata, and relationships"),
        ("Page", "Represents a Logseq page with blocks, properties, and metadata"),
        ("LogseqGraph", "Represents an entire Logseq graph with advanced operations"),
        ("QueryBuilder", "Fluent interface for building complex Logseq queries"),
        ("LogseqUtils", "Utility functions for parsing, formatting, and data manipulation"),
        ("TaskState", "Enum for task states (TODO, DOING, DONE, etc.)"),
        ("Priority", "Enum for task priorities (A, B, C)"),
        ("BlockType", "Enum for different block types"),
        ("Template", "Represents Logseq templates"),
        ("Annotation", "Represents PDF and other annotations"),
        ("WhiteboardElement", "Represents whiteboard/drawing elements")
    ]
    
    for component, description in components:
        table.add_row(component, description)
    
    console.print(table)

def show_examples():
    """Display some quick examples to get started."""
    
    examples_text = """
[bold yellow]Quick Examples:[/bold yellow]

[cyan]# Connect to a Logseq graph[/cyan]
[white]client = LogseqClient('/path/to/your/logseq/graph')[/white]
[white]graph = client.load_graph()[/white]

[cyan]# Search for pages and blocks[/cyan]
[white]pages = graph.search_pages('project')[/white]
[white]blocks = graph.search_blocks('TODO')[/white]

[cyan]# Query with advanced filters[/cyan]
[white]query = QueryBuilder().blocks().with_content('meeting').with_task_state(TaskState.TODO)[/white]
[white]results = graph.query(query)[/white]

[cyan]# Work with individual blocks[/cyan]
[white]block = Block(content='This is a new block #tag')[/white]
[white]block.properties['priority'] = Priority.A[/white]
[white]block.task_state = TaskState.DOING[/white]

[cyan]# Access help for any component[/cyan]
[white]help(LogseqClient)  # or any other component[/white]
    """
    
    console.print(Panel(examples_text, title="🚀 Quick Start Examples", border_style="yellow"))

def demo_sample_data():
    """Create some sample data to experiment with."""
    rprint("\n[bold green]Creating sample data for experimentation...[/bold green]")
    
    # Sample blocks using proper initialization
    sample_blocks = [
        Block(content="TODO Review the quarterly reports #work #urgent"),
        Block(content="DOING Research new frameworks for the project"),
        Block(content="Meeting notes from yesterday [[Daily Notes]]"),
        Block(content="```python\nprint('Hello Logseq!')\n```"),
        Block(content="$$ E = mc^2 $$")
    ]
    
    # Sample pages using proper initialization
    sample_pages = [
        Page(name="Project Planning", title="Project Planning"),
        Page(name="Daily Notes/2024-10-12", title="Daily Notes/2024-10-12"),
        Page(name="Research/AI Tools", title="Research/AI Tools")
    ]
    
    rprint("[green]✓ Created sample blocks and pages[/green]")
    rprint("[dim]Access them via: sample_blocks, sample_pages[/dim]")
    
    # Show sample content
    rprint("\n[bold cyan]Sample Blocks:[/bold cyan]")
    for i, block in enumerate(sample_blocks[:3], 1):
        rprint(f"[dim]{i}.[/dim] {block.content[:50]}{'...' if len(block.content) > 50 else ''}")
        if block.task_state:
            rprint(f"   [yellow]Task State: {block.task_state.value}[/yellow]")
        if block.tags:
            rprint(f"   [blue]Tags: {', '.join(block.tags)}[/blue]")
    
    return sample_blocks, sample_pages

def show_save_methods():
    """Display available methods for saving to filesystem."""
    save_text = """
[bold yellow]Saving Changes to Filesystem:[/bold yellow]

[cyan]# Save individual pages[/cyan]
[white]client._save_page(page)  # Save a specific page[/white]

[cyan]# Update existing blocks[/cyan]
[white]client.update_block(block_id, new_content)[/white]

[cyan]# Add new blocks to existing pages[/cyan]
[white]block = client.add_block_to_page('page_name', 'New block content')[/white]

[cyan]# Create new pages[/cyan]
[white]page = client.create_page('New Page Name', 'Initial content #tag')[/white]

[cyan]# Add journal entries (auto-saves)[/cyan]
[white]journal = client.add_journal_entry('Today I did something! #progress')[/white]

[cyan]# Delete blocks[/cyan]
[white]success = client.delete_block(block_id)[/white]

[cyan]# Save entire graph (helper function)[/cyan]
[white]save_graph(client)  # Save all modified pages[/white]
    """
    
    console.print(Panel(save_text, title="💾 Save to Filesystem", border_style="green"))

def show_context_manager_examples():
    """Display context manager usage examples."""
    context_text = """
[bold cyan]Context Manager Support:[/bold cyan]

[cyan]# Basic usage with auto-save[/cyan]
[white]with LogseqClient('/path/to/graph') as client:[/white]
[white]    client.add_journal_entry('Auto-saved on exit!')
    # Changes automatically saved when context exits[/white]

[cyan]# With backup protection[/cyan]
[white]with LogseqClient('/path', backup_on_enter=True) as client:[/white]
[white]    # Backup created automatically
    client.create_page('New Page', 'Content')
    # If exception occurs, can rollback to backup[/white]

[cyan]# Manual save control[/cyan]
[white]with LogseqClient('/path', auto_save=False) as client:[/white]
[white]    client.add_journal_entry('Changes tracked but not auto-saved')
    saved_count = client.save_all()  # Manual save
    # Can check session info: client.get_session_info()[/white]

[cyan]# Session information[/cyan]
[white]with LogseqClient('/path') as client:[/white]
[white]    info = client.get_session_info()
    # Shows: modified pages, duration, backup status, etc.[/white]
    """
    
    console.print(Panel(context_text, title="🎭 Context Manager Usage", border_style="magenta"))

def save_graph(client):
    """Helper function to save all pages in the graph."""
    if not client.graph:
        rprint("[red]No graph loaded. Load a graph first with client.load_graph()[/red]")
        return
    
    saved_count = 0
    for page in client.graph.pages.values():
        if page.file_path:  # Only save pages that have file paths
            client._save_page(page)
            saved_count += 1
    
    rprint(f"[green]✓ Saved {saved_count} pages to filesystem[/green]")

def quick_add_task(client, content, page_name=None):
    """Quick helper to add a task to today's journal or specified page."""
    if page_name:
        block = client.add_block_to_page(page_name, content)
    else:
        # Add to today's journal
        journal = client.add_journal_entry(content)
        block = journal.blocks[-1] if journal.blocks else None
    
    if block and block.is_task():
        rprint(f"[green]✓ Added task: {block.content}[/green]")
        rprint(f"[blue]Task state: {block.task_state.value if block.task_state else 'None'}[/blue]")
    else:
        rprint(f"[green]✓ Added content: {content}[/green]")
    
    return block

def preview_markdown(item):
    """Preview how a page or block will look in markdown format."""
    if hasattr(item, 'to_markdown'):
        markdown = item.to_markdown()
        rprint("\n[bold cyan]Markdown Preview:[/bold cyan]")
        rprint(f"[dim]{markdown}[/dim]")
        return markdown
    else:
        rprint("[red]Item doesn't have a to_markdown() method[/red]")
        return None

def quick_context_demo(graph_path):
    """Quick demo of context manager functionality."""
    rprint("\n[bold green]Quick Context Manager Demo:[/bold green]")
    
    try:
        with LogseqClient(graph_path) as client:
            rprint("[green]✓ Entered context manager[/green]")
            
            # Show session info
            session_info = client.get_session_info()
            rprint(f"[blue]Session started at: {session_info['session_start'].strftime('%H:%M:%S')}[/blue]")
            
            # Add a quick journal entry
            import datetime
            timestamp = datetime.datetime.now().strftime('%H:%M:%S')
            journal = client.add_journal_entry(
                f"Context manager demo at {timestamp} #context-manager #demo"
            )
            
            # Show what was modified
            session_info = client.get_session_info()
            rprint(f"[yellow]Modified pages: {session_info['modified_pages']}[/yellow]")
            
            rprint("[green]✓ Added journal entry - will auto-save on exit[/green]")
            
        rprint("[green]✓ Context exited - changes automatically saved![/green]")
        
    except Exception as e:
        rprint(f"[red]Demo failed: {e}[/red]")

# Set up the environment
if __name__ == "__main__":
    show_welcome()
    show_examples()
    show_save_methods()
    show_context_manager_examples()
    
    # Create sample data
    sample_blocks, sample_pages = demo_sample_data()
    
    console.print("\n[bold green]Environment ready! Start exploring the library.[/bold green]")
    console.print("[dim]Available helpers: show_welcome(), show_examples(), show_save_methods(), show_context_manager_examples()[/dim]")
    console.print("[dim]Quick demos: quick_context_demo('/path/to/graph'), help(component_name)[/dim]\n")
