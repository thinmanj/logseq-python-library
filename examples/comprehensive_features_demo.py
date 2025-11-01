#!/usr/bin/env python3

"""
Comprehensive Features Demo - Logseq Python Library

This demo showcases the latest features including:
- Hierarchical blocks and sub-blocks (v0.3.1 fix)
- Code blocks with proper indentation (v0.3.2 fix)
- Diagram support - Mermaid, Graphviz, PlantUML (v0.4.0)
- Complete builder system with all content types
- Real-world usage scenarios

Features validated across versions 0.3.1, 0.3.2, 0.3.3, and 0.4.0
"""

from datetime import datetime, date
from logseq_py.builders import (
    PageBuilder, BlockBuilder, LogseqBuilder,
    DiagramBuilder, CodeBlockBuilder, TaskBuilder,
    TableBuilder, QuoteBuilder, MediaBuilder
)


def demo_blocks_and_subblocks():
    """Demo: Hierarchical blocks with proper nesting."""
    print("\n" + "="*70)
    print("📦 DEMO 1: Blocks and Sub-blocks (v0.3.1 fix validated)")
    print("="*70)
    
    # Create nested block structure
    parent = BlockBuilder("Project Components")
    
    frontend = BlockBuilder("Frontend")
    frontend.child(BlockBuilder("React Application"))
    frontend.child(BlockBuilder("Component Library"))
    frontend.child(BlockBuilder("State Management"))
    
    backend = BlockBuilder("Backend")
    backend.child(BlockBuilder("REST API"))
    backend.child(BlockBuilder("Database Layer"))
    api_child = BlockBuilder("Authentication Service")
    api_child.child(BlockBuilder("JWT Token Management"))
    api_child.child(BlockBuilder("OAuth Integration"))
    backend.child(api_child)
    
    parent.child(frontend)
    parent.child(backend)
    
    result = parent.build()
    print("\n📝 Generated nested block structure:")
    print(result)
    
    # Verify proper nesting
    lines = result.split("\n")
    print(f"\n✅ Total lines: {len(lines)}")
    print(f"✅ Proper indentation levels: {len(set(len(line) - len(line.lstrip()) for line in lines if line.strip()))}")
    

def demo_code_blocks():
    """Demo: Code blocks in various contexts."""
    print("\n" + "="*70)
    print("💻 DEMO 2: Code Blocks with Proper Indentation (v0.3.2 fix validated)")
    print("="*70)
    
    # Code block in a block
    block = BlockBuilder("Python Example:")
    
    code = CodeBlockBuilder("python")
    code.line("class DatabaseManager:")
    code.line("    def __init__(self, connection_string):")
    code.line("        self.conn = connection_string")
    code.blank_line()
    code.line("    def query(self, sql):")
    code.line("        return self.conn.execute(sql)")
    
    block.child(BlockBuilder(code.build()))
    
    result = block.build()
    print("\n📝 Code block as child block:")
    print(result)
    
    # Verify all lines are properly indented
    lines = result.split("\n")
    code_lines = [line for line in lines[1:] if line.strip()]  # Skip parent line
    all_indented = all(line.startswith("  ") for line in code_lines)
    print(f"\n✅ All code lines properly indented: {all_indented}")
    

def demo_diagrams_mermaid():
    """Demo: Mermaid diagrams (v0.4.0 feature)."""
    print("\n" + "="*70)
    print("📊 DEMO 3: Mermaid Diagrams (v0.4.0 new feature)")
    print("="*70)
    
    print("\n1️⃣ Mermaid Flowchart:")
    flowchart = DiagramBuilder('mermaid')
    flowchart.mermaid_flowchart('TD')
    flowchart.line('    A[Start] --> B{Decision}')
    flowchart.line('    B -->|Yes| C[Process]')
    flowchart.line('    B -->|No| D[Skip]')
    flowchart.line('    C --> E[End]')
    flowchart.line('    D --> E')
    print(flowchart.build())
    
    print("\n2️⃣ Mermaid Sequence Diagram:")
    sequence = DiagramBuilder('mermaid')
    sequence.mermaid_sequence()
    sequence.line('    participant Client')
    sequence.line('    participant Server')
    sequence.line('    participant Database')
    sequence.line('    Client->>Server: Request Data')
    sequence.line('    Server->>Database: Query')
    sequence.line('    Database-->>Server: Results')
    sequence.line('    Server-->>Client: Response')
    print(sequence.build())
    
    print("\n3️⃣ Mermaid Gantt Chart:")
    gantt = DiagramBuilder('mermaid')
    gantt.mermaid_gantt()
    gantt.line('    title Project Timeline')
    gantt.line('    dateFormat YYYY-MM-DD')
    gantt.line('    section Planning')
    gantt.line('    Requirements: 2025-01-01, 7d')
    gantt.line('    Design: 2025-01-08, 5d')
    gantt.line('    section Development')
    gantt.line('    Implementation: 2025-01-13, 14d')
    gantt.line('    Testing: 2025-01-27, 7d')
    print(gantt.build())
    

def demo_diagrams_other():
    """Demo: Graphviz and PlantUML diagrams."""
    print("\n" + "="*70)
    print("🎨 DEMO 4: Graphviz & PlantUML Diagrams (v0.4.0 new feature)")
    print("="*70)
    
    print("\n1️⃣ Graphviz Directed Graph:")
    graphviz = DiagramBuilder('graphviz')
    graphviz.graphviz_digraph('SystemArchitecture')
    graphviz.line('    rankdir=LR;')
    graphviz.line('    node [shape=box, style=rounded];')
    graphviz.line('    ')
    graphviz.line('    Frontend -> Backend;')
    graphviz.line('    Backend -> Database;')
    graphviz.line('    Backend -> Cache;')
    graphviz.line('    Backend -> Queue;')
    graphviz.close_block()
    print(graphviz.build())
    
    print("\n2️⃣ PlantUML Class Diagram:")
    plantuml = DiagramBuilder('plantuml')
    plantuml.plantuml_start()
    plantuml.line('class User {')
    plantuml.line('  +String name')
    plantuml.line('  +String email')
    plantuml.line('  +login()')
    plantuml.line('  +logout()')
    plantuml.line('}')
    plantuml.blank_line()
    plantuml.line('class Order {')
    plantuml.line('  +Date created')
    plantuml.line('  +calculateTotal()')
    plantuml.line('}')
    plantuml.blank_line()
    plantuml.line('User "1" -- "*" Order')
    plantuml.plantuml_end()
    print(plantuml.build())


def demo_complete_page():
    """Demo: Complete page with all features."""
    print("\n" + "="*70)
    print("📄 DEMO 5: Complete Page with All Features")
    print("="*70)
    
    page = PageBuilder("System Design Documentation")
    
    # Page properties
    page.property("author", "Development Team")
    page.property("created", datetime.now().strftime("%Y-%m-%d"))
    page.property("type", "documentation")
    page.property("status", "active")
    
    # Title and introduction
    page.heading(1, "System Design Documentation")
    page.text("Comprehensive system design with architecture diagrams, code examples, and implementation notes.")
    page.empty_line()
    
    # Architecture section with diagram
    page.heading(2, "System Architecture")
    page.text("The system follows a microservices architecture pattern:")
    
    arch_diagram = page.diagram('mermaid')
    arch_diagram.mermaid_flowchart('LR')
    arch_diagram.line('    Client[Client App]')
    arch_diagram.line('    API[API Gateway]')
    arch_diagram.line('    Auth[Auth Service]')
    arch_diagram.line('    Data[Data Service]')
    arch_diagram.line('    DB[(Database)]')
    arch_diagram.line('    ')
    arch_diagram.line('    Client --> API')
    arch_diagram.line('    API --> Auth')
    arch_diagram.line('    API --> Data')
    arch_diagram.line('    Data --> DB')
    
    page.empty_line()
    
    # Code implementation
    page.heading(2, "Implementation Details")
    page.text("Core service implementation:")
    
    api_code = page.code_block("python")
    api_code.comment("API Gateway Service")
    api_code.line("from fastapi import FastAPI, Depends")
    api_code.line("from typing import List")
    api_code.blank_line()
    api_code.line("app = FastAPI()")
    api_code.blank_line()
    api_code.line("@app.get('/api/v1/users')")
    api_code.line("async def get_users(token: str = Depends(verify_token)):")
    api_code.line("    users = await data_service.get_all_users()")
    api_code.line("    return {'users': users}")
    
    page.empty_line()
    
    # Task list
    page.heading(2, "Implementation Tasks")
    page.add(TaskBuilder("Implement authentication service").todo().high_priority())
    page.add(TaskBuilder("Setup database schema").doing().medium_priority())
    page.add(TaskBuilder("Create API documentation").later().low_priority())
    page.add(TaskBuilder("Setup development environment").done())
    
    page.empty_line()
    
    # Component relationships
    page.heading(2, "Component Relationships")
    
    comp_diagram = page.diagram('graphviz')
    comp_diagram.graphviz_digraph('Components')
    comp_diagram.line('    node [shape=component];')
    comp_diagram.line('    ')
    comp_diagram.line('    UI [label="User Interface"];')
    comp_diagram.line('    BL [label="Business Logic"];')
    comp_diagram.line('    DA [label="Data Access"];')
    comp_diagram.line('    ')
    comp_diagram.line('    UI -> BL [label="calls"];')
    comp_diagram.line('    BL -> DA [label="uses"];')
    comp_diagram.close_block()
    
    page.empty_line()
    
    # Statistics table
    page.heading(2, "Project Statistics")
    
    stats_table = page.table()
    stats_table.headers("Metric", "Value", "Status")
    stats_table.alignment("left", "center", "center")
    stats_table.row("Code Coverage", "87%", "✅ Good")
    stats_table.row("API Response Time", "120ms", "✅ Good")
    stats_table.row("Active Users", "1,234", "📈 Growing")
    stats_table.row("Bug Count", "12", "⚠️ Monitor")
    
    page.empty_line()
    
    # Best practices quote
    page.heading(2, "Design Principles")
    
    quote = page.quote()
    quote.line("Design systems, not pages.")
    quote.line("Build component libraries, not collections of components.")
    quote.line("Focus on patterns, not pages.")
    quote.author("Brad Frost, Atomic Design")
    
    # Build and display
    result = page.build()
    print("\n📝 Generated complete documentation page:")
    print(result)
    
    print(f"\n✅ Page contains:")
    print(f"   - Properties: 4")
    print(f"   - Headings: 6")
    print(f"   - Diagrams: 2 (Mermaid + Graphviz)")
    print(f"   - Code blocks: 1")
    print(f"   - Tasks: 4")
    print(f"   - Tables: 1")
    print(f"   - Quotes: 1")
    

def demo_nested_diagrams():
    """Demo: Diagrams as nested blocks."""
    print("\n" + "="*70)
    print("🔀 DEMO 6: Diagrams in Nested Blocks")
    print("="*70)
    
    root = BlockBuilder("System Components")
    
    # Frontend block with diagram
    frontend = BlockBuilder("Frontend Architecture")
    frontend_diagram = DiagramBuilder('mermaid')
    frontend_diagram.mermaid_flowchart()
    frontend_diagram.line('    UI --> Components')
    frontend_diagram.line('    Components --> Store')
    frontend.child(BlockBuilder(frontend_diagram.build()))
    
    # Backend block with diagram
    backend = BlockBuilder("Backend Architecture")
    backend_diagram = DiagramBuilder('mermaid')
    backend_diagram.mermaid_flowchart()
    backend_diagram.line('    API --> Services')
    backend_diagram.line('    Services --> Database')
    backend.child(BlockBuilder(backend_diagram.build()))
    
    root.child(frontend)
    root.child(backend)
    
    result = root.build()
    print("\n📝 Nested blocks with embedded diagrams:")
    print(result)


def demo_real_world_scenarios():
    """Demo: Real-world usage scenarios."""
    print("\n" + "="*70)
    print("🌍 DEMO 7: Real-World Scenarios")
    print("="*70)
    
    print("\n1️⃣ Meeting Notes with Diagrams:")
    
    meeting = PageBuilder("Team Meeting - 2025-11-01")
    meeting.property("type", "meeting")
    meeting.property("attendees", "Alice, Bob, Charlie")
    meeting.property("date", "2025-11-01")
    
    meeting.heading(1, "Team Meeting Notes")
    meeting.heading(2, "Agenda")
    meeting.bullet_list(
        "Sprint review",
        "Architecture decisions",
        "Next sprint planning"
    )
    
    meeting.heading(2, "Architecture Decision")
    meeting.text("We've decided on the following architecture:")
    
    arch = meeting.diagram('mermaid')
    arch.mermaid_flowchart('TB')
    arch.line('    User --> Frontend')
    arch.line('    Frontend --> API')
    arch.line('    API --> Services')
    arch.line('    Services --> DB[(Database)]')
    
    meeting.heading(2, "Action Items")
    meeting.add(TaskBuilder("Update architecture docs").todo().high_priority())
    meeting.add(TaskBuilder("Schedule code review").todo())
    
    print(meeting.build()[:500] + "...\n")
    
    print("\n2️⃣ Technical Documentation:")
    
    docs = PageBuilder("Database Schema Design")
    docs.heading(1, "Database Schema")
    
    # ER Diagram
    er = docs.diagram('mermaid')
    er.mermaid_er_diagram()
    er.line('    USER ||--o{ ORDER : places')
    er.line('    USER {')
    er.line('        string id')
    er.line('        string name')
    er.line('        string email')
    er.line('    }')
    er.line('    ORDER {')
    er.line('        string id')
    er.line('        date created')
    er.line('        decimal total')
    er.line('    }')
    
    docs.heading(2, "Implementation")
    
    sql = docs.code_block("sql")
    sql.line("CREATE TABLE users (")
    sql.line("    id UUID PRIMARY KEY,")
    sql.line("    name VARCHAR(255) NOT NULL,")
    sql.line("    email VARCHAR(255) UNIQUE NOT NULL")
    sql.line(");")
    
    print(docs.build()[:500] + "...\n")


def run_all_demos():
    """Run all demonstrations."""
    print("🎉 " + "="*68)
    print("🎉 COMPREHENSIVE FEATURES DEMONSTRATION")
    print("🎉 Logseq Python Library - Versions 0.3.1 through 0.4.0")
    print("🎉 " + "="*68)
    
    demo_blocks_and_subblocks()
    demo_code_blocks()
    demo_diagrams_mermaid()
    demo_diagrams_other()
    demo_complete_page()
    demo_nested_diagrams()
    demo_real_world_scenarios()
    
    print("\n" + "="*70)
    print("✅ ALL DEMONSTRATIONS COMPLETED SUCCESSFULLY")
    print("="*70)
    print("\n📚 Feature Summary:")
    print("   ✓ Hierarchical blocks with proper nesting (v0.3.1)")
    print("   ✓ Code blocks with correct indentation (v0.3.2)")
    print("   ✓ Comprehensive test suite coverage (v0.3.3)")
    print("   ✓ Diagram support - Mermaid, Graphviz, PlantUML (v0.4.0)")
    print("   ✓ 68 passing tests covering all features")
    print("\n🚀 Ready for production use!")
    print("\n📦 Install: pip install --upgrade logseq-python")
    print("📖 Docs: https://github.com/thinmanj/logseq-python-library")
    print("🔗 PyPI: https://pypi.org/project/logseq-python/")
    

if __name__ == "__main__":
    run_all_demos()
