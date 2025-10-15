"""
Unit tests for core logseq_py models.
"""

import pytest
from datetime import datetime
from typing import Dict, Any

from logseq_py.models import Block, Page


class TestBlock:
    """Test cases for Block model."""

    def test_block_creation(self):
        """Test basic block creation."""
        block = Block(content="Test content")
        
        assert block.content == "Test content"
        assert block.id is None
        assert block.properties is None
        assert block.children is None

    def test_block_with_properties(self):
        """Test block creation with properties."""
        properties = {"type": "task", "priority": "high"}
        block = Block(content="TODO: Test task", properties=properties)
        
        assert block.content == "TODO: Test task"
        assert block.properties == properties
        assert block.properties["type"] == "task"
        assert block.properties["priority"] == "high"

    def test_block_with_children(self):
        """Test block with child blocks."""
        child1 = Block(content="Child 1")
        child2 = Block(content="Child 2")
        parent = Block(content="Parent", children=[child1, child2])
        
        assert len(parent.children) == 2
        assert parent.children[0].content == "Child 1"
        assert parent.children[1].content == "Child 2"

    def test_block_equality(self):
        """Test block equality comparison."""
        block1 = Block(id="1", content="Same content")
        block2 = Block(id="1", content="Same content")
        block3 = Block(id="2", content="Same content")
        
        assert block1 == block2
        assert block1 != block3

    def test_block_equality_without_id(self):
        """Test block equality when no ID is present."""
        block1 = Block(content="Same content")
        block2 = Block(content="Same content")
        block3 = Block(content="Different content")
        
        # Without IDs, blocks are equal if all attributes match
        assert block1 == block2
        assert block1 != block3

    def test_block_repr(self):
        """Test block string representation."""
        block = Block(id="test-id", content="Test content")
        repr_str = repr(block)
        
        assert "Block" in repr_str
        assert "test-id" in repr_str
        assert "Test content" in repr_str

    def test_block_with_none_content(self):
        """Test block with None content."""
        block = Block(content=None)
        assert block.content is None

    def test_block_property_access(self):
        """Test accessing block properties."""
        properties = {"tag": "important", "date": "2024-01-15"}
        block = Block(content="Test", properties=properties)
        
        assert block.properties["tag"] == "important"
        assert block.properties["date"] == "2024-01-15"

    def test_block_nested_children(self):
        """Test block with nested child hierarchy."""
        grandchild = Block(content="Grandchild")
        child = Block(content="Child", children=[grandchild])
        parent = Block(content="Parent", children=[child])
        
        assert len(parent.children) == 1
        assert len(parent.children[0].children) == 1
        assert parent.children[0].children[0].content == "Grandchild"


class TestPage:
    """Test cases for Page model."""

    def test_page_creation(self):
        """Test basic page creation."""
        page = Page(name="Test Page")
        
        assert page.name == "Test Page"
        assert page.blocks is None
        assert page.properties is None

    def test_page_with_blocks(self):
        """Test page creation with blocks."""
        blocks = [
            Block(content="First block"),
            Block(content="Second block")
        ]
        page = Page(name="Test Page", blocks=blocks)
        
        assert page.name == "Test Page"
        assert len(page.blocks) == 2
        assert page.blocks[0].content == "First block"
        assert page.blocks[1].content == "Second block"

    def test_page_with_properties(self):
        """Test page with properties."""
        properties = {"type": "daily", "date": "2024-01-15"}
        page = Page(name="Daily Notes", properties=properties)
        
        assert page.properties == properties
        assert page.properties["type"] == "daily"
        assert page.properties["date"] == "2024-01-15"

    def test_page_equality(self):
        """Test page equality comparison."""
        page1 = Page(name="Same Name")
        page2 = Page(name="Same Name") 
        page3 = Page(name="Different Name")
        
        assert page1 == page2
        assert page1 != page3

    def test_page_with_same_name_different_content(self):
        """Test pages with same name but different content."""
        blocks1 = [Block(content="Block 1")]
        blocks2 = [Block(content="Block 2")]
        
        page1 = Page(name="Same Name", blocks=blocks1)
        page2 = Page(name="Same Name", blocks=blocks2)
        
        # Pages are equal by name, not by content
        assert page1 == page2

    def test_page_repr(self):
        """Test page string representation."""
        page = Page(name="Test Page")
        repr_str = repr(page)
        
        assert "Page" in repr_str
        assert "Test Page" in repr_str

    def test_page_with_empty_blocks(self):
        """Test page with empty blocks list."""
        page = Page(name="Empty Page", blocks=[])
        
        assert page.blocks == []
        assert len(page.blocks) == 0

    def test_page_block_access(self):
        """Test accessing blocks in a page."""
        blocks = [
            Block(id="1", content="First"),
            Block(id="2", content="Second"),
            Block(id="3", content="Third")
        ]
        page = Page(name="Test Page", blocks=blocks)
        
        assert len(page.blocks) == 3
        assert page.blocks[0].id == "1"
        assert page.blocks[1].content == "Second"
        assert page.blocks[2].content == "Third"

    def test_page_property_access(self):
        """Test accessing page properties."""
        properties = {
            "created": "2024-01-15T10:00:00Z",
            "modified": "2024-01-15T12:00:00Z",
            "tags": ["important", "project"]
        }
        page = Page(name="Project Page", properties=properties)
        
        assert page.properties["created"] == "2024-01-15T10:00:00Z"
        assert page.properties["tags"] == ["important", "project"]
        assert len(page.properties["tags"]) == 2

    def test_page_complex_structure(self):
        """Test page with complex block structure."""
        # Create a page with nested blocks
        child_blocks = [
            Block(content="Sub-item 1"),
            Block(content="Sub-item 2")
        ]
        
        main_blocks = [
            Block(content="Header block"),
            Block(content="Parent block", children=child_blocks),
            Block(content="Footer block")
        ]
        
        properties = {"type": "outline", "level": "detailed"}
        page = Page(name="Complex Page", blocks=main_blocks, properties=properties)
        
        assert len(page.blocks) == 3
        assert page.blocks[1].children is not None
        assert len(page.blocks[1].children) == 2
        assert page.properties["type"] == "outline"


class TestModelInteractions:
    """Test interactions between models."""

    def test_page_block_relationship(self):
        """Test relationship between pages and blocks."""
        blocks = [
            Block(id="1", content="Block 1", properties={"order": 1}),
            Block(id="2", content="Block 2", properties={"order": 2})
        ]
        
        page = Page(
            name="Test Page",
            blocks=blocks,
            properties={"block_count": len(blocks)}
        )
        
        # Test that we can access blocks from page
        assert len(page.blocks) == page.properties["block_count"]
        assert page.blocks[0].properties["order"] == 1
        assert page.blocks[1].properties["order"] == 2

    def test_hierarchical_block_structure(self):
        """Test complex hierarchical block structure."""
        # Create a tree structure: Parent -> [Child1, Child2 -> [Grandchild]]
        grandchild = Block(content="Grandchild block")
        child1 = Block(content="Child 1")
        child2 = Block(content="Child 2", children=[grandchild])
        parent = Block(content="Parent block", children=[child1, child2])
        
        page = Page(name="Hierarchical Page", blocks=[parent])
        
        # Test navigation through hierarchy
        assert len(page.blocks) == 1
        parent_block = page.blocks[0]
        assert len(parent_block.children) == 2
        assert parent_block.children[0].content == "Child 1"
        assert parent_block.children[1].content == "Child 2"
        assert len(parent_block.children[1].children) == 1
        assert parent_block.children[1].children[0].content == "Grandchild block"

    def test_model_with_various_data_types(self):
        """Test models with various property data types."""
        properties = {
            "string_prop": "text value",
            "int_prop": 42,
            "float_prop": 3.14,
            "bool_prop": True,
            "list_prop": ["item1", "item2", "item3"],
            "dict_prop": {"nested": "value"},
            "none_prop": None
        }
        
        block = Block(content="Test block", properties=properties)
        page = Page(name="Test page", blocks=[block], properties=properties.copy())
        
        # Test that all data types are preserved
        assert isinstance(block.properties["string_prop"], str)
        assert isinstance(block.properties["int_prop"], int)
        assert isinstance(block.properties["float_prop"], float)
        assert isinstance(block.properties["bool_prop"], bool)
        assert isinstance(block.properties["list_prop"], list)
        assert isinstance(block.properties["dict_prop"], dict)
        assert block.properties["none_prop"] is None
        
        # Test same for page
        assert page.properties["list_prop"] == ["item1", "item2", "item3"]
        assert page.properties["dict_prop"]["nested"] == "value"

    def test_empty_and_none_handling(self):
        """Test handling of empty and None values."""
        # Test various empty/None scenarios
        block1 = Block(content="")
        block2 = Block(content=None)
        block3 = Block(content="content", properties={})
        block4 = Block(content="content", properties=None)
        
        page1 = Page(name="", blocks=None)
        page2 = Page(name="name", blocks=[])
        
        assert block1.content == ""
        assert block2.content is None
        assert block3.properties == {}
        assert block4.properties is None
        
        assert page1.name == ""
        assert page1.blocks is None
        assert page2.blocks == []