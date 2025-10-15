"""
Unit tests for pipeline filtering system.
"""

import pytest
from datetime import datetime, date

from logseq_py.models import Block, Page
from logseq_py.pipeline.filters import (
    PropertyFilter, ContentFilter, TypeFilter, DateFilter, TagFilter,
    CompositeFilter, PredicateFilter, PageFilter,
    create_task_filter, create_content_filter, create_and_filter, create_or_filter
)


class TestPropertyFilter:
    """Test PropertyFilter functionality."""
    
    def test_property_exists(self):
        """Test filtering by property existence."""
        block_with_prop = Block(content="Test", properties={"type": "task"})
        block_without_prop = Block(content="Test", properties={})
        block_no_properties = Block(content="Test", properties=None)
        
        filter_exists = PropertyFilter(property_name="type", property_exists=True)
        filter_not_exists = PropertyFilter(property_name="type", property_exists=False)
        
        assert filter_exists.matches(block_with_prop) is True
        assert filter_exists.matches(block_without_prop) is False
        assert filter_exists.matches(block_no_properties) is False
        
        assert filter_not_exists.matches(block_with_prop) is False
        assert filter_not_exists.matches(block_without_prop) is True
        assert filter_not_exists.matches(block_no_properties) is True
    
    def test_property_value_equals(self):
        """Test filtering by property value equality."""
        block1 = Block(content="Test", properties={"priority": "high"})
        block2 = Block(content="Test", properties={"priority": "low"})
        block3 = Block(content="Test", properties={"type": "task"})
        
        filter_high = PropertyFilter(property_name="priority", property_value="high")
        
        assert filter_high.matches(block1) is True
        assert filter_high.matches(block2) is False
        assert filter_high.matches(block3) is False
    
    def test_property_value_contains(self):
        """Test filtering by property value containment."""
        block1 = Block(content="Test", properties={"description": "important task"})
        block2 = Block(content="Test", properties={"description": "simple note"})
        
        filter_contains = PropertyFilter(
            property_name="description",
            property_value="task",
            operator="contains"
        )
        
        assert filter_contains.matches(block1) is True
        assert filter_contains.matches(block2) is False
    
    def test_property_numeric_comparison(self):
        """Test numeric property comparisons."""
        block1 = Block(content="Test", properties={"score": 85})
        block2 = Block(content="Test", properties={"score": 65})
        block3 = Block(content="Test", properties={"score": "85"})  # String number
        
        filter_gte = PropertyFilter(property_name="score", property_value=80, operator="gte")
        filter_lt = PropertyFilter(property_name="score", property_value=70, operator="lt")
        
        assert filter_gte.matches(block1) is True
        assert filter_gte.matches(block2) is False
        assert filter_gte.matches(block3) is True  # String converted to number
        
        assert filter_lt.matches(block1) is False
        assert filter_lt.matches(block2) is True


class TestContentFilter:
    """Test ContentFilter functionality."""
    
    def test_content_contains(self):
        """Test filtering by content containment."""
        block1 = Block(content="TODO: Complete the task")
        block2 = Block(content="This is a regular note")
        
        filter_todo = ContentFilter(contains="TODO")
        
        assert filter_todo.matches(block1) is True
        assert filter_todo.matches(block2) is False
    
    def test_content_pattern(self):
        """Test filtering by regex pattern."""
        block1 = Block(content="Visit https://example.com for more info")
        block2 = Block(content="No links in this block")
        
        filter_url = ContentFilter(pattern=r'https?://[^\s]+')
        
        assert filter_url.matches(block1) is True
        assert filter_url.matches(block2) is False
    
    def test_content_length(self):
        """Test filtering by content length."""
        short_block = Block(content="Short")
        long_block = Block(content="This is a much longer block of text content")
        
        filter_min = ContentFilter(min_length=20)
        filter_max = ContentFilter(max_length=10)
        
        assert filter_min.matches(short_block) is False
        assert filter_min.matches(long_block) is True
        
        assert filter_max.matches(short_block) is True
        assert filter_max.matches(long_block) is False
    
    def test_case_sensitivity(self):
        """Test case sensitive/insensitive filtering."""
        block = Block(content="TODO: Important Task")
        
        filter_sensitive = ContentFilter(contains="todo", case_sensitive=True)
        filter_insensitive = ContentFilter(contains="todo", case_sensitive=False)
        
        assert filter_sensitive.matches(block) is False
        assert filter_insensitive.matches(block) is True
    
    def test_starts_with_ends_with(self):
        """Test starts_with and ends_with filtering."""
        block = Block(content="## Header content here")
        
        filter_starts = ContentFilter(starts_with="##")
        filter_ends = ContentFilter(ends_with="here")
        
        assert filter_starts.matches(block) is True
        assert filter_ends.matches(block) is True
        
        filter_wrong_start = ContentFilter(starts_with="###")
        filter_wrong_end = ContentFilter(ends_with="there")
        
        assert filter_wrong_start.matches(block) is False
        assert filter_wrong_end.matches(block) is False


class TestTypeFilter:
    """Test TypeFilter functionality."""
    
    def test_task_detection(self):
        """Test detection of task blocks."""
        todo_block = Block(content="TODO: Complete project")
        doing_block = Block(content="DOING: Working on feature")
        done_block = Block(content="DONE: Finished documentation")
        regular_block = Block(content="Just a regular note")
        
        task_filter = TypeFilter("task")
        
        assert task_filter.matches(todo_block) is True
        assert task_filter.matches(doing_block) is True
        assert task_filter.matches(done_block) is True
        assert task_filter.matches(regular_block) is False
    
    def test_code_detection(self):
        """Test detection of code blocks."""
        code_block = Block(content="```python\nprint('hello')\n```")
        regular_block = Block(content="This is regular text")
        
        code_filter = TypeFilter("code")
        
        assert code_filter.matches(code_block) is True
        assert code_filter.matches(regular_block) is False
    
    def test_quote_detection(self):
        """Test detection of quote blocks."""
        quote_block = Block(content="> This is a quote")
        regular_block = Block(content="This is regular text")
        
        quote_filter = TypeFilter("quote")
        
        assert quote_filter.matches(quote_block) is True
        assert quote_filter.matches(regular_block) is False
    
    def test_multiple_types(self):
        """Test filtering with multiple types."""
        todo_block = Block(content="TODO: Task")
        code_block = Block(content="```python\ncode\n```")
        regular_block = Block(content="Regular text")
        
        multi_filter = TypeFilter(["task", "code"])
        
        assert multi_filter.matches(todo_block) is True
        assert multi_filter.matches(code_block) is True
        assert multi_filter.matches(regular_block) is False


class TestTagFilter:
    """Test TagFilter functionality."""
    
    def test_hashtag_detection(self):
        """Test detection of hashtags in content."""
        tagged_block = Block(content="This is #important and #urgent")
        untagged_block = Block(content="This has no tags")
        
        tag_filter = TagFilter("important")
        
        assert tag_filter.matches(tagged_block) is True
        assert tag_filter.matches(untagged_block) is False
    
    def test_property_tags(self):
        """Test detection of tags in properties."""
        block_with_tags = Block(
            content="Content",
            properties={"tags": ["work", "project"]}
        )
        
        tag_filter = TagFilter("work")
        
        assert tag_filter.matches(block_with_tags) is True
    
    def test_tag_modes(self):
        """Test different tag matching modes."""
        block = Block(content="#python #programming #tutorial")
        
        any_filter = TagFilter(["python", "nonexistent"], mode="any")
        all_filter = TagFilter(["python", "programming"], mode="all")
        all_missing_filter = TagFilter(["python", "nonexistent"], mode="all")
        
        assert any_filter.matches(block) is True
        assert all_filter.matches(block) is True
        assert all_missing_filter.matches(block) is False


class TestCompositeFilter:
    """Test CompositeFilter functionality."""
    
    def test_and_filter(self):
        """Test AND logic combining filters."""
        block1 = Block(content="TODO: #important task", properties={"priority": "high"})
        block2 = Block(content="TODO: regular task", properties={"priority": "low"})
        block3 = Block(content="Regular #important note", properties={"priority": "high"})
        
        task_filter = TypeFilter("task")
        tag_filter = TagFilter("important")
        priority_filter = PropertyFilter(property_name="priority", property_value="high")
        
        and_filter = CompositeFilter([task_filter, tag_filter, priority_filter], "and")
        
        assert and_filter.matches(block1) is True  # Matches all
        assert and_filter.matches(block2) is False  # Missing tag and high priority
        assert and_filter.matches(block3) is False  # Not a task
    
    def test_or_filter(self):
        """Test OR logic combining filters."""
        block1 = Block(content="TODO: task")
        block2 = Block(content="Regular note", properties={"priority": "high"})
        block3 = Block(content="Regular note", properties={"priority": "low"})
        
        task_filter = TypeFilter("task")
        priority_filter = PropertyFilter(property_name="priority", property_value="high")
        
        or_filter = CompositeFilter([task_filter, priority_filter], "or")
        
        assert or_filter.matches(block1) is True  # Is a task
        assert or_filter.matches(block2) is True  # Has high priority
        assert or_filter.matches(block3) is False  # Neither condition


class TestPredicateFilter:
    """Test PredicateFilter functionality."""
    
    def test_custom_predicate(self):
        """Test custom predicate function."""
        block1 = Block(content="Short")
        block2 = Block(content="This is a much longer content block")
        
        def long_content(block):
            return len(block.content or "") > 20
        
        predicate_filter = PredicateFilter(long_content)
        
        assert predicate_filter.matches(block1) is False
        assert predicate_filter.matches(block2) is True
    
    def test_predicate_with_properties(self):
        """Test predicate using block properties."""
        block1 = Block(content="Test", properties={"score": 85, "reviewed": True})
        block2 = Block(content="Test", properties={"score": 60, "reviewed": False})
        
        def high_score_reviewed(block):
            props = block.properties or {}
            return props.get("score", 0) > 80 and props.get("reviewed", False)
        
        predicate_filter = PredicateFilter(high_score_reviewed)
        
        assert predicate_filter.matches(block1) is True
        assert predicate_filter.matches(block2) is False


class TestPageFilter:
    """Test PageFilter functionality."""
    
    def test_name_pattern(self):
        """Test filtering pages by name pattern."""
        daily_page = Page(name="Daily Notes - 2024-01-15")
        project_page = Page(name="Project Planning")
        
        daily_filter = PageFilter(name_pattern=r"Daily Notes")
        
        assert daily_filter.matches(daily_page) is True
        assert daily_filter.matches(project_page) is False
    
    def test_block_count_filtering(self):
        """Test filtering by block count."""
        empty_page = Page(name="Empty", blocks=[])
        small_page = Page(name="Small", blocks=[Block(content="One block")])
        large_page = Page(name="Large", blocks=[
            Block(content="Block 1"),
            Block(content="Block 2"), 
            Block(content="Block 3")
        ])
        
        min_filter = PageFilter(min_blocks=2)
        max_filter = PageFilter(max_blocks=1)
        has_blocks_filter = PageFilter(has_blocks=True)
        
        assert min_filter.matches(large_page) is True
        assert min_filter.matches(small_page) is False
        
        assert max_filter.matches(empty_page) is True
        assert max_filter.matches(large_page) is False
        
        assert has_blocks_filter.matches(small_page) is True
        assert has_blocks_filter.matches(empty_page) is False


class TestFilterFactoryFunctions:
    """Test filter factory functions."""
    
    def test_create_task_filter(self):
        """Test task filter creation."""
        todo_block = Block(content="TODO: Complete task")
        regular_block = Block(content="Regular note")
        
        task_filter = create_task_filter()
        
        assert task_filter.matches(todo_block) is True
        assert task_filter.matches(regular_block) is False
    
    def test_create_content_filter(self):
        """Test content filter creation."""
        url_block = Block(content="Visit https://example.com")
        regular_block = Block(content="No links here")
        
        url_filter = create_content_filter(pattern=r'https?://')
        
        assert url_filter.matches(url_block) is True
        assert url_filter.matches(regular_block) is False
    
    def test_create_composite_filters(self):
        """Test composite filter creation."""
        block = Block(content="TODO: #important task")
        
        task_filter = create_task_filter()
        tag_filter = TagFilter("important")
        
        and_filter = create_and_filter(task_filter, tag_filter)
        or_filter = create_or_filter(task_filter, tag_filter)
        
        assert and_filter.matches(block) is True
        assert or_filter.matches(block) is True
    
    def test_filter_blocks_method(self):
        """Test filtering multiple blocks."""
        blocks = [
            Block(content="TODO: Task 1"),
            Block(content="Regular note"),
            Block(content="DONE: Task 2"),
            Block(content="Another note")
        ]
        
        task_filter = create_task_filter()
        filtered_blocks = task_filter.filter_blocks(blocks)
        
        assert len(filtered_blocks) == 2
        assert "TODO" in filtered_blocks[0].content
        assert "DONE" in filtered_blocks[1].content