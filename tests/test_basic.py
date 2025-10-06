#!/usr/bin/env python3
"""
Basic tests for the Logseq Python library.

These tests cover the core functionality of the library.
"""

import unittest
import tempfile
import os
from pathlib import Path
from datetime import date, datetime

# Add the parent directory to Python path
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from logseq_py import LogseqClient, Block, Page, LogseqGraph
from logseq_py.utils import LogseqUtils


class TestLogseqModels(unittest.TestCase):
    """Test the core data models."""
    
    def test_block_creation(self):
        """Test Block creation and basic functionality."""
        block = Block(content="This is a test block #test")
        
        self.assertEqual(block.content, "This is a test block #test")
        self.assertEqual(block.level, 0)
        self.assertIn("test", block.tags)
        self.assertIsInstance(block.id, str)
        self.assertEqual(len(block.children_ids), 0)
    
    def test_block_properties(self):
        """Test Block property extraction."""
        block = Block(content="status:: todo\npriority:: high\nThis is content")
        
        self.assertIn("status", block.properties)
        self.assertIn("priority", block.properties)
        self.assertEqual(block.properties["status"], "todo")
        self.assertEqual(block.properties["priority"], "high")
    
    def test_block_links(self):
        """Test Block link extraction."""
        block = Block(content="This links to [[Page 1]] and [[Page 2]]")
        links = block.get_links()
        
        self.assertIn("Page 1", links)
        self.assertIn("Page 2", links)
        self.assertEqual(len(links), 2)
    
    def test_block_references(self):
        """Test Block reference extraction."""
        block = Block(content="This references ((block-id-1)) and ((block-id-2))")
        refs = block.get_block_references()
        
        self.assertIn("block-id-1", refs)
        self.assertIn("block-id-2", refs)
        self.assertEqual(len(refs), 2)
    
    def test_page_creation(self):
        """Test Page creation and basic functionality."""
        page = Page(name="Test Page")
        
        self.assertEqual(page.name, "Test Page")
        self.assertEqual(page.title, "Test Page")
        self.assertEqual(len(page.blocks), 0)
        self.assertFalse(page.is_journal)
    
    def test_page_with_blocks(self):
        """Test Page with blocks."""
        page = Page(name="Test Page")
        
        block1 = Block(content="First block #tag1")
        block2 = Block(content="Second block #tag2")
        
        page.add_block(block1)
        page.add_block(block2)
        
        self.assertEqual(len(page.blocks), 2)
        self.assertIn("tag1", page.tags)
        self.assertIn("tag2", page.tags)
        self.assertEqual(block1.page_name, "Test Page")
        self.assertEqual(block2.page_name, "Test Page")


class TestLogseqUtils(unittest.TestCase):
    """Test utility functions."""
    
    def test_journal_page_detection(self):
        """Test journal page name detection."""
        self.assertTrue(LogseqUtils.is_journal_page("2024-01-15"))
        self.assertTrue(LogseqUtils.is_journal_page("2024_01_15"))
        self.assertFalse(LogseqUtils.is_journal_page("Regular Page"))
        self.assertFalse(LogseqUtils.is_journal_page("2024-13-45"))  # Invalid date
    
    def test_journal_date_parsing(self):
        """Test journal date parsing."""
        date_obj = LogseqUtils.parse_journal_date("2024-01-15")
        self.assertIsInstance(date_obj, datetime)
        self.assertEqual(date_obj.year, 2024)
        self.assertEqual(date_obj.month, 1)
        self.assertEqual(date_obj.day, 15)
        
        # Test invalid date
        self.assertIsNone(LogseqUtils.parse_journal_date("Invalid Date"))
    
    def test_page_name_validation(self):
        """Test page name validation."""
        self.assertEqual(LogseqUtils.ensure_valid_page_name("Valid Name"), "Valid Name")
        self.assertEqual(LogseqUtils.ensure_valid_page_name("Name/With/Slashes"), "Name_With_Slashes")
        self.assertEqual(LogseqUtils.ensure_valid_page_name(""), "Untitled")
        self.assertEqual(LogseqUtils.ensure_valid_page_name("  Spaced  "), "Spaced")
    
    def test_block_level_detection(self):
        """Test block indentation level detection."""
        self.assertEqual(LogseqUtils.get_block_level("- Top level"), 0)
        self.assertEqual(LogseqUtils.get_block_level("\t- Level 1"), 1)
        self.assertEqual(LogseqUtils.get_block_level("\t\t- Level 2"), 2)
        self.assertEqual(LogseqUtils.get_block_level("  - Level 1 (spaces)"), 1)
        self.assertEqual(LogseqUtils.get_block_level("    - Level 2 (spaces)"), 2)
    
    def test_block_content_cleaning(self):
        """Test block content cleaning."""
        self.assertEqual(LogseqUtils.clean_block_content("- Content"), "Content")
        self.assertEqual(LogseqUtils.clean_block_content("* Content"), "Content")
        self.assertEqual(LogseqUtils.clean_block_content("+ Content"), "Content")
        self.assertEqual(LogseqUtils.clean_block_content("1. Content"), "Content")
        self.assertEqual(LogseqUtils.clean_block_content("10. Content"), "Content")
    
    def test_blocks_parsing(self):
        """Test parsing blocks from markdown content."""
        content = """- First block #tag1
\t- Nested block
- Second block
\t- Another nested
\t\t- Deeply nested"""
        
        blocks = LogseqUtils.parse_blocks_from_content(content, "Test Page")
        
        self.assertEqual(len(blocks), 5)
        self.assertEqual(blocks[0].content, "First block #tag1")
        self.assertEqual(blocks[0].level, 0)
        self.assertEqual(blocks[1].content, "Nested block")
        self.assertEqual(blocks[1].level, 1)
        self.assertEqual(blocks[4].content, "Deeply nested")
        self.assertEqual(blocks[4].level, 2)


class TestLogseqClientBasic(unittest.TestCase):
    """Test LogseqClient basic functionality with temporary files."""
    
    def setUp(self):
        """Set up temporary directory for testing."""
        self.temp_dir = tempfile.mkdtemp()
        self.graph_path = Path(self.temp_dir)
        
        # Create some test files
        test_content = """- This is a test page #test
\t- With nested content
- Another block with [[Link to Other Page]]"""
        
        test_file = self.graph_path / "Test Page.md"
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(test_content)
        
        # Create a journal file
        journal_content = """- Today I learned about Logseq #learning
- It's pretty cool #awesome"""
        
        journals_dir = self.graph_path / "journals"
        journals_dir.mkdir(exist_ok=True)
        journal_file = journals_dir / "2024-01-15.md"
        with open(journal_file, 'w', encoding='utf-8') as f:
            f.write(journal_content)
    
    def tearDown(self):
        """Clean up temporary directory."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_client_initialization(self):
        """Test LogseqClient initialization."""
        client = LogseqClient(self.graph_path)
        self.assertEqual(client.graph_path, self.graph_path)
        self.assertIsNone(client.graph)
    
    def test_graph_loading(self):
        """Test loading a graph."""
        client = LogseqClient(self.graph_path)
        graph = client.load_graph()
        
        self.assertIsInstance(graph, LogseqGraph)
        self.assertEqual(len(graph.pages), 2)  # Test Page + journal
        
        # Check if pages were loaded correctly
        test_page = graph.get_page("Test Page")
        self.assertIsNotNone(test_page)
        self.assertEqual(len(test_page.blocks), 3)
        
        # Check journal page
        journal_page = graph.get_page("2024-01-15")
        self.assertIsNotNone(journal_page)
        self.assertTrue(journal_page.is_journal)
    
    def test_page_retrieval(self):
        """Test retrieving specific pages."""
        client = LogseqClient(self.graph_path)
        client.load_graph()
        
        page = client.get_page("Test Page")
        self.assertIsNotNone(page)
        self.assertEqual(page.name, "Test Page")
        
        # Test non-existent page
        non_existent = client.get_page("Non-existent Page")
        self.assertIsNone(non_existent)
    
    def test_basic_search(self):
        """Test basic content search."""
        client = LogseqClient(self.graph_path)
        client.load_graph()
        
        results = client.search("test")
        self.assertIsInstance(results, dict)
        self.assertIn("Test Page", results)
        
        # Case-insensitive search
        results_case = client.search("TEST", case_sensitive=False)
        self.assertIn("Test Page", results_case)
        
        # Case-sensitive search
        results_sensitive = client.search("TEST", case_sensitive=True)
        self.assertEqual(len(results_sensitive), 0)
    
    def test_statistics(self):
        """Test graph statistics."""
        client = LogseqClient(self.graph_path)
        client.load_graph()
        
        stats = client.get_statistics()
        
        self.assertEqual(stats["total_pages"], 2)
        self.assertEqual(stats["journal_pages"], 1)
        self.assertEqual(stats["regular_pages"], 1)
        self.assertGreater(stats["total_blocks"], 0)
        self.assertIn("test", stats["unique_tags"])


class TestLogseqQuery(unittest.TestCase):
    """Test query functionality."""
    
    def setUp(self):
        """Set up temporary graph for testing."""
        self.temp_dir = tempfile.mkdtemp()
        self.graph_path = Path(self.temp_dir)
        
        # Create test pages
        test_pages = {
            "Project Alpha.md": "- Project alpha work #project #active\n- Important task #important",
            "Project Beta.md": "- Project beta notes #project\n- Some details",
            "Random Notes.md": "- Random thoughts #random\n- More thoughts",
            "2024-01-15.md": "- Journal entry #journal\n- Daily notes"
        }
        
        for filename, content in test_pages.items():
            if filename.startswith("2024"):
                journals_dir = self.graph_path / "journals"
                journals_dir.mkdir(exist_ok=True)
                file_path = journals_dir / filename
            else:
                file_path = self.graph_path / filename
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
        
        self.client = LogseqClient(self.graph_path)
        self.client.load_graph()
    
    def tearDown(self):
        """Clean up temporary directory."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_query_by_tag(self):
        """Test querying by tags."""
        # Query for pages with 'project' tag
        project_pages = self.client.query().pages().has_tag("project").execute()
        self.assertEqual(len(project_pages), 2)
        
        page_names = [p.name for p in project_pages]
        self.assertIn("Project Alpha", page_names)
        self.assertIn("Project Beta", page_names)
    
    def test_query_blocks(self):
        """Test querying blocks."""
        # Query for blocks with 'project' tag
        project_blocks = self.client.query().blocks().has_tag("project").execute()
        self.assertEqual(len(project_blocks), 2)
    
    def test_query_journal_pages(self):
        """Test querying journal pages."""
        journal_pages = self.client.query().pages().is_journal().execute()
        self.assertEqual(len(journal_pages), 1)
        self.assertEqual(journal_pages[0].name, "2024-01-15")
    
    def test_query_content_contains(self):
        """Test content-based queries."""
        alpha_results = self.client.query().blocks().content_contains("alpha").execute()
        self.assertEqual(len(alpha_results), 1)
        self.assertEqual(alpha_results[0].page_name, "Project Alpha")
    
    def test_query_chaining(self):
        """Test chaining multiple query conditions."""
        results = (self.client.query()
                  .pages()
                  .has_tag("project")
                  .sort_by("name")
                  .limit(1)
                  .execute())
        
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "Project Alpha")  # Alphabetically first
    
    def test_query_count(self):
        """Test query count functionality."""
        count = self.client.query().pages().has_tag("project").count()
        self.assertEqual(count, 2)
    
    def test_query_first(self):
        """Test query first() functionality."""
        first_project = self.client.query().pages().has_tag("project").first()
        self.assertIsNotNone(first_project)
        self.assertIn(first_project.name, ["Project Alpha", "Project Beta"])
    
    def test_query_exists(self):
        """Test query exists() functionality."""
        exists = self.client.query().pages().has_tag("project").exists()
        self.assertTrue(exists)
        
        not_exists = self.client.query().pages().has_tag("nonexistent").exists()
        self.assertFalse(not_exists)


if __name__ == '__main__':
    unittest.main()