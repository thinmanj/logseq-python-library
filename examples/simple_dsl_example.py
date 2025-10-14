#!/usr/bin/env python3
"""
Simple DSL Example

This demonstrates the new Logseq Builder DSL with a basic example.
"""

import sys
from pathlib import Path

# Add the parent directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from logseq_py.builders import PageBuilder, TaskBuilder, CodeBlockBuilder, QuoteBuilder, TableBuilder


def main():
    """Demonstrate the DSL builders."""
    print("🎯 Logseq DSL Example")
    
    # Create a page using the fluent interface
    page = (PageBuilder("DSL Example Page")
            .author("DSL Demo")
            .created()
            .page_type("example")
            .tags("dsl", "demo", "builders")
            
            # Add content using method chaining
            .heading(1, "Welcome to the DSL!")
            .text("This page demonstrates the new builder patterns.")
            .empty_line()
            
            .heading(2, "Task Management")
            .text("Tasks created with TaskBuilder:"))
    
    # Add tasks using TaskBuilder
    page.add(TaskBuilder("Learn the new DSL").todo().high_priority())
    page.add(TaskBuilder("Create example content").doing().medium_priority().effort("2h"))
    page.add(TaskBuilder("Share with the team").todo().low_priority().context("email"))
    
    # Add code example
    page.empty_line().heading(2, "Code Example")
    code_block = (page.code_block("python")
                 .comment("Example of using the DSL")
                 .line("page = (PageBuilder('My Page')")
                 .line("       .author('Me')")
                 .line("       .heading(1, 'Hello World!')")
                 .line("       .text('Content here'))")
                 .blank_line()
                 .line("task = TaskBuilder('Do something').todo().high_priority()")
                 .line("page.add(task)"))
    
    # Add quote
    page.empty_line().heading(2, "Quote Example")
    quote_block = (page.quote()
                  .line("The best way to predict the future is to create it.")
                  .author("Peter Drucker"))
    
    # Add table
    page.empty_line().heading(2, "Table Example")
    table = (page.table()
            .headers("Feature", "Status", "Priority")
            .row("Core DSL", "✅ Complete", "High")
            .row("Advanced Features", "🔄 In Progress", "Medium")
            .row("Documentation", "📝 Planned", "Low"))
    
    page.empty_line().separator().empty_line()
    page.text("*Generated with the Logseq Builder DSL!* 🚀")
    
    # Build and output
    content = page.build()
    
    print("\n" + "="*50)
    print("GENERATED CONTENT:")
    print("="*50)
    print(content)
    print("="*50)
    
    # Write to file for inspection
    output_file = Path(__file__).parent / "dsl_example_output.md"
    with open(output_file, "w") as f:
        f.write(content)
    
    print(f"\n✅ Content written to: {output_file}")
    print("🎉 DSL example completed successfully!")


if __name__ == "__main__":
    main()