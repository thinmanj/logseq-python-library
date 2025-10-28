"""
Terminal User Interface for Logseq.

This module provides an interactive TUI for viewing and editing Logseq pages,
journals, and templates using the Textual library.
"""

from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Optional, List, Dict, Any

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical, ScrollableContainer
from textual.widgets import (
    Header, Footer, Static, Button, Input, TextArea, 
    Tree, ListView, ListItem, Label, TabbedContent, TabPane,
    DataTable, Select
)
from textual.binding import Binding
from textual.reactive import reactive
from textual.message import Message
from textual import work

from .logseq_client import LogseqClient
from .models import Page, Block, Template


class PageList(ListView):
    """Widget for listing pages."""
    
    BINDINGS = [
        Binding("j", "cursor_down", "Down", show=False),
        Binding("k", "cursor_up", "Up", show=False),
        Binding("enter", "select_cursor", "Open", show=True),
    ]


class PageEditor(Container):
    """Widget for editing page content."""
    
    current_page: reactive[Optional[str]] = reactive(None)
    
    def compose(self) -> ComposeResult:
        yield Static("", id="page-title")
        yield TextArea("", id="page-content", language="markdown")
        with Horizontal(id="editor-buttons"):
            yield Button("Save", variant="primary", id="save-button")
            yield Button("Cancel", variant="default", id="cancel-button")
    
    def on_mount(self) -> None:
        self.query_one("#page-content", TextArea).focus()
    
    async def load_page(self, page_name: str, client: LogseqClient):
        """Load a page for editing."""
        self.current_page = page_name
        page = client.get_page(page_name)
        
        if page:
            self.query_one("#page-title", Static).update(f"📄 {page.title}")
            content = page.to_markdown()
            self.query_one("#page-content", TextArea).text = content
        else:
            self.query_one("#page-title", Static).update(f"📄 {page_name} (new)")
            self.query_one("#page-content", TextArea).text = ""
    
    def get_content(self) -> str:
        """Get current editor content."""
        return self.query_one("#page-content", TextArea).text


class JournalView(Container):
    """Widget for viewing and navigating journal entries."""
    
    current_date: reactive[date] = reactive(date.today())
    
    def compose(self) -> ComposeResult:
        with Horizontal(id="journal-nav"):
            yield Button("◀ Prev", id="prev-day")
            yield Static(date.today().isoformat(), id="current-date")
            yield Button("Next ▶", id="next-day")
            yield Button("Today", id="today-button")
        yield PageEditor(id="journal-editor")
    
    def watch_current_date(self, date_val: date) -> None:
        """Update display when date changes."""
        self.query_one("#current-date", Static).update(date_val.strftime("%Y-%m-%d (%A)"))


class TemplateManager(Container):
    """Widget for managing templates."""
    
    def compose(self) -> ComposeResult:
        with Horizontal():
            with Vertical(id="template-list-container"):
                yield Static("📋 Templates", id="template-header")
                yield ListView(id="template-list")
                yield Button("+ New Template", id="new-template-button")
            with Vertical(id="template-editor-container"):
                yield Static("Template Editor", id="template-editor-header")
                yield Input(placeholder="Template name", id="template-name")
                yield TextArea("", id="template-content", language="markdown")
                with Horizontal():
                    yield Button("Save Template", variant="primary", id="save-template")
                    yield Button("Delete Template", variant="error", id="delete-template")
                yield Static("Variables: {{}}", id="template-variables")


class SearchPane(Container):
    """Widget for searching across pages."""
    
    def compose(self) -> ComposeResult:
        yield Input(placeholder="Search...", id="search-input")
        yield DataTable(id="search-results")
    
    def on_mount(self) -> None:
        table = self.query_one("#search-results", DataTable)
        table.add_columns("Page", "Block Content", "Tags")


class LogseqTUI(App):
    """Main Logseq TUI application."""
    
    CSS = """
    Screen {
        background: $surface;
    }
    
    #main-container {
        height: 100%;
    }
    
    #sidebar {
        width: 30;
        background: $panel;
        border-right: solid $primary;
    }
    
    #content {
        width: 1fr;
        padding: 1;
    }
    
    #page-title {
        text-style: bold;
        color: $accent;
        margin-bottom: 1;
    }
    
    #page-content {
        height: 1fr;
        border: solid $primary;
    }
    
    #editor-buttons {
        height: auto;
        margin-top: 1;
        align: center middle;
    }
    
    #journal-nav {
        height: auto;
        margin-bottom: 1;
        align: center middle;
    }
    
    #current-date {
        width: auto;
        margin: 0 2;
        text-style: bold;
        color: $accent;
    }
    
    ListView {
        height: 1fr;
        border: solid $primary;
    }
    
    ListItem {
        padding: 0 1;
    }
    
    #template-list-container {
        width: 30%;
        margin-right: 1;
    }
    
    #template-editor-container {
        width: 70%;
    }
    
    #template-header, #template-editor-header {
        text-style: bold;
        color: $accent;
        margin-bottom: 1;
    }
    
    #template-name {
        margin-bottom: 1;
    }
    
    #template-content {
        height: 1fr;
        margin-bottom: 1;
    }
    
    #template-variables {
        margin-top: 1;
        color: $text-muted;
    }
    
    DataTable {
        height: 1fr;
    }
    """
    
    BINDINGS = [
        Binding("q", "quit", "Quit", priority=True),
        Binding("ctrl+s", "save", "Save", show=True),
        Binding("ctrl+j", "show_journals", "Journals", show=True),
        Binding("ctrl+p", "show_pages", "Pages", show=True),
        Binding("ctrl+t", "show_templates", "Templates", show=True),
        Binding("ctrl+f", "show_search", "Search", show=True),
        Binding("ctrl+n", "new_page", "New Page", show=True),
    ]
    
    TITLE = "Logseq TUI"
    SUB_TITLE = "Terminal Knowledge Manager"
    
    def __init__(self, graph_path: Path):
        super().__init__()
        self.graph_path = graph_path
        self.client: Optional[LogseqClient] = None
        self.current_page: Optional[str] = None
        self.current_template: Optional[str] = None
    
    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal(id="main-container"):
            with Vertical(id="sidebar"):
                yield Static("📚 Logseq", id="sidebar-title")
                yield Tree("Pages", id="page-tree")
            with Container(id="content"):
                with TabbedContent(initial="journals"):
                    with TabPane("Journals", id="journals"):
                        yield JournalView()
                    with TabPane("Pages", id="pages"):
                        with Horizontal():
                            yield PageList(id="page-list")
                            yield PageEditor(id="page-editor")
                    with TabPane("Templates", id="templates"):
                        yield TemplateManager()
                    with TabPane("Search", id="search"):
                        yield SearchPane()
        yield Footer()
    
    async def on_mount(self) -> None:
        """Initialize the app on mount."""
        self.client = LogseqClient(self.graph_path)
        await self.load_graph()
        await self.populate_sidebar()
        await self.populate_page_list()
        await self.populate_templates()
        
        # Load today's journal
        await self.load_journal(date.today())
    
    @work
    async def load_graph(self):
        """Load the Logseq graph."""
        if self.client:
            self.client.load_graph()
            self.notify("Graph loaded successfully")
    
    @work
    async def populate_sidebar(self):
        """Populate the sidebar with page tree."""
        if not self.client or not self.client.graph:
            return
        
        tree = self.query_one("#page-tree", Tree)
        tree.clear()
        
        # Add journals
        journals_node = tree.root.add("📅 Journals", expand=True)
        journal_pages = self.client.graph.get_journal_pages()
        for page in journal_pages[-10:]:  # Last 10 journals
            if page.journal_date:
                journals_node.add_leaf(page.journal_date.strftime("%Y-%m-%d"))
        
        # Add regular pages
        pages_node = tree.root.add("📄 Pages", expand=True)
        regular_pages = [p for p in self.client.graph.pages.values() if not p.is_journal]
        
        # Group by namespace
        namespaces: Dict[str, List[Page]] = {}
        no_namespace: List[Page] = []
        
        for page in regular_pages[:50]:  # Limit to first 50
            if page.namespace:
                if page.namespace not in namespaces:
                    namespaces[page.namespace] = []
                namespaces[page.namespace].append(page)
            else:
                no_namespace.append(page)
        
        # Add namespaced pages
        for namespace, pages in sorted(namespaces.items()):
            ns_node = pages_node.add(f"📁 {namespace}", expand=False)
            for page in sorted(pages, key=lambda p: p.name):
                ns_node.add_leaf(page.name)
        
        # Add non-namespaced pages
        for page in sorted(no_namespace, key=lambda p: p.name):
            pages_node.add_leaf(page.name)
    
    @work
    async def populate_page_list(self):
        """Populate the page list view."""
        if not self.client or not self.client.graph:
            return
        
        page_list = self.query_one("#page-list", PageList)
        page_list.clear()
        
        for page_name in sorted(self.client.graph.pages.keys()):
            page = self.client.graph.pages[page_name]
            if not page.is_journal:
                icon = "📋" if page.is_template else "📄"
                page_list.append(ListItem(Label(f"{icon} {page_name}")))
    
    @work
    async def populate_templates(self):
        """Populate the template list."""
        if not self.client or not self.client.graph:
            return
        
        template_list = self.query_one("#template-list", ListView)
        template_list.clear()
        
        templates = self.client.graph.get_all_templates()
        for template in sorted(templates, key=lambda t: t.name):
            template_list.append(ListItem(Label(f"📋 {template.name}")))
        
        if not templates:
            template_list.append(ListItem(Label("No templates found")))
    
    async def load_journal(self, date_val: date):
        """Load journal for a specific date."""
        if not self.client:
            return
        
        journal_view = self.query_one(JournalView)
        journal_view.current_date = date_val
        
        # Format page name for journal
        from .utils import LogseqUtils
        page_name = LogseqUtils.format_date_for_journal(date_val)
        
        # Load into editor
        editor = journal_view.query_one("#journal-editor", PageEditor)
        await editor.load_page(page_name, self.client)
        self.current_page = page_name
    
    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events."""
        button_id = event.button.id
        
        if button_id == "prev-day":
            journal_view = self.query_one(JournalView)
            new_date = journal_view.current_date - timedelta(days=1)
            await self.load_journal(new_date)
        
        elif button_id == "next-day":
            journal_view = self.query_one(JournalView)
            new_date = journal_view.current_date + timedelta(days=1)
            await self.load_journal(new_date)
        
        elif button_id == "today-button":
            await self.load_journal(date.today())
        
        elif button_id == "save-button":
            await self.action_save()
        
        elif button_id == "cancel-button":
            self.notify("Edit cancelled")
        
        elif button_id == "new-template-button":
            await self.create_new_template()
        
        elif button_id == "save-template":
            await self.save_current_template()
        
        elif button_id == "delete-template":
            await self.delete_current_template()
    
    async def on_page_list_selected(self, event: ListView.Selected) -> None:
        """Handle page selection from list."""
        if not self.client:
            return
        
        label = event.item.query_one(Label)
        # Extract page name (remove icon)
        page_name = label.renderable.plain.split(" ", 1)[1]
        
        editor = self.query_one("#page-editor", PageEditor)
        await editor.load_page(page_name, self.client)
        self.current_page = page_name
    
    async def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Handle template selection from list."""
        if event.list_view.id != "template-list" or not self.client:
            return
        
        label = event.item.query_one(Label)
        template_name = label.renderable.plain.split(" ", 1)[1]
        
        template = self.client.graph.get_template(template_name)
        if template:
            self.current_template = template_name
            self.query_one("#template-name", Input).value = template.name
            self.query_one("#template-content", TextArea).text = template.content
            
            # Show variables
            vars_text = f"Variables: {', '.join(template.variables)}" if template.variables else "No variables"
            self.query_one("#template-variables", Static).update(vars_text)
    
    async def on_tree_node_selected(self, event: Tree.NodeSelected) -> None:
        """Handle tree node selection."""
        node_label = event.node.label
        
        # Check if it's a journal date or page name
        if isinstance(node_label, str):
            # Try to load as page
            if self.client:
                page = self.client.get_page(node_label)
                if page:
                    if page.is_journal:
                        # Switch to journal tab and load
                        tabs = self.query_one(TabbedContent)
                        tabs.active = "journals"
                        if page.journal_date:
                            await self.load_journal(page.journal_date.date())
                    else:
                        # Switch to pages tab and load
                        tabs = self.query_one(TabbedContent)
                        tabs.active = "pages"
                        editor = self.query_one("#page-editor", PageEditor)
                        await editor.load_page(node_label, self.client)
                        self.current_page = node_label
    
    async def action_save(self) -> None:
        """Save the current page."""
        if not self.client or not self.current_page:
            self.notify("No page to save", severity="warning")
            return
        
        try:
            # Get active tab
            tabs = self.query_one(TabbedContent)
            
            if tabs.active == "journals":
                editor = self.query_one("#journal-editor", PageEditor)
            elif tabs.active == "pages":
                editor = self.query_one("#page-editor", PageEditor)
            else:
                self.notify("Not in edit mode", severity="warning")
                return
            
            content = editor.get_content()
            
            # Get or create page
            page = self.client.get_page(self.current_page)
            if not page:
                # Create new page
                page = self.client.create_page(self.current_page, content)
            else:
                # Update existing page
                from .utils import LogseqUtils
                page.blocks.clear()
                new_blocks = LogseqUtils.parse_blocks_from_content(content, self.current_page)
                for block in new_blocks:
                    page.add_block(block)
                
                self.client._save_page(page)
            
            self.notify(f"✅ Saved: {self.current_page}", severity="information")
        
        except Exception as e:
            self.notify(f"❌ Error saving: {str(e)}", severity="error")
    
    async def action_quit(self) -> None:
        """Quit the application."""
        self.exit()
    
    async def action_show_journals(self) -> None:
        """Switch to journals tab."""
        tabs = self.query_one(TabbedContent)
        tabs.active = "journals"
    
    async def action_show_pages(self) -> None:
        """Switch to pages tab."""
        tabs = self.query_one(TabbedContent)
        tabs.active = "pages"
    
    async def action_show_templates(self) -> None:
        """Switch to templates tab."""
        tabs = self.query_one(TabbedContent)
        tabs.active = "templates"
    
    async def action_show_search(self) -> None:
        """Switch to search tab."""
        tabs = self.query_one(TabbedContent)
        tabs.active = "search"
        self.query_one("#search-input", Input).focus()
    
    async def action_new_page(self) -> None:
        """Create a new page."""
        # Switch to pages tab
        tabs = self.query_one(TabbedContent)
        tabs.active = "pages"
        
        # For now, just notify - could open a dialog
        self.notify("💡 Edit page name in title and save to create", severity="information")
    
    async def create_new_template(self) -> None:
        """Create a new template."""
        self.current_template = None
        self.query_one("#template-name", Input).value = ""
        self.query_one("#template-content", TextArea).text = "- Template content here\n  - Use {{variable}} for placeholders"
        self.query_one("#template-variables", Static).update("Variables: none")
        self.query_one("#template-name", Input).focus()
    
    async def save_current_template(self) -> None:
        """Save the current template."""
        if not self.client or not self.client.graph:
            return
        
        name = self.query_one("#template-name", Input).value
        content = self.query_one("#template-content", TextArea).text
        
        if not name:
            self.notify("Template name is required", severity="warning")
            return
        
        # Extract variables
        import re
        variables = list(set(re.findall(r'\{\{([^}]+)\}\}', content)))
        
        # Create or update template
        template = Template(
            name=name,
            content=content,
            variables=variables,
            template_type="block"
        )
        
        self.client.graph.templates[name] = template
        
        # Save as a page with template property
        page_name = f"template/{name}"
        try:
            page = self.client.get_page(page_name)
            if not page:
                self.client.create_page(page_name, content, {"template": "true"})
            else:
                from .utils import LogseqUtils
                page.blocks.clear()
                new_blocks = LogseqUtils.parse_blocks_from_content(content, page_name)
                for block in new_blocks:
                    page.add_block(block)
                page.properties["template"] = "true"
                self.client._save_page(page)
            
            self.notify(f"✅ Template saved: {name}", severity="information")
            await self.populate_templates()
        
        except Exception as e:
            self.notify(f"❌ Error saving template: {str(e)}", severity="error")
    
    async def delete_current_template(self) -> None:
        """Delete the current template."""
        if not self.current_template or not self.client or not self.client.graph:
            self.notify("No template selected", severity="warning")
            return
        
        # Remove from graph
        if self.current_template in self.client.graph.templates:
            del self.client.graph.templates[self.current_template]
        
        # Delete page file
        page_name = f"template/{self.current_template}"
        page = self.client.get_page(page_name)
        if page and page.file_path:
            page.file_path.unlink(missing_ok=True)
        
        self.notify(f"🗑️ Template deleted: {self.current_template}", severity="information")
        self.current_template = None
        
        # Clear editor
        self.query_one("#template-name", Input).value = ""
        self.query_one("#template-content", TextArea).text = ""
        
        await self.populate_templates()
    
    async def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle search input submission."""
        if event.input.id == "search-input" and self.client:
            query = event.value
            if query:
                await self.perform_search(query)
    
    @work
    async def perform_search(self, query: str):
        """Perform search across all pages."""
        if not self.client or not self.client.graph:
            return
        
        results = self.client.search(query)
        table = self.query_one("#search-results", DataTable)
        table.clear()
        
        for page_name, blocks in results.items():
            for block in blocks:
                tags_str = ", ".join(block.tags) if block.tags else ""
                table.add_row(page_name, block.content[:100], tags_str)
        
        self.notify(f"Found {sum(len(blocks) for blocks in results.values())} results")


def launch_tui(graph_path: str):
    """Launch the Logseq TUI application."""
    app = LogseqTUI(Path(graph_path))
    app.run()
