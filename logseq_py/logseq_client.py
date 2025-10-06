"""
Main client class for Logseq operations.

This module provides the primary interface for interacting with Logseq graphs.
"""

import os
from datetime import datetime, date
from pathlib import Path
from typing import List, Dict, Any, Optional, Union

from .models import Block, Page, LogseqGraph
from .utils import LogseqUtils
from .query import QueryBuilder


class LogseqClient:
    """Main client for interacting with Logseq graphs."""
    
    def __init__(self, graph_path: Union[str, Path]):
        """
        Initialize the Logseq client.
        
        Args:
            graph_path: Path to the Logseq graph directory
        """
        self.graph_path = Path(graph_path).resolve()
        self.graph: Optional[LogseqGraph] = None
        
        if not self.graph_path.exists():
            raise FileNotFoundError(f"Graph directory not found: {self.graph_path}")
        
        if not self.graph_path.is_dir():
            raise ValueError(f"Path is not a directory: {self.graph_path}")
    
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