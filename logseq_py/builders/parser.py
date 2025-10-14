"""
Builder-based Content Parser

This module provides functionality to parse Logseq content and convert it back 
into the same builder constructs used for generation, creating a unified 
read/write system.
"""

import re
from pathlib import Path
from typing import List, Dict, Any, Optional, Union, Type
from datetime import datetime, date

from .core import BlockBuilder, LogseqBuilder, ContentBuilder
from .content_types import (
    TaskBuilder, CodeBlockBuilder, MathBuilder, HeadingBuilder,
    QuoteBuilder, TableBuilder, QueryBuilder
)
from .page_builders import PageBuilder, JournalBuilder
from ..models import Block, Page, TaskState, Priority, BlockType


class BuilderParser:
    """Parser that converts Logseq content into builder objects."""
    
    @classmethod
    def parse_page_to_builder(cls, page: Page) -> PageBuilder:
        """
        Convert a parsed Page object into a PageBuilder.
        
        Args:
            page: Page object to convert
            
        Returns:
            PageBuilder with equivalent content
        """
        # Determine builder type
        if page.is_journal:
            builder = JournalBuilder(page.journal_date.date() if page.journal_date else None)
        else:
            builder = PageBuilder(page.name)
        
        # Add page properties
        if page.properties:
            builder.properties(page.properties)
        
        # Convert blocks to builders
        for block in page.blocks:
            block_builder = cls.parse_block_to_builder(block)
            if block_builder:
                builder.add(block_builder)
        
        return builder
    
    @classmethod
    def parse_block_to_builder(cls, block: Block) -> Optional[ContentBuilder]:
        """
        Convert a Block object into the appropriate builder type.
        
        Args:
            block: Block object to convert
            
        Returns:
            Appropriate ContentBuilder subclass or None
        """
        content = block.content.strip()
        
        # Task blocks
        if block.task_state:
            return cls._create_task_builder(block)
        
        # Code blocks
        if content.startswith('```') and content.endswith('```'):
            return cls._create_code_block_builder(block)
        
        # Math blocks
        if content.startswith('$$') and content.endswith('$$'):
            return cls._create_math_builder(block)
        
        # Headings
        if block.heading_level or cls._is_heading_content(content):
            return cls._create_heading_builder(block)
        
        # Quotes
        if cls._is_quote_content(content):
            return cls._create_quote_builder(block)
        
        # Tables
        if cls._is_table_content(content):
            return cls._create_table_builder(block)
        
        # Queries
        if cls._is_query_content(content):
            return cls._create_query_builder(block)
        
        # Default block
        return cls._create_basic_block_builder(block)
    
    @classmethod
    def _create_task_builder(cls, block: Block) -> TaskBuilder:
        """Create TaskBuilder from block."""
        builder = TaskBuilder()
        
        # Extract task content (remove status marker)
        content = block.content
        status_pattern = r'^-?\s*(TODO|DOING|DONE|LATER|NOW|WAITING|CANCELLED|DELEGATED)\s+'
        match = re.match(status_pattern, content)
        if match:
            task_content = content[match.end():].strip()
        else:
            task_content = content
        
        # Set status
        if block.task_state:
            builder.status(block.task_state.value)
        
        # Set priority
        if block.priority:
            builder.priority(block.priority.value)
        
        # Set content
        builder.content(task_content)
        
        # Add properties
        if block.properties:
            for key, value in block.properties.items():
                builder.property(key, value)
        
        # Handle scheduled/deadline dates
        if block.scheduled:
            builder.scheduled(block.scheduled.date)
        if block.deadline:
            builder.deadline(block.deadline.date)
        
        # Add child blocks
        cls._add_child_blocks(builder, block)
        
        return builder
    
    @classmethod
    def _create_code_block_builder(cls, block: Block) -> CodeBlockBuilder:
        """Create CodeBlockBuilder from block."""
        content = block.content
        
        # Extract language and code
        lines = content.split('\n')
        first_line = lines[0].strip()
        
        # Get language from first line
        language = 'text'
        if first_line.startswith('```'):
            language = first_line[3:].strip() or 'text'
        
        # Get code content (excluding ``` markers)
        if len(lines) > 2:
            code_content = '\n'.join(lines[1:-1])
        else:
            code_content = ''
        
        builder = CodeBlockBuilder(language)
        
        # Add code lines
        for line in code_content.split('\n'):
            builder.line(line)
        
        # Add properties
        if block.properties:
            for key, value in block.properties.items():
                builder.property(key, value)
        
        return builder
    
    @classmethod
    def _create_math_builder(cls, block: Block) -> MathBuilder:
        """Create MathBuilder from block."""
        content = block.content
        
        # Extract math content (remove $$ markers)
        lines = content.split('\n')
        if len(lines) > 2 and lines[0].strip() == '$$' and lines[-1].strip() == '$$':
            math_content = '\n'.join(lines[1:-1])
        else:
            # Inline math
            math_content = content.strip('$')
        
        builder = MathBuilder()
        builder.expression(math_content)
        
        # Add properties
        if block.properties:
            for key, value in block.properties.items():
                builder.property(key, value)
        
        return builder
    
    @classmethod
    def _create_heading_builder(cls, block: Block) -> HeadingBuilder:
        """Create HeadingBuilder from block."""
        content = block.content
        
        # Determine heading level
        level = block.heading_level
        if not level:
            # Extract from content
            match = re.match(r'^-?\s*(#{1,6})\s+(.+)', content)
            if match:
                level = len(match.group(1))
                heading_text = match.group(2)
            else:
                level = 1
                heading_text = content
        else:
            # Remove heading markers if present
            match = re.match(r'^-?\s*#{1,6}\s+(.+)', content)
            heading_text = match.group(1) if match else content
        
        builder = HeadingBuilder(level, heading_text)
        
        # Add properties
        if block.properties:
            for key, value in block.properties.items():
                builder.property(key, value)
        
        # Add child blocks
        cls._add_child_blocks(builder, block)
        
        return builder
    
    @classmethod
    def _create_quote_builder(cls, block: Block) -> QuoteBuilder:
        """Create QuoteBuilder from block."""
        content = block.content
        
        # Remove quote marker
        if content.startswith('> '):
            quote_content = content[2:]
        elif content.startswith('>'):
            quote_content = content[1:]
        else:
            quote_content = content
        
        builder = QuoteBuilder()
        builder.text(quote_content)
        
        # Add properties
        if block.properties:
            for key, value in block.properties.items():
                builder.property(key, value)
        
        return builder
    
    @classmethod
    def _create_table_builder(cls, block: Block) -> TableBuilder:
        """Create TableBuilder from block."""
        content = block.content
        lines = content.split('\n')
        
        builder = TableBuilder()
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line.startswith('|') or not line.endswith('|'):
                continue
            
            # Split cells and clean them
            cells = [cell.strip() for cell in line[1:-1].split('|')]
            
            if i == 0:
                # Header row
                builder.headers(*cells)
            elif i == 1 and all(re.match(r'^[-:]+$', cell.strip()) for cell in cells):
                # Separator row - skip
                continue
            else:
                # Data row
                builder.row(*cells)
        
        return builder
    
    @classmethod
    def _create_query_builder(cls, block: Block) -> QueryBuilder:
        """Create QueryBuilder from block."""
        content = block.content
        
        # Extract query content
        if content.startswith('```query\n') and content.endswith('\n```'):
            query_content = content[9:-4].strip()
        else:
            query_content = content
        
        builder = QueryBuilder()
        builder.query(query_content)
        
        return builder
    
    @classmethod
    def _create_basic_block_builder(cls, block: Block) -> BlockBuilder:
        """Create basic BlockBuilder from block."""
        content = block.content
        
        # Remove list markers
        clean_content = cls._clean_list_markers(content)
        
        builder = BlockBuilder(clean_content)
        
        # Add properties
        if block.properties:
            for key, value in block.properties.items():
                builder.property(key, value)
        
        # Add child blocks
        cls._add_child_blocks(builder, block)
        
        return builder
    
    @classmethod
    def _add_child_blocks(cls, parent_builder: ContentBuilder, parent_block: Block):
        """Add child blocks to a parent builder."""
        # Note: This would require access to the full graph to resolve child relationships
        # For now, we'll add a placeholder method that can be enhanced when needed
        pass
    
    @staticmethod
    def _is_heading_content(content: str) -> bool:
        """Check if content represents a heading."""
        return bool(re.match(r'^-?\s*#{1,6}\s+', content))
    
    @staticmethod
    def _is_quote_content(content: str) -> bool:
        """Check if content represents a quote."""
        return content.startswith('> ') or content.startswith('>')
    
    @staticmethod
    def _is_table_content(content: str) -> bool:
        """Check if content represents a table."""
        lines = content.split('\n')
        return (len(lines) >= 2 and 
                any(line.strip().startswith('|') and line.strip().endswith('|') 
                    for line in lines))
    
    @staticmethod
    def _is_query_content(content: str) -> bool:
        """Check if content represents a query."""
        return (content.startswith('```query') or 
                '{{query}}' in content.lower() or
                ':query' in content)
    
    @staticmethod
    def _clean_list_markers(content: str) -> str:
        """Remove list markers from content."""
        # Remove leading bullet markers
        content = re.sub(r'^-?\s*', '', content.strip())
        return content


class ContentReconstructor:
    """Reconstructs content using builders from parsed Logseq data."""
    
    @classmethod
    def reconstruct_page(cls, page: Page) -> str:
        """
        Reconstruct a page using builders to generate equivalent content.
        
        Args:
            page: Page to reconstruct
            
        Returns:
            Reconstructed content string
        """
        builder = BuilderParser.parse_page_to_builder(page)
        return builder.build()
    
    @classmethod
    def reconstruct_block(cls, block: Block) -> str:
        """
        Reconstruct a block using builders to generate equivalent content.
        
        Args:
            block: Block to reconstruct
            
        Returns:
            Reconstructed content string
        """
        builder = BuilderParser.parse_block_to_builder(block)
        if builder:
            return builder.build()
        return block.content
    
    @classmethod
    def modify_and_reconstruct(cls, page: Page, 
                             modifications: Dict[str, Any]) -> str:
        """
        Modify a page using builders and reconstruct it.
        
        Args:
            page: Page to modify
            modifications: Dictionary of modifications to apply
            
        Returns:
            Modified and reconstructed content
        """
        builder = BuilderParser.parse_page_to_builder(page)
        
        # Apply modifications
        if 'properties' in modifications:
            builder.properties(modifications['properties'])
        
        if 'add_blocks' in modifications:
            for block_content in modifications['add_blocks']:
                builder.text(block_content)
        
        if 'add_tasks' in modifications:
            for task_info in modifications['add_tasks']:
                task_builder = builder.task(task_info.get('content', ''))
                if 'status' in task_info:
                    task_builder.status(task_info['status'])
                if 'priority' in task_info:
                    task_builder.priority(task_info['priority'])
        
        return builder.build()


class BuilderBasedLoader:
    """Loader that returns builder objects instead of model objects."""
    
    def __init__(self, graph_path: str):
        """Initialize with graph path."""
        self.graph_path = Path(graph_path) if isinstance(graph_path, str) else graph_path
    
    def load_page_as_builder(self, page_name: str) -> Optional[PageBuilder]:
        """
        Load a page as a PageBuilder object.
        
        Args:
            page_name: Name of the page to load
            
        Returns:
            PageBuilder object or None if not found
        """
        from ..utils import LogseqUtils
        
        # Find the file
        page_file = self.graph_path / f"{page_name}.md"
        if not page_file.exists():
            # Try in journals
            page_file = self.graph_path / "journals" / f"{page_name}.md"
            if not page_file.exists():
                return None
        
        # Parse to Page object first
        page = LogseqUtils.parse_markdown_file(page_file)
        
        # Convert to builder
        return BuilderParser.parse_page_to_builder(page)
    
    def load_all_pages_as_builders(self) -> Dict[str, PageBuilder]:
        """
        Load all pages as builder objects.
        
        Returns:
            Dictionary mapping page names to PageBuilder objects
        """
        from ..utils import LogseqUtils
        
        builders = {}
        
        # Load regular pages
        for md_file in self.graph_path.glob("*.md"):
            if md_file.name.startswith('.'):
                continue
            
            try:
                page = LogseqUtils.parse_markdown_file(md_file)
                builder = BuilderParser.parse_page_to_builder(page)
                builders[page.name] = builder
            except Exception as e:
                print(f"Warning: Could not load {md_file} as builder: {e}")
        
        # Load journal pages
        journals_path = self.graph_path / "journals"
        if journals_path.exists():
            for md_file in journals_path.glob("*.md"):
                try:
                    page = LogseqUtils.parse_markdown_file(md_file)
                    builder = BuilderParser.parse_page_to_builder(page)
                    builders[page.name] = builder
                except Exception as e:
                    print(f"Warning: Could not load {md_file} as builder: {e}")
        
        return builders
    
    def modify_page_content(self, page_name: str, 
                           modifier_func) -> Optional[str]:
        """
        Load a page as a builder, apply modifications, and return rebuilt content.
        
        Args:
            page_name: Name of the page to modify
            modifier_func: Function that takes a PageBuilder and modifies it
            
        Returns:
            Modified content string or None if page not found
        """
        builder = self.load_page_as_builder(page_name)
        if not builder:
            return None
        
        # Apply modifications
        modifier_func(builder)
        
        # Return rebuilt content
        return builder.build()