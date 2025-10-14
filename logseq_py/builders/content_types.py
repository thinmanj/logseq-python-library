"""
Specialized builders for different Logseq content types.

This module provides builders for tasks, code blocks, math expressions, quotes,
tables, media, and other specific content types with their own formatting rules.
"""

from typing import List, Dict, Any, Optional, Union
from datetime import datetime, date
from .core import ContentBuilder, format_date


class TextBuilder(ContentBuilder):
    """Builder for plain text content with formatting options."""
    
    def __init__(self, text: str = ""):
        super().__init__()
        self._text = text
    
    def bold(self, text: str) -> 'TextBuilder':
        """Add bold text."""
        self._text += f"**{text}**"
        return self
    
    def italic(self, text: str) -> 'TextBuilder':
        """Add italic text."""
        self._text += f"*{text}*"
        return self
    
    def code(self, text: str) -> 'TextBuilder':
        """Add inline code."""
        self._text += f"`{text}`"
        return self
    
    def link(self, target: str, text: Optional[str] = None) -> 'TextBuilder':
        """Add a link."""
        if text:
            self._text += f"[{text}]([[{target}]])"
        else:
            self._text += f"[[{target}]]"
        return self
    
    def tag(self, tag_name: str) -> 'TextBuilder':
        """Add a tag."""
        self._text += f"#{tag_name}"
        return self
    
    def text(self, content: str) -> 'TextBuilder':
        """Add plain text."""
        self._text += content
        return self
    
    def space(self) -> 'TextBuilder':
        """Add a space."""
        self._text += " "
        return self
    
    def build(self) -> str:
        return self._text


class HeadingBuilder(ContentBuilder):
    """Builder for headings."""
    
    def __init__(self, level: int, content: str):
        super().__init__()
        if not 1 <= level <= 6:
            raise ValueError("Heading level must be between 1 and 6")
        self._level = level
        self._content = content
    
    def build(self) -> str:
        return "#" * self._level + " " + self._content


class ListBuilder(ContentBuilder):
    """Builder for lists (bullet and numbered)."""
    
    def __init__(self, list_type: str = "bullet"):
        super().__init__()
        self._type = list_type  # "bullet" or "numbered"
        self._items: List[Dict[str, Any]] = []
    
    def item(self, content: str, indent: int = 0) -> 'ListBuilder':
        """Add a list item."""
        self._items.append({"content": content, "indent": indent})
        return self
    
    def items(self, *contents: str, indent: int = 0) -> 'ListBuilder':
        """Add multiple list items."""
        for content in contents:
            self.item(content, indent)
        return self
    
    def nested_item(self, content: str, parent_indent: int = 0) -> 'ListBuilder':
        """Add a nested list item."""
        return self.item(content, parent_indent + 1)
    
    def build(self) -> str:
        lines = []
        for i, item in enumerate(self._items):
            indent_str = "  " * item["indent"]
            if self._type == "numbered":
                prefix = f"{i + 1}. "
            else:
                prefix = "- "
            lines.append(f"{indent_str}{prefix}{item['content']}")
        return "\n".join(lines)


class TaskBuilder(ContentBuilder):
    """Builder for task items with states, priorities, and scheduling."""
    
    def __init__(self, content: str = ""):
        super().__init__()
        self._content = content
        self._state = "TODO"
        self._priority: Optional[str] = None
        self._scheduled: Optional[str] = None
        self._deadline: Optional[str] = None
        self._properties: Dict[str, Any] = {}
        self._tags: List[str] = []
        self._contexts: List[str] = []
    
    def todo(self) -> 'TaskBuilder':
        """Set task state to TODO."""
        self._state = "TODO"
        return self
    
    def doing(self) -> 'TaskBuilder':
        """Set task state to DOING."""
        self._state = "DOING"
        return self
    
    def done(self) -> 'TaskBuilder':
        """Set task state to DONE."""
        self._state = "DONE"
        return self
    
    def later(self) -> 'TaskBuilder':
        """Set task state to LATER."""
        self._state = "LATER"
        return self
    
    def now(self) -> 'TaskBuilder':
        """Set task state to NOW."""
        self._state = "NOW"
        return self
    
    def waiting(self) -> 'TaskBuilder':
        """Set task state to WAITING."""
        self._state = "WAITING"
        return self
    
    def cancelled(self) -> 'TaskBuilder':
        """Set task state to CANCELLED."""
        self._state = "CANCELLED"
        return self
    
    def delegated(self) -> 'TaskBuilder':
        """Set task state to DELEGATED."""
        self._state = "DELEGATED"
        return self
    
    def priority(self, level: str) -> 'TaskBuilder':
        """Set task priority (A, B, or C)."""
        if level.upper() not in ["A", "B", "C"]:
            raise ValueError("Priority must be A, B, or C")
        self._priority = level.upper()
        return self
    
    def high_priority(self) -> 'TaskBuilder':
        """Set high priority (A)."""
        return self.priority("A")
    
    def medium_priority(self) -> 'TaskBuilder':
        """Set medium priority (B)."""
        return self.priority("B")
    
    def low_priority(self) -> 'TaskBuilder':
        """Set low priority (C)."""
        return self.priority("C")
    
    def scheduled(self, when: Union[str, date, datetime]) -> 'TaskBuilder':
        """Set scheduled date/time."""
        self._scheduled = format_date(when)
        return self
    
    def deadline(self, when: Union[str, date, datetime]) -> 'TaskBuilder':
        """Set deadline date/time."""
        self._deadline = format_date(when)
        return self
    
    def property(self, key: str, value: Any) -> 'TaskBuilder':
        """Add a property to the task."""
        self._properties[key] = value
        return self
    
    def effort(self, hours: Union[int, float, str]) -> 'TaskBuilder':
        """Set effort estimate."""
        return self.property("EFFORT", f"{hours}h")
    
    def assigned_to(self, person: str) -> 'TaskBuilder':
        """Set who the task is assigned to."""
        return self.property("ASSIGNED", person)
    
    def project(self, project_name: str) -> 'TaskBuilder':
        """Associate with a project."""
        return self.property("PROJECT", project_name)
    
    def context(self, *contexts: str) -> 'TaskBuilder':
        """Add GTD-style contexts."""
        for ctx in contexts:
            if not ctx.startswith("@"):
                ctx = "@" + ctx
            self._contexts.append(ctx)
        return self
    
    def tag(self, *tags: str) -> 'TaskBuilder':
        """Add tags to the task."""
        self._tags.extend(tags)
        return self
    
    def text(self, content: str) -> 'TaskBuilder':
        """Set the task text content."""
        self._content = content
        return self
    
    def build(self) -> str:
        lines = []
        
        # Build main task line
        task_line = self._state
        if self._priority:
            task_line += f" [#{self._priority}]"
        task_line += f" {self._content}"
        
        # Add contexts
        if self._contexts:
            task_line += " " + " ".join(self._contexts)
        
        # Add tags
        if self._tags:
            task_line += " " + " ".join(f"#{tag}" for tag in self._tags)
        
        lines.append(task_line)
        
        # Add scheduling
        if self._scheduled:
            lines.append(f"SCHEDULED: <{self._scheduled}>")
        if self._deadline:
            lines.append(f"DEADLINE: <{self._deadline}>")
        
        # Add properties
        if self._properties:
            lines.append(":PROPERTIES:")
            for key, value in self._properties.items():
                lines.append(f":{key.upper()}: {value}")
            lines.append(":END:")
        
        return "\n".join(lines)


class CodeBlockBuilder(ContentBuilder):
    """Builder for code blocks."""
    
    def __init__(self, language: str = ""):
        super().__init__()
        self._language = language
        self._code_lines: List[str] = []
    
    def language(self, lang: str) -> 'CodeBlockBuilder':
        """Set the programming language."""
        self._language = lang
        return self
    
    def line(self, code: str) -> 'CodeBlockBuilder':
        """Add a line of code."""
        self._code_lines.append(code)
        return self
    
    def lines(self, *code_lines: str) -> 'CodeBlockBuilder':
        """Add multiple lines of code."""
        self._code_lines.extend(code_lines)
        return self
    
    def blank_line(self) -> 'CodeBlockBuilder':
        """Add a blank line."""
        self._code_lines.append("")
        return self
    
    def comment(self, text: str) -> 'CodeBlockBuilder':
        """Add a comment line (language-aware)."""
        comment_chars = {
            "python": "#", "javascript": "//", "java": "//", "c": "//", "cpp": "//",
            "rust": "//", "go": "//", "swift": "//", "kotlin": "//", "scala": "//",
            "sql": "--", "bash": "#", "shell": "#", "sh": "#", "zsh": "#",
            "html": "<!-- ", "css": "/*", "r": "#", "ruby": "#", "perl": "#"
        }
        
        char = comment_chars.get(self._language.lower(), "#")
        if char in ["<!-- ", "/*"]:
            # Multi-character comment styles
            if char == "<!-- ":
                self._code_lines.append(f"<!-- {text} -->")
            else:  # /*
                self._code_lines.append(f"/* {text} */")
        else:
            self._code_lines.append(f"{char} {text}")
        return self
    
    def build(self) -> str:
        # For Logseq, code blocks should be a single block with embedded newlines
        lines = [f"```{self._language}"]
        lines.extend(self._code_lines)
        lines.append("```")
        # Join with \n but return as single string to be treated as one block
        return "\n".join(lines)


class MathBuilder(ContentBuilder):
    """Builder for mathematical expressions."""
    
    def __init__(self, inline: bool = False):
        super().__init__()
        self._inline = inline
        self._expressions: List[str] = []
    
    def expression(self, expr: str) -> 'MathBuilder':
        """Add a mathematical expression."""
        self._expressions.append(expr)
        return self
    
    def fraction(self, numerator: str, denominator: str) -> 'MathBuilder':
        """Add a fraction."""
        return self.expression(f"\\frac{{{numerator}}}{{{denominator}}}")
    
    def sqrt(self, expr: str) -> 'MathBuilder':
        """Add square root."""
        return self.expression(f"\\sqrt{{{expr}}}")
    
    def integral(self, expr: str, lower: str = "", upper: str = "") -> 'MathBuilder':
        """Add integral."""
        if lower or upper:
            return self.expression(f"\\int_{{{lower}}}^{{{upper}}} {expr}")
        return self.expression(f"\\int {expr}")
    
    def sum_notation(self, expr: str, lower: str = "", upper: str = "") -> 'MathBuilder':
        """Add summation."""
        if lower or upper:
            return self.expression(f"\\sum_{{{lower}}}^{{{upper}}} {expr}")
        return self.expression(f"\\sum {expr}")
    
    def build(self) -> str:
        content = " ".join(self._expressions)
        if self._inline:
            return f"${content}$"
        else:
            return f"$$\n{content}\n$$"


class QuoteBuilder(ContentBuilder):
    """Builder for quote blocks."""
    
    def __init__(self):
        super().__init__()
        self._lines: List[str] = []
    
    def line(self, content: str) -> 'QuoteBuilder':
        """Add a line to the quote."""
        self._lines.append(content)
        return self
    
    def lines(self, *contents: str) -> 'QuoteBuilder':
        """Add multiple lines to the quote."""
        self._lines.extend(contents)
        return self
    
    def author(self, name: str) -> 'QuoteBuilder':
        """Add quote attribution."""
        self._lines.append(f"— {name}")
        return self
    
    def build(self) -> str:
        return "\n".join(f"> {line}" for line in self._lines)


class TableBuilder(ContentBuilder):
    """Builder for markdown tables."""
    
    def __init__(self):
        super().__init__()
        self._headers: List[str] = []
        self._rows: List[List[str]] = []
        self._alignment: List[str] = []  # "left", "center", "right"
    
    def headers(self, *headers: str) -> 'TableBuilder':
        """Set table headers."""
        self._headers = list(headers)
        # Default to left alignment
        self._alignment = ["left"] * len(headers)
        return self
    
    def alignment(self, *alignments: str) -> 'TableBuilder':
        """Set column alignments."""
        self._alignment = list(alignments)
        return self
    
    def row(self, *values: str) -> 'TableBuilder':
        """Add a row to the table."""
        self._rows.append(list(values))
        return self
    
    def rows(self, *rows: List[str]) -> 'TableBuilder':
        """Add multiple rows."""
        self._rows.extend(rows)
        return self
    
    def build(self) -> str:
        if not self._headers:
            raise ValueError("Table must have headers")
        
        lines = []
        
        # Headers
        lines.append("| " + " | ".join(self._headers) + " |")
        
        # Separator with alignment
        separators = []
        for align in self._alignment:
            if align == "center":
                separators.append(":---:")
            elif align == "right":
                separators.append("---:")
            else:  # left or default
                separators.append("---")
        lines.append("|" + "|".join(separators) + "|")
        
        # Rows
        for row in self._rows:
            lines.append("| " + " | ".join(row) + " |")
        
        return "\n".join(lines)


class MediaBuilder(ContentBuilder):
    """Builder for media embeds (images, videos, etc.)."""
    
    def __init__(self):
        super().__init__()
        self._media_items: List[str] = []
    
    def image(self, url: str, alt_text: str = "", title: str = "") -> 'MediaBuilder':
        """Add an image."""
        if title:
            self._media_items.append(f'![{alt_text}]({url} "{title}")')
        else:
            self._media_items.append(f"![{alt_text}]({url})")
        return self
    
    def youtube(self, url: str) -> 'MediaBuilder':
        """Add YouTube video embed."""
        self._media_items.append(f"{{{{video {url}}}}}")
        return self
    
    def twitter(self, url: str) -> 'MediaBuilder':
        """Add Twitter embed."""
        self._media_items.append(f"{{{{twitter {url}}}}}")
        return self
    
    def pdf(self, url: str, page: Optional[int] = None) -> 'MediaBuilder':
        """Add PDF embed."""
        if page:
            self._media_items.append(f"{{{{pdf {url}#{page}}}}}")
        else:
            self._media_items.append(f"{{{{pdf {url}}}}}")
        return self
    
    def build(self) -> str:
        return "\n\n".join(self._media_items)


class DrawingBuilder(ContentBuilder):
    """Builder for drawing/whiteboard blocks."""
    
    def __init__(self, drawing_id: Optional[str] = None):
        super().__init__()
        self._drawing_id = drawing_id or self._generate_drawing_id()
    
    def _generate_drawing_id(self) -> str:
        """Generate a unique drawing ID."""
        import uuid
        return str(uuid.uuid4())[:8]
    
    def id(self, drawing_id: str) -> 'DrawingBuilder':
        """Set the drawing ID."""
        self._drawing_id = drawing_id
        return self
    
    def build(self) -> str:
        return f"{{{{drawing {self._drawing_id}}}}}"