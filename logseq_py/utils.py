"""
Utility functions for Logseq operations.

This module contains helper functions for parsing Logseq files,
handling dates, and other common operations.
"""

import re
import yaml
import json
from datetime import datetime, date
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from .models import Block, Page


class LogseqUtils:
    """Utility class for Logseq operations."""
    
    @staticmethod
    def is_journal_page(page_name: str) -> bool:
        """Check if a page name represents a journal entry."""
        # Journal pages typically follow YYYY-MM-DD or similar formats
        date_patterns = [
            r'^\d{4}-\d{2}-\d{2}$',  # YYYY-MM-DD
            r'^\d{4}_\d{2}_\d{2}$',  # YYYY_MM_DD
            r'^[A-Z][a-z]{2} \d{1,2}[a-z]{2}, \d{4}$',  # Jan 1st, 2024
        ]
        
        return any(re.match(pattern, page_name) for pattern in date_patterns)
    
    @staticmethod
    def parse_journal_date(page_name: str) -> Optional[datetime]:
        """Parse journal date from page name."""
        try:
            # Try YYYY-MM-DD format first
            if re.match(r'^\d{4}-\d{2}-\d{2}$', page_name):
                return datetime.strptime(page_name, '%Y-%m-%d')
            
            # Try YYYY_MM_DD format
            if re.match(r'^\d{4}_\d{2}_\d{2}$', page_name):
                return datetime.strptime(page_name, '%Y_%m_%d')
            
            # Try other formats as needed
            # Add more patterns here if you use different journal formats
            
        except ValueError:
            pass
        
        return None
    
    @staticmethod
    def parse_markdown_file(file_path: Path) -> Page:
        """Parse a Logseq markdown file into a Page object."""
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        page_name = file_path.stem
        page = Page(name=page_name, file_path=file_path)
        
        # Check if it's a journal page
        page.is_journal = LogseqUtils.is_journal_page(page_name)
        if page.is_journal:
            page.journal_date = LogseqUtils.parse_journal_date(page_name)
        
        # Parse blocks from content
        blocks = LogseqUtils.parse_blocks_from_content(content, page_name)
        for block in blocks:
            page.add_block(block)
        
        # Extract page-level properties from the first few lines
        page.properties = LogseqUtils.extract_page_properties(content)
        
        return page
    
    @staticmethod
    def parse_blocks_from_content(content: str, page_name: str) -> List[Block]:
        """Parse blocks from markdown content, handling multi-line constructs."""
        lines = content.split('\n')
        blocks = []
        block_stack = []  # Stack to keep track of parent blocks
        i = 0
        
        while i < len(lines):
            line = lines[i]
            stripped_line = line.strip()
            
            # Skip empty lines and page properties
            if not stripped_line or '::' in stripped_line:
                i += 1
                continue
            
            # Handle code blocks (multi-line)
            if stripped_line.startswith('```'):
                code_lines = [line]
                i += 1
                # Continue reading until closing ```
                while i < len(lines):
                    code_lines.append(lines[i])
                    if lines[i].strip() == '```':
                        break
                    i += 1
                
                # Create single block with all code content
                level = LogseqUtils.get_block_level(line)
                block_content = '\n'.join(code_lines)
                
                block = Block(
                    content=block_content,
                    level=level,
                    page_name=page_name
                )
                
                # Handle parent-child relationships
                if level == 0:
                    block_stack = [block]
                else:
                    while len(block_stack) > level:
                        block_stack.pop()
                    if block_stack:
                        parent = block_stack[-1]
                        parent.add_child(block)
                    block_stack.append(block)
                
                blocks.append(block)
                i += 1
                continue
            
            # Handle math blocks ($$...$$)
            if stripped_line.startswith('$$'):
                math_lines = [line]
                i += 1
                # Continue reading until closing $$
                while i < len(lines):
                    math_lines.append(lines[i])
                    if lines[i].strip() == '$$':
                        break
                    i += 1
                
                level = LogseqUtils.get_block_level(line)
                block_content = '\n'.join(math_lines)
                
                block = Block(
                    content=block_content,
                    level=level,
                    page_name=page_name
                )
                
                # Handle parent-child relationships
                if level == 0:
                    block_stack = [block]
                else:
                    while len(block_stack) > level:
                        block_stack.pop()
                    if block_stack:
                        parent = block_stack[-1]
                        parent.add_child(block)
                    block_stack.append(block)
                
                blocks.append(block)
                i += 1
                continue
            
            # Regular single-line block processing
            level = LogseqUtils.get_block_level(line)
            
            # Remove markdown list markers
            block_content = LogseqUtils.clean_block_content(stripped_line)
            
            if not block_content:
                i += 1
                continue
            
            # Create new block
            block = Block(
                content=block_content,
                level=level,
                page_name=page_name
            )
            
            # Handle parent-child relationships
            if level == 0:
                block_stack = [block]  # New top-level block
            else:
                # Find the appropriate parent
                while len(block_stack) > level:
                    block_stack.pop()
                
                if block_stack:
                    parent = block_stack[-1]
                    parent.add_child(block)
                
                block_stack.append(block)
            
            blocks.append(block)
            i += 1
        
        return blocks
    
    @staticmethod
    def get_block_level(line: str) -> int:
        """Determine the indentation level of a block."""
        # Count leading tabs and spaces (tabs count as 1 level each)
        level = 0
        for char in line:
            if char == '\t':
                level += 1
            elif char == ' ':
                # Logseq typically uses 2 spaces per level
                continue  # We'll handle spaces differently
            else:
                break
        
        # If no tabs, count spaces (assuming 2 spaces = 1 level)
        if level == 0:
            leading_spaces = len(line) - len(line.lstrip(' '))
            level = leading_spaces // 2
        
        return level
    
    @staticmethod
    def clean_block_content(content: str) -> str:
        """Clean block content by removing markdown list markers."""
        # Remove leading list markers (-, *, +)
        content = re.sub(r'^[\-\*\+]\s+', '', content)
        
        # Remove leading numbers for ordered lists
        content = re.sub(r'^\d+\.\s+', '', content)
        
        return content.strip()
    
    @staticmethod
    def extract_page_properties(content: str) -> Dict[str, Any]:
        """Extract page-level properties from content."""
        properties = {}
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Stop when we hit the first block (starting with -)
            if line.startswith('-'):
                break
            
            # Match property format: key:: value
            match = re.match(r'^([a-zA-Z0-9_-]+)::\s*(.+)$', line)
            if match:
                key, value = match.groups()
                properties[key.lower()] = value.strip()
        
        return properties
    
    @staticmethod
    def load_logseq_config(graph_path: Path) -> Dict[str, Any]:
        """Load Logseq configuration from the .logseq directory."""
        config = {}
        
        config_dir = graph_path / '.logseq'
        if not config_dir.exists():
            return config
        
        # Load config.edn (Clojure format - simplified parsing)
        config_file = config_dir / 'config.edn'
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                # Basic EDN parsing (this is simplified)
                config['raw_config'] = content
            except Exception as e:
                print(f"Warning: Could not parse config.edn: {e}")
        
        # Load metadata.edn if exists
        metadata_file = config_dir / 'metadata.edn'
        if metadata_file.exists():
            try:
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                config['metadata'] = content
            except Exception as e:
                print(f"Warning: Could not parse metadata.edn: {e}")
        
        return config
    
    @staticmethod
    def format_date_for_journal(date_obj: date) -> str:
        """Format a date object for Logseq journal page naming."""
        return date_obj.strftime('%Y-%m-%d')
    
    @staticmethod
    def ensure_valid_page_name(name: str) -> str:
        """Ensure a page name is valid for Logseq."""
        # Remove or replace invalid characters
        # Logseq generally accepts most characters, but let's be safe
        invalid_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
        
        for char in invalid_chars:
            name = name.replace(char, '_')
        
        # Trim whitespace
        name = name.strip()
        
        # Ensure it's not empty
        if not name:
            name = 'Untitled'
        
        return name
    
    @staticmethod
    def create_block_id() -> str:
        """Create a unique block ID in Logseq format."""
        import uuid
        return str(uuid.uuid4())
    
    @staticmethod
    def get_file_modification_time(file_path: Path) -> Optional[datetime]:
        """Get the last modification time of a file."""
        try:
            timestamp = file_path.stat().st_mtime
            return datetime.fromtimestamp(timestamp)
        except (OSError, ValueError):
            return None