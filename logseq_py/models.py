"""
Core data models for Logseq entities.

This module defines the main data structures used throughout the library:
- Block: Individual content blocks in Logseq
- Page: Logseq pages (both regular pages and journal entries)
- LogseqGraph: Container for the entire graph data
"""

import re
import uuid
from datetime import datetime, date
from typing import List, Dict, Optional, Any, Set, Union
from dataclasses import dataclass, field
from pathlib import Path
from enum import Enum


class TaskState(Enum):
    """Task states in Logseq."""
    TODO = "TODO"
    DOING = "DOING"
    DONE = "DONE"
    LATER = "LATER"
    NOW = "NOW"
    WAITING = "WAITING"
    CANCELLED = "CANCELLED"
    DELEGATED = "DELEGATED"
    IN_PROGRESS = "IN-PROGRESS"


class Priority(Enum):
    """Priority levels in Logseq."""
    A = "A"
    B = "B"
    C = "C"


class BlockType(Enum):
    """Types of blocks in Logseq."""
    BULLET = "bullet"
    NUMBERED = "numbered"
    QUOTE = "quote"
    HEADING = "heading"
    CODE = "code"
    MATH = "math"
    EXAMPLE = "example"
    EXPORT = "export"
    VERSE = "verse"
    DRAWER = "drawer"


@dataclass
class BlockEmbed:
    """Represents an embedded block reference."""
    block_id: str
    content_preview: Optional[str] = None
    embed_type: str = "block"  # "block", "page", "query"


@dataclass
class ScheduledDate:
    """Represents scheduled/deadline dates in Logseq."""
    date: date
    time: Optional[str] = None
    repeater: Optional[str] = None  # e.g., "+1w", "+3d"
    delay: Optional[str] = None


@dataclass
class LogseqQuery:
    """Represents a Logseq query block."""
    query_string: str
    query_type: str = "simple"  # "simple", "advanced", "custom"
    results: List[Dict[str, Any]] = field(default_factory=list)
    live: bool = True
    collapsed: bool = False


@dataclass
class Template:
    """Represents a Logseq template."""
    name: str
    content: str
    variables: List[str] = field(default_factory=list)
    usage_count: int = 0
    template_type: str = "block"  # "block", "page"


@dataclass
class Annotation:
    """Represents PDF annotations or highlights."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    content: str = ""
    page_number: Optional[int] = None
    highlight_text: Optional[str] = None
    annotation_type: str = "highlight"  # "highlight", "note", "underline"
    color: Optional[str] = None
    pdf_path: Optional[str] = None
    coordinates: Optional[Dict[str, float]] = None


@dataclass
class WhiteboardElement:
    """Represents elements on a Logseq whiteboard."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    element_type: str = "shape"  # "shape", "text", "block", "page", "image"
    content: str = ""
    position: Dict[str, float] = field(default_factory=dict)  # x, y coordinates
    size: Dict[str, float] = field(default_factory=dict)  # width, height
    style: Dict[str, Any] = field(default_factory=dict)  # color, stroke, etc.
    block_id: Optional[str] = None  # If linking to a block


@dataclass
class Block:
    """Represents a single block in Logseq."""
    
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    content: str = ""
    level: int = 0  # Indentation level (0 = top-level)
    parent_id: Optional[str] = None
    children_ids: List[str] = field(default_factory=list)
    properties: Dict[str, Any] = field(default_factory=dict)
    tags: Set[str] = field(default_factory=set)
    page_name: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    # Advanced Logseq features
    task_state: Optional[TaskState] = None
    priority: Optional[Priority] = None
    scheduled: Optional[ScheduledDate] = None
    deadline: Optional[ScheduledDate] = None
    block_type: BlockType = BlockType.BULLET
    collapsed: bool = False
    heading_level: Optional[int] = None  # 1-6 for headings
    
    # Block references and embeds
    referenced_blocks: Set[str] = field(default_factory=set)
    embedded_blocks: List[BlockEmbed] = field(default_factory=list)
    
    # Advanced content types
    query: Optional[LogseqQuery] = None
    latex_content: Optional[str] = None
    code_language: Optional[str] = None
    
    # Drawing and whiteboard
    drawing_data: Optional[Dict[str, Any]] = None
    whiteboard_elements: List[WhiteboardElement] = field(default_factory=list)
    
    # Annotations and highlights
    annotations: List[Annotation] = field(default_factory=list)
    
    # Plugin data
    plugin_data: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Extract tags and properties from content after initialization."""
        self._extract_tags()
        self._extract_properties()
        self._extract_task_info()
        self._extract_scheduled_dates()
        self._extract_block_references()
        self._detect_content_type()
    
    def _extract_tags(self):
        """Extract hashtags from content."""
        # Match hashtags (but not inside code blocks or links)
        tag_pattern = r'(?:^|\s)#([a-zA-Z0-9_-]+)(?:\s|$|[.,;!?])'
        matches = re.findall(tag_pattern, self.content)
        self.tags.update(matches)
    
    def _extract_properties(self):
        """Extract properties from content (key:: value format)."""
        # Match property format: key:: value
        prop_pattern = r'^([a-zA-Z0-9_-]+)::\s*(.+)$'
        lines = self.content.split('\n')
        
        for line in lines:
            match = re.match(prop_pattern, line.strip())
            if match:
                key, value = match.groups()
                self.properties[key.lower()] = value.strip()
    
    def add_child(self, child_block: 'Block'):
        """Add a child block."""
        if child_block.id not in self.children_ids:
            self.children_ids.append(child_block.id)
            child_block.parent_id = self.id
            child_block.level = self.level + 1
    
    def get_links(self) -> Set[str]:
        """Extract page links from content."""
        # Match [[Page Name]] format
        link_pattern = r'\[\[([^\]]+)\]\]'
        matches = re.findall(link_pattern, self.content)
        return set(matches)
    
    def get_block_references(self) -> Set[str]:
        """Extract block references from content."""
        # Match ((block-id)) format
        ref_pattern = r'\(\(([^)]+)\)\)'
        matches = re.findall(ref_pattern, self.content)
        return set(matches)
    
    def _extract_task_info(self):
        """Extract task state and priority from content."""
        # Extract task state (TODO, DONE, etc.)
        task_pattern = r'^(TODO|DOING|DONE|LATER|NOW|WAITING|CANCELLED|DELEGATED|IN-PROGRESS)\s+'
        match = re.match(task_pattern, self.content)
        if match:
            try:
                self.task_state = TaskState(match.group(1))
                # Remove task state from content for cleaner processing
                self.content = re.sub(task_pattern, '', self.content)
            except ValueError:
                pass
        
        # Extract priority [#A], [#B], [#C]
        priority_pattern = r'\[#([ABC])\]'
        match = re.search(priority_pattern, self.content)
        if match:
            try:
                self.priority = Priority(match.group(1))
                # Remove priority from content
                self.content = re.sub(priority_pattern, '', self.content).strip()
            except ValueError:
                pass
    
    def _extract_scheduled_dates(self):
        """Extract SCHEDULED and DEADLINE dates."""
        # SCHEDULED: <2024-01-15 Mon 10:00 +1w>
        scheduled_pattern = r'SCHEDULED:\s*<([^>]+)>'
        match = re.search(scheduled_pattern, self.content)
        if match:
            self.scheduled = self._parse_logseq_date(match.group(1))
        
        # DEADLINE: <2024-01-20 Sat>
        deadline_pattern = r'DEADLINE:\s*<([^>]+)>'
        match = re.search(deadline_pattern, self.content)
        if match:
            self.deadline = self._parse_logseq_date(match.group(1))
    
    def _parse_logseq_date(self, date_str: str) -> Optional[ScheduledDate]:
        """Parse Logseq date format."""
        try:
            # Basic date parsing - can be enhanced for full Org-mode format
            parts = date_str.split()
            if parts:
                date_part = parts[0]
                parsed_date = datetime.strptime(date_part, '%Y-%m-%d').date()
                
                time_part = None
                repeater = None
                
                if len(parts) > 2:  # Has time
                    time_part = parts[2]
                
                # Look for repeater (+1w, +3d, etc.)
                repeater_match = re.search(r'([+-]\d+[dwmy])', date_str)
                if repeater_match:
                    repeater = repeater_match.group(1)
                
                return ScheduledDate(date=parsed_date, time=time_part, repeater=repeater)
        except (ValueError, IndexError):
            pass
        return None
    
    def _extract_block_references(self):
        """Extract block references and embeds."""
        # Block references ((block-id))
        ref_pattern = r'\(\(([^)]+)\)\)'
        matches = re.findall(ref_pattern, self.content)
        self.referenced_blocks.update(matches)
        
        # Block embeds {{embed ((block-id))}}
        embed_pattern = r'\{\{embed\s+\(\(([^)]+)\)\)\}\}'
        matches = re.findall(embed_pattern, self.content)
        for match in matches:
            embed = BlockEmbed(block_id=match, embed_type="block")
            self.embedded_blocks.append(embed)
        
        # Page embeds {{embed [[Page Name]]}}
        page_embed_pattern = r'\{\{embed\s+\[\[([^\]]+)\]\]\}\}'
        matches = re.findall(page_embed_pattern, self.content)
        for match in matches:
            embed = BlockEmbed(block_id=match, embed_type="page")
            self.embedded_blocks.append(embed)
    
    def _detect_content_type(self):
        """Detect special content types."""
        content_lower = self.content.lower().strip()
        
        # Query blocks
        if content_lower.startswith('{{query') or content_lower.startswith('#+begin_query'):
            self._extract_query()
        
        # LaTeX/Math blocks
        if '$$' in self.content or '\\(' in self.content:
            self.latex_content = self._extract_latex()
        
        # Code blocks
        if self.content.startswith('```') or content_lower.startswith('#+begin_src'):
            self._extract_code_info()
        
        # Heading detection
        if self.content.startswith('#'):
            self.heading_level = len(self.content) - len(self.content.lstrip('#'))
            if self.heading_level > 0:
                self.block_type = BlockType.HEADING
    
    def _extract_query(self):
        """Extract query information from query blocks."""
        # Simple query: {{query "search term"}}
        simple_pattern = r'\{\{query\s+"([^"]+)"\s*\}\}'
        match = re.search(simple_pattern, self.content)
        if match:
            self.query = LogseqQuery(query_string=match.group(1), query_type="simple")
            return
        
        # Advanced query block
        if '#+begin_query' in self.content.lower():
            query_content = re.search(r'\+\+begin_query([\s\S]*?)\+\+end_query', 
                                    self.content, re.IGNORECASE)
            if query_content:
                self.query = LogseqQuery(query_string=query_content.group(1).strip(), 
                                       query_type="advanced")
    
    def _extract_latex(self) -> Optional[str]:
        """Extract LaTeX content."""
        # Extract content between $$ or \( \)
        latex_patterns = [r'\$\$([^$]+)\$\$', r'\\\(([^)]+)\\\)']
        for pattern in latex_patterns:
            match = re.search(pattern, self.content)
            if match:
                return match.group(1).strip()
        return None
    
    def _extract_code_info(self):
        """Extract code language from code blocks."""
        # ```python or #+begin_src python
        patterns = [r'```(\w+)', r'\+\+begin_src\s+(\w+)']
        for pattern in patterns:
            match = re.search(pattern, self.content, re.IGNORECASE)
            if match:
                self.code_language = match.group(1)
                self.block_type = BlockType.CODE
                break
    
    def is_task(self) -> bool:
        """Check if this block is a task."""
        return self.task_state is not None
    
    def is_completed_task(self) -> bool:
        """Check if this is a completed task."""
        return self.task_state == TaskState.DONE
    
    def is_scheduled(self) -> bool:
        """Check if this block is scheduled."""
        return self.scheduled is not None
    
    def has_deadline(self) -> bool:
        """Check if this block has a deadline."""
        return self.deadline is not None
    
    def get_all_dates(self) -> List[date]:
        """Get all dates associated with this block."""
        dates = []
        if self.scheduled:
            dates.append(self.scheduled.date)
        if self.deadline:
            dates.append(self.deadline.date)
        return dates
    
    def to_markdown(self) -> str:
        """Convert block to Logseq markdown format."""
        indent = "\t" * self.level if self.level > 0 else ""
        prefix = "- " if self.level == 0 else ""
        
        # Add task state if present
        content = self.content
        if self.task_state:
            content = f"{self.task_state.value} {content}"
        
        # Add priority if present
        if self.priority:
            content = f"[#{self.priority.value}] {content}"
        
        return f"{indent}{prefix}{content}"


@dataclass
class Page:
    """Represents a page in Logseq."""
    
    name: str
    title: str = ""
    file_path: Optional[Path] = None
    blocks: List[Block] = field(default_factory=list)
    properties: Dict[str, Any] = field(default_factory=dict)
    tags: Set[str] = field(default_factory=set)
    links: Set[str] = field(default_factory=set)
    backlinks: Set[str] = field(default_factory=set)
    is_journal: bool = False
    journal_date: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    # Advanced Logseq features
    namespace: Optional[str] = None  # e.g., "project/backend" -> namespace="project"
    is_whiteboard: bool = False
    whiteboard_data: Optional[Dict[str, Any]] = None
    
    # Templates
    templates: List[Template] = field(default_factory=list)
    is_template: bool = False
    
    # PDF and annotations
    pdf_path: Optional[str] = None
    annotations: List[Annotation] = field(default_factory=list)
    
    # Plugin and theme data
    plugin_data: Dict[str, Any] = field(default_factory=dict)
    
    # Page hierarchy and aliases
    aliases: Set[str] = field(default_factory=set)
    parent_pages: Set[str] = field(default_factory=set)
    child_pages: Set[str] = field(default_factory=set)
    
    def __post_init__(self):
        """Process page data after initialization."""
        if not self.title:
            self.title = self.name
        self._extract_page_data()
        self._extract_namespace()
        self._extract_aliases()
        self._detect_special_pages()
    
    def _extract_page_data(self):
        """Extract tags and links from all blocks."""
        for block in self.blocks:
            self.tags.update(block.tags)
            self.links.update(block.get_links())
    
    def add_block(self, block: Block):
        """Add a block to the page."""
        block.page_name = self.name
        self.blocks.append(block)
        self.tags.update(block.tags)
        self.links.update(block.get_links())
    
    def get_block_by_id(self, block_id: str) -> Optional[Block]:
        """Get a block by its ID."""
        for block in self.blocks:
            if block.id == block_id:
                return block
        return None
    
    def get_blocks_by_content(self, search_text: str, case_sensitive: bool = False) -> List[Block]:
        """Find blocks containing specific text."""
        results = []
        search_text = search_text if case_sensitive else search_text.lower()
        
        for block in self.blocks:
            content = block.content if case_sensitive else block.content.lower()
            if search_text in content:
                results.append(block)
        
        return results
    
    def get_blocks_by_tag(self, tag: str) -> List[Block]:
        """Find blocks with a specific tag."""
        return [block for block in self.blocks if tag in block.tags]
    
    def _extract_namespace(self):
        """Extract namespace from page name."""
        if '/' in self.name:
            parts = self.name.split('/')
            if len(parts) > 1:
                self.namespace = parts[0]
    
    def _extract_aliases(self):
        """Extract aliases from page properties."""
        if 'alias' in self.properties:
            alias_value = self.properties['alias']
            if isinstance(alias_value, str):
                # Handle comma-separated or bracket-separated aliases
                if '[[' in alias_value:
                    # Extract from [[alias1]] [[alias2]] format
                    alias_matches = re.findall(r'\[\[([^\]]+)\]\]', alias_value)
                    self.aliases.update(alias_matches)
                else:
                    # Handle comma-separated
                    self.aliases.update([a.strip() for a in alias_value.split(',') if a.strip()])
            elif isinstance(alias_value, list):
                self.aliases.update(alias_value)
    
    def _detect_special_pages(self):
        """Detect special page types."""
        # Template pages
        if 'template' in self.properties or self.name.lower().startswith('template'):
            self.is_template = True
            self._extract_templates()
        
        # Whiteboard pages
        if self.name.endswith('.whiteboard') or 'whiteboard' in self.properties:
            self.is_whiteboard = True
    
    def _extract_templates(self):
        """Extract template information from template pages."""
        if not self.is_template:
            return
        
        template_content = "\n".join(block.content for block in self.blocks)
        
        # Extract template variables {{variable}}
        variables = re.findall(r'\{\{([^}]+)\}\}', template_content)
        
        template = Template(
            name=self.name,
            content=template_content,
            variables=list(set(variables)),
            template_type="page"
        )
        self.templates.append(template)
    
    def get_task_blocks(self) -> List[Block]:
        """Get all task blocks in this page."""
        return [block for block in self.blocks if block.is_task()]
    
    def get_completed_tasks(self) -> List[Block]:
        """Get all completed task blocks."""
        return [block for block in self.blocks if block.is_completed_task()]
    
    def get_scheduled_blocks(self) -> List[Block]:
        """Get all scheduled blocks."""
        return [block for block in self.blocks if block.is_scheduled()]
    
    def get_blocks_with_deadline(self) -> List[Block]:
        """Get all blocks with deadlines."""
        return [block for block in self.blocks if block.has_deadline()]
    
    def get_blocks_by_priority(self, priority: Priority) -> List[Block]:
        """Get blocks with specific priority."""
        return [block for block in self.blocks if block.priority == priority]
    
    def get_query_blocks(self) -> List[Block]:
        """Get all query blocks."""
        return [block for block in self.blocks if block.query is not None]
    
    def get_code_blocks(self, language: Optional[str] = None) -> List[Block]:
        """Get code blocks, optionally filtered by language."""
        code_blocks = [block for block in self.blocks if block.block_type == BlockType.CODE]
        if language:
            return [block for block in code_blocks if block.code_language == language]
        return code_blocks
    
    def get_math_blocks(self) -> List[Block]:
        """Get blocks containing LaTeX/math content."""
        return [block for block in self.blocks if block.latex_content is not None]
    
    def get_heading_blocks(self, level: Optional[int] = None) -> List[Block]:
        """Get heading blocks, optionally filtered by level."""
        heading_blocks = [block for block in self.blocks if block.block_type == BlockType.HEADING]
        if level:
            return [block for block in heading_blocks if block.heading_level == level]
        return heading_blocks
    
    def get_page_outline(self) -> Dict[str, Any]:
        """Generate a hierarchical outline of the page."""
        outline = {
            'title': self.title,
            'headings': [],
            'tasks': {
                'total': len(self.get_task_blocks()),
                'completed': len(self.get_completed_tasks()),
                'scheduled': len(self.get_scheduled_blocks())
            },
            'blocks': {
                'total': len(self.blocks),
                'code': len(self.get_code_blocks()),
                'queries': len(self.get_query_blocks()),
                'math': len(self.get_math_blocks())
            }
        }
        
        # Build heading hierarchy
        for block in self.get_heading_blocks():
            outline['headings'].append({
                'level': block.heading_level,
                'text': block.content,
                'id': block.id
            })
        
        return outline
    
    def is_namespace_root(self) -> bool:
        """Check if this page is a namespace root."""
        return self.namespace is None and '/' not in self.name
    
    def get_namespace_pages(self, graph: 'LogseqGraph') -> List['Page']:
        """Get all pages in the same namespace."""
        if not self.namespace:
            return []
        
        return [page for page in graph.pages.values() 
                if page.namespace == self.namespace]
    
    def to_markdown(self) -> str:
        """Convert page to Logseq markdown format."""
        lines = []
        
        # Add page properties if any
        if self.properties:
            for key, value in self.properties.items():
                lines.append(f"{key}:: {value}")
            lines.append("")  # Empty line after properties
        
        # Add aliases if any
        if self.aliases:
            alias_str = ", ".join(f"[[{alias}]]" for alias in self.aliases)
            lines.append(f"alias:: {alias_str}")
            lines.append("")
        
        # Add blocks
        for block in self.blocks:
            lines.append(block.to_markdown())
        
        return "\n".join(lines)


@dataclass 
class LogseqGraph:
    """Represents the entire Logseq graph."""
    
    root_path: Path
    pages: Dict[str, Page] = field(default_factory=dict)
    blocks: Dict[str, Block] = field(default_factory=dict)
    config: Dict[str, Any] = field(default_factory=dict)
    
    # Advanced features
    templates: Dict[str, Template] = field(default_factory=dict)
    namespaces: Dict[str, List[str]] = field(default_factory=dict)  # namespace -> page names
    whiteboards: Dict[str, Page] = field(default_factory=dict)
    
    # Plugin and theme data
    plugins: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    themes: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    custom_css: Optional[str] = None
    
    # Index for fast lookups
    alias_index: Dict[str, str] = field(default_factory=dict)  # alias -> page_name
    tag_index: Dict[str, Set[str]] = field(default_factory=dict)  # tag -> page_names
    
    def add_page(self, page: Page):
        """Add a page to the graph."""
        self.pages[page.name] = page
        
        # Add all blocks to the blocks index
        for block in page.blocks:
            self.blocks[block.id] = block
        
        # Update advanced indexes
        self._update_indexes_for_page(page)
    
    def get_page(self, name: str) -> Optional[Page]:
        """Get a page by name."""
        return self.pages.get(name)
    
    def get_block(self, block_id: str) -> Optional[Block]:
        """Get a block by ID."""
        return self.blocks.get(block_id)
    
    def get_pages_by_tag(self, tag: str) -> List[Page]:
        """Find pages containing a specific tag."""
        return [page for page in self.pages.values() if tag in page.tags]
    
    def get_journal_pages(self) -> List[Page]:
        """Get all journal pages sorted by date."""
        journal_pages = [page for page in self.pages.values() if page.is_journal]
        return sorted(journal_pages, key=lambda p: p.journal_date or datetime.min)
    
    def search_content(self, search_text: str, case_sensitive: bool = False) -> Dict[str, List[Block]]:
        """Search for text across all pages."""
        results = {}
        
        for page_name, page in self.pages.items():
            matching_blocks = page.get_blocks_by_content(search_text, case_sensitive)
            if matching_blocks:
                results[page_name] = matching_blocks
        
        return results
    
    def get_backlinks(self, page_name: str) -> Set[str]:
        """Get all pages that link to the specified page."""
        backlinks = set()
        
        for page in self.pages.values():
            if page_name in page.links:
                backlinks.add(page.name)
        
        return backlinks
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get graph statistics."""
        total_blocks = len(self.blocks)
        total_pages = len(self.pages)
        journal_pages = len([p for p in self.pages.values() if p.is_journal])
        regular_pages = total_pages - journal_pages
        
        all_tags = set()
        all_links = set()
        
        for page in self.pages.values():
            all_tags.update(page.tags)
            all_links.update(page.links)
        
        return {
            "total_pages": total_pages,
            "regular_pages": regular_pages,
            "journal_pages": journal_pages,
            "total_blocks": total_blocks,
            "total_tags": len(all_tags),
            "total_links": len(all_links),
            "unique_tags": sorted(list(all_tags)),
            "unique_links": sorted(list(all_links)),
            "templates": len(self.templates),
            "namespaces": len(self.namespaces),
            "whiteboards": len(self.whiteboards),
            "task_blocks": len([b for b in self.blocks.values() if b.is_task()]),
            "completed_tasks": len([b for b in self.blocks.values() if b.is_completed_task()]),
            "scheduled_blocks": len([b for b in self.blocks.values() if b.is_scheduled()]),
            "code_blocks": len([b for b in self.blocks.values() if b.block_type == BlockType.CODE]),
            "query_blocks": len([b for b in self.blocks.values() if b.query is not None])
        }
    
    def _update_indexes_for_page(self, page: Page):
        """Update various indexes when a page is added."""
        # Update namespace index
        if page.namespace:
            if page.namespace not in self.namespaces:
                self.namespaces[page.namespace] = []
            self.namespaces[page.namespace].append(page.name)
        
        # Update alias index
        for alias in page.aliases:
            self.alias_index[alias] = page.name
        
        # Update tag index
        for tag in page.tags:
            if tag not in self.tag_index:
                self.tag_index[tag] = set()
            self.tag_index[tag].add(page.name)
        
        # Update templates index
        for template in page.templates:
            self.templates[template.name] = template
        
        # Update whiteboards index
        if page.is_whiteboard:
            self.whiteboards[page.name] = page
    
    def get_page_by_alias(self, alias: str) -> Optional[Page]:
        """Get a page by its alias."""
        if alias in self.alias_index:
            page_name = self.alias_index[alias]
            return self.pages.get(page_name)
        return None
    
    def get_pages_by_namespace(self, namespace: str) -> List[Page]:
        """Get all pages in a namespace."""
        if namespace in self.namespaces:
            return [self.pages[name] for name in self.namespaces[namespace] 
                   if name in self.pages]
        return []
    
    def get_all_namespaces(self) -> List[str]:
        """Get all namespaces in the graph."""
        return list(self.namespaces.keys())
    
    def get_template(self, name: str) -> Optional[Template]:
        """Get a template by name."""
        return self.templates.get(name)
    
    def get_all_templates(self) -> List[Template]:
        """Get all templates in the graph."""
        return list(self.templates.values())
    
    def get_whiteboards(self) -> List[Page]:
        """Get all whiteboard pages."""
        return list(self.whiteboards.values())
    
    def get_task_blocks(self) -> List[Block]:
        """Get all task blocks in the graph."""
        return [block for block in self.blocks.values() if block.is_task()]
    
    def get_completed_tasks(self) -> List[Block]:
        """Get all completed task blocks."""
        return [block for block in self.blocks.values() if block.is_completed_task()]
    
    def get_scheduled_blocks(self, date_filter: Optional[date] = None) -> List[Block]:
        """Get scheduled blocks, optionally filtered by date."""
        scheduled = [block for block in self.blocks.values() if block.is_scheduled()]
        if date_filter:
            return [block for block in scheduled 
                   if block.scheduled and block.scheduled.date == date_filter]
        return scheduled
    
    def get_blocks_with_deadline(self, date_filter: Optional[date] = None) -> List[Block]:
        """Get blocks with deadlines, optionally filtered by date."""
        deadline_blocks = [block for block in self.blocks.values() if block.has_deadline()]
        if date_filter:
            return [block for block in deadline_blocks 
                   if block.deadline and block.deadline.date == date_filter]
        return deadline_blocks
    
    def get_blocks_by_priority(self, priority: Priority) -> List[Block]:
        """Get blocks with specific priority."""
        return [block for block in self.blocks.values() if block.priority == priority]
    
    def get_query_blocks(self) -> List[Block]:
        """Get all query blocks in the graph."""
        return [block for block in self.blocks.values() if block.query is not None]
    
    def get_code_blocks(self, language: Optional[str] = None) -> List[Block]:
        """Get code blocks, optionally filtered by language."""
        code_blocks = [block for block in self.blocks.values() 
                      if block.block_type == BlockType.CODE]
        if language:
            return [block for block in code_blocks if block.code_language == language]
        return code_blocks
    
    def get_math_blocks(self) -> List[Block]:
        """Get all blocks containing LaTeX/math content."""
        return [block for block in self.blocks.values() if block.latex_content is not None]
    
    def search_blocks_by_task_state(self, state: TaskState) -> List[Block]:
        """Search blocks by task state."""
        return [block for block in self.blocks.values() if block.task_state == state]
    
    def get_workflow_summary(self) -> Dict[str, Any]:
        """Get a summary of workflow/task information."""
        task_blocks = self.get_task_blocks()
        
        # Count by state
        state_counts = {}
        for state in TaskState:
            state_counts[state.value] = len([b for b in task_blocks if b.task_state == state])
        
        # Count by priority
        priority_counts = {}
        for priority in Priority:
            priority_counts[priority.value] = len([b for b in task_blocks if b.priority == priority])
        
        return {
            "total_tasks": len(task_blocks),
            "task_states": state_counts,
            "task_priorities": priority_counts,
            "scheduled_tasks": len([b for b in task_blocks if b.is_scheduled()]),
            "tasks_with_deadline": len([b for b in task_blocks if b.has_deadline()])
        }
    
    def get_graph_insights(self) -> Dict[str, Any]:
        """Get comprehensive graph insights."""
        insights = self.get_statistics()
        insights["workflow"] = self.get_workflow_summary()
        
        # Most connected pages (by backlinks)
        page_connections = [(name, len(page.backlinks)) 
                          for name, page in self.pages.items()]
        page_connections.sort(key=lambda x: x[1], reverse=True)
        insights["most_connected_pages"] = page_connections[:10]
        
        # Most used tags
        tag_usage = [(tag, len(pages)) for tag, pages in self.tag_index.items()]
        tag_usage.sort(key=lambda x: x[1], reverse=True)
        insights["most_used_tags"] = tag_usage[:20]
        
        return insights
