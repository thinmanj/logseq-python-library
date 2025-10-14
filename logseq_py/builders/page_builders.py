"""
Page-level builders for managing properties, metadata, and page composition.

These builders handle the creation of complete pages with properties, content blocks,
and specialized page types like templates.
"""

from typing import List, Dict, Any, Optional, Union, TYPE_CHECKING
from datetime import datetime, date
from .core import ContentBuilder, LogseqBuilder, format_date

if TYPE_CHECKING:
    from .content_types import *


class PropertyBuilder:
    """Builder for page and block properties."""
    
    def __init__(self):
        self._properties: Dict[str, Any] = {}
    
    def add(self, key: str, value: Any) -> 'PropertyBuilder':
        """Add a property."""
        self._properties[key] = value
        return self
    
    def title(self, title: str) -> 'PropertyBuilder':
        """Set page title."""
        return self.add("title", title)
    
    def author(self, author: str) -> 'PropertyBuilder':
        """Set author."""
        return self.add("author", author)
    
    def created(self, when: Union[str, date, datetime]) -> 'PropertyBuilder':
        """Set creation date."""
        return self.add("created", format_date(when))
    
    def updated(self, when: Union[str, date, datetime]) -> 'PropertyBuilder':
        """Set update date."""
        return self.add("updated", format_date(when))
    
    def type(self, page_type: str) -> 'PropertyBuilder':
        """Set page type."""
        return self.add("type", page_type)
    
    def category(self, category: str) -> 'PropertyBuilder':
        """Set category."""
        return self.add("category", category)
    
    def status(self, status: str) -> 'PropertyBuilder':
        """Set status."""
        return self.add("status", status)
    
    def priority(self, priority: str) -> 'PropertyBuilder':
        """Set priority."""
        return self.add("priority", priority)
    
    def tags(self, *tags: str) -> 'PropertyBuilder':
        """Set tags."""
        return self.add("tags", ", ".join(tags))
    
    def project(self, project: str) -> 'PropertyBuilder':
        """Set associated project."""
        return self.add("project", project)
    
    def deadline(self, when: Union[str, date, datetime]) -> 'PropertyBuilder':
        """Set deadline."""
        return self.add("deadline", format_date(when))
    
    def budget(self, amount: Union[str, int, float]) -> 'PropertyBuilder':
        """Set budget."""
        return self.add("budget", str(amount))
    
    def team(self, *members: str) -> 'PropertyBuilder':
        """Set team members."""
        formatted_members = [f"[[{member}]]" for member in members]
        return self.add("team", ", ".join(formatted_members))
    
    def progress(self, percentage: Union[str, int]) -> 'PropertyBuilder':
        """Set progress percentage."""
        if isinstance(percentage, int):
            return self.add("progress", f"{percentage}%")
        return self.add("progress", percentage)
    
    def custom(self, **kwargs) -> 'PropertyBuilder':
        """Add custom properties."""
        self._properties.update(kwargs)
        return self
    
    def build(self) -> str:
        """Build the properties block."""
        if not self._properties:
            return ""
        
        lines = []
        for key, value in self._properties.items():
            lines.append(f"{key}:: {value}")
        
        return "\n".join(lines)


class PageBuilder(LogseqBuilder):
    """Builder for complete Logseq pages."""
    
    def __init__(self, title: str = ""):
        super().__init__()
        self._title = title
        self._properties = PropertyBuilder()
        self._content_blocks: List[Union[ContentBuilder, str]] = []
    
    @classmethod
    def from_page(cls, page: 'Page') -> 'PageBuilder':
        """Create a PageBuilder from a Page object."""
        from .parser import BuilderParser
        return BuilderParser.parse_page_to_builder(page)
    
    @classmethod
    def from_content(cls, title: str, content: str) -> 'PageBuilder':
        """Create a PageBuilder from content string."""
        builder = cls(title)
        builder.add(content)
        return builder
    
    def title(self, title: str) -> 'PageBuilder':
        """Set page title."""
        self._title = title
        return self
    
    def property(self, key: str, value: Any) -> 'PageBuilder':
        """Add a page property."""
        self._properties.add(key, value)
        return self
    
    def properties(self, **kwargs) -> 'PageBuilder':
        """Add multiple properties."""
        self._properties.custom(**kwargs)
        return self
    
    def author(self, author: str) -> 'PageBuilder':
        """Set page author."""
        self._properties.author(author)
        return self
    
    def created(self, when: Union[str, date, datetime] = None) -> 'PageBuilder':
        """Set creation date (defaults to now)."""
        if when is None:
            when = datetime.now()
        self._properties.created(when)
        return self
    
    def page_type(self, page_type: str) -> 'PageBuilder':
        """Set page type."""
        self._properties.type(page_type)
        return self
    
    def category(self, category: str) -> 'PageBuilder':
        """Set page category."""
        self._properties.category(category)
        return self
    
    def status(self, status: str) -> 'PageBuilder':
        """Set page status."""
        self._properties.status(status)
        return self
    
    def tags(self, *tags: str) -> 'PageBuilder':
        """Set page tags."""
        self._properties.tags(*tags)
        return self
    
    def team(self, *members: str) -> 'PageBuilder':
        """Set team members."""
        self._properties.team(*members)
        return self
    
    def progress(self, percentage: Union[str, int]) -> 'PageBuilder':
        """Set progress percentage."""
        self._properties.progress(percentage)
        return self
    
    def heading(self, level: int, content: str) -> 'PageBuilder':
        """Add a heading."""
        from .content_types import HeadingBuilder
        self._content_blocks.append(HeadingBuilder(level, content))
        return self
    
    def text(self, content: str) -> 'PageBuilder':
        """Add plain text."""
        self._content_blocks.append(content)
        return self
    
    def paragraph(self, content: str) -> 'PageBuilder':
        """Add a paragraph (text + empty line)."""
        self._content_blocks.append(content)
        self._content_blocks.append("")
        return self
    
    def bullet_list(self, *items: str) -> 'PageBuilder':
        """Add a bullet list."""
        from .content_types import ListBuilder
        list_builder = ListBuilder("bullet")
        for item in items:
            list_builder.item(item)
        self._content_blocks.append(list_builder)
        return self
    
    def numbered_list(self, *items: str) -> 'PageBuilder':
        """Add a numbered list."""
        from .content_types import ListBuilder
        list_builder = ListBuilder("numbered")
        for item in items:
            list_builder.item(item)
        self._content_blocks.append(list_builder)
        return self
    
    def task(self, content: str = "") -> 'TaskBuilder':
        """Create and add a task, returning it for chaining."""
        from .content_types import TaskBuilder
        task = TaskBuilder(content)
        self._content_blocks.append(task)
        return task
    
    def code_block(self, language: str = "") -> 'CodeBlockBuilder':
        """Create and add a code block, returning it for chaining."""
        from .content_types import CodeBlockBuilder
        code = CodeBlockBuilder(language)
        self._content_blocks.append(code)
        return code
    
    def quote(self) -> 'QuoteBuilder':
        """Create and add a quote block, returning it for chaining."""
        from .content_types import QuoteBuilder
        quote = QuoteBuilder()
        self._content_blocks.append(quote)
        return quote
    
    def table(self) -> 'TableBuilder':
        """Create and add a table, returning it for chaining."""
        from .content_types import TableBuilder
        table = TableBuilder()
        self._content_blocks.append(table)
        return table
    
    def math(self, inline: bool = False) -> 'MathBuilder':
        """Create and add a math block, returning it for chaining."""
        from .content_types import MathBuilder
        math = MathBuilder(inline)
        self._content_blocks.append(math)
        return math
    
    def media(self) -> 'MediaBuilder':
        """Create and add a media block, returning it for chaining."""
        from .content_types import MediaBuilder
        media = MediaBuilder()
        self._content_blocks.append(media)
        return media
    
    def drawing(self, drawing_id: Optional[str] = None) -> 'DrawingBuilder':
        """Create and add a drawing block, returning it for chaining."""
        from .content_types import DrawingBuilder
        drawing = DrawingBuilder(drawing_id)
        self._content_blocks.append(drawing)
        return drawing
    
    def add(self, builder: Union[ContentBuilder, str]) -> 'PageBuilder':
        """Add a content builder or raw string."""
        self._content_blocks.append(builder)
        return self
    
    def empty_line(self) -> 'PageBuilder':
        """Add an empty line."""
        self._content_blocks.append("")
        return self
    
    def separator(self, char: str = "-", length: int = 3) -> 'PageBuilder':
        """Add a separator line."""
        self._content_blocks.append(char * length)
        return self
    
    def link_to(self, target: str, text: Optional[str] = None) -> str:
        """Generate a link string."""
        if text:
            return f"[{text}]([[{target}]])"
        return f"[[{target}]]"
    
    def tag_ref(self, tag_name: str) -> str:
        """Generate a tag reference string."""
        return f"#{tag_name}"
    
    def build(self) -> str:
        """Build the complete page content."""
        lines = []
        
        # Add properties if any
        properties_content = self._properties.build()
        if properties_content:
            lines.append(properties_content)
            lines.append("")  # Empty line after properties
        
        # Add content blocks
        for block in self._content_blocks:
            if isinstance(block, str):
                lines.append(block)
            elif hasattr(block, 'build'):
                lines.append(block.build())
            else:
                lines.append(str(block))
        
        return "\n".join(lines)


class TemplateBuilder(ContentBuilder):
    """Builder for Logseq templates."""
    
    def __init__(self, name: str):
        super().__init__()
        self._name = name
        self._template_content: List[str] = []
        self._variables: Dict[str, str] = {}
    
    def name(self, template_name: str) -> 'TemplateBuilder':
        """Set template name."""
        self._name = template_name
        return self
    
    def variable(self, name: str, default: str = "") -> 'TemplateBuilder':
        """Define a template variable."""
        self._variables[name] = default
        return self
    
    def line(self, content: str) -> 'TemplateBuilder':
        """Add a line to the template."""
        self._template_content.append(content)
        return self
    
    def placeholder(self, name: str) -> str:
        """Generate a template placeholder."""
        return f"{{{{{name}}}}}"
    
    def date_placeholder(self) -> str:
        """Generate a date placeholder."""
        return "{{date}}"
    
    def time_placeholder(self) -> str:
        """Generate a time placeholder."""
        return "{{time}}"
    
    def build(self) -> str:
        """Build the template."""
        lines = [f"template:: {self._name}"]
        lines.extend(self._template_content)
        return "\n".join(lines)


# Convenience functions for quick page creation
def create_page(title: str) -> PageBuilder:
    """Create a new page builder."""
    return PageBuilder(title)


def create_meeting_page(title: str, date_val: Union[str, date, datetime] = None) -> PageBuilder:
    """Create a meeting page with standard structure."""
    if date_val is None:
        date_val = datetime.now()
    
    return (PageBuilder(title)
            .page_type("meeting")
            .created(date_val)
            .heading(1, title)
            .heading(2, "Attendees")
            .text("- ")
            .empty_line()
            .heading(2, "Agenda")
            .text("- ")
            .empty_line()
            .heading(2, "Notes")
            .text("")
            .empty_line()
            .heading(2, "Action Items")
            .text("- ")
            .empty_line()
            .heading(2, "Next Meeting")
            .text(""))


def create_project_page(title: str, deadline: Union[str, date, datetime] = None) -> PageBuilder:
    """Create a project page with standard structure."""
    page = (PageBuilder(title)
            .page_type("project")
            .status("active")
            .created())
    
    if deadline:
        page.property("deadline", format_date(deadline))
    
    return (page
            .heading(1, title)
            .heading(2, "Overview")
            .text("")
            .empty_line()
            .heading(2, "Goals")
            .bullet_list("")
            .empty_line()
            .heading(2, "Timeline")
            .text("")
            .empty_line()
            .heading(2, "Resources")
            .bullet_list("")
            .empty_line()
            .heading(2, "Tasks")
            .text(""))


def create_person_page(name: str, role: str = "") -> PageBuilder:
    """Create a person page with contact information structure."""
    page = (PageBuilder(name)
            .page_type("person")
            .created())
    
    if role:
        page.property("role", role)
    
    return (page
            .heading(1, name)
            .heading(2, "Contact Information")
            .bullet_list("Email: ", "Phone: ", "Location: ")
            .empty_line()
            .heading(2, "Notes")
            .text("")
            .empty_line()
            .heading(2, "Meetings")
            .text("")
            .empty_line()
            .heading(2, "Projects")
            .text(""))