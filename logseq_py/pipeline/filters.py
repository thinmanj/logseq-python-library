"""
Filtering System for Pipeline Processing

Provides flexible filtering capabilities for blocks, pages, and content
with support for property-based filtering, content matching, and custom predicates.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Callable, Union, Pattern, Set
from dataclasses import dataclass
import re
from datetime import datetime, date, timedelta
from pathlib import Path

from ..models import Block, Page
from ..builders import BlockBuilder, PageBuilder


class BlockFilter(ABC):
    """Abstract base class for block filtering."""
    
    @abstractmethod
    def matches(self, block: Block) -> bool:
        """Check if block matches this filter."""
        pass
    
    def filter_blocks(self, blocks: List[Block]) -> List[Block]:
        """Filter a list of blocks."""
        return [block for block in blocks if self.matches(block)]


class PropertyFilter(BlockFilter):
    """Filter blocks based on properties."""
    
    def __init__(self, 
                 property_name: str = None,
                 property_value: Any = None,
                 property_exists: bool = None,
                 operator: str = "equals"):
        """
        Initialize property filter.
        
        Args:
            property_name: Name of property to check
            property_value: Value to match (if specified)
            property_exists: Whether property should exist (if specified)
            operator: Comparison operator (equals, contains, starts_with, ends_with, regex, gt, lt, gte, lte)
        """
        self.property_name = property_name
        self.property_value = property_value
        self.property_exists = property_exists
        self.operator = operator
    
    def matches(self, block: Block) -> bool:
        """Check if block matches property criteria."""
        if not block.properties:
            return self.property_exists is False if self.property_exists is not None else True
        
        # Check property existence
        if self.property_exists is not None:
            has_prop = self.property_name in block.properties
            if self.property_exists != has_prop:
                return False
        
        # Check property value
        if self.property_name and self.property_value is not None:
            if self.property_name not in block.properties:
                return False
            
            actual_value = block.properties[self.property_name]
            return self._compare_values(actual_value, self.property_value, self.operator)
        
        return True
    
    def _compare_values(self, actual: Any, expected: Any, operator: str) -> bool:
        """Compare values using specified operator."""
        if operator == "equals":
            return actual == expected
        elif operator == "contains":
            return str(expected).lower() in str(actual).lower()
        elif operator == "starts_with":
            return str(actual).lower().startswith(str(expected).lower())
        elif operator == "ends_with":
            return str(actual).lower().endswith(str(expected).lower())
        elif operator == "regex":
            return bool(re.search(str(expected), str(actual), re.IGNORECASE))
        elif operator in ["gt", "gte", "lt", "lte"]:
            try:
                actual_num = float(actual)
                expected_num = float(expected)
                if operator == "gt":
                    return actual_num > expected_num
                elif operator == "gte":
                    return actual_num >= expected_num
                elif operator == "lt":
                    return actual_num < expected_num
                elif operator == "lte":
                    return actual_num <= expected_num
            except (ValueError, TypeError):
                return False
        
        return False


class ContentFilter(BlockFilter):
    """Filter blocks based on content."""
    
    def __init__(self, 
                 pattern: Union[str, Pattern] = None,
                 contains: str = None,
                 starts_with: str = None,
                 ends_with: str = None,
                 min_length: int = None,
                 max_length: int = None,
                 case_sensitive: bool = False):
        """
        Initialize content filter.
        
        Args:
            pattern: Regex pattern to match
            contains: Text that must be contained in content
            starts_with: Text that content must start with
            ends_with: Text that content must end with
            min_length: Minimum content length
            max_length: Maximum content length
            case_sensitive: Whether text matching is case sensitive
        """
        self.pattern = re.compile(pattern) if isinstance(pattern, str) else pattern
        self.contains = contains
        self.starts_with = starts_with
        self.ends_with = ends_with
        self.min_length = min_length
        self.max_length = max_length
        self.case_sensitive = case_sensitive
    
    def matches(self, block: Block) -> bool:
        """Check if block content matches criteria."""
        content = block.content or ""
        
        # Apply case sensitivity
        if not self.case_sensitive:
            content_check = content.lower()
        else:
            content_check = content
        
        # Check regex pattern
        if self.pattern and not self.pattern.search(content):
            return False
        
        # Check contains
        if self.contains:
            contains_check = self.contains if self.case_sensitive else self.contains.lower()
            if contains_check not in content_check:
                return False
        
        # Check starts with
        if self.starts_with:
            starts_check = self.starts_with if self.case_sensitive else self.starts_with.lower()
            if not content_check.startswith(starts_check):
                return False
        
        # Check ends with
        if self.ends_with:
            ends_check = self.ends_with if self.case_sensitive else self.ends_with.lower()
            if not content_check.endswith(ends_check):
                return False
        
        # Check length constraints
        if self.min_length is not None and len(content) < self.min_length:
            return False
        
        if self.max_length is not None and len(content) > self.max_length:
            return False
        
        return True


class TypeFilter(BlockFilter):
    """Filter blocks by type (e.g., task, code block, etc.)."""
    
    def __init__(self, block_types: Union[str, List[str]]):
        """
        Initialize type filter.
        
        Args:
            block_types: Block type(s) to match
        """
        if isinstance(block_types, str):
            self.block_types = {block_types}
        else:
            self.block_types = set(block_types)
    
    def matches(self, block: Block) -> bool:
        """Check if block matches type criteria."""
        # Check for task markers
        if "task" in self.block_types:
            if block.content and any(marker in block.content for marker in ["TODO", "DOING", "DONE"]):
                return True
        
        # Check for code blocks
        if "code" in self.block_types:
            if block.content and block.content.strip().startswith("```"):
                return True
        
        # Check for quotes
        if "quote" in self.block_types:
            if block.content and block.content.strip().startswith(">"):
                return True
        
        # Check for links
        if "link" in self.block_types:
            if block.content and re.search(r'\[.*?\]\(.*?\)', block.content):
                return True
        
        # Check properties for custom types
        if block.properties:
            block_type = block.properties.get("type", "").lower()
            if block_type in self.block_types:
                return True
        
        return False


class DateFilter(BlockFilter):
    """Filter blocks by date properties or content."""
    
    def __init__(self, 
                 date_property: str = None,
                 after: Union[str, date, datetime] = None,
                 before: Union[str, date, datetime] = None,
                 on: Union[str, date, datetime] = None):
        """
        Initialize date filter.
        
        Args:
            date_property: Property name containing date (if None, uses creation date)
            after: Only include blocks after this date
            before: Only include blocks before this date  
            on: Only include blocks on this exact date
        """
        self.date_property = date_property
        self.after = self._parse_date(after) if after else None
        self.before = self._parse_date(before) if before else None
        self.on = self._parse_date(on) if on else None
    
    def matches(self, block: Block) -> bool:
        """Check if block matches date criteria."""
        block_date = self._get_block_date(block)
        if not block_date:
            return False
        
        # Extract date part for comparison
        if isinstance(block_date, datetime):
            block_date = block_date.date()
        
        # Check exact date match
        if self.on and block_date != self.on:
            return False
        
        # Check after constraint
        if self.after and block_date <= self.after:
            return False
        
        # Check before constraint
        if self.before and block_date >= self.before:
            return False
        
        return True
    
    def _get_block_date(self, block: Block) -> Optional[date]:
        """Extract date from block."""
        if self.date_property and block.properties:
            date_value = block.properties.get(self.date_property)
            return self._parse_date(date_value) if date_value else None
        
        # TODO: Implement creation date extraction from block metadata if available
        return None
    
    def _parse_date(self, date_input: Any) -> Optional[date]:
        """Parse various date formats."""
        if isinstance(date_input, date):
            return date_input
        elif isinstance(date_input, datetime):
            return date_input.date()
        elif isinstance(date_input, str):
            # Try common date formats
            for fmt in ["%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y", "%Y.%m.%d"]:
                try:
                    return datetime.strptime(date_input, fmt).date()
                except ValueError:
                    continue
        
        return None


class TagFilter(BlockFilter):
    """Filter blocks by tags."""
    
    def __init__(self, 
                 tags: Union[str, List[str]],
                 mode: str = "any"):
        """
        Initialize tag filter.
        
        Args:
            tags: Tag(s) to match
            mode: "any" (match any tag), "all" (match all tags), "exact" (match exactly these tags)
        """
        if isinstance(tags, str):
            self.tags = {tags}
        else:
            self.tags = set(tags)
        self.mode = mode
    
    def matches(self, block: Block) -> bool:
        """Check if block matches tag criteria."""
        block_tags = self._extract_tags(block)
        
        if self.mode == "any":
            return bool(self.tags.intersection(block_tags))
        elif self.mode == "all":
            return self.tags.issubset(block_tags)
        elif self.mode == "exact":
            return self.tags == block_tags
        
        return False
    
    def _extract_tags(self, block: Block) -> Set[str]:
        """Extract tags from block content and properties."""
        tags = set()
        
        # Extract hashtags from content
        if block.content:
            hashtags = re.findall(r'#(\w+)', block.content)
            tags.update(hashtags)
        
        # Extract from properties
        if block.properties and "tags" in block.properties:
            prop_tags = block.properties["tags"]
            if isinstance(prop_tags, str):
                tags.add(prop_tags)
            elif isinstance(prop_tags, list):
                tags.update(prop_tags)
        
        return tags


class CompositeFilter(BlockFilter):
    """Combine multiple filters with AND/OR logic."""
    
    def __init__(self, 
                 filters: List[BlockFilter],
                 operator: str = "and"):
        """
        Initialize composite filter.
        
        Args:
            filters: List of filters to combine
            operator: "and" (all must match) or "or" (any must match)
        """
        self.filters = filters
        self.operator = operator.lower()
    
    def matches(self, block: Block) -> bool:
        """Check if block matches composite criteria."""
        if not self.filters:
            return True
        
        if self.operator == "and":
            return all(f.matches(block) for f in self.filters)
        elif self.operator == "or":
            return any(f.matches(block) for f in self.filters)
        
        return False


class PredicateFilter(BlockFilter):
    """Filter using a custom predicate function."""
    
    def __init__(self, predicate: Callable[[Block], bool]):
        """
        Initialize predicate filter.
        
        Args:
            predicate: Function that takes a block and returns True if it matches
        """
        self.predicate = predicate
    
    def matches(self, block: Block) -> bool:
        """Check if block matches predicate."""
        return self.predicate(block)


class PageFilter:
    """Filter for pages."""
    
    def __init__(self, 
                 name_pattern: Union[str, Pattern] = None,
                 has_blocks: bool = None,
                 min_blocks: int = None,
                 max_blocks: int = None,
                 properties: Dict[str, Any] = None):
        """
        Initialize page filter.
        
        Args:
            name_pattern: Pattern to match page name
            has_blocks: Whether page should have blocks
            min_blocks: Minimum number of blocks
            max_blocks: Maximum number of blocks
            properties: Properties that page should have
        """
        self.name_pattern = re.compile(name_pattern) if isinstance(name_pattern, str) else name_pattern
        self.has_blocks = has_blocks
        self.min_blocks = min_blocks
        self.max_blocks = max_blocks
        self.properties = properties or {}
    
    def matches(self, page: Page) -> bool:
        """Check if page matches criteria."""
        # Check name pattern
        if self.name_pattern and not self.name_pattern.search(page.name):
            return False
        
        # Check block constraints
        block_count = len(page.blocks) if page.blocks else 0
        
        if self.has_blocks is not None:
            if self.has_blocks and block_count == 0:
                return False
            if not self.has_blocks and block_count > 0:
                return False
        
        if self.min_blocks is not None and block_count < self.min_blocks:
            return False
        
        if self.max_blocks is not None and block_count > self.max_blocks:
            return False
        
        # Check properties
        if self.properties and page.properties:
            for key, expected_value in self.properties.items():
                if key not in page.properties or page.properties[key] != expected_value:
                    return False
        
        return True
    
    def filter_pages(self, pages: List[Page]) -> List[Page]:
        """Filter a list of pages."""
        return [page for page in pages if self.matches(page)]


# Convenience functions for creating common filters
def create_task_filter() -> TypeFilter:
    """Create filter for task blocks."""
    return TypeFilter("task")


def create_code_filter() -> TypeFilter:
    """Create filter for code blocks."""
    return TypeFilter("code")


def create_recent_filter(days: int = 7) -> DateFilter:
    """Create filter for recently created content."""
    cutoff_date = (datetime.now() - timedelta(days=days)).date()
    return DateFilter(after=cutoff_date)


def create_property_filter(name: str, value: Any = None, operator: str = "equals") -> PropertyFilter:
    """Create a property-based filter."""
    return PropertyFilter(name, value, operator=operator)


def create_content_filter(pattern: str = None, contains: str = None, **kwargs) -> ContentFilter:
    """Create a content-based filter."""
    return ContentFilter(pattern=pattern, contains=contains, **kwargs)


def create_tag_filter(tags: Union[str, List[str]], mode: str = "any") -> TagFilter:
    """Create a tag-based filter."""
    return TagFilter(tags, mode)


def create_and_filter(*filters: BlockFilter) -> CompositeFilter:
    """Create AND composite filter."""
    return CompositeFilter(list(filters), "and")


def create_or_filter(*filters: BlockFilter) -> CompositeFilter:
    """Create OR composite filter."""
    return CompositeFilter(list(filters), "or")


def create_predicate_filter(func: Callable[[Block], bool]) -> PredicateFilter:
    """Create predicate-based filter."""
    return PredicateFilter(func)