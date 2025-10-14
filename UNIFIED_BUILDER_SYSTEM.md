# 🔄 Unified Builder System

A comprehensive read/write system for Logseq content that uses the same builder constructs for both content generation and parsing, creating a seamless unified workflow.

## 🎯 Overview

The Unified Builder System extends the existing DSL builder architecture with parsing capabilities, allowing you to:

- **Read** existing Logseq content as builder objects
- **Modify** content using the same fluent builder interface
- **Write** content back seamlessly
- **Round-trip** process content (read → modify → write)

This creates a **unified API** where the same builder classes are used for both content generation and content manipulation.

## 🏗️ Architecture

```
📊 PARSING LAYER
┌─────────────────────────────────────────────┐
│ BuilderParser                               │
│ • Analyzes content structure               │  
│ • Detects content types                    │
│ • Creates appropriate builders             │
└─────────────────────────────────────────────┘
                        ⬇️
🔧 BUILDER LAYER  
┌─────────────────────────────────────────────┐
│ ContentBuilders (TaskBuilder, CodeBuilder) │
│ • Fluent interface for modification        │
│ • Type-safe content construction           │
│ • Chainable operations                     │
└─────────────────────────────────────────────┘
                        ⬇️
📝 GENERATION LAYER
┌─────────────────────────────────────────────┐
│ ContentReconstructor                        │
│ • Converts builders back to content        │
│ • Maintains Logseq format compatibility    │
│ • Handles complex structures               │
└─────────────────────────────────────────────┘
```

## 📚 Core Components

### BuilderParser
**Purpose**: Converts parsed Logseq content back into builder objects

**Key Methods**:
- `parse_page_to_builder(page: Page) -> PageBuilder`
- `parse_block_to_builder(block: Block) -> ContentBuilder`

**Content Type Detection**:
- Automatically detects tasks, code blocks, math, headings, quotes, tables, queries
- Creates appropriate builder types (TaskBuilder, CodeBlockBuilder, etc.)
- Preserves content structure and metadata

### ContentReconstructor  
**Purpose**: Reconstructs content using builders from parsed data

**Key Methods**:
- `reconstruct_page(page: Page) -> str`
- `reconstruct_block(block: Block) -> str`  
- `modify_and_reconstruct(page: Page, modifications: dict) -> str`

### BuilderBasedLoader
**Purpose**: High-level loader that returns builder objects instead of model objects

**Key Methods**:
- `load_page_as_builder(page_name: str) -> PageBuilder`
- `load_all_pages_as_builders() -> Dict[str, PageBuilder]`
- `modify_page_content(page_name: str, modifier_func) -> str`

## 🔧 Enhanced LogseqClient

The `LogseqClient` is extended with builder-based methods:

```python
# Get pages and blocks as builders
page_builder = client.get_page_as_builder("My Page")
block_builder = client.get_block_as_builder("block-id")

# Modify pages using builders
def enhance_page(builder):
    builder.heading(2, "Enhancement")
    builder.add(TaskBuilder().todo().text("New task"))

success = client.modify_page_with_builder("My Page", enhance_page)
```

## 🎨 Builder Extensions

All builder classes are enhanced with parsing methods:

```python
# Class methods for creating builders from existing content
page_builder = PageBuilder.from_page(page_object)
task_builder = TaskBuilder.from_block(block_object)
code_builder = CodeBlockBuilder.from_content(code_string)
```

## 💻 Usage Examples

### Example 1: Loading Content as Builders

```python
from logseq_py.builders import BuilderBasedLoader

# Initialize loader
loader = BuilderBasedLoader("/path/to/logseq")

# Load page as builder
page_builder = loader.load_page_as_builder("My Project")

# Modify using builder methods
page_builder.add(
    TaskBuilder()
    .todo()
    .priority("A")
    .text("New high-priority task")
)

# Generate modified content
modified_content = page_builder.build()
```

### Example 2: Round-trip Processing

```python
from logseq_py import LogseqClient

client = LogseqClient("/path/to/logseq")

def add_status_update(page_builder):
    page_builder.heading(2, "Status Update")
    page_builder.text(f"Updated on {datetime.now()}")
    page_builder.add(
        TaskBuilder().doing().text("Integration testing")
    )

# Modify page using builder workflow
success = client.modify_page_with_builder(
    "Project Status", 
    add_status_update
)
```

### Example 3: Content Reconstruction

```python
from logseq_py.builders import ContentReconstructor

# Parse existing page
page = client.get_page("Documentation")

# Reconstruct using builders (for analysis/modification)
reconstructed = ContentReconstructor.reconstruct_page(page)

# Or modify and reconstruct in one step
enhanced = ContentReconstructor.modify_and_reconstruct(page, {
    'add_tasks': [
        {'content': 'Update API docs', 'status': 'TODO', 'priority': 'A'},
        {'content': 'Review examples', 'status': 'LATER', 'priority': 'B'}
    ]
})
```

### Example 4: Advanced Content Manipulation

```python
from logseq_py.builders import BuilderBasedLoader, BuilderParser

loader = BuilderBasedLoader("/path/to/logseq")

# Load multiple pages as builders
all_builders = loader.load_all_pages_as_builders()

# Analyze and enhance content
for page_name, builder in all_builders.items():
    # Add standard footer to all pages
    builder.empty_line()
    builder.separator()
    builder.text(f"Last updated: {datetime.now()}")
    
    # Save enhanced content
    enhanced_content = builder.build()
    # ... save logic
```

## 🎯 Key Benefits

### 1. Unified API
- **Same interface** for reading and writing content
- **Consistent** builder patterns across all operations
- **Type-safe** content manipulation

### 2. Seamless Round-trip Processing  
- **Load** existing content as builders
- **Modify** using fluent interface
- **Write** back without format loss

### 3. Advanced Content Analysis
- **Automatic** content type detection
- **Intelligent** builder selection  
- **Preserved** structure and metadata

### 4. Flexible Workflows
- **Batch processing** of multiple pages
- **Dynamic content** generation from existing data
- **Automated** content enhancement and maintenance

## 📊 Content Type Mapping

| Logseq Content | Builder Type | Detection Logic |
|----------------|--------------|-----------------|
| `- TODO Task [#A]` | `TaskBuilder` | Task state markers |
| `# Heading` | `HeadingBuilder` | `#` prefix patterns |
| ````code```` | `CodeBlockBuilder` | Code fence detection |
| `$$math$$` | `MathBuilder` | Math delimiters |
| `> Quote` | `QuoteBuilder` | Quote prefix |
| `\| Table \|` | `TableBuilder` | Table format detection |
| ````query```` | `QueryBuilder` | Query block detection |
| Regular text | `BlockBuilder` | Default fallback |

## 🔄 Workflow Examples

### Content Migration Workflow
```
Existing Content → Parse → Analyze → Transform → Rebuild → Export
```

### Maintenance Workflow  
```
Load as Builders → Batch Modify → Generate → Save → Verify
```

### Enhancement Workflow
```
Parse Content → Extract Patterns → Generate Enhancements → Merge → Output
```

## 🚀 Use Cases

### 📝 Content Migration
- **Transform** content between different formats
- **Preserve** structure during migration  
- **Enhance** content during the process

### 🔄 Automated Maintenance
- **Standardize** formatting across pages
- **Update** templates and structures
- **Add** metadata and cross-references

### 📊 Dynamic Reporting
- **Generate** summaries from existing content
- **Create** dashboards and analytics pages
- **Build** cross-reference indexes

### 🧹 Bulk Operations
- **Apply** changes across multiple pages
- **Format** content consistently
- **Validate** and fix content issues

### 🔍 Content Analysis
- **Extract** patterns and insights
- **Identify** content gaps and opportunities
- **Generate** recommendations

### ⚡ Real-time Processing
- **Live** content modification
- **Interactive** content enhancement  
- **Dynamic** content adaptation

## 🛡️ Robustness Features

### Error Handling
- **Graceful** fallbacks for unknown content types
- **Validation** of builder operations
- **Recovery** from parsing errors

### Content Preservation
- **Maintains** original structure when possible  
- **Preserves** metadata and properties
- **Handles** complex nested content

### Performance Optimization
- **Lazy** parsing for large content
- **Efficient** builder creation
- **Optimized** content reconstruction

## 📈 Future Enhancements

### Advanced Parsing
- **Machine learning** content classification
- **Context-aware** builder selection
- **Semantic** content understanding

### Enhanced Builders  
- **Template-based** builder creation
- **Rule-based** content transformation
- **Plugin** system for custom builders

### Integration Expansion
- **API** endpoints for remote processing
- **Streaming** content processing
- **Real-time** collaboration features

## 🎉 Summary

The Unified Builder System creates a **complete content lifecycle management solution** that:

✅ **Unifies** content generation and manipulation  
✅ **Preserves** content structure and metadata  
✅ **Enables** sophisticated content workflows  
✅ **Provides** type-safe programmatic access  
✅ **Supports** advanced analysis and enhancement  

This system transforms Logseq content management from a simple read/write operation into a powerful, flexible, and intelligent content processing platform.

**Ready for**: migration, automation, analysis, enhancement, and any advanced content workflow you can imagine!