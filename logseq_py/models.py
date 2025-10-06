"""
Core data models for Logseq entities.

This module defines the main data structures used throughout the library:
- Block: Individual content blocks in Logseq
- Page: Logseq pages (both regular pages and journal entries)
- LogseqGraph: Container for the entire graph data
"""

import re
import uuid
from datetime import datetime
from typing import List, Dict, Optional, Any, Set
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Block:
    """Represents a single block in Logseq."""
    
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    content: str = ""
    level: int = 0  # Indentation level (0 = top-level)
    parent_id: Optional[str] = None
    children_ids: List[str] = field(default_factory=list)
    properties: Dict[str, Any] = field(default_factory=dict)
    tags: Set[str] = field(default_factory=set)
    page_name: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        """Extract tags and properties from content after initialization."""
        self._extract_tags()
        self._extract_properties()
    
    def _extract_tags(self):
        """Extract hashtags from content."""
        # Match hashtags (but not inside code blocks or links)
        tag_pattern = r'(?:^|\s)#([a-zA-Z0-9_-]+)(?:\s|$|[.,;!?])'
        matches = re.findall(tag_pattern, self.content)
        self.tags.update(matches)
    
    def _extract_properties(self):
        """Extract properties from content (key:: value format)."""
        # Match property format: key:: value
        prop_pattern = r'^([a-zA-Z0-9_-]+)::\s*(.+)$'
        lines = self.content.split('\n')
        
        for line in lines:
            match = re.match(prop_pattern, line.strip())
            if match:
                key, value = match.groups()
                self.properties[key.lower()] = value.strip()
    
    def add_child(self, child_block: 'Block'):
        """Add a child block."""
        if child_block.id not in self.children_ids:
            self.children_ids.append(child_block.id)
            child_block.parent_id = self.id
            child_block.level = self.level + 1
    
    def get_links(self) -> Set[str]:
        """Extract page links from content."""
        # Match [[Page Name]] format
        link_pattern = r'\[\[([^\]]+)\]\]'
        matches = re.findall(link_pattern, self.content)
        return set(matches)
    
    def get_block_references(self) -> Set[str]:
        """Extract block references from content."""
        # Match ((block-id)) format
        ref_pattern = r'\(\(([^)]+)\)\)'
        matches = re.findall(ref_pattern, self.content)
        return set(matches)
    
    def to_markdown(self) -> str:
        """Convert block to Logseq markdown format."""
        indent = "\t" * self.level if self.level > 0 else ""
        prefix = "- " if self.level == 0 else ""
        return f"{indent}{prefix}{self.content}"


@dataclass
class Page:
    """Represents a page in Logseq."""
    
    name: str
    title: str = ""
    file_path: Optional[Path] = None
    blocks: List[Block] = field(default_factory=list)
    properties: Dict[str, Any] = field(default_factory=dict)
    tags: Set[str] = field(default_factory=set)
    links: Set[str] = field(default_factory=set)
    backlinks: Set[str] = field(default_factory=set)
    is_journal: bool = False
    journal_date: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        """Process page data after initialization."""
        if not self.title:
            self.title = self.name
        self._extract_page_data()
    
    def _extract_page_data(self):
        """Extract tags and links from all blocks."""
        for block in self.blocks:
            self.tags.update(block.tags)
            self.links.update(block.get_links())
    
    def add_block(self, block: Block):
        """Add a block to the page."""
        block.page_name = self.name
        self.blocks.append(block)
        self.tags.update(block.tags)
        self.links.update(block.get_links())
    
    def get_block_by_id(self, block_id: str) -> Optional[Block]:
        """Get a block by its ID."""
        for block in self.blocks:
            if block.id == block_id:
                return block
        return None
    
    def get_blocks_by_content(self, search_text: str, case_sensitive: bool = False) -> List[Block]:
        """Find blocks containing specific text."""
        results = []
        search_text = search_text if case_sensitive else search_text.lower()
        
        for block in self.blocks:
            content = block.content if case_sensitive else block.content.lower()
            if search_text in content:
                results.append(block)
        
        return results
    
    def get_blocks_by_tag(self, tag: str) -> List[Block]:
        """Find blocks with a specific tag."""
        return [block for block in self.blocks if tag in block.tags]
    
    def to_markdown(self) -> str:
        """Convert page to Logseq markdown format."""
        lines = []
        
        # Add page properties if any
        if self.properties:
            for key, value in self.properties.items():
                lines.append(f"{key}:: {value}")
            lines.append("")  # Empty line after properties
        
        # Add blocks
        for block in self.blocks:
            lines.append(block.to_markdown())
        
        return "\n".join(lines)


@dataclass 
class LogseqGraph:
    """Represents the entire Logseq graph."""
    
    root_path: Path
    pages: Dict[str, Page] = field(default_factory=dict)
    blocks: Dict[str, Block] = field(default_factory=dict)
    config: Dict[str, Any] = field(default_factory=dict)
    
    def add_page(self, page: Page):
        """Add a page to the graph."""
        self.pages[page.name] = page
        
        # Add all blocks to the blocks index
        for block in page.blocks:
            self.blocks[block.id] = block
    
    def get_page(self, name: str) -> Optional[Page]:
        """Get a page by name."""
        return self.pages.get(name)
    
    def get_block(self, block_id: str) -> Optional[Block]:
        """Get a block by ID."""
        return self.blocks.get(block_id)
    
    def get_pages_by_tag(self, tag: str) -> List[Page]:
        """Find pages containing a specific tag."""
        return [page for page in self.pages.values() if tag in page.tags]
    
    def get_journal_pages(self) -> List[Page]:
        """Get all journal pages sorted by date."""
        journal_pages = [page for page in self.pages.values() if page.is_journal]
        return sorted(journal_pages, key=lambda p: p.journal_date or datetime.min)
    
    def search_content(self, search_text: str, case_sensitive: bool = False) -> Dict[str, List[Block]]:
        """Search for text across all pages."""
        results = {}
        
        for page_name, page in self.pages.items():
            matching_blocks = page.get_blocks_by_content(search_text, case_sensitive)
            if matching_blocks:
                results[page_name] = matching_blocks
        
        return results
    
    def get_backlinks(self, page_name: str) -> Set[str]:
        """Get all pages that link to the specified page."""
        backlinks = set()
        
        for page in self.pages.values():
            if page_name in page.links:
                backlinks.add(page.name)
        
        return backlinks
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get graph statistics."""
        total_blocks = len(self.blocks)
        total_pages = len(self.pages)
        journal_pages = len([p for p in self.pages.values() if p.is_journal])
        regular_pages = total_pages - journal_pages
        
        all_tags = set()
        all_links = set()
        
        for page in self.pages.values():
            all_tags.update(page.tags)
            all_links.update(page.links)
        
        return {
            "total_pages": total_pages,
            "regular_pages": regular_pages,
            "journal_pages": journal_pages,
            "total_blocks": total_blocks,
            "total_tags": len(all_tags),
            "total_links": len(all_links),
            "unique_tags": sorted(list(all_tags)),
            "unique_links": sorted(list(all_links))
        }