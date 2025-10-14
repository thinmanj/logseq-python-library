"""
Logseq Content Builders - DSL for Programmatic Content Generation

This module provides a fluent interface for building Logseq content programmatically,
eliminating the need for string templates and providing type-safe content construction.

Example Usage:
    >>> from logseq_py.builders import PageBuilder, TaskBuilder, CodeBlockBuilder
    >>> 
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
"""

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
    'DrawingBuilder',
    
    # Page builders
    'PageBuilder',
    'PropertyBuilder',
    'TemplateBuilder',
    
    # Advanced builders
    'QueryBuilder',
    'JournalBuilder',
    'WorkflowBuilder',
    'DemoBuilder'
]