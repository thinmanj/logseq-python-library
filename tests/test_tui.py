"""
Tests for the TUI (Terminal User Interface) module.
"""

import pytest
from pathlib import Path
from datetime import date, timedelta
from unittest.mock import Mock, MagicMock, patch

# Skip all TUI tests if textual is not installed
textual = pytest.importorskip("textual")

from logseq_py.tui import (
    PageList, PageEditor, JournalView, TemplateManager, 
    SearchPane, LogseqTUI, launch_tui
)
from logseq_py.models import Page, Block, Template
from logseq_py.logseq_client import LogseqClient


class TestPageEditor:
    """Test PageEditor widget."""
    
    def test_page_editor_compose(self):
        """Test PageEditor composition."""
        editor = PageEditor()
        # Should have title, content, and buttons
        assert editor is not None
        assert editor.current_page is None
    
    def test_page_editor_get_content(self):
        """Test getting editor content."""
        editor = PageEditor()
        # Mock the TextArea
        with patch.object(editor, 'query_one') as mock_query:
            mock_textarea = Mock()
            mock_textarea.text = "Test content"
            mock_query.return_value = mock_textarea
            
            content = editor.get_content()
            assert content == "Test content"


class TestJournalView:
    """Test JournalView widget."""
    
    def test_journal_view_compose(self):
        """Test JournalView composition."""
        view = JournalView()
        assert view.current_date == date.today()
    
    def test_watch_current_date(self):
        """Test date change watcher."""
        view = JournalView()
        test_date = date(2025, 10, 28)
        
        # Mock the query_one method
        with patch.object(view, 'query_one') as mock_query:
            mock_static = Mock()
            mock_query.return_value = mock_static
            
            view.watch_current_date(test_date)
            
            # Verify update was called with formatted date
            mock_static.update.assert_called_once()
            call_args = str(mock_static.update.call_args)
            assert "2025-10-28" in call_args


class TestTemplateManager:
    """Test TemplateManager widget."""
    
    def test_template_manager_compose(self):
        """Test TemplateManager composition."""
        manager = TemplateManager()
        assert manager is not None


class TestSearchPane:
    """Test SearchPane widget."""
    
    def test_search_pane_compose(self):
        """Test SearchPane composition."""
        pane = SearchPane()
        assert pane is not None


class TestLogseqTUI:
    """Test main LogseqTUI application."""
    
    @pytest.fixture
    def temp_graph(self, tmp_path):
        """Create a temporary graph for testing."""
        graph_path = tmp_path / "test_graph"
        graph_path.mkdir()
        
        # Create journals directory
        (graph_path / "journals").mkdir()
        
        # Create a test journal
        journal_file = graph_path / "journals" / "2025-10-28.md"
        journal_file.write_text("- Test journal entry\n- TODO Test task\n")
        
        # Create pages directory
        (graph_path / "pages").mkdir()
        
        # Create a test page
        page_file = graph_path / "pages" / "Test_Page.md"
        page_file.write_text("- Test page content\n")
        
        # Create a template
        template_file = graph_path / "pages" / "template__Test_Template.md"
        template_file.write_text("template:: true\n\n- {{variable}} template\n")
        
        return graph_path
    
    def test_tui_init(self, temp_graph):
        """Test TUI initialization."""
        app = LogseqTUI(temp_graph)
        assert app.graph_path == temp_graph
        assert app.client is None
        assert app.current_page is None
        assert app.current_template is None
    
    def test_tui_title(self, temp_graph):
        """Test TUI title."""
        app = LogseqTUI(temp_graph)
        assert app.TITLE == "Logseq TUI"
        assert app.SUB_TITLE == "Terminal Knowledge Manager"
    
    def test_tui_bindings(self, temp_graph):
        """Test TUI keyboard bindings."""
        app = LogseqTUI(temp_graph)
        bindings = {b.key for b in app.BINDINGS}
        
        assert "q" in bindings
        assert "ctrl+s" in bindings
        assert "ctrl+j" in bindings
        assert "ctrl+p" in bindings
        assert "ctrl+t" in bindings
        assert "ctrl+f" in bindings
        assert "ctrl+n" in bindings


class TestLaunchTUI:
    """Test TUI launch function."""
    
    def test_launch_tui_creates_app(self):
        """Test that launch_tui creates an app instance."""
        test_path = "/tmp/test_graph"
        
        with patch('logseq_py.tui.LogseqTUI') as mock_tui_class:
            mock_app = Mock()
            mock_tui_class.return_value = mock_app
            
            launch_tui(test_path)
            
            mock_tui_class.assert_called_once_with(Path(test_path))
            mock_app.run.assert_called_once()


class TestTUIIntegration:
    """Integration tests for TUI with LogseqClient."""
    
    @pytest.fixture
    def graph_with_content(self, tmp_path):
        """Create a graph with various content types."""
        graph_path = tmp_path / "integration_graph"
        graph_path.mkdir()
        
        # Create structure
        (graph_path / "journals").mkdir()
        (graph_path / "pages").mkdir()
        
        # Add multiple journals
        for i in range(5):
            date_str = (date.today() - timedelta(days=i)).strftime("%Y-%m-%d")
            journal = graph_path / "journals" / f"{date_str}.md"
            journal.write_text(f"- Entry for {date_str}\n")
        
        # Add pages with namespaces
        (graph_path / "pages" / "project__backend.md").write_text(
            "- Backend project\n"
        )
        (graph_path / "pages" / "project__frontend.md").write_text(
            "- Frontend project\n"
        )
        
        # Add template
        (graph_path / "pages" / "template__Meeting.md").write_text(
            "template:: true\n\n- Meeting: {{topic}}\n  - Date: {{date}}\n"
        )
        
        return graph_path
    
    def test_load_graph_integration(self, graph_with_content):
        """Test loading a real graph in TUI."""
        app = LogseqTUI(graph_with_content)
        app.client = LogseqClient(graph_with_content)
        
        # Load graph
        graph = app.client.load_graph()
        
        assert len(graph.pages) > 0
        assert len(graph.get_journal_pages()) == 5
    
    def test_search_functionality(self, graph_with_content):
        """Test search across graph."""
        app = LogseqTUI(graph_with_content)
        app.client = LogseqClient(graph_with_content)
        graph = app.client.load_graph()
        
        # Search for content
        results = app.client.search("Entry")
        assert len(results) > 0
    
    def test_template_detection(self, graph_with_content):
        """Test template detection."""
        app = LogseqTUI(graph_with_content)
        app.client = LogseqClient(graph_with_content)
        graph = app.client.load_graph()
        
        templates = graph.get_all_templates()
        assert len(templates) > 0
        
        # Check template has variables
        template = templates[0]
        assert "topic" in template.variables or "date" in template.variables


class TestTUIEditing:
    """Test TUI editing operations."""
    
    @pytest.fixture
    def editable_graph(self, tmp_path):
        """Create a graph for editing tests."""
        graph_path = tmp_path / "edit_graph"
        graph_path.mkdir()
        (graph_path / "journals").mkdir()
        (graph_path / "pages").mkdir()
        
        # Create a page to edit
        page_file = graph_path / "pages" / "Editable.md"
        page_file.write_text("- Original content\n")
        
        return graph_path
    
    def test_page_save_operation(self, editable_graph):
        """Test saving a page through TUI."""
        client = LogseqClient(editable_graph)
        graph = client.load_graph()
        
        # Get page
        page = client.get_page("Editable")
        assert page is not None
        
        # Modify content
        new_content = "- Modified content\n- New bullet\n"
        
        # Create page with new content
        client.create_page("Editable", new_content)
        
        # Reload and verify
        graph = client.load_graph(force_reload=True)
        page = client.get_page("Editable")
        assert "Modified content" in page.blocks[0].content
    
    def test_journal_creation(self, editable_graph):
        """Test creating journal entry."""
        client = LogseqClient(editable_graph)
        
        # Add journal entry
        today = date.today()
        page = client.add_journal_entry("- New journal entry")
        
        assert page is not None
        assert page.is_journal
        assert len(page.blocks) > 0
    
    def test_template_application(self, editable_graph):
        """Test applying template."""
        client = LogseqClient(editable_graph)
        
        # Create template
        template_content = "template:: true\n\n- Task: {{task}}\n  - Status: {{status}}\n"
        client.create_page("template/Task", template_content)
        
        # Verify template
        graph = client.load_graph(force_reload=True)
        templates = graph.get_all_templates()
        
        assert len(templates) > 0
        template = templates[0]
        assert "task" in template.variables or "status" in template.variables


class TestTUINavigation:
    """Test TUI navigation features."""
    
    def test_journal_date_navigation(self):
        """Test journal date navigation logic."""
        view = JournalView()
        
        today = date.today()
        yesterday = today - timedelta(days=1)
        tomorrow = today + timedelta(days=1)
        
        # Test date arithmetic
        assert (today - timedelta(days=1)) == yesterday
        assert (today + timedelta(days=1)) == tomorrow
    
    def test_page_list_navigation(self):
        """Test page list navigation."""
        page_list = PageList()
        
        # Check bindings exist
        bindings = {b.key for b in page_list.BINDINGS}
        assert "j" in bindings
        assert "k" in bindings
        assert "enter" in bindings


class TestTUIErrorHandling:
    """Test TUI error handling."""
    
    def test_missing_graph_path(self):
        """Test handling of missing graph path."""
        with pytest.raises(FileNotFoundError):
            client = LogseqClient("/nonexistent/path")
    
    def test_invalid_graph_path(self, tmp_path):
        """Test handling of invalid graph path (file instead of directory)."""
        file_path = tmp_path / "file.txt"
        file_path.write_text("not a directory")
        
        with pytest.raises(ValueError):
            client = LogseqClient(file_path)
    
    def test_missing_page(self, tmp_path):
        """Test handling of missing page."""
        graph_path = tmp_path / "test_graph"
        graph_path.mkdir()
        
        client = LogseqClient(graph_path)
        graph = client.load_graph()
        
        page = client.get_page("NonexistentPage")
        assert page is None


class TestTUIPerformance:
    """Test TUI performance considerations."""
    
    def test_large_graph_loading(self, tmp_path):
        """Test loading graph with many pages."""
        graph_path = tmp_path / "large_graph"
        graph_path.mkdir()
        (graph_path / "pages").mkdir()
        
        # Create 100 pages
        for i in range(100):
            page_file = graph_path / "pages" / f"Page_{i:03d}.md"
            page_file.write_text(f"- Content for page {i}\n")
        
        client = LogseqClient(graph_path)
        graph = client.load_graph()
        
        assert len(graph.pages) == 100
    
    def test_search_performance(self, tmp_path):
        """Test search with many results."""
        graph_path = tmp_path / "search_graph"
        graph_path.mkdir()
        (graph_path / "pages").mkdir()
        
        # Create pages with common term
        for i in range(50):
            page_file = graph_path / "pages" / f"Page_{i:03d}.md"
            page_file.write_text(f"- Common term appears here\n- Block {i}\n")
        
        client = LogseqClient(graph_path)
        graph = client.load_graph()
        
        results = client.search("Common term")
        assert len(results) > 0
