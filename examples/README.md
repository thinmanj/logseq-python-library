# Logseq Demo

This directory contains a comprehensive demonstration of all Logseq features, generated programmatically using the **Logseq Builder DSL**.

## 🎯 What's Included

### Complete Logseq Feature Showcase
- **15+ demonstration pages** covering all major Logseq features
- **All block types**: text, headings, code, math, quotes, tables, embeds
- **Task management**: TODO/DOING/DONE with priorities, scheduling, GTD workflows
- **Page properties**: metadata, queries, automation
- **Linking systems**: bidirectional links, backlinks, namespaces, tags
- **Templates**: reusable content for meetings, projects, workflows
- **Journal entries**: 7 days of realistic daily notes
- **Advanced features**: queries, automation, plugin integration
- **Learning resources**: tutorials, best practices, troubleshooting

### Builder DSL Features
- **Type-safe content creation** - No string templates, all programmatically built
- **Fluent interface** - Readable, chainable method calls
- **Language-aware code blocks** - Smart comment generation for 15+ languages
- **Multi-line content support** - Proper handling of code blocks, math expressions
- **Modular building blocks** - TaskBuilder, CodeBlockBuilder, MathBuilder, etc.

### Real-World Examples
- **Project management** workflows and templates
- **Software development** documentation and processes
- **Academic research** note-taking and citation management
- **Personal productivity** systems and habit tracking
- **Team collaboration** meeting notes and communication

### Plugin Integration
- Comprehensive plugin ecosystem overview
- 18+ plugin categories with detailed descriptions
- Integration examples and code snippets
- Plugin development guidance
- External tool connections (GitHub, APIs, browsers)

## 🚀 Getting Started

### 1. Generated Demo Location
The demo is automatically generated in the `logseq-demo/` directory:
```
examples/
├── generate_logseq_demo.py    # DSL-based demo generator script
├── logseq-demo/              # Generated Logseq graph
│   ├── .logseq/              # Configuration files
│   ├── journals_*.md         # Daily note examples
│   └── (various demo pages)  # Feature demonstration pages
└── README.md                 # This file
```

### 2. Opening in Logseq
1. **Open Logseq** application
2. Click **"Add graph"** or **"Open existing graph"**
3. Navigate to and select the `examples/logseq-demo` directory
4. Start exploring with the **"Welcome to Demo"** page

### 3. Navigation Guide
- **Start here**: [[Welcome to Demo]]
- **Core features**: Task Management, Block Types, Page Properties
- **Advanced features**: Templates, Namespaces, Advanced Features
- **Learning**: Learning Resources, Plugin Integration

## 📋 Demo Contents Overview

### Core Feature Pages
| Page | Description | Key Features |
|------|-------------|--------------|
| **Task Management Demo** | Complete task workflows | TODO/DOING/DONE, priorities, scheduling, GTD |
| **Block Types Showcase** | All supported block formats | Code, math, tables, embeds, drawings |
| **Page Properties Demo** | Metadata and automation | Properties, queries, relationships |
| **Linking and Tagging System** | Knowledge graph features | Links, backlinks, tags, references |

### Advanced Feature Pages  
| Page | Description | Key Features |
|------|-------------|--------------|
| **Templates and Workflows** | Automation and standardization | Meeting notes, project plans, workflows |
| **Namespace Hierarchy Demo** | Organizational structures | Projects/, People/, Learning/ hierarchies |
| **Advanced Features Demo** | Power user capabilities | Complex queries, automation, integrations |
| **Plugin Integration Demo** | Ecosystem and extensions | 18+ plugin categories, development guide |

### Sample Content
- **7 days of journal entries** with realistic daily workflows
- **Project examples** with full hierarchies (Projects/Website Redesign/)
- **People profiles** with roles and relationships
- **Meeting templates** and follow-up workflows
- **Learning resources** with progressive skill development

## ⚙️ Customization and Configuration

### Demo Configuration
The demo includes pre-configured settings in `.logseq/`:
- **config.edn**: Optimal settings for demo exploration
- **custom.css**: Enhanced styling for better visualization
- **metadata.edn**: Demo metadata and feature tracking

### Regenerating the Demo
To create a fresh demo with updated content:
```bash
cd examples
python generate_logseq_demo.py my-custom-demo
```

### Customizing Content
Edit `generate_logseq_demo.py` to:
- Add new feature demonstrations
- Modify example content
- Include custom templates
- Add organization-specific examples

## 🎓 Learning Path

### Beginner (Explore these first)
1. **Welcome to Demo** - Overview and navigation
2. **Block Types Showcase** - Basic content creation
3. **Task Management Demo** - Essential productivity features
4. **Linking and Tagging System** - Knowledge connections

### Intermediate (After basics)
1. **Page Properties Demo** - Structured data and queries
2. **Templates and Workflows** - Process automation
3. **Namespace Hierarchy Demo** - Organizational strategies
4. **Journal entries** (7 sample days) - Daily workflow patterns

### Advanced (Power user features)
1. **Advanced Features Demo** - Complex queries and automation
2. **Plugin Integration Demo** - Ecosystem and extensions
3. **Workflow Examples** - Professional and academic patterns
4. **Learning Resources** - Mastery and troubleshooting

## 🔧 Development and Extension

### Adding Features to Demo
The demo generator is modular and extensible:
```python
def _create_custom_demo(self):
    """Add your custom demo content here."""
    content = """# My Custom Feature Demo
    Your custom content here...
    """
    self.client.create_page("Custom Demo", content)
```

### Plugin Development Examples
The demo includes:
- Plugin architecture examples
- API integration patterns  
- Custom command implementations
- Theme and UI customizations

### External Integrations
Real-world integration examples for:
- **Version Control**: Git workflow documentation
- **APIs**: External service connections
- **Databases**: Query and visualization
- **Automation**: Scheduled content generation

## 📊 Demo Statistics

- **Pages**: 25+ comprehensive demonstration pages
- **Block Types**: All 10+ supported formats with examples
- **Tasks**: 50+ task management examples
- **Templates**: 10+ production-ready templates
- **Queries**: 20+ query examples from basic to advanced
- **Links**: 100+ internal connections demonstrating knowledge graphs
- **Features**: Complete coverage of Logseq capabilities

## 🤝 Contributing

To improve the demo:
1. **Fork** the repository
2. **Modify** `generate_logseq_demo.py`
3. **Test** with `python generate_logseq_demo.py test-demo`
4. **Submit** pull request with improvements

### Ideas for Contributions
- Industry-specific workflow examples
- Additional language code samples
- Plugin integration tutorials
- Performance optimization examples
- Accessibility feature demonstrations

## 🎉 Conclusion

This demo showcases the full power of Logseq as a knowledge management and productivity platform. It serves as both a learning resource for new users and a reference for advanced implementations.

The programmatic generation approach demonstrates how the **Logseq Python Library** can be used for:
- **Bulk content creation**
- **Knowledge base migration**  
- **Automated documentation**
- **Template and workflow distribution**
- **Integration with existing systems**

Explore, experiment, and adapt these patterns to your own Logseq workflows!

---
*Generated with ❤️ by the [Logseq Python Library](../README.md)*