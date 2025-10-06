"""
Query builder for advanced Logseq data queries.

This module provides a fluent interface for constructing complex queries
to search and filter Logseq data.
"""

import re
from datetime import datetime, date
from typing import List, Dict, Any, Optional, Union, Set, Callable
from .models import Block, Page, LogseqGraph


class QueryBuilder:
    """Builder class for constructing complex queries against Logseq data."""
    
    def __init__(self, graph: LogseqGraph):
        """
        Initialize the query builder.
        
        Args:
            graph: LogseqGraph instance to query against
        """
        self.graph = graph
        self._filters: List[Callable] = []
        self._target = 'blocks'  # 'blocks' or 'pages'
        self._sort_by: Optional[str] = None
        self._sort_desc: bool = False
        self._limit: Optional[int] = None
    
    def pages(self) -> 'QueryBuilder':
        """Query pages instead of blocks."""
        self._target = 'pages'
        return self
    
    def blocks(self) -> 'QueryBuilder':
        """Query blocks (default behavior)."""
        self._target = 'blocks'
        return self
    
    def content_contains(self, text: str, case_sensitive: bool = False) -> 'QueryBuilder':
        """
        Filter by content containing specific text.
        
        Args:
            text: Text to search for
            case_sensitive: Whether search should be case-sensitive
        """
        def filter_func(item):
            content = item.content if hasattr(item, 'content') else ''
            search_text = text if case_sensitive else text.lower()
            search_content = content if case_sensitive else content.lower()
            return search_text in search_content
        
        self._filters.append(filter_func)
        return self
    
    def content_matches(self, pattern: str, flags: int = 0) -> 'QueryBuilder':
        """
        Filter by content matching a regex pattern.
        
        Args:
            pattern: Regular expression pattern
            flags: Regex flags (e.g., re.IGNORECASE)
        """
        compiled_pattern = re.compile(pattern, flags)
        
        def filter_func(item):
            content = item.content if hasattr(item, 'content') else ''
            return bool(compiled_pattern.search(content))
        
        self._filters.append(filter_func)
        return self
    
    def has_tag(self, tag: str) -> 'QueryBuilder':
        """
        Filter by items containing a specific tag.
        
        Args:
            tag: Tag to search for (without #)
        """
        def filter_func(item):
            return tag in getattr(item, 'tags', set())
        
        self._filters.append(filter_func)
        return self
    
    def has_any_tag(self, tags: List[str]) -> 'QueryBuilder':
        """
        Filter by items containing any of the specified tags.
        
        Args:
            tags: List of tags to search for
        """
        tag_set = set(tags)
        
        def filter_func(item):
            item_tags = getattr(item, 'tags', set())
            return bool(tag_set.intersection(item_tags))
        
        self._filters.append(filter_func)
        return self
    
    def has_all_tags(self, tags: List[str]) -> 'QueryBuilder':
        """
        Filter by items containing all of the specified tags.
        
        Args:
            tags: List of tags that must all be present
        """
        tag_set = set(tags)
        
        def filter_func(item):
            item_tags = getattr(item, 'tags', set())
            return tag_set.issubset(item_tags)
        
        self._filters.append(filter_func)
        return self
    
    def has_property(self, key: str, value: Optional[str] = None) -> 'QueryBuilder':
        """
        Filter by items having a specific property.
        
        Args:
            key: Property key
            value: Property value (if None, just checks for key existence)
        """
        def filter_func(item):
            properties = getattr(item, 'properties', {})
            if key.lower() not in properties:
                return False
            if value is None:
                return True
            return str(properties[key.lower()]).lower() == str(value).lower()
        
        self._filters.append(filter_func)
        return self
    
    def links_to(self, page_name: str) -> 'QueryBuilder':
        """
        Filter by items that link to a specific page.
        
        Args:
            page_name: Name of the page to check for links to
        """
        def filter_func(item):
            if hasattr(item, 'get_links'):
                return page_name in item.get_links()
            elif hasattr(item, 'links'):
                return page_name in item.links
            return False
        
        self._filters.append(filter_func)
        return self
    
    def in_page(self, page_name: str) -> 'QueryBuilder':
        """
        Filter blocks that are in a specific page.
        
        Args:
            page_name: Name of the page
        """
        def filter_func(item):
            return getattr(item, 'page_name', None) == page_name
        
        self._filters.append(filter_func)
        return self
    
    def is_journal(self, is_journal: bool = True) -> 'QueryBuilder':
        """
        Filter by journal pages (only works when querying pages).
        
        Args:
            is_journal: Whether to filter for journal pages
        """
        def filter_func(item):
            return getattr(item, 'is_journal', False) == is_journal
        
        self._filters.append(filter_func)
        return self
    
    def created_after(self, date_obj: Union[datetime, date]) -> 'QueryBuilder':
        """
        Filter by items created after a specific date.
        
        Args:
            date_obj: Date to compare against
        """
        if isinstance(date_obj, date) and not isinstance(date_obj, datetime):
            date_obj = datetime.combine(date_obj, datetime.min.time())
        
        def filter_func(item):
            created_at = getattr(item, 'created_at', None)
            if not created_at:
                return False
            return created_at > date_obj
        
        self._filters.append(filter_func)
        return self
    
    def created_before(self, date_obj: Union[datetime, date]) -> 'QueryBuilder':
        """
        Filter by items created before a specific date.
        
        Args:
            date_obj: Date to compare against
        """
        if isinstance(date_obj, date) and not isinstance(date_obj, datetime):
            date_obj = datetime.combine(date_obj, datetime.min.time())
        
        def filter_func(item):
            created_at = getattr(item, 'created_at', None)
            if not created_at:
                return False
            return created_at < date_obj
        
        self._filters.append(filter_func)
        return self
    
    def updated_after(self, date_obj: Union[datetime, date]) -> 'QueryBuilder':
        """
        Filter by items updated after a specific date.
        
        Args:
            date_obj: Date to compare against
        """
        if isinstance(date_obj, date) and not isinstance(date_obj, datetime):
            date_obj = datetime.combine(date_obj, datetime.min.time())
        
        def filter_func(item):
            updated_at = getattr(item, 'updated_at', None)
            if not updated_at:
                return False
            return updated_at > date_obj
        
        self._filters.append(filter_func)
        return self
    
    def level(self, level: int) -> 'QueryBuilder':
        """
        Filter blocks by indentation level.
        
        Args:
            level: Indentation level (0 = top-level)
        """
        def filter_func(item):
            return getattr(item, 'level', None) == level
        
        self._filters.append(filter_func)
        return self
    
    def min_level(self, level: int) -> 'QueryBuilder':
        """
        Filter blocks by minimum indentation level.
        
        Args:
            level: Minimum indentation level
        """
        def filter_func(item):
            item_level = getattr(item, 'level', None)
            return item_level is not None and item_level >= level
        
        self._filters.append(filter_func)
        return self
    
    def max_level(self, level: int) -> 'QueryBuilder':
        """
        Filter blocks by maximum indentation level.
        
        Args:
            level: Maximum indentation level
        """
        def filter_func(item):
            item_level = getattr(item, 'level', None)
            return item_level is not None and item_level <= level
        
        self._filters.append(filter_func)
        return self
    
    def has_children(self) -> 'QueryBuilder':
        """Filter blocks that have child blocks."""
        def filter_func(item):
            children_ids = getattr(item, 'children_ids', [])
            return len(children_ids) > 0
        
        self._filters.append(filter_func)
        return self
    
    def is_orphan(self) -> 'QueryBuilder':
        """Filter blocks that have no parent (top-level blocks)."""
        def filter_func(item):
            return getattr(item, 'parent_id', None) is None
        
        self._filters.append(filter_func)
        return self
    
    def custom_filter(self, filter_func: Callable) -> 'QueryBuilder':
        """
        Add a custom filter function.
        
        Args:
            filter_func: Function that takes an item and returns bool
        """
        self._filters.append(filter_func)
        return self
    
    def sort_by(self, field: str, desc: bool = False) -> 'QueryBuilder':
        """
        Sort results by a field.
        
        Args:
            field: Field name to sort by
            desc: Whether to sort in descending order
        """
        self._sort_by = field
        self._sort_desc = desc
        return self
    
    def limit(self, count: int) -> 'QueryBuilder':
        """
        Limit the number of results.
        
        Args:
            count: Maximum number of results to return
        """
        self._limit = count
        return self
    
    def execute(self) -> Union[List[Block], List[Page]]:
        """
        Execute the query and return results.
        
        Returns:
            List of matching blocks or pages
        """
        # Get the items to query
        if self._target == 'pages':
            items = list(self.graph.pages.values())
        else:
            items = list(self.graph.blocks.values())
        
        # Apply filters
        for filter_func in self._filters:
            items = [item for item in items if filter_func(item)]
        
        # Apply sorting
        if self._sort_by:
            def get_sort_key(item):
                value = getattr(item, self._sort_by, None)
                # Handle None values by putting them last
                if value is None:
                    return (1, '')  # Sort None values last
                if isinstance(value, str):
                    return (0, value.lower())
                return (0, value)
            
            items.sort(key=get_sort_key, reverse=self._sort_desc)
        
        # Apply limit
        if self._limit:
            items = items[:self._limit]
        
        return items
    
    def count(self) -> int:
        """
        Count the number of matching items without returning them.
        
        Returns:
            Number of items that match the query
        """
        return len(self.execute())
    
    def first(self) -> Optional[Union[Block, Page]]:
        """
        Get the first matching item.
        
        Returns:
            First matching item or None if no matches
        """
        results = self.limit(1).execute()
        return results[0] if results else None
    
    def exists(self) -> bool:
        """
        Check if any items match the query.
        
        Returns:
            True if at least one item matches, False otherwise
        """
        return self.count() > 0


class QueryStats:
    """Helper class for computing statistics on query results."""
    
    @staticmethod
    def tag_frequency(items: List[Union[Block, Page]]) -> Dict[str, int]:
        """
        Compute tag frequency from a list of items.
        
        Args:
            items: List of blocks or pages
            
        Returns:
            Dictionary mapping tags to their frequency
        """
        tag_counts = {}
        
        for item in items:
            tags = getattr(item, 'tags', set())
            for tag in tags:
                tag_counts[tag] = tag_counts.get(tag, 0) + 1
        
        return dict(sorted(tag_counts.items(), key=lambda x: x[1], reverse=True))
    
    @staticmethod
    def page_distribution(blocks: List[Block]) -> Dict[str, int]:
        """
        Compute page distribution for a list of blocks.
        
        Args:
            blocks: List of blocks
            
        Returns:
            Dictionary mapping page names to block counts
        """
        page_counts = {}
        
        for block in blocks:
            page_name = block.page_name
            if page_name:
                page_counts[page_name] = page_counts.get(page_name, 0) + 1
        
        return dict(sorted(page_counts.items(), key=lambda x: x[1], reverse=True))
    
    @staticmethod
    def level_distribution(blocks: List[Block]) -> Dict[int, int]:
        """
        Compute level distribution for a list of blocks.
        
        Args:
            blocks: List of blocks
            
        Returns:
            Dictionary mapping levels to block counts
        """
        level_counts = {}
        
        for block in blocks:
            level = block.level
            level_counts[level] = level_counts.get(level, 0) + 1
        
        return dict(sorted(level_counts.items()))
    
    @staticmethod
    def property_frequency(items: List[Union[Block, Page]]) -> Dict[str, int]:
        """
        Compute property frequency from a list of items.
        
        Args:
            items: List of blocks or pages
            
        Returns:
            Dictionary mapping property keys to their frequency
        """
        prop_counts = {}
        
        for item in items:
            properties = getattr(item, 'properties', {})
            for key in properties.keys():
                prop_counts[key] = prop_counts.get(key, 0) + 1
        
        return dict(sorted(prop_counts.items(), key=lambda x: x[1], reverse=True))