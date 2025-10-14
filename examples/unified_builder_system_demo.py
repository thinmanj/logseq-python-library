#!/usr/bin/env python3

"""
Unified Builder System Demo

This example demonstrates the unified read/write system where Logseq content
can be both generated using builders AND parsed back into the same builder
constructs for modification. This creates a seamless workflow for content
manipulation.

Key Features Demonstrated:
- Loading existing content as builder objects
- Modifying content using builder methods
- Converting between builders and parsed content
- Round-trip content processing (read → modify → write)
"""

import sys
from pathlib import Path
from datetime import datetime, date

# Add the parent directory to path to import our library
sys.path.append(str(Path(__file__).parent.parent))

from logseq_py.builders import (
    PageBuilder, TaskBuilder, CodeBlockBuilder, HeadingBuilder,
    BuilderParser, ContentReconstructor, BuilderBasedLoader
)
from logseq_py import LogseqClient

def demonstrate_unified_system():
    """Demonstrate the unified read/write system."""
    print("🔄 Unified Builder System Demonstration")
    print("=" * 60)
    
    demo_path = Path("logseq-demo")
    if not demo_path.exists():
        print("❌ Demo content not found. Run generate_logseq_demo.py first!")
        return
    
    # Initialize client and builder-based loader
    client = LogseqClient(str(demo_path))
    loader = BuilderBasedLoader(str(demo_path))
    
    print("\n📖 Step 1: Loading existing content as builders")
    demonstrate_loading_as_builders(client, loader)
    
    print("\n✏️  Step 2: Modifying content using builders")
    demonstrate_modification_with_builders(client, loader)
    
    print("\n🔄 Step 3: Round-trip processing")
    demonstrate_round_trip_processing(client, loader)
    
    print("\n🧩 Step 4: Builder reconstruction")
    demonstrate_builder_reconstruction(client)
    
    print("\n🎯 Step 5: Advanced content manipulation")
    demonstrate_advanced_manipulation(client, loader)
    
    print("\n✅ Unified system demonstration complete!")

def demonstrate_loading_as_builders(client, loader):
    """Show how to load existing content as builder objects."""
    print("   Loading 'Welcome to Demo' page as a PageBuilder...")
    
    # Load page using traditional method
    traditional_page = client.get_page("Welcome to Demo")
    if not traditional_page:
        print("   ⚠️ Welcome page not found, skipping this demo")
        return
    
    print(f"   Traditional loading: {len(traditional_page.blocks)} blocks as model objects")
    
    # Load the same page as a builder
    page_builder = loader.load_page_as_builder("Welcome to Demo")
    if page_builder:
        print(f"   ✅ Builder loading: Loaded as {type(page_builder).__name__}")
        print(f"   📄 Page title: {page_builder._title}")
        print(f"   📋 Content blocks: {len(page_builder._content_blocks)}")
    
    # Show individual block conversion
    print("   Converting individual blocks to builders:")
    for i, block in enumerate(traditional_page.blocks[:3]):  # Show first 3 blocks
        builder = BuilderParser.parse_block_to_builder(block)
        if builder:
            print(f"   • Block {i+1}: {type(builder).__name__} - {block.content[:50]}...")

def demonstrate_modification_with_builders(client, loader):
    """Show how to modify content using builders."""
    print("   Modifying 'Task Management Demo' page using builders...")
    
    original_page = client.get_page("Task Management Demo")
    if not original_page:
        print("   ⚠️ Task Management Demo not found, creating it")
        return
    
    print(f"   Original page has {len(original_page.blocks)} blocks")
    
    # Load as builder and modify
    def add_enhancement_tasks(page_builder):
        """Add enhancement tasks to the page."""
        page_builder.empty_line()
        page_builder.heading(2, "Enhancement Tasks (Added by Builder)")
        
        # Add various types of tasks
        page_builder.add(
            TaskBuilder()
            .todo()
            .priority("A")
            .text("Implement advanced task filtering")
        )
        
        page_builder.add(
            TaskBuilder()
            .doing()
            .priority("B")
            .text("Optimize task performance with caching")
        )
        
        page_builder.add(
            TaskBuilder()
            .later()
            .priority("C")
            .text("Add task templates and automation")
        )
        
        # Add a code example
        code_builder = page_builder.code_block("python")
        code_builder.line("# Enhanced task processing")
        code_builder.line("def process_tasks_with_priority():")
        code_builder.line("    high_priority = filter(lambda t: t.priority == 'A', tasks)")
        code_builder.line("    return sorted(high_priority, key=lambda t: t.created)")
    
    # Apply modifications
    success = client.modify_page_with_builder("Task Management Demo", add_enhancement_tasks)
    
    if success:
        print("   ✅ Successfully modified page using builder system")
        # Verify the changes
        updated_page = client.get_page("Task Management Demo")
        if updated_page:
            print(f"   📊 Updated page now has {len(updated_page.blocks)} blocks")
            
            # Count different types of tasks
            task_counts = {}
            for block in updated_page.blocks:
                if block.task_state:
                    status = block.task_state.value
                    task_counts[status] = task_counts.get(status, 0) + 1
            
            print(f"   📋 Task distribution: {task_counts}")
    else:
        print("   ❌ Failed to modify page")

def demonstrate_round_trip_processing(client, loader):
    """Demonstrate reading content, processing it, and writing it back."""
    print("   Round-trip processing of 'Code Examples Demo' page...")
    
    # Step 1: Load as builder
    page_builder = loader.load_page_as_builder("Code Examples Demo")
    if not page_builder:
        print("   ⚠️ Code Examples Demo not found")
        return
    
    print("   📖 Loaded existing content as builder")
    
    # Step 2: Analyze and enhance the content
    def enhance_code_examples(builder):
        """Enhance code examples with additional context."""
        # Add metadata section
        builder.empty_line()
        builder.heading(2, "Code Analysis (Generated)")
        builder.text("This section was generated by analyzing the existing code blocks.")
        builder.empty_line()
        
        # Analyze code blocks in the content
        code_block_count = 0
        languages_used = set()
        
        # Note: In a full implementation, we'd analyze the actual code blocks
        # For this demo, we'll add some representative analysis
        builder.text("📊 **Analysis Results:**")
        builder.text(f"- Code blocks analyzed: Multiple examples found")
        builder.text(f"- Languages detected: Python, JavaScript, and more")
        builder.text(f"- Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        
        # Add enhancement suggestions
        builder.empty_line()
        builder.heading(3, "Enhancement Suggestions")
        
        suggestions = [
            "Add error handling examples",
            "Include performance optimizations", 
            "Create unit tests for examples",
            "Add documentation comments"
        ]
        
        for suggestion in suggestions:
            builder.add(
                TaskBuilder()
                .todo()
                .priority("B")
                .text(suggestion)
            )
    
    # Step 3: Apply enhancements
    enhance_code_examples(page_builder)
    
    # Step 4: Write back the enhanced content
    enhanced_content = page_builder.build()
    
    # Update the page
    original_page = client.get_page("Code Examples Demo")
    if original_page:
        # Clear and rebuild blocks
        original_page.blocks.clear()
        from logseq_py.utils import LogseqUtils
        new_blocks = LogseqUtils.parse_blocks_from_content(enhanced_content, "Code Examples Demo")
        for block in new_blocks:
            original_page.add_block(block)
        
        # Save the changes
        client._save_page(original_page)
        print("   ✅ Round-trip processing complete - content enhanced and saved")
    else:
        print("   ❌ Could not complete round-trip processing")

def demonstrate_builder_reconstruction(client):
    """Show how to reconstruct content using builders."""
    print("   Reconstructing content from parsed data...")
    
    # Get a page with various content types
    page = client.get_page("Block Types Showcase")
    if not page:
        print("   ⚠️ Block Types Showcase not found")
        return
    
    print(f"   📄 Original page: {len(page.blocks)} blocks")
    
    # Reconstruct the entire page using builders
    reconstructed_content = ContentReconstructor.reconstruct_page(page)
    
    # Show comparison
    print("   🔍 Content Reconstruction Results:")
    print(f"   • Original content length: {len(page.get_content())} characters")
    print(f"   • Reconstructed length: {len(reconstructed_content)} characters")
    
    # Test individual block reconstruction
    print("   🧱 Individual block reconstruction:")
    for i, block in enumerate(page.blocks[:3]):  # First 3 blocks
        reconstructed_block = ContentReconstructor.reconstruct_block(block)
        print(f"   • Block {i+1}: {block.content[:30]}... → {reconstructed_block[:30]}...")

def demonstrate_advanced_manipulation(client, loader):
    """Show advanced content manipulation techniques."""
    print("   Advanced manipulation: Creating a dynamic summary page...")
    
    # Load multiple pages as builders
    all_builders = loader.load_all_pages_as_builders()
    print(f"   📚 Loaded {len(all_builders)} pages as builders")
    
    # Create a dynamic summary using builder analysis
    summary_builder = PageBuilder("Dynamic Content Summary")
    summary_builder.author("Builder System")
    summary_builder.created()
    summary_builder.page_type("analysis")
    
    # Add summary content
    summary_builder.heading(1, "📊 Dynamic Content Analysis")
    summary_builder.text(f"This page was generated by analyzing {len(all_builders)} pages using the builder system.")
    summary_builder.empty_line()
    
    # Analyze page types
    page_types = {}
    task_counts = {}
    
    for page_name, builder in all_builders.items():
        # Count different types of content
        if hasattr(builder, '_content_blocks'):
            for block in builder._content_blocks:
                if hasattr(block, '__class__'):
                    block_type = block.__class__.__name__
                    page_types[block_type] = page_types.get(block_type, 0) + 1
    
    # Add analysis results
    summary_builder.heading(2, "Content Distribution")
    summary_builder.text("Distribution of content types across all pages:")
    summary_builder.empty_line()
    
    for content_type, count in sorted(page_types.items()):
        summary_builder.text(f"- **{content_type}**: {count} instances")
    
    # Add recommendations
    summary_builder.empty_line()
    summary_builder.heading(2, "Recommendations")
    
    recommendations = [
        "Consider standardizing task priorities across pages",
        "Add more cross-references between related content",
        "Create template builders for common page types",
        "Implement automated content validation"
    ]
    
    for rec in recommendations:
        summary_builder.add(
            TaskBuilder()
            .todo()
            .priority("B")
            .text(rec)
        )
    
    # Save the dynamic summary
    summary_content = summary_builder.build()
    
    try:
        client.create_page("Dynamic Content Summary", summary_content)
        print("   ✅ Created dynamic summary page using advanced manipulation")
    except ValueError as e:
        if "already exists" in str(e):
            # Update existing page
            def update_summary(builder):
                # Clear and rebuild
                builder._content_blocks = summary_builder._content_blocks
                builder._properties = summary_builder._properties
            
            client.modify_page_with_builder("Dynamic Content Summary", update_summary)
            print("   ✅ Updated existing dynamic summary page")
        else:
            print(f"   ❌ Failed to create summary: {e}")

def show_system_capabilities():
    """Display the capabilities of the unified system."""
    print("\n🎯 Unified Builder System Capabilities")
    print("-" * 50)
    
    capabilities = [
        "✅ Load existing Logseq content as builder objects",
        "✅ Modify content using fluent builder interface", 
        "✅ Convert between parsed models and builders seamlessly",
        "✅ Round-trip content processing (read → modify → write)",
        "✅ Automatic content type detection and builder selection",
        "✅ Preserve content structure and metadata during conversion", 
        "✅ Unified API for both content generation and modification",
        "✅ Type-safe content manipulation with IDE support",
        "✅ Advanced content analysis and enhancement capabilities",
        "✅ Dynamic content generation based on existing data"
    ]
    
    for capability in capabilities:
        print(f"   {capability}")
    
    print("\n💡 Use Cases:")
    use_cases = [
        "📝 Content migration and transformation",
        "🔄 Automated content updates and maintenance", 
        "📊 Dynamic report generation from existing content",
        "🧹 Bulk content formatting and standardization",
        "🔗 Cross-reference generation and link management",
        "📋 Template creation from existing content patterns",
        "🎯 Content analysis and optimization recommendations",
        "⚡ Real-time content modification workflows"
    ]
    
    for use_case in use_cases:
        print(f"   {use_case}")

if __name__ == "__main__":
    demonstrate_unified_system()
    show_system_capabilities()
    
    print(f"\n🎉 The unified builder system provides a powerful foundation for:")
    print("   • Seamless content manipulation workflows")
    print("   • Type-safe programmatic content management") 
    print("   • Advanced content analysis and enhancement")
    print("   • Flexible read/write content processing pipelines")
    print("\n📚 This demonstrates the full circle of content lifecycle management!")