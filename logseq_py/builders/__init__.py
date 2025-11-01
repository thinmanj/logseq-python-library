"""
Logseq Content Builders - DSL for Programmatic Content Generation

This module provides a fluent interface for building Logseq content programmatically,
eliminating the need for string templates and providing type-safe content construction.

It also includes parsing functionality to convert existing Logseq content back into
builder objects, creating a unified read/write system.

Example Usage:
    >>> from logseq_py.builders import PageBuilder, TaskBuilder, CodeBlockBuilder
    >>> 
    >>> # Creating new content
    >>> page = (PageBuilder("My Demo Page")
    ...     .property("author", "John Doe")
    ...     .property("created", "2025-01-08")
    ...     .heading(1, "Welcome to My Demo")
    ...     .text("This page demonstrates programmatic content creation.")
    ...     .add(TaskBuilder().todo().priority("A").text("Complete the demo"))
    ...     .add(CodeBlockBuilder("python")
    ...         .line("def hello_world():")
    ...         .line("    print('Hello, Logseq!')"))
    ...     .build())
    >>>
    >>> # Reading existing content as builders
    >>> from logseq_py.builders import BuilderBasedLoader
    >>> loader = BuilderBasedLoader("/path/to/logseq")
    >>> page_builder = loader.load_page_as_builder("My Page")
    >>> modified_content = loader.modify_page_content("My Page", 
    ...     lambda p: p.add(TaskBuilder().todo().text("New task")))
"""

from pathlib import Path

from .core import (
    ContentBuilder,
    BlockBuilder,
    LogseqBuilder
)

from .content_types import (
    TextBuilder,
    HeadingBuilder,
    ListBuilder,
    TaskBuilder,
    CodeBlockBuilder,
    MathBuilder,
    QuoteBuilder,
    TableBuilder,
    MediaBuilder,
    DiagramBuilder,
    DrawingBuilder
)

from .page_builders import (
    PageBuilder,
    PropertyBuilder,
    TemplateBuilder
)

from .advanced_builders import (
    QueryBuilder,
    JournalBuilder,
    WorkflowBuilder,
    DemoBuilder
)

from .parser import (
    BuilderParser,
    ContentReconstructor,
    BuilderBasedLoader
)

__all__ = [
    # Core builders
    'ContentBuilder',
    'BlockBuilder', 
    'LogseqBuilder',
    
    # Content type builders
    'TextBuilder',
    'HeadingBuilder',
    'ListBuilder',
    'TaskBuilder',
    'CodeBlockBuilder',
    'MathBuilder',
    'QuoteBuilder',
    'TableBuilder',
    'MediaBuilder',
    'DiagramBuilder',
    'DrawingBuilder',
    
    # Page builders
    'PageBuilder',
    'PropertyBuilder',
    'TemplateBuilder',
    
    # Advanced builders
    'QueryBuilder',
    'JournalBuilder',
    'WorkflowBuilder',
    'DemoBuilder',
    
    # Parser and reconstruction
    'BuilderParser',
    'ContentReconstructor', 
    'BuilderBasedLoader'
]
