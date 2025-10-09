"""
Logseq Python Library

A Python library for interacting with Logseq knowledge graphs.
Provides functionality to read, query, and modify Logseq data.
"""

from .logseq_client import LogseqClient
from .models import (
    Block, Page, LogseqGraph,
    TaskState, Priority, BlockType,
    BlockEmbed, ScheduledDate, LogseqQuery,
    Template, Annotation, WhiteboardElement
)
from .query import QueryBuilder
from .utils import LogseqUtils

__version__ = "0.1.0"
__author__ = "Julio Ona"
__email__ = "thinmanj@gmail.com"

__all__ = [
    "LogseqClient",
    "Block", 
    "Page",
    "LogseqGraph",
    "QueryBuilder",
    "LogseqUtils",
    # Advanced models
    "TaskState",
    "Priority",
    "BlockType",
    "BlockEmbed",
    "ScheduledDate",
    "LogseqQuery",
    "Template",
    "Annotation",
    "WhiteboardElement"
]
