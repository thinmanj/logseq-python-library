"""
Main client class for Logseq operations.

This module provides the primary interface for interacting with Logseq graphs.
"""

import os
import shutil
import tempfile
from datetime import datetime, date
from pathlib import Path
from typing import List, Dict, Any, Optional, Union, Set

from .models import Block, Page, LogseqGraph
from .utils import LogseqUtils
from .query import QueryBuilder


class LogseqClient:
    """Main client for interacting with Logseq graphs.
    
    Supports context manager usage for automatic session management:
    
    with LogseqClient('/path/to/graph') as client:
        # Make changes
        client.add_journal_entry('Today I used context managers!')
        # Changes are automatically saved on exit
    """
    
    def __init__(self, graph_path: Union[str, Path], auto_save: bool = True, backup_on_enter: bool = False):
        """
        Initialize the Logseq client.
        
        Args:
            graph_path: Path to the Logseq graph directory
            auto_save: Whether to automatically save changes on context exit
            backup_on_enter: Whether to create a backup when entering context
        """
        self.graph_path = Path(graph_path).resolve()
        self.graph: Optional[LogseqGraph] = None
        self.auto_save = auto_save
        self.backup_on_enter = backup_on_enter
        
        # Context manager state
        self._in_context = False
        self._modified_pages: Set[str] = set()
        self._backup_dir: Optional[Path] = None
        self._session_start_time: Optional[datetime] = None
        
        if not self.graph_path.exists():
            raise FileNotFoundError(f"Graph directory not found: {self.graph_path}")
        
        if not self.graph_path.is_dir():
            raise ValueError(f"Path is not a directory: {self.graph_path}")
    
    def __enter__(self) -> 'LogseqClient':
        """Enter context manager."""
        self._in_context = True
        self._session_start_time = datetime.now()
        self._modified_pages.clear()
        
        # Load the graph if not already loaded
        if not self.graph:
            self.load_graph()
        
        # Create backup if requested
        if self.backup_on_enter:
            self._create_backup()
        
        print(f"🔄 Started Logseq session at {self._session_start_time.strftime('%H:%M:%S')}")
        if self._backup_dir:
            print(f"💾 Backup created at: {self._backup_dir}")
        
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        """Exit context manager."""
        session_end = datetime.now()
        duration = session_end - self._session_start_time if self._session_start_time else None
        
        if exc_type is not None:
            # Exception occurred - handle rollback or cleanup
            print(f"❌ Exception occurred in Logseq session: {exc_type.__name__}: {exc_val}")
            
            if self._backup_dir:
                print(f"🔄 Rollback available from backup: {self._backup_dir}")
                rollback = input("Would you like to rollback to backup? (y/N): ").lower().strip() == 'y'
                if rollback:
                    self._rollback_from_backup()
                    print("✅ Rolled back to backup successfully")
                else:
                    self._cleanup_backup()
            
            self._in_context = False
            return False  # Don't suppress the exception
        
        # Normal exit - save if auto_save is enabled
        if self.auto_save and self._modified_pages:
            print(f"💾 Auto-saving {len(self._modified_pages)} modified pages...")
            self._save_all_modified_pages()
            print("✅ All changes saved successfully")
        elif self._modified_pages:
            print(f"⚠️  {len(self._modified_pages)} pages were modified but auto_save is disabled")
            print("   Call save_all() or save individual pages manually if needed")
        
        # Cleanup backup if everything went well
        if self._backup_dir:
            self._cleanup_backup()
        
        # Session summary
        duration_str = f" (duration: {duration.total_seconds():.1f}s)" if duration else ""
        print(f"🏁 Logseq session completed at {session_end.strftime('%H:%M:%S')}{duration_str}")
        
        self._in_context = False
        return False
    
    def _create_backup(self):
        """Create a backup of the current graph state."""
        self._backup_dir = Path(tempfile.mkdtemp(prefix="logseq_backup_"))
        
        # Copy all markdown files
        for md_file in self.graph_path.glob("**/*.md"):
            if '.logseq' not in md_file.parts:  # Skip .logseq directory
                relative_path = md_file.relative_to(self.graph_path)
                backup_file = self._backup_dir / relative_path
                backup_file.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(md_file, backup_file)
    
    def _rollback_from_backup(self):
        """Rollback changes from backup."""
        if not self._backup_dir or not self._backup_dir.exists():
            raise ValueError("No backup available for rollback")
        
        # Remove current files that exist in backup
        for backup_file in self._backup_dir.glob("**/*.md"):
            relative_path = backup_file.relative_to(self._backup_dir)
            current_file = self.graph_path / relative_path
            if current_file.exists():
                current_file.unlink()
        
        # Copy backup files back
        for backup_file in self._backup_dir.glob("**/*.md"):
            relative_path = backup_file.relative_to(self._backup_dir)
            current_file = self.graph_path / relative_path
            current_file.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(backup_file, current_file)
    
    def _cleanup_backup(self):
        """Clean up temporary backup directory."""
        if self._backup_dir and self._backup_dir.exists():
            shutil.rmtree(self._backup_dir)
            self._backup_dir = None
    
    def _save_all_modified_pages(self):
        """Save all pages that were modified during the context session."""
        if not self.graph:
            return
        
        saved_count = 0
        for page_name in self._modified_pages:
            page = self.graph.get_page(page_name)
            if page:
                self._save_page(page)
                saved_count += 1
        
        return saved_count
    
    def _track_page_modification(self, page_name: str):
        """Track that a page has been modified during context session."""
        if self._in_context:
            self._modified_pages.add(page_name)
    
    def save_all(self) -> int:
        """Manually save all modified pages. Returns number of pages saved."""
        if not self._in_context:
            # Save all pages if not in context
            if not self.graph:
                return 0
            
            saved_count = 0
            for page in self.graph.pages.values():
                if page.file_path:
                    self._save_page(page)
                    saved_count += 1
            return saved_count
        else:
            # Save only modified pages if in context
            return self._save_all_modified_pages()
    
    def get_session_info(self) -> Dict[str, Any]:
        """Get information about the current context session."""
        if not self._in_context:
            return {"in_context": False}
        
        duration = datetime.now() - self._session_start_time if self._session_start_time else None
        
        return {
            "in_context": True,
            "session_start": self._session_start_time,
            "duration_seconds": duration.total_seconds() if duration else None,
            "modified_pages": len(self._modified_pages),
            "modified_page_names": list(self._modified_pages),
            "auto_save_enabled": self.auto_save,
            "backup_created": self._backup_dir is not None,
            "backup_path": str(self._backup_dir) if self._backup_dir else None
        }
    
    def load_graph(self, force_reload: bool = False) -> LogseqGraph:
        """
        Load the Logseq graph from disk.
        
        Args:
            force_reload: Force reload even if graph is already loaded
            
        Returns:
            LogseqGraph object containing all pages and blocks
        """
        if self.graph and not force_reload:
            return self.graph
        
        self.graph = LogseqGraph(root_path=self.graph_path)
        
        # Load configuration
        self.graph.config = LogseqUtils.load_logseq_config(self.graph_path)
        
        # Find all markdown files
        markdown_files = list(self.graph_path.glob("**/*.md"))
        
        for md_file in markdown_files:
            # Skip files in .logseq directory
            if '.logseq' in md_file.parts:
                continue
                
            try:
                page = LogseqUtils.parse_markdown_file(md_file)
                self.graph.add_page(page)
            except Exception as e:
                print(f"Warning: Could not parse {md_file}: {e}")
        
        # Update backlinks
        self._update_backlinks()
        
        return self.graph
    
    def _update_backlinks(self):
        """Update backlink information for all pages."""
        if not self.graph:
            return
        
        for page in self.graph.pages.values():
            page.backlinks = self.graph.get_backlinks(page.name)
    
    def query(self) -> QueryBuilder:
        """
        Create a new query builder.
        
        Returns:
            QueryBuilder instance for constructing queries
        """
        if not self.graph:
            self.load_graph()
        
        return QueryBuilder(self.graph)
    
    def get_page(self, page_name: str) -> Optional[Page]:
        """
        Get a page by name.
        
        Args:
            page_name: Name of the page to retrieve
            
        Returns:
            Page object or None if not found
        """
        if not self.graph:
            self.load_graph()
        
        return self.graph.get_page(page_name)
    
    def get_block(self, block_id: str) -> Optional[Block]:
        """
        Get a block by ID.
        
        Args:
            block_id: ID of the block to retrieve
            
        Returns:
            Block object or None if not found
        """
        if not self.graph:
            self.load_graph()
        
        return self.graph.get_block(block_id)
    
    def get_page_as_builder(self, page_name: str) -> Optional['PageBuilder']:
        """
        Get a page as a PageBuilder object for easy modification.
        
        Args:
            page_name: Name of the page to retrieve
            
        Returns:
            PageBuilder object or None if not found
        """
        from .builders.parser import BuilderParser
        
        page = self.get_page(page_name)
        if not page:
            return None
        
        return BuilderParser.parse_page_to_builder(page)
    
    def get_block_as_builder(self, block_id: str) -> Optional['ContentBuilder']:
        """
        Get a block as a ContentBuilder object for easy modification.
        
        Args:
            block_id: ID of the block to retrieve
            
        Returns:
            Appropriate ContentBuilder subclass or None if not found
        """
        from .builders.parser import BuilderParser
        
        block = self.get_block(block_id)
        if not block:
            return None
        
        return BuilderParser.parse_block_to_builder(block)
    
    def modify_page_with_builder(self, page_name: str, modifier_func) -> bool:
        """
        Load a page as a builder, modify it, and save it back.
        
        Args:
            page_name: Name of the page to modify
            modifier_func: Function that takes a PageBuilder and modifies it
            
        Returns:
            True if successful, False if page not found
        """
        page_builder = self.get_page_as_builder(page_name)
        if not page_builder:
            return False
        
        # Apply modifications
        modifier_func(page_builder)
        
        # Update the page content
        modified_content = page_builder.build()
        page = self.get_page(page_name)
        if page:
            # Clear existing blocks and parse new ones
            page.blocks.clear()
            new_blocks = LogseqUtils.parse_blocks_from_content(modified_content, page_name)
            for block in new_blocks:
                page.add_block(block)
            
            # Save the updated page
            self._save_page(page)
            
            return True
        
        return False
    
    def load_builder_based_loader(self) -> 'BuilderBasedLoader':
        """
        Get a BuilderBasedLoader for this graph.
        
        Returns:
            BuilderBasedLoader instance
        """
        from .builders.parser import BuilderBasedLoader
        return BuilderBasedLoader(self.graph_path)
    
    def create_page(self, name: str, content: str = "", properties: Dict[str, Any] = None) -> Page:
        """
        Create a new page.
        
        Args:
            name: Name of the new page
            content: Initial content for the page
            properties: Page properties
            
        Returns:
            Created Page object
        """
        if not self.graph:
            self.load_graph()
        
        # Ensure valid page name
        name = LogseqUtils.ensure_valid_page_name(name)
        
        # Check if page already exists
        if self.graph.get_page(name):
            raise ValueError(f"Page '{name}' already exists")
        
        # Create file path
        file_path = self.graph_path / f"{name}.md"
        
        # Create page object
        page = Page(name=name, file_path=file_path, properties=properties or {})
        
        # Add content as blocks if provided
        if content:
            blocks = LogseqUtils.parse_blocks_from_content(content, name)
            for block in blocks:
                page.add_block(block)
        
        # Save to disk
        self._save_page(page)
        
        # Add to graph
        self.graph.add_page(page)
        
        return page
    
    def add_journal_entry(self, content: str, date_obj: Optional[date] = None) -> Page:
        """
        Add a journal entry.
        
        Args:
            content: Content of the journal entry
            date_obj: Date for the journal entry (defaults to today)
            
        Returns:
            Journal page object
        """
        if not self.graph:
            self.load_graph()
        
        if not date_obj:
            date_obj = date.today()
        
        page_name = LogseqUtils.format_date_for_journal(date_obj)
        
        # Get or create journal page
        page = self.graph.get_page(page_name)
        if not page:
            page = self.create_journal_page(date_obj)
        
        # Add content as a new block
        block = Block(content=content, page_name=page_name)
        page.add_block(block)
        self.graph.blocks[block.id] = block
        
        # Save to disk
        self._save_page(page)
        
        return page
    
    def create_journal_page(self, date_obj: date) -> Page:
        """
        Create a new journal page.
        
        Args:
            date_obj: Date for the journal page
            
        Returns:
            Created journal page
        """
        page_name = LogseqUtils.format_date_for_journal(date_obj)
        file_path = self.graph_path / "journals" / f"{page_name}.md"
        
        # Ensure journals directory exists
        file_path.parent.mkdir(exist_ok=True)
        
        page = Page(
            name=page_name,
            file_path=file_path,
            is_journal=True,
            journal_date=datetime.combine(date_obj, datetime.min.time())
        )
        
        # Save to disk
        self._save_page(page)
        
        # Add to graph if it's loaded
        if self.graph:
            self.graph.add_page(page)
        
        return page
    
    def add_block_to_page(self, page_name: str, content: str, parent_block_id: Optional[str] = None) -> Block:
        """
        Add a new block to a page.
        
        Args:
            page_name: Name of the target page
            content: Block content
            parent_block_id: ID of parent block (for nested blocks)
            
        Returns:
            Created Block object
        """
        if not self.graph:
            self.load_graph()
        
        page = self.graph.get_page(page_name)
        if not page:
            raise ValueError(f"Page '{page_name}' not found")
        
        # Create new block
        block = Block(content=content, page_name=page_name)
        
        # Handle parent-child relationship
        if parent_block_id:
            parent_block = self.graph.get_block(parent_block_id)
            if parent_block and parent_block.page_name == page_name:
                parent_block.add_child(block)
        
        # Add to page and graph
        page.add_block(block)
        self.graph.blocks[block.id] = block
        
        # Save to disk
        self._save_page(page)
        
        return block
    
    def update_block(self, block_id: str, content: str) -> Optional[Block]:
        """
        Update the content of an existing block.
        
        Args:
            block_id: ID of the block to update
            content: New content for the block
            
        Returns:
            Updated Block object or None if not found
        """
        if not self.graph:
            self.load_graph()
        
        block = self.graph.get_block(block_id)
        if not block:
            return None
        
        # Update content
        old_content = block.content
        block.content = content
        block.updated_at = datetime.now()
        
        # Re-extract tags and properties
        block._extract_tags()
        block._extract_properties()
        
        # Update page tags and links
        if block.page_name:
            page = self.graph.get_page(block.page_name)
            if page:
                page._extract_page_data()
        
        # Save to disk
        if block.page_name:
            page = self.graph.get_page(block.page_name)
            if page:
                self._save_page(page)
        
        return block
    
    def delete_block(self, block_id: str) -> bool:
        """
        Delete a block.
        
        Args:
            block_id: ID of the block to delete
            
        Returns:
            True if deleted successfully, False if not found
        """
        if not self.graph:
            self.load_graph()
        
        block = self.graph.get_block(block_id)
        if not block:
            return False
        
        page = self.graph.get_page(block.page_name) if block.page_name else None
        if not page:
            return False
        
        # Remove from parent
        if block.parent_id:
            parent = self.graph.get_block(block.parent_id)
            if parent and block_id in parent.children_ids:
                parent.children_ids.remove(block_id)
        
        # Handle children (promote to parent level or delete)
        for child_id in block.children_ids:
            child = self.graph.get_block(child_id)
            if child:
                child.parent_id = block.parent_id
                child.level = max(0, child.level - 1)
        
        # Remove from page and graph
        page.blocks = [b for b in page.blocks if b.id != block_id]
        del self.graph.blocks[block_id]
        
        # Update page data
        page._extract_page_data()
        
        # Save to disk
        self._save_page(page)
        
        return True
    
    def _save_page(self, page: Page):
        """Save a page to disk."""
        if not page.file_path:
            return
        
        # Track modification if in context
        self._track_page_modification(page.name)
        
        # Ensure parent directory exists
        page.file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Generate markdown content
        content = page.to_markdown()
        
        # Write to file
        with open(page.file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Update timestamps
        page.updated_at = datetime.now()
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get graph statistics.
        
        Returns:
            Dictionary containing various graph statistics
        """
        if not self.graph:
            self.load_graph()
        
        return self.graph.get_statistics()
    
    def search(self, query: str, case_sensitive: bool = False) -> Dict[str, List[Block]]:
        """
        Search for text across all pages.
        
        Args:
            query: Text to search for
            case_sensitive: Whether to perform case-sensitive search
            
        Returns:
            Dictionary mapping page names to matching blocks
        """
        if not self.graph:
            self.load_graph()
        
        return self.graph.search_content(query, case_sensitive)
    
    def export_to_json(self, output_path: Union[str, Path]) -> None:
        """
        Export the graph to JSON format.
        
        Args:
            output_path: Path where to save the JSON file
        """
        import json
        from dataclasses import asdict
        
        if not self.graph:
            self.load_graph()
        
        # Convert graph to serializable format
        graph_data = {
            "root_path": str(self.graph.root_path),
            "config": self.graph.config,
            "pages": {},
            "statistics": self.graph.get_statistics()
        }
        
        for page_name, page in self.graph.pages.items():
            page_dict = {
                "name": page.name,
                "title": page.title,
                "file_path": str(page.file_path) if page.file_path else None,
                "properties": page.properties,
                "tags": list(page.tags),
                "links": list(page.links),
                "backlinks": list(page.backlinks),
                "is_journal": page.is_journal,
                "journal_date": page.journal_date.isoformat() if page.journal_date else None,
                "created_at": page.created_at.isoformat() if page.created_at else None,
                "updated_at": page.updated_at.isoformat() if page.updated_at else None,
                "blocks": []
            }
            
            for block in page.blocks:
                block_dict = {
                    "id": block.id,
                    "content": block.content,
                    "level": block.level,
                    "parent_id": block.parent_id,
                    "children_ids": block.children_ids,
                    "properties": block.properties,
                    "tags": list(block.tags),
                    "page_name": block.page_name,
                    "created_at": block.created_at.isoformat() if block.created_at else None,
                    "updated_at": block.updated_at.isoformat() if block.updated_at else None
                }
                page_dict["blocks"].append(block_dict)
            
            graph_data["pages"][page_name] = page_dict
        
        # Write to file
        output_path = Path(output_path)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(graph_data, f, indent=2, ensure_ascii=False)
    
    def reload_graph(self) -> LogseqGraph:
        """
        Reload the graph from disk.
        
        Returns:
            Reloaded LogseqGraph object
        """
        return self.load_graph(force_reload=True)