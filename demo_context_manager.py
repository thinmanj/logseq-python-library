#!/usr/bin/env python3
"""
Demo script showing context manager capabilities of the Logseq Python library.
This demonstrates automatic session management, change tracking, and rollback features.
"""

import sys
from pathlib import Path
from datetime import datetime
from logseq_py import LogseqClient, Block, Page, TaskState, Priority

def demo_basic_context_manager():
    """Demo basic context manager usage with auto-save."""
    
    graph_path = input("Enter path to your Logseq graph (or press Enter for '/Volumes/Projects/logseq'): ").strip()
    if not graph_path:
        graph_path = '/Volumes/Projects/logseq'
    
    print("🔄 Demo 1: Basic Context Manager Usage")
    print("=" * 50)
    
    # Use context manager with auto-save (default)
    with LogseqClient(graph_path) as client:
        print(f"📊 Graph loaded. Stats: {client.get_statistics()}")
        
        # Add some content
        timestamp = datetime.now().strftime('%H:%M:%S')
        
        # Add journal entry
        journal = client.add_journal_entry(
            f"Context Manager Demo at {timestamp} #demo #context-manager"
        )
        print(f"✅ Added journal entry")
        
        # Create a new page
        page_name = f"Context Demo {datetime.now().strftime('%Y%m%d_%H%M%S')}"
        page = client.create_page(page_name, "")
        print(f"✅ Created page: {page_name}")
        
        # Add blocks
        task_block = client.add_block_to_page(page_name, "TODO Test context manager features #demo")
        code_block = client.add_block_to_page(page_name, "```python\nwith LogseqClient(path) as client:\n    # Auto-saves on exit!\n    client.add_journal_entry('Hello!')\n```")
        
        print(f"✅ Added {len([task_block, code_block])} blocks")
        
        # Show session info
        session_info = client.get_session_info()
        print(f"📈 Session info: {session_info['modified_pages']} pages modified")
    
    print("🏁 Context exited - all changes automatically saved!\n")

def demo_context_manager_with_backup():
    """Demo context manager with backup and rollback capability."""
    
    graph_path = input("Enter path to your Logseq graph (or press Enter for '/Volumes/Projects/logseq'): ").strip()
    if not graph_path:
        graph_path = '/Volumes/Projects/logseq'
    
    print("🔄 Demo 2: Context Manager with Backup")
    print("=" * 50)
    
    # Use context manager with backup enabled
    with LogseqClient(graph_path, backup_on_enter=True) as client:
        print(f"📊 Graph loaded with backup enabled")
        
        # Show session info including backup path
        session_info = client.get_session_info()
        print(f"💾 Backup created at: {session_info.get('backup_path', 'N/A')}")
        
        # Add some content
        timestamp = datetime.now().strftime('%H:%M:%S')
        
        # Create a page for testing
        test_page = f"Backup Test {datetime.now().strftime('%Y%m%d_%H%M%S')}"
        page = client.create_page(test_page, "This page will be safely backed up")
        
        # Add multiple blocks
        for i in range(3):
            client.add_block_to_page(
                test_page, 
                f"Test block {i+1} created at {timestamp} #backup-test"
            )
        
        print(f"✅ Created test content with backup protection")
        
        # Show what's been modified
        session_info = client.get_session_info()
        print(f"📝 Modified pages: {session_info['modified_page_names']}")
    
    print("🏁 Context exited - changes saved and backup cleaned up!\n")

def demo_manual_save_control():
    """Demo context manager with manual save control."""
    
    graph_path = input("Enter path to your Logseq graph (or press Enter for '/Volumes/Projects/logseq'): ").strip()
    if not graph_path:
        graph_path = '/Volumes/Projects/logseq'
    
    print("🔄 Demo 3: Manual Save Control")
    print("=" * 50)
    
    # Use context manager with auto-save disabled
    with LogseqClient(graph_path, auto_save=False) as client:
        print(f"📊 Graph loaded with auto-save disabled")
        
        # Add some content
        timestamp = datetime.now().strftime('%H:%M:%S')
        
        # Create content but don't auto-save
        journal = client.add_journal_entry(
            f"Manual save demo at {timestamp} #manual-save #demo"
        )
        
        # Create blocks manually (these would normally auto-save)
        test_page = f"Manual Save Test {datetime.now().strftime('%Y%m%d_%H%M%S')}"
        page = client.create_page(test_page, "")
        
        # Add blocks
        block1 = client.add_block_to_page(test_page, "DOING Manual save testing #test")
        block2 = client.add_block_to_page(test_page, "TODO Verify manual save works")
        
        # Show session info
        session_info = client.get_session_info()
        print(f"📝 Modified {session_info['modified_pages']} pages")
        print(f"⚠️  Auto-save is disabled - changes are tracked but not auto-saved")
        
        # Manually save all changes
        saved_count = client.save_all()
        print(f"💾 Manually saved {saved_count} pages")
    
    print("🏁 Context exited - manual save was used!\n")

def demo_exception_handling():
    """Demo context manager exception handling and rollback."""
    
    graph_path = input("Enter path to your Logseq graph (or press Enter for '/Volumes/Projects/logseq'): ").strip()
    if not graph_path:
        graph_path = '/Volumes/Projects/logseq'
    
    print("🔄 Demo 4: Exception Handling and Rollback")
    print("=" * 50)
    
    try:
        # Use context manager with backup for safety
        with LogseqClient(graph_path, backup_on_enter=True) as client:
            print(f"📊 Graph loaded with backup for exception testing")
            
            # Add some content
            timestamp = datetime.now().strftime('%H:%M:%S')
            test_page = f"Exception Test {datetime.now().strftime('%Y%m%d_%H%M%S')}"
            page = client.create_page(test_page, "This will test exception handling")
            
            # Add a block
            client.add_block_to_page(test_page, f"Created before exception at {timestamp}")
            
            print(f"✅ Added content before simulated exception")
            
            # Simulate an exception
            print("⚠️  Simulating an exception...")
            raise ValueError("Simulated exception for testing rollback!")
            
    except ValueError as e:
        print(f"❌ Caught exception: {e}")
        print("🔄 Context manager handled the exception and offered rollback option")
    
    print("🏁 Exception demo completed!\n")

def main():
    """Run all context manager demos."""
    
    print("🎭 Logseq Python Library - Context Manager Demos")
    print("=" * 55)
    print()
    
    demos = [
        ("Basic Context Manager (Auto-save)", demo_basic_context_manager),
        ("Context Manager with Backup", demo_context_manager_with_backup),
        ("Manual Save Control", demo_manual_save_control),
        ("Exception Handling & Rollback", demo_exception_handling),
    ]
    
    for i, (name, demo_func) in enumerate(demos, 1):
        print(f"🎯 Available Demos:")
        for j, (demo_name, _) in enumerate(demos, 1):
            marker = "👉 " if j == i else "   "
            print(f"{marker}{j}. {demo_name}")
        
        print(f"\nRunning Demo {i}: {name}")
        print("-" * 40)
        
        try:
            demo_func()
        except KeyboardInterrupt:
            print("\n⛔ Demo interrupted by user")
            break
        except Exception as e:
            print(f"❌ Demo failed: {e}")
        
        if i < len(demos):
            cont = input("\nPress Enter to continue to next demo (or 'q' to quit): ").strip().lower()
            if cont == 'q':
                break
            print("\n")
    
    print("🎉 Context Manager demos completed!")
    print("\n💡 Key Benefits:")
    print("   ✅ Automatic session management")
    print("   ✅ Change tracking and auto-save")
    print("   ✅ Backup and rollback capabilities")
    print("   ✅ Exception-safe resource cleanup")
    print("   ✅ Manual save control when needed")

if __name__ == "__main__":
    main()