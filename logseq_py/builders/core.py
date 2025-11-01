"""
Core builder classes providing the foundation for Logseq content construction.

These classes implement the Builder pattern with a fluent interface, allowing for
intuitive and readable content generation code.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Union, TYPE_CHECKING
from datetime import datetime, date
import uuid

if TYPE_CHECKING:
    from ..models import Block, Page


class ContentBuilder(ABC):
    """Base class for all content builders."""
    
    def __init__(self):
        self._content: List[str] = []
        self._properties: Dict[str, Any] = {}
        self._metadata: Dict[str, Any] = {}
    
    @abstractmethod
    def build(self) -> str:
        """Build and return the final content string."""
        pass
    
    def _add_line(self, line: str, indent: int = 0) -> 'ContentBuilder':
        """Add a line with optional indentation."""
        indent_str = "  " * indent  # 2 spaces per indent level
        self._content.append(f"{indent_str}{line}")
        return self
    
    def _add_empty_line(self) -> 'ContentBuilder':
        """Add an empty line for spacing."""
        self._content.append("")
        return self
    
    def raw(self, content: str) -> 'ContentBuilder':
        """Add raw content directly."""
        self._content.append(content)
        return self
    
    def line(self, content: str, indent: int = 0) -> 'ContentBuilder':
        """Add a single line of content."""
        return self._add_line(content, indent)
    
    def lines(self, *lines: str, indent: int = 0) -> 'ContentBuilder':
        """Add multiple lines of content."""
        for line in lines:
            self._add_line(line, indent)
        return self
    
    def empty_line(self) -> 'ContentBuilder':
        """Add an empty line."""
        return self._add_empty_line()
    
    def separator(self, char: str = "-", length: int = 3) -> 'ContentBuilder':
        """Add a separator line."""
        return self._add_line(char * length)


class BlockBuilder(ContentBuilder):
    """Builder for individual Logseq blocks."""
    
    def __init__(self, content: str = ""):
        super().__init__()
        self._block_content = content
        self._block_properties: Dict[str, Any] = {}
        self._children: List['BlockBuilder'] = []
        self._indent_level = 0
    
    @classmethod
    def from_block(cls, block: 'Block') -> 'BlockBuilder':
        """Create a BlockBuilder from a Block object."""
        from .parser import BuilderParser
        builder = BuilderParser.parse_block_to_builder(block)
        if isinstance(builder, cls):
            return builder
        # Fallback to basic block builder
        return cls(block.content)
    
    @classmethod
    def from_content(cls, content: str) -> 'BlockBuilder':
        """Create a BlockBuilder from content string."""
        return cls(content)
    
    def content(self, text: str) -> 'BlockBuilder':
        """Set the main content of the block."""
        self._block_content = text
        return self
    
    def property(self, key: str, value: Any) -> 'BlockBuilder':
        """Add a property to this block."""
        self._block_properties[key] = value
        return self
    
    def properties(self, props: Dict[str, Any]) -> 'BlockBuilder':
        """Add multiple properties."""
        self._block_properties.update(props)
        return self
    
    def child(self, child_block: 'BlockBuilder') -> 'BlockBuilder':
        """Add a child block."""
        child_block._indent_level = self._indent_level + 1
        self._children.append(child_block)
        return self
    
    def children(self, *child_blocks: 'BlockBuilder') -> 'BlockBuilder':
        """Add multiple child blocks."""
        for child in child_blocks:
            self.child(child)
        return self
    
    def indent(self, level: int) -> 'BlockBuilder':
        """Set the indent level for this block."""
        self._indent_level = level
        return self
    
    def build(self) -> str:
        """Build the block content."""
        lines = []
        
        # Add main block content
        if self._block_content:
            # Handle multi-line content (e.g., code blocks)
            content_lines = self._block_content.split("\n")
            if content_lines:
                # First line gets the bullet
                lines.append("  " * self._indent_level + "- " + content_lines[0])
                # Subsequent lines get proper indentation (2 spaces more than bullet)
                for line in content_lines[1:]:
                    lines.append("  " * self._indent_level + "  " + line)
        
        # Add block properties if any
        if self._block_properties:
            lines.append("  " * self._indent_level + ":PROPERTIES:")
            for key, value in self._block_properties.items():
                lines.append("  " * self._indent_level + f":{key.upper()}: {value}")
            lines.append("  " * self._indent_level + ":END:")
        
        # Add children
        for child in self._children:
            child._indent_level = self._indent_level + 1
            lines.append(child.build())
        
        return "\n".join(lines)


class LogseqBuilder(ContentBuilder):
    """Main builder orchestrating the creation of Logseq content."""
    
    def __init__(self):
        super().__init__()
        self._blocks: List[Union[BlockBuilder, ContentBuilder]] = []
    
    @classmethod
    def from_content(cls, content: str) -> 'LogseqBuilder':
        """Create a LogseqBuilder from content string."""
        builder = cls()
        builder.raw(content)
        return builder
    
    @classmethod
    def from_blocks(cls, blocks: List['Block']) -> 'LogseqBuilder':
        """Create a LogseqBuilder from a list of Block objects."""
        from .parser import BuilderParser
        builder = cls()
        
        for block in blocks:
            block_builder = BuilderParser.parse_block_to_builder(block)
            if block_builder:
                builder.add(block_builder)
        
        return builder
    
    def add(self, builder: Union[BlockBuilder, ContentBuilder, str]) -> 'LogseqBuilder':
        """Add a builder or raw content."""
        if isinstance(builder, str):
            self._content.append(builder)
        else:
            self._blocks.append(builder)
        return self
    
    def block(self, content: str = "") -> BlockBuilder:
        """Create and add a new block, returning it for chaining."""
        block = BlockBuilder(content)
        self._blocks.append(block)
        return block
    
    def text(self, content: str, indent: int = 0) -> 'LogseqBuilder':
        """Add plain text content."""
        self._add_line(content, indent)
        return self
    
    def bullet(self, content: str, indent: int = 0) -> 'LogseqBuilder':
        """Add a bullet point."""
        self._add_line(f"- {content}", indent)
        return self
    
    def numbered(self, content: str, number: Optional[int] = None, indent: int = 0) -> 'LogseqBuilder':
        """Add a numbered list item."""
        prefix = f"{number}. " if number else "1. "
        self._add_line(f"{prefix}{content}", indent)
        return self
    
    def heading(self, level: int, content: str) -> 'LogseqBuilder':
        """Add a heading."""
        if not 1 <= level <= 6:
            raise ValueError("Heading level must be between 1 and 6")
        self._add_line("#" * level + " " + content)
        return self
    
    def link(self, target: str, text: Optional[str] = None) -> str:
        """Generate a link string."""
        if text:
            return f"[{text}]([[{target}]])"
        return f"[[{target}]]"
    
    def tag(self, tag_name: str) -> str:
        """Generate a tag string."""
        return f"#{tag_name}"
    
    def build(self) -> str:
        """Build the complete content."""
        result = []
        
        # Add direct content lines
        result.extend(self._content)
        
        # Add built blocks
        for builder in self._blocks:
            if hasattr(builder, 'build'):
                result.append(builder.build())
            else:
                result.append(str(builder))
        
        return "\n".join(result)


def create_id() -> str:
    """Generate a unique ID for blocks or pages."""
    return str(uuid.uuid4())[:8]


def format_date(d: Union[date, datetime, str]) -> str:
    """Format a date for Logseq."""
    if isinstance(d, str):
        return d
    elif isinstance(d, datetime):
        return d.strftime("%Y-%m-%d")
    elif isinstance(d, date):
        return d.strftime("%Y-%m-%d")
    else:
        return str(d)


def escape_content(content: str) -> str:
    """Escape special characters in content if needed."""
    # For now, just return as-is, but this could handle special Logseq characters
    return content