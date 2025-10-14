#!/usr/bin/env python3
"""
Comprehensive Logseq Demo Generator

This script creates a complete Logseq graph using the Builder DSL,
demonstrating all features available in the Logseq Python Library.

Features:
- Type-safe content creation using Builder DSL
- Fluent interface for readable code
- Modular building blocks for every content type
- Comprehensive feature coverage (tasks, code, math, tables, etc.)
- Professional templates and real-world examples
- Zero hardcoded strings - everything programmatically built

The generated demo can be opened in Logseq to explore all features interactively.
"""

import sys
import os
from pathlib import Path
from datetime import datetime, date, timedelta
from typing import List, Dict, Any

# Add the parent directory to Python path to import our library
sys.path.insert(0, str(Path(__file__).parent.parent))

from logseq_py import (
    LogseqClient,
    # Builders
    PageBuilder, TaskBuilder, CodeBlockBuilder, MathBuilder,
    QuoteBuilder, TableBuilder, MediaBuilder, QueryBuilder,
    JournalBuilder, DemoBuilder, WorkflowBuilder
)


class LogseqDemoGenerator:
    """Generates a comprehensive Logseq demo using the Builder DSL."""
    
    def __init__(self, demo_path: str):
        """Initialize the demo generator."""
        self.demo_path = Path(demo_path)
        self.demo_path.mkdir(parents=True, exist_ok=True)
        
        print(f"🎭 Logseq Demo Generator")
        print(f"📁 Demo path: {self.demo_path}")
    
    def generate_complete_demo(self):
        """Generate the complete Logseq demo using builders."""
        
        print("\\n🚀 Starting comprehensive Logseq demo generation...")
        
        with LogseqClient(self.demo_path, auto_save=True) as client:
            # Create welcome page
            self._create_welcome_page(client)
            
            # Create task management demo
            self._create_task_management_demo(client)
            
            # Create block types showcase
            self._create_block_types_showcase(client)
            
            # Create page properties demo
            self._create_page_properties_demo(client)
            
            # Create code examples
            self._create_code_examples_demo(client)
            
            # Create math examples
            self._create_math_examples_demo(client)
            
            # Create tables and media demo
            self._create_tables_media_demo(client)
            
            # Create query examples
            self._create_query_examples_demo(client)
            
            # Create workflow documentation
            self._create_workflow_demo(client)
            
            # Create journal entries
            self._create_journal_entries_demo(client)
            
            # Create project pages
            self._create_project_pages_demo(client)
            
            # Create logseq configuration
            self._create_logseq_config()
            
        print("\\n✅ Logseq demo generation completed successfully!")
        print(f"📚 Open the demo in Logseq by pointing to: {self.demo_path}")
        print(f"🎯 Start with the 'Welcome to Demo' page")
    
    def _create_welcome_page(self, client):
        """Create the main welcome page using PageBuilder."""
        print("📝 Creating welcome page...")
        
        welcome = (PageBuilder("Welcome to Demo")
                  .author("Demo Generator")
                  .created()
                  .page_type("documentation")
                  .category("demo")
                  .tags("welcome", "demo", "dsl")
                  
                  .heading(1, "Welcome to the Logseq Demo! 🎉")
                  .paragraph(f"This demo was generated on {datetime.now().strftime('%Y-%m-%d at %H:%M:%S')} using the **Logseq Builder DSL**.")
                  
                  .heading(2, "What's New in This Demo")
                  .bullet_list(
                      "🏗️ **Type-safe content creation** - No more string templates!",
                      "🎯 **Fluent interface** - Readable and intuitive code",
                      "🧩 **Modular building blocks** - Compose complex content easily",
                      "🔍 **Complete feature coverage** - Every Logseq feature demonstrated",
                      "⚡ **Zero hardcoded strings** - Everything built programmatically"
                  )
                  
                  .heading(2, "Demo Pages")
                  .text("Explore these demonstration pages:"))
        
        # Create nested demo pages structure
        from logseq_py.builders.content_types import ListBuilder
        demo_pages = ListBuilder("bullet")
        demo_pages.item("**Core Features**")
        demo_pages.item("[[Task Management Demo]] - Programmatic task creation", 1)
        demo_pages.item("[[Block Types Showcase]] - All content types via builders", 1)
        demo_pages.item("[[Page Properties Demo]] - Metadata and properties", 1)
        demo_pages.item("**Content Types**")
        demo_pages.item("[[Code Examples Demo]] - Language-aware code blocks", 1)
        demo_pages.item("[[Math Examples Demo]] - LaTeX math expressions", 1)
        demo_pages.item("[[Tables and Media Demo]] - Structured content", 1)
        demo_pages.item("**Advanced Features**")
        demo_pages.item("[[Query Examples Demo]] - Dynamic content queries", 1)
        demo_pages.item("[[Workflow Demo]] - Process documentation", 1)
        demo_pages.item("**Project Examples**")
        demo_pages.item("[[Project: E-commerce Platform]] - Full project showcase", 1)
        demo_pages.item("[[Project: Task Management Mobile App]] - Mobile development", 1)
        
        welcome.add(demo_pages)
        
        welcome = (welcome
                  
                  .heading(2, "Builder Usage Example")
                  .text("Here's how this page was created:")
                  )
        
        # Add example code
        welcome.code_block("python").lines(
            "welcome = (PageBuilder('Welcome to Demo')",
            "          .author('Demo Generator')",
            "          .created()",
            "          .heading(1, 'Welcome to the Logseq Demo! 🎉')",
            "          .paragraph('This demo was generated...')",
            "          .bullet_list(",
            "              '🏗️ Type-safe content creation',",
            "              '🎯 Fluent interface',",
            "              '🧩 Modular building blocks'",
            "          ))"
        )
        
        welcome.empty_line().separator().empty_line().text("*Generated with the Logseq Builder DSL - no strings attached!* 🚀")
        
        client.create_page("Welcome to Demo", welcome.build())
    
    def _create_task_management_demo(self, client):
        """Create comprehensive task management examples using TaskBuilder."""
        print("✅ Creating task management demo...")
        
        page = (PageBuilder("Task Management Demo")
               .author("Demo Generator")
               .created()
               .page_type("demo")
               .category("productivity")
               .tags("tasks", "gtd", "productivity")
               
               .heading(1, "Task Management with DSL Builders")
               .text("This page demonstrates programmatic task creation using the TaskBuilder DSL.")
               .empty_line()
               
               .heading(2, "Basic Task States")
               .text("Created using fluent TaskBuilder interface:"))
        
        # Add various task examples using TaskBuilder
        page.add(TaskBuilder("Basic task without any additional metadata").todo())
        page.add(TaskBuilder("Task currently in progress").doing())  
        page.add(TaskBuilder("Completed task ✓").done())
        page.add(TaskBuilder("Task postponed for later").later())
        page.add(TaskBuilder("High priority task for immediate attention").now())
        page.add(TaskBuilder("Task waiting for external dependency").waiting())
        page.add(TaskBuilder("Task that was cancelled").cancelled())
        page.add(TaskBuilder("Task assigned to someone else").delegated())
        
        page.empty_line().heading(2, "Tasks with Priorities")
        page.add(TaskBuilder("High priority task - most important").todo().high_priority())
        page.add(TaskBuilder("Medium priority task - normal importance").todo().medium_priority())
        page.add(TaskBuilder("Low priority task - when time permits").todo().low_priority())
        page.add(TaskBuilder("Critical task in progress right now").doing().high_priority())
        page.add(TaskBuilder("Completed high priority task ✓").done().high_priority())
        
        page.empty_line().heading(2, "Scheduled and Deadline Tasks")
        page.add(TaskBuilder("Review quarterly reports").todo()
                 .scheduled("2025-01-15")
                 .effort(2))
        
        page.add(TaskBuilder("Submit project proposal").todo()
                 .deadline("2025-01-20")
                 .high_priority()
                 .assigned_to("John Doe"))
        
        page.add(TaskBuilder("Weekly team meeting").todo()
                 .scheduled("2025-01-08")
                 .property("REPEAT", "Weekly"))
        
        page.empty_line().heading(2, "GTD-Style Context Tasks")
        page.add(TaskBuilder("Call client about project requirements").todo()
                 .context("phone", "office")
                 .medium_priority())
        
        page.add(TaskBuilder("Buy groceries after work").todo()
                 .context("errands", "car"))
        
        page.add(TaskBuilder("Read research papers").todo()
                 .context("home", "evening", "lowenergy"))
        
        page.add(TaskBuilder("Review code changes").todo()
                 .context("computer", "focused")
                 .effort("1h"))
        
        page.empty_line().heading(2, "Project Tasks with Properties")
        page.add(TaskBuilder("Implement new feature").todo()
                 .high_priority()
                 .project("WebApp Redesign")
                 .effort("4h")
                 .assigned_to("Alice Johnson")
                 .tag("development", "frontend"))
        
        page.add(TaskBuilder("Code review for PR #123").doing()
                 .effort("1h")
                 .property("URGENCY", "High")
                 .property("COMPLEXITY", "Medium")
                 .context("computer"))
        
        page.empty_line().heading(2, "Hierarchical Task Organization")
        page.text("Example of nested task structure using custom blocks:")
        
        # Create nested task structure using blocks
        from logseq_py.builders.core import BlockBuilder
        project_block = BlockBuilder("📋 **Project: Website Redesign**")
        
        frontend_block = BlockBuilder("🎨 Frontend Development")
        frontend_block.child(BlockBuilder("TODO Design new homepage layout [#A]"))
        frontend_block.child(BlockBuilder("DOING Implement responsive navigation [#B]"))
        frontend_block.child(BlockBuilder("TODO Add dark mode support [#C]"))
        
        backend_block = BlockBuilder("⚙️ Backend Development")
        backend_block.child(BlockBuilder("TODO Upgrade database schema [#A]"))
        backend_block.child(BlockBuilder("TODO Implement new API endpoints [#B]"))
        backend_block.child(BlockBuilder("DONE Set up automated testing [#A] ✓"))
        
        project_block.child(frontend_block)
        project_block.child(backend_block)
        
        testing_block = BlockBuilder("🧪 Testing & QA")
        testing_block.child(BlockBuilder("TODO Write unit tests for new features [#B]"))
        testing_block.child(BlockBuilder("TODO Perform cross-browser testing [#C]"))
        testing_block.child(BlockBuilder("TODO Load testing with realistic data [#A]"))
        
        project_block.child(testing_block)
        
        page.add(project_block)
        
        page.empty_line().heading(2, "Builder Code Example")
        page.text("The tasks above were created using code like this:")
        
        page.code_block("python").lines(
            "# Create a high-priority task with scheduling and context",
            "task = (TaskBuilder('Review quarterly reports')",
            "        .todo()",
            "        .scheduled('2025-01-15')", 
            "        .effort(2)",
            "        .high_priority()",
            "        .context('office', 'computer')",
            "        .tag('review', 'quarterly'))",
            "",
            "# Add to page",
            "page.add(task)"
        )
        
        client.create_page("Task Management Demo", page.build())
    
    def _create_block_types_showcase(self, client):
        """Create block types showcase using various builders."""
        print("📋 Creating block types showcase...")
        
        page = (PageBuilder("Block Types Showcase")
               .author("Demo Generator")  
               .created()
               .page_type("demo")
               .category("reference")
               .tags("blocks", "formatting", "reference")
               
               .heading(1, "Logseq Block Types via DSL")
               .text("This page demonstrates every block type created programmatically.")
               .empty_line()
               
               .heading(2, "Text Formatting")
               .text("Plain text created with .text() method")
               .bullet_list(
                   "Bullet point created with .bullet_list()",
                   "**Bold text** and *italic text* via TextBuilder",
                   "Link to [[Welcome to Demo][welcome page]] using .link()"
               )
               
               .empty_line()
               .heading(2, "Nested Block Structure"))
        
        # Create a nested list structure using ListBuilder
        from logseq_py.builders.content_types import ListBuilder
        nested_list = ListBuilder("bullet")
        nested_list.item("Main topic: Content Management")
        nested_list.item("Creating content", 1)
        nested_list.item("Text blocks with formatting", 2)
        nested_list.item("Code blocks with syntax highlighting", 2)
        nested_list.item("Math expressions with LaTeX", 2)
        nested_list.item("Organizing content", 1)
        nested_list.item("Tags and properties", 2)
        nested_list.item("Page relationships", 2)
        nested_list.item("Hierarchical structure", 2)
        nested_list.item("Advanced features", 1)
        nested_list.item("Queries and filters", 2)
        nested_list.item("Workflows and templates", 2)
        
        page.add(nested_list)
        
        page.empty_line().heading(2, "Numbered Lists")
        page.numbered_list(
            "First numbered item via .numbered_list()", 
            "Second numbered item with programmatic creation",
            "Third item showing consistent formatting"
        )
        
        # Add quote
        page.empty_line().heading(2, "Quote Blocks")
        quote = (page.quote()
                .line("This is a blockquote demonstrating the QuoteBuilder.")
                .line("Blockquotes can span multiple lines and are great for:")
                .line("- Highlighting key insights")
                .line("- Citing external sources")  
                .line("- Creating visual emphasis")
                .author("QuoteBuilder DSL"))
        
        # Add separator and metadata section
        page.empty_line().separator().empty_line()
        page.text("*All content on this page was generated using type-safe builders!*")
        
        client.create_page("Block Types Showcase", page.build())
    
    def _create_page_properties_demo(self, client):
        """Create page properties demo."""
        print("🏷️ Creating page properties demo...")
        
        page = (PageBuilder("Page Properties Demo")
               .author("Demo Generator")
               .created()
               .page_type("documentation")
               .category("demo")
               .status("complete")
               .tags("properties", "metadata", "configuration")
               .property("version", "1.0.0")
               .property("complexity", "intermediate")
               
               .heading(1, "Page Properties and Metadata via DSL")
               .text("This page demonstrates property management using PropertyBuilder.")
               .empty_line()
               
               .heading(2, "This Page's Properties")
               .text("The properties above were set using:")
               )
        
        page.code_block("python").lines(
            "page = (PageBuilder('Page Properties Demo')",
            "       .author('Demo Generator')",
            "       .created()",
            "       .page_type('documentation')",
            "       .category('demo')",
            "       .status('complete')",
            "       .tags('properties', 'metadata', 'configuration')",
            "       .property('version', '1.0.0')",
            "       .property('complexity', 'intermediate'))"
        )
        
        page.empty_line().heading(2, "Property Usage Patterns")
        page.bullet_list(
            "**.author()** - Set page author",
            "**.created()** - Set creation date (defaults to now)",
            "**.page_type()** - Set semantic page type",
            "**.tags()** - Add multiple tags at once",
            "**.property()** - Add custom key-value properties",
            "**.status()**, **.category()**, **.priority()** - Common properties"
        )
        
        client.create_page("Page Properties Demo", page.build())
    
    def _create_code_examples_demo(self, client):
        """Create code examples using CodeBlockBuilder."""
        print("💻 Creating code examples demo...")
        
        page = (PageBuilder("Code Examples Demo")
               .author("Demo Generator")
               .created()
               .page_type("demo")
               .category("development")
               .tags("code", "programming", "examples")
               
               .heading(1, "Code Block Examples via DSL")
               .text("This page demonstrates language-aware code generation using CodeBlockBuilder.")
               .empty_line()
               
               .heading(2, "Python Code with Comments"))
        
        python_code = (page.code_block("python")
                      .comment("Fibonacci sequence generator with memoization")
                      .line("def fibonacci(n, memo={}):")
                      .line("    if n in memo:")
                      .line("        return memo[n]")
                      .line("    if n <= 1:")
                      .line("        return n")
                      .blank_line()
                      .line("    memo[n] = fibonacci(n-1, memo) + fibonacci(n-2, memo)")
                      .line("    return memo[n]")
                      .blank_line()
                      .comment("Generate and display first 10 numbers")
                      .line("for i in range(10):")
                      .line("    print(f'F({i}) = {fibonacci(i)}')")
        )
        
        page.empty_line().heading(2, "JavaScript with Async/Await")
        js_code = (page.code_block("javascript")
                  .comment("Modern API fetching with error handling")
                  .line("const fetchUserData = async (userId) => {")
                  .line("  try {")
                  .line("    const response = await fetch(`/api/users/${userId}`);")
                  .line("    if (!response.ok) {")
                  .line("      throw new Error(`HTTP error! status: ${response.status}`);")
                  .line("    }")
                  .blank_line()
                  .line("    const userData = await response.json();")
                  .line("    return userData;")
                  .line("  } catch (error) {")
                  .line("    console.error('Failed to fetch user data:', error);")
                  .line("    throw error;")
                  .line("  }")
                  .line("};"))
        
        page.empty_line().heading(2, "SQL Query")
        sql_code = (page.code_block("sql")
                   .comment("Complex query with joins and aggregation")
                   .line("SELECT ")
                   .line("    u.name,")
                   .line("    u.email,")
                   .line("    COUNT(o.id) as order_count,")
                   .line("    AVG(o.total_amount) as avg_order_value")
                   .line("FROM users u")
                   .line("LEFT JOIN orders o ON u.id = o.user_id")
                   .line("WHERE u.created_at >= '2024-01-01'")
                   .line("GROUP BY u.id, u.name, u.email")
                   .line("HAVING COUNT(o.id) > 0")
                   .line("ORDER BY order_count DESC, avg_order_value DESC")
                   .line("LIMIT 10;"))
        
        page.empty_line().heading(2, "Builder Code Example")
        page.text("The code blocks above were generated using:")
        
        page.code_block("python").lines(
            "# Language-aware code generation",
            "python_code = (page.code_block('python')",
            "              .comment('Fibonacci sequence generator')",
            "              .line('def fibonacci(n, memo={}):') ",
            "              .line('    if n in memo:')",
            "              .line('        return memo[n]')",
            "              .blank_line())",
            "",
            "# Automatic comment formatting per language",
            "js_code = (page.code_block('javascript')",
            "          .comment('Modern API fetching')  # Uses // comments",
            "          .line('const fetchUserData = async (userId) => {'))"
        )
        
        client.create_page("Code Examples Demo", page.build())
    
    def _create_math_examples_demo(self, client):
        """Create math examples using MathBuilder."""
        print("🧮 Creating math examples demo...")
        
        page = (PageBuilder("Math Examples Demo")
               .author("Demo Generator")
               .created()
               .page_type("demo")
               .category("mathematics")
               .tags("math", "latex", "formulas")
               
               .heading(1, "Mathematical Expressions via DSL")
               .text("This page demonstrates LaTeX math generation using MathBuilder.")
               .empty_line()
               
               .heading(2, "Inline Math"))
        
        quadratic_formula = page.math(inline=True).expression('x = \\frac{-b \\pm \\sqrt{b^2 - 4ac}}{2a}').build()
        page.text(f"The quadratic formula is {quadratic_formula}")
        
        page.empty_line().heading(2, "Block Math Expressions")
        
        # Famous equations
        einstein = (page.math()
                   .expression("E = mc^2"))
        
        page.empty_line()
        gaussian_integral = (page.math()
                            .integral("e^{-x^2}", "-\\infty", "\\infty")
                            .expression(" = \\sqrt{\\pi}"))
        
        page.empty_line().heading(2, "Maxwell's Equations")
        maxwell = (page.math()
                  .expression("\\begin{align}")
                  .expression("\\nabla \\cdot \\mathbf{E} &= \\frac{\\rho}{\\epsilon_0} \\\\")
                  .expression("\\nabla \\times \\mathbf{E} &= -\\frac{\\partial \\mathbf{B}}{\\partial t} \\\\")
                  .expression("\\nabla \\cdot \\mathbf{B} &= 0 \\\\")
                  .expression("\\nabla \\times \\mathbf{B} &= \\mu_0\\mathbf{J} + \\mu_0\\epsilon_0\\frac{\\partial \\mathbf{E}}{\\partial t}")
                  .expression("\\end{align}"))
        
        page.empty_line().heading(2, "Builder Usage")
        page.text("Mathematical expressions were created using:")
        
        page.code_block("python").lines(
            "# Inline math",
            "inline_math = page.math(inline=True).expression('x = \\\\frac{-b \\\\pm \\\\sqrt{b^2 - 4ac}}{2a}')",
            "",
            "# Block math with integrals",
            "gaussian = (page.math()",
            "           .integral('e^{-x^2}', '-\\\\infty', '\\\\infty')",
            "           .expression(' = \\\\sqrt{\\\\pi}'))",
            "",
            "# Complex multi-line expressions",
            "maxwell = (page.math()",
            "          .expression('\\\\begin{align}')",
            "          .expression('\\\\nabla \\\\cdot \\\\mathbf{E} &= \\\\frac{\\\\rho}{\\\\epsilon_0}')",
            "          .expression('\\\\end{align}'))"
        )
        
        client.create_page("Math Examples Demo", page.build())
    
    def _create_tables_media_demo(self, client):
        """Create tables and media examples."""
        print("📊 Creating tables and media demo...")
        
        page = (PageBuilder("Tables and Media Demo")
               .author("Demo Generator")
               .created()
               .page_type("demo")
               .category("multimedia")
               .tags("tables", "media", "structured-data")
               
               .heading(1, "Tables and Media via DSL")
               .text("This page demonstrates structured content using TableBuilder and MediaBuilder.")
               .empty_line()
               
               .heading(2, "Project Timeline Table"))
        
        timeline_table = (page.table()
                         .headers("Phase", "Duration", "Status", "Owner")
                         .alignment("left", "center", "center", "left")
                         .row("Planning", "1 week", "✅ Complete", "Alice")
                         .row("Development", "3 weeks", "🔄 In Progress", "Bob")
                         .row("Testing", "1 week", "⏳ Pending", "Charlie")
                         .row("Deployment", "2 days", "⏳ Pending", "Diana"))
        
        page.empty_line().heading(2, "Feature Comparison Table")
        feature_table = (page.table()
                        .headers("Feature", "Basic Plan", "Pro Plan", "Enterprise")
                        .alignment("left", "center", "center", "center")
                        .row("Storage", "10 GB", "100 GB", "Unlimited")
                        .row("Users", "5", "50", "Unlimited")
                        .row("Support", "Email", "Email + Chat", "24/7 Phone")
                        .row("Price/month", "$10", "$50", "$200"))
        
        page.empty_line().heading(2, "Media Embeds")
        page.text("Media embeds using MediaBuilder:")
        
        media = (page.media()
                .image("https://logseq.com/logo.png", "Logseq Logo", "Official Logseq Logo")
                .youtube("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
                .pdf("https://example.com/document.pdf", 1))
        
        page.empty_line().heading(2, "Builder Code")
        page.text("Tables and media were created using:")
        
        page.code_block("python").lines(
            "# Create table with headers and alignment",
            "table = (page.table()",
            "        .headers('Phase', 'Duration', 'Status', 'Owner')",
            "        .alignment('left', 'center', 'center', 'left')",
            "        .row('Planning', '1 week', '✅ Complete', 'Alice')",
            "        .row('Development', '3 weeks', '🔄 In Progress', 'Bob'))",
            "",
            "# Add various media types",
            "media = (page.media()",
            "        .image('https://example.com/logo.png', 'Logo')",
            "        .youtube('https://youtube.com/watch?v=...')",
            "        .pdf('https://example.com/doc.pdf', page=1))"
        )
        
        client.create_page("Tables and Media Demo", page.build())
    
    def _create_query_examples_demo(self, client):
        """Create query examples using QueryBuilder."""
        print("🔍 Creating query examples demo...")
        
        page = (PageBuilder("Query Examples Demo")
               .author("Demo Generator")
               .created()
               .page_type("demo")
               .category("queries")
               .tags("queries", "search", "dynamic-content")
               
               .heading(1, "Dynamic Queries via DSL")
               .text("This page demonstrates dynamic content queries using QueryBuilder.")
               .empty_line()
               
               .heading(2, "Task Queries"))
        
        from logseq_py.builders.advanced_builders import QueryBuilder as DSLQueryBuilder
        
        # Find all TODO tasks
        page.text("All TODO tasks:")
        todo_query = DSLQueryBuilder().todo()
        page.text(todo_query.build())
        
        page.empty_line()
        page.text("High priority tasks (TODO or DOING):")
        priority_query = (DSLQueryBuilder()
                         .and_query()
                         .task_state("TODO", "DOING")
                         .property("priority", "A"))
        page.text(priority_query.build())
        
        page.empty_line().heading(2, "Date-based Queries")
        page.text("Tasks from this week:")
        week_query = DSLQueryBuilder().task_state("TODO", "DONE").this_week()
        page.text(week_query.build())
        
        page.empty_line()
        page.text("Items from last 30 days:")
        month_query = DSLQueryBuilder().last_days(30)
        page.text(month_query.build())
        
        page.empty_line().heading(2, "Property-based Queries")
        page.text("Demo pages:")
        demo_query = DSLQueryBuilder().property("type", "demo")
        page.text(demo_query.build())
        
        page.empty_line()
        page.text("Pages by specific author:")
        author_query = DSLQueryBuilder().property("author", "Demo Generator")
        page.text(author_query.build())
        
        page.empty_line().heading(2, "Complex Combined Queries")
        page.text("Demo pages created this month:")
        complex_query = (DSLQueryBuilder()
                        .and_query()
                        .property("type", "demo")
                        .property("author", "Demo Generator")
                        .this_month())
        page.text(complex_query.build())
        
        page.empty_line().heading(2, "Builder Usage")
        page.text("Queries above were created using:")
        
        page.code_block("python").lines(
            "# Simple task query",
            "todo_query = DSLQueryBuilder().todo()",
            "",
            "# Complex combined query",
            "complex_query = (DSLQueryBuilder()",
            "                .and_query()",
            "                .property('type', 'demo')",
            "                .property('author', 'Demo Generator')",
            "                .this_month())",
            "",
            "# Add to page",
            "page.text(complex_query.build())"
        )
        
        client.create_page("Query Examples Demo", page.build())
    
    def _create_workflow_demo(self, client):
        """Create workflow documentation using WorkflowBuilder."""
        print("⚙️ Creating workflow demo...")
        
        # Create workflow using WorkflowBuilder
        workflow = (WorkflowBuilder("Code Review Process")
                   .prerequisite("Pull request submitted")
                   .prerequisite("All tests passing")
                   .prerequisite("Code coverage meets threshold")
                   
                   .tool("GitHub/GitLab")
                   .tool("CI/CD pipeline")
                   .tool("Code analysis tools")
                   
                   .step("Initial Review", 
                        "Automated checks run and reviewer is assigned",
                        ["GitHub Actions", "Linting tools"])
                   
                   .step("Code Analysis",
                        "Reviewer examines code for logic, style, and best practices",
                        ["IDE", "Code review checklist"])
                   
                   .step("Feedback & Discussion",
                        "Comments are added and discussion happens",
                        ["GitHub comments", "Slack/Teams"])
                   
                   .step("Approval & Merge",
                        "Code is approved and merged to main branch",
                        ["Git", "Deployment tools"])
                   
                   .outcome("High-quality code in production")
                   .outcome("Knowledge sharing among team")
                   .outcome("Consistent coding standards"))
        
        page = (PageBuilder("Workflow Demo")
               .author("Demo Generator")
               .created()
               .page_type("demo")
               .category("process")
               .tags("workflow", "process", "documentation")
               
               .heading(1, "Workflow Documentation via DSL")
               .text("This page demonstrates process documentation using WorkflowBuilder.")
               .empty_line())
        
        # Add the workflow content
        page.add(workflow)
        
        page.empty_line().heading(2, "Builder Usage")
        page.text("The workflow above was created using:")
        
        page.code_block("python").lines(
            "workflow = (WorkflowBuilder('Code Review Process')",
            "           .prerequisite('Pull request submitted')",
            "           .prerequisite('All tests passing')",
            "",
            "           .tool('GitHub/GitLab')",
            "           .tool('CI/CD pipeline')",
            "",
            "           .step('Initial Review',", 
            "                'Automated checks run and reviewer assigned',",
            "                ['GitHub Actions', 'Linting tools'])",
            "",
            "           .step('Code Analysis',",
            "                'Reviewer examines code for quality')",
            "",
            "           .outcome('High-quality code in production')",
            "           .outcome('Knowledge sharing among team'))"
        )
        
        client.create_page("Workflow Demo", page.build())
    
    def _create_journal_entries_demo(self, client):
        """Create journal entries using JournalBuilder."""
        print("📔 Creating journal entries demo...")
        
        # Create journals directory
        journals_dir = self.demo_path / "journals"
        journals_dir.mkdir(exist_ok=True)
        
        # Create a week of journal entries
        start_date = date.today() - timedelta(days=6)
        
        for i in range(7):
            current_date = start_date + timedelta(days=i)
            day_name = current_date.strftime("%A")
            
            journal = (JournalBuilder(current_date)
                      .daily_note(f"{day_name}: Focused on DSL development and testing")
                      .mood("productive", 8 - (i % 3))
                      .weather("sunny" if i % 2 == 0 else "cloudy", f"{20 + i}°C")
                      
                      .gratitude(
                          "Progress on the DSL implementation",
                          "Clear requirements and good documentation",
                          "Supportive development environment"
                      )
                      
                      .habit_tracker(
                          exercise=i % 2 == 0,
                          meditation=i % 3 == 0,
                          reading=i % 4 == 0,
                          journaling=True
                      )
                      
                      .work_log(
                          f"Implemented {['core', 'content', 'page', 'advanced'][i % 4]} builders",
                          "Tested DSL functionality with real examples",
                          "Documented builder patterns and usage"
                      )
                      
                      .learning_log(
                          "Builder Pattern",
                          "Learned how to create fluent interfaces and method chaining for intuitive APIs",
                          "Gang of Four Design Patterns"
                      ))
            
            # Create journal file with standard Logseq naming
            journal_filename = current_date.strftime("%Y_%m_%d.md")
            journal_path = journals_dir / journal_filename
            
            with open(journal_path, 'w', encoding='utf-8') as f:
                f.write(journal.build())
    
    def _create_project_pages_demo(self, client):
        """Create project pages using convenience functions."""
        print("📋 Creating project pages demo...")
        
        # E-commerce project
        ecommerce = (PageBuilder("Project: E-commerce Platform")
                    .author("Demo Generator")
                    .created()
                    .page_type("project")
                    .status("active")
                    .property("deadline", "2025-03-01")
                    .property("budget", "$75000")
                    .team("Alice Johnson", "Bob Smith", "Charlie Brown")
                    .progress(65)
                    .tags("ecommerce", "web-development", "react")
                    
                    .heading(1, "E-commerce Platform Development")
                    .text("Modern, scalable e-commerce solution with React frontend and Node.js backend.")
                    .empty_line()
                    
                    .heading(2, "Project Goals")
                    .bullet_list(
                        "🚀 Launch MVP within 3 months",
                        "💰 Handle $1M+ in transactions",
                        "👥 Support 10,000+ concurrent users",
                        "📱 Mobile-first responsive design",
                        "🔒 PCI DSS compliance"
                    )
                    
                    .heading(2, "Technology Stack"))
        
        # Add tech stack table
        tech_table = (ecommerce.table()
                     .headers("Layer", "Technology", "Version", "Status")
                     .row("Frontend", "React + TypeScript", "18.x", "✅ Set up")
                     .row("Backend", "Node.js + Express", "20.x", "✅ Set up")
                     .row("Database", "PostgreSQL", "15.x", "✅ Set up")
                     .row("Payment", "Stripe API", "Latest", "🔄 Integration")
                     .row("Hosting", "AWS ECS", "Latest", "⏳ Pending"))
        
        ecommerce.empty_line().heading(2, "Active Tasks")
        ecommerce.add(TaskBuilder("Implement product catalog API").doing().high_priority()
                     .assigned_to("Alice Johnson").effort("2d"))
        ecommerce.add(TaskBuilder("Design checkout flow UI").todo().high_priority()
                     .assigned_to("Bob Smith").effort("1d"))
        ecommerce.add(TaskBuilder("Set up payment processing").todo().medium_priority()
                     .assigned_to("Charlie Brown").effort("3d"))
        ecommerce.add(TaskBuilder("Configure production deployment").todo().low_priority()
                     .effort("1d"))
        
        client.create_page("Project: E-commerce Platform", ecommerce.build())
        
        # Mobile app project
        mobile_app = (PageBuilder("Project: Task Management Mobile App")
                     .author("Demo Generator")
                     .created()
                     .page_type("project")
                     .status("planning")
                     .property("deadline", "2025-04-15")
                     .team("Diana Wilson", "Eve Davis")
                     .progress(25)
                     .tags("mobile", "ios", "android", "productivity")
                     
                     .heading(1, "Task Management Mobile App")
                     .text("Cross-platform mobile app for personal productivity and task management.")
                     .empty_line()
                     
                     .heading(2, "App Features")
                     .bullet_list(
                         "📝 Create and manage tasks",
                         "🏷️ Tag-based organization",
                         "⏰ Reminders and notifications",
                         "📊 Progress tracking and analytics",
                         "☁️ Cloud sync across devices"
                     )
                     
                     .heading(2, "Development Milestones"))
        
        milestone_table = (mobile_app.table()
                          .headers("Milestone", "Target Date", "Status", "Progress")
                          .row("Design & Prototyping", "2025-02-01", "🔄 In Progress", "80%")
                          .row("Core Development", "2025-03-15", "⏳ Pending", "0%")
                          .row("Testing & Polish", "2025-04-01", "⏳ Pending", "0%")
                          .row("App Store Release", "2025-04-15", "⏳ Pending", "0%"))
        
        client.create_page("Project: Task Management Mobile App", mobile_app.build())
    
    def _create_logseq_config(self):
        """Create Logseq configuration files."""
        print("⚙️ Creating Logseq configuration...")
        
        config_dir = self.demo_path / ".logseq"
        config_dir.mkdir(exist_ok=True)
        
        # Enhanced config.edn
        config_content = '''{:meta/version 1
 :feature/enable-timetracking? true
 :feature/enable-journals? true
 :property-pages/enabled? true
 :property-pages/excludelist #{"template" "Public"}
 
 :graph/settings {:journal/page-title-format "yyyy_MM_dd"
                 :preferred-format :markdown
                 :hidden [".logseq"]
                 :default-templates {:journals "journals"}}
 
 :editor/logical-outdenting? true
 :ui/show-brackets? false
 :ui/auto-expand-block-refs? true
 
 :favorites ["Welcome to Demo"]
 
 :quick-capture-templates
 {:text "{{date}} {{time}}: [[quick capture]] $INPUT"
  :media "{{date}} {{time}}: [[media]] "}
}'''
        
        with open(config_dir / "config.edn", "w") as f:
            f.write(config_content)
        
        # Enhanced custom.css
        css_content = '''/* Demo Custom Styles */

/* Enhanced page properties */
.page-properties {
    background: #f8f9fa;
    border: 1px solid #e9ecef;
    border-radius: 6px;
    padding: 12px;
    margin-bottom: 16px;
}

/* Task styling */
.task-marker {
    font-weight: bold;
}

/* Code block enhancements */
.CodeMirror {
    font-family: 'JetBrains Mono', 'SF Mono', Monaco, 'Consolas', monospace;
    border-radius: 6px;
}

/* Table styling */
table {
    border-collapse: collapse;
    margin: 16px 0;
}

table th, table td {
    padding: 8px 12px;
    border: 1px solid #e1e5e9;
}

table th {
    background-color: #f8f9fa;
    font-weight: 600;
}

/* Quote block styling */
blockquote {
    border-left: 4px solid #0066cc;
    background: #f8faff;
    margin: 16px 0;
    padding: 12px 16px;
    border-radius: 0 4px 4px 0;
}

/* Math block styling */
.katex-display {
    margin: 16px 0;
    padding: 12px;
    background: #fafafa;
    border-radius: 4px;
}

/* Demo page indicators */
.page-title[data-ref*="Demo"] {
    color: #0066cc;
}

/* Priority indicators */
.priority-a { color: #dc3545; font-weight: bold; }
.priority-b { color: #fd7e14; }
.priority-c { color: #6c757d; }

/* Status indicators */
.status-active { color: #198754; }
.status-complete { color: #0d6efd; }
.status-planning { color: #6f42c1; }
'''
        
        with open(config_dir / "custom.css", "w") as f:
            f.write(css_content)


def main():
    """Main function to run the DSL demo generator."""
    demo_path = Path(__file__).parent / "logseq-demo"
    generator = LogseqDemoGenerator(demo_path)
    generator.generate_complete_demo()


if __name__ == "__main__":
    main()