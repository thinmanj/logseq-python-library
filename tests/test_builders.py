"""
Comprehensive tests for Logseq builders.

Tests cover:
- BlockBuilder newline handling (regression test for v0.3.1 fix)
- BlockBuilder multi-line content (regression test for v0.3.2 fix)
- Code blocks in blocks
- Nested block structures
- PageBuilder integration
- Content type builders (tasks, tables, quotes, etc.)
"""

import pytest
from datetime import datetime, date
from logseq_py.builders import BlockBuilder, LogseqBuilder, PageBuilder
from logseq_py.builders.content_types import (
    CodeBlockBuilder, TaskBuilder, TableBuilder, QuoteBuilder,
    ListBuilder, TextBuilder, MathBuilder, MediaBuilder
)
from logseq_py.builders.advanced_builders import QueryBuilder, JournalBuilder, WorkflowBuilder


class TestBlockBuilderNewlines:
    """Regression tests for v0.3.1 - blocks must render on separate lines."""
    
    def test_simple_block_has_newline(self):
        """Single block should end with content, no trailing newline needed."""
        block = BlockBuilder("Test content")
        result = block.build()
        assert result == "- Test content"
    
    def test_parent_child_blocks_on_separate_lines(self):
        """Parent and child blocks must be on separate lines."""
        parent = BlockBuilder("Parent")
        child = BlockBuilder("Child")
        parent.child(child)
        
        result = parent.build()
        lines = result.split("\n")
        
        assert len(lines) == 2
        assert lines[0] == "- Parent"
        assert lines[1] == "  - Child"
    
    def test_multiple_children_each_on_own_line(self):
        """Each child block should be on its own line."""
        parent = BlockBuilder("Parent")
        parent.child(BlockBuilder("Child 1"))
        parent.child(BlockBuilder("Child 2"))
        parent.child(BlockBuilder("Child 3"))
        
        result = parent.build()
        lines = result.split("\n")
        
        assert len(lines) == 4
        assert lines[0] == "- Parent"
        assert lines[1] == "  - Child 1"
        assert lines[2] == "  - Child 2"
        assert lines[3] == "  - Child 3"
    
    def test_nested_block_hierarchy(self):
        """Deeply nested blocks should maintain proper hierarchy."""
        level1 = BlockBuilder("Level 1")
        level2 = BlockBuilder("Level 2")
        level3 = BlockBuilder("Level 3")
        
        level2.child(level3)
        level1.child(level2)
        
        result = level1.build()
        lines = result.split("\n")
        
        assert len(lines) == 3
        assert lines[0] == "- Level 1"
        assert lines[1] == "  - Level 2"
        assert lines[2] == "    - Level 3"
    
    def test_siblings_at_same_level(self):
        """Sibling blocks should have same indentation."""
        parent = BlockBuilder("Parent")
        child1 = BlockBuilder("Child 1")
        child2 = BlockBuilder("Child 2")
        
        grandchild1 = BlockBuilder("Grandchild 1")
        grandchild2 = BlockBuilder("Grandchild 2")
        
        child1.child(grandchild1)
        child2.child(grandchild2)
        parent.child(child1)
        parent.child(child2)
        
        result = parent.build()
        lines = result.split("\n")
        
        assert "  - Child 1" in lines
        assert "  - Child 2" in lines
        assert "    - Grandchild 1" in lines
        assert "    - Grandchild 2" in lines


class TestBlockBuilderMultiLineContent:
    """Regression tests for v0.3.2 - multi-line content must not split incorrectly."""
    
    def test_code_block_in_block_keeps_structure(self):
        """Code blocks should maintain their structure within a block."""
        code = CodeBlockBuilder("python")
        code.line("def hello():")
        code.line("    print('world')")
        
        block = BlockBuilder(code.build())
        result = block.build()
        lines = result.split("\n")
        
        # Should have: bullet+opening, code line 1, code line 2, closing
        assert len(lines) == 4
        assert lines[0] == "- ```python"
        assert lines[1] == "  def hello():"
        assert lines[2] == "      print('world')"
        assert lines[3] == "  ```"
    
    def test_code_block_as_child_block(self):
        """Code block as child should be properly indented."""
        parent = BlockBuilder("Here is some code:")
        code = CodeBlockBuilder("javascript")
        code.line("console.log('test');")
        
        parent.child(BlockBuilder(code.build()))
        result = parent.build()
        lines = result.split("\n")
        
        assert lines[0] == "- Here is some code:"
        assert lines[1] == "  - ```javascript"
        assert lines[2] == "    console.log('test');"
        assert lines[3] == "    ```"
    
    def test_multiline_text_content_indents_correctly(self):
        """Multi-line plain text should indent continuation lines."""
        content = "Line 1\nLine 2\nLine 3"
        block = BlockBuilder(content)
        result = block.build()
        lines = result.split("\n")
        
        assert len(lines) == 3
        assert lines[0] == "- Line 1"
        assert lines[1] == "  Line 2"
        assert lines[2] == "  Line 3"
    
    def test_code_block_with_blank_lines(self):
        """Code blocks with blank lines should preserve them."""
        code = CodeBlockBuilder("python")
        code.line("def foo():")
        code.blank_line()
        code.line("    return 42")
        
        block = BlockBuilder(code.build())
        result = block.build()
        lines = result.split("\n")
        
        assert lines[0] == "- ```python"
        assert lines[1] == "  def foo():"
        assert lines[2] == "  "  # Blank line with indentation
        assert lines[3] == "      return 42"
        assert lines[4] == "  ```"
    
    def test_nested_code_blocks(self):
        """Code blocks in nested blocks should maintain proper indentation."""
        root = BlockBuilder("Root")
        child = BlockBuilder("Child with code:")
        
        code = CodeBlockBuilder("bash")
        code.line("echo 'hello'")
        child.child(BlockBuilder(code.build()))
        root.child(child)
        
        result = root.build()
        lines = result.split("\n")
        
        assert lines[0] == "- Root"
        assert lines[1] == "  - Child with code:"
        assert lines[2] == "    - ```bash"
        assert lines[3] == "      echo 'hello'"
        assert lines[4] == "      ```"
    
    def test_long_code_block_maintains_indentation(self):
        """Longer code blocks should maintain consistent indentation."""
        code = CodeBlockBuilder("python")
        code.line("class Example:")
        code.line("    def __init__(self):")
        code.line("        self.value = 0")
        code.blank_line()
        code.line("    def increment(self):")
        code.line("        self.value += 1")
        
        block = BlockBuilder(code.build())
        result = block.build()
        
        # Verify no lines are unindented
        for line in result.split("\n")[1:]:  # Skip first line with bullet
            assert line.startswith("  "), f"Line not properly indented: {line}"


class TestBlockBuilderProperties:
    """Test block properties rendering."""
    
    def test_block_with_properties(self):
        """Block with properties should render PROPERTIES drawer."""
        block = BlockBuilder("Content")
        block.property("id", "123")
        block.property("status", "done")
        
        result = block.build()
        lines = result.split("\n")
        
        assert "- Content" in lines
        assert ":PROPERTIES:" in lines
        assert ":ID: 123" in lines
        assert ":STATUS: done" in lines
        assert ":END:" in lines
    
    def test_properties_multiple_blocks(self):
        """Multiple blocks can have independent properties."""
        block1 = BlockBuilder("Block 1").property("priority", "high")
        block2 = BlockBuilder("Block 2").property("priority", "low")
        
        result1 = block1.build()
        result2 = block2.build()
        
        assert ":PRIORITY: high" in result1
        assert ":PRIORITY: low" in result2


class TestCodeBlockBuilder:
    """Test CodeBlockBuilder standalone and in various contexts."""
    
    def test_empty_code_block(self):
        """Empty code block should have opening and closing."""
        code = CodeBlockBuilder("python")
        result = code.build()
        
        assert result == "```python\n```"
    
    def test_code_block_with_language(self):
        """Code block should include language identifier."""
        code = CodeBlockBuilder("javascript")
        code.line("const x = 1;")
        
        result = code.build()
        assert result.startswith("```javascript")
        assert "const x = 1;" in result
    
    def test_code_block_language_change(self):
        """Can change language after creation."""
        code = CodeBlockBuilder()
        code.language("rust")
        code.line("fn main() {}")
        
        result = code.build()
        assert "```rust" in result
    
    def test_code_block_with_comments(self):
        """Code block should handle language-specific comments."""
        # Python
        python_code = CodeBlockBuilder("python")
        python_code.comment("This is a comment")
        assert "# This is a comment" in python_code.build()
        
        # JavaScript
        js_code = CodeBlockBuilder("javascript")
        js_code.comment("This is a comment")
        assert "// This is a comment" in js_code.build()
        
        # SQL
        sql_code = CodeBlockBuilder("sql")
        sql_code.comment("This is a comment")
        assert "-- This is a comment" in sql_code.build()
    
    def test_code_block_multiple_lines(self):
        """Code block with multiple lines using lines() method."""
        code = CodeBlockBuilder("python")
        code.lines(
            "def calculate(x, y):",
            "    return x + y",
            "",
            "result = calculate(5, 3)"
        )
        
        result = code.build()
        assert "def calculate(x, y):" in result
        assert "return x + y" in result
        assert "result = calculate(5, 3)" in result


class TestTaskBuilder:
    """Test TaskBuilder for task blocks."""
    
    def test_basic_todo_task(self):
        """Basic TODO task."""
        task = TaskBuilder("Buy groceries")
        result = task.build()
        
        assert "TODO Buy groceries" in result
    
    def test_task_states(self):
        """Different task states."""
        assert "DOING" in TaskBuilder("Task").doing().build()
        assert "DONE" in TaskBuilder("Task").done().build()
        assert "LATER" in TaskBuilder("Task").later().build()
        assert "NOW" in TaskBuilder("Task").now().build()
    
    def test_task_with_priority(self):
        """Tasks with priorities."""
        high = TaskBuilder("Urgent task").todo().high_priority()
        assert "[#A]" in high.build()
        
        medium = TaskBuilder("Normal task").todo().medium_priority()
        assert "[#B]" in medium.build()
        
        low = TaskBuilder("Optional task").todo().low_priority()
        assert "[#C]" in low.build()
    
    def test_task_with_scheduling(self):
        """Task with scheduled date."""
        task = TaskBuilder("Meeting").scheduled("2025-01-15")
        result = task.build()
        
        assert "SCHEDULED: <2025-01-15>" in result
    
    def test_task_with_deadline(self):
        """Task with deadline."""
        task = TaskBuilder("Report").deadline("2025-01-20")
        result = task.build()
        
        assert "DEADLINE: <2025-01-20>" in result


class TestTableBuilder:
    """Test TableBuilder for markdown tables."""
    
    def test_simple_table(self):
        """Simple table with headers and rows."""
        table = TableBuilder()
        table.headers("Name", "Age", "City")
        table.row("Alice", "30", "NYC")
        table.row("Bob", "25", "LA")
        
        result = table.build()
        lines = result.split("\n")
        
        assert "| Name | Age | City |" in lines[0]
        assert "|---|---|---|" in lines[1]
        assert "| Alice | 30 | NYC |" in lines[2]
        assert "| Bob | 25 | LA |" in lines[3]
    
    def test_table_with_alignment(self):
        """Table with column alignment."""
        table = TableBuilder()
        table.headers("Left", "Center", "Right")
        table.alignment("left", "center", "right")
        table.row("A", "B", "C")
        
        result = table.build()
        assert "|---|:---:|---:|" in result


class TestQuoteBuilder:
    """Test QuoteBuilder for quote blocks."""
    
    def test_simple_quote(self):
        """Simple quote."""
        quote = QuoteBuilder()
        quote.line("To be or not to be")
        
        result = quote.build()
        assert "> To be or not to be" in result
    
    def test_multiline_quote(self):
        """Multi-line quote."""
        quote = QuoteBuilder()
        quote.lines("First line", "Second line", "Third line")
        
        result = quote.build()
        lines = result.split("\n")
        
        assert len(lines) == 3
        assert all(line.startswith("> ") for line in lines)
    
    def test_quote_with_author(self):
        """Quote with attribution."""
        quote = QuoteBuilder()
        quote.line("The only way to do great work is to love what you do")
        quote.author("Steve Jobs")
        
        result = quote.build()
        assert "> — Steve Jobs" in result


class TestMediaBuilder:
    """Test MediaBuilder for embeds."""
    
    def test_youtube_embed(self):
        """YouTube video embed."""
        media = MediaBuilder()
        media.youtube("https://youtube.com/watch?v=abc123")
        
        result = media.build()
        assert "{{video https://youtube.com/watch?v=abc123}}" in result
    
    def test_twitter_embed(self):
        """Twitter post embed."""
        media = MediaBuilder()
        media.twitter("https://twitter.com/user/status/123")
        
        result = media.build()
        assert "{{twitter https://twitter.com/user/status/123}}" in result
    
    def test_pdf_embed(self):
        """PDF embed."""
        media = MediaBuilder()
        media.pdf("https://example.com/doc.pdf")
        
        result = media.build()
        assert "{{pdf https://example.com/doc.pdf}}" in result
    
    def test_pdf_embed_with_page(self):
        """PDF embed with specific page."""
        media = MediaBuilder()
        media.pdf("https://example.com/doc.pdf", page=5)
        
        result = media.build()
        assert "{{pdf https://example.com/doc.pdf#5}}" in result
    
    def test_multiple_media_items(self):
        """Multiple media items separated properly."""
        media = MediaBuilder()
        media.youtube("https://youtube.com/watch?v=1")
        media.twitter("https://twitter.com/user/status/1")
        
        result = media.build()
        # Multiple items should be separated by double newline
        assert "{{video" in result
        assert "{{twitter" in result


class TestPageBuilder:
    """Test PageBuilder for complete pages."""
    
    def test_page_with_title(self):
        """Page with title."""
        page = PageBuilder("My Page")
        result = page.build()
        
        # Title is typically metadata, not in content
        # Properties might be present
        assert isinstance(result, str)
    
    def test_page_with_properties(self):
        """Page with properties."""
        page = PageBuilder("Project Page")
        page.property("status", "active")
        page.property("priority", "high")
        
        result = page.build()
        assert "status:: active" in result
        assert "priority:: high" in result
    
    def test_page_with_headings_and_content(self):
        """Page with structured content."""
        page = PageBuilder("Documentation")
        page.heading(1, "Introduction")
        page.text("This is the introduction.")
        page.heading(2, "Details")
        page.text("More details here.")
        
        result = page.build()
        assert "# Introduction" in result
        assert "## Details" in result
        assert "This is the introduction." in result
    
    def test_page_with_code_block(self):
        """Page with code block."""
        page = PageBuilder("Code Example")
        page.heading(2, "Python Example")
        code = page.code_block("python")
        code.line("print('Hello, World!')")
        
        result = page.build()
        assert "## Python Example" in result
        assert "```python" in result
        assert "print('Hello, World!')" in result
    
    def test_page_with_task_list(self):
        """Page with task list."""
        page = PageBuilder("Todo List")
        page.heading(2, "Tasks")
        page.add(TaskBuilder("Task 1").todo())
        page.add(TaskBuilder("Task 2").done())
        
        result = page.build()
        assert "TODO Task 1" in result
        assert "DONE Task 2" in result


class TestLogseqBuilder:
    """Test LogseqBuilder as orchestrator."""
    
    def test_multiple_blocks(self):
        """LogseqBuilder with multiple top-level blocks."""
        builder = LogseqBuilder()
        builder.add(BlockBuilder("Block 1"))
        builder.add(BlockBuilder("Block 2"))
        
        result = builder.build()
        lines = result.split("\n")
        
        assert "- Block 1" in lines
        assert "- Block 2" in lines
    
    def test_mixed_content(self):
        """LogseqBuilder with mixed content types."""
        builder = LogseqBuilder()
        builder.text("Plain text")
        builder.add(BlockBuilder("A block"))
        builder.text("More text")
        
        result = builder.build()
        assert "Plain text" in result
        assert "- A block" in result
        assert "More text" in result


class TestQueryBuilder:
    """Test QueryBuilder for Logseq queries."""
    
    def test_simple_todo_query(self):
        """Simple TODO query."""
        query = QueryBuilder().todo()
        result = query.build()
        
        assert "{{query" in result
        assert "(task TODO)" in result
    
    def test_property_query(self):
        """Query with property condition."""
        query = QueryBuilder().property("status", "active")
        result = query.build()
        
        assert '(property status "active")' in result
    
    def test_combined_query(self):
        """Query with multiple conditions."""
        query = QueryBuilder()
        query.and_query()
        query.todo()
        query.property("priority", "high")
        
        result = query.build()
        assert "and" in result
        assert "(task TODO)" in result
        assert '(property priority "high")' in result


class TestJournalBuilder:
    """Test JournalBuilder for journal entries."""
    
    def test_journal_with_date(self):
        """Journal entry with specific date."""
        journal = JournalBuilder("2025-01-15")
        result = journal.build()
        
        # Should contain date-related metadata
        assert isinstance(result, str)
    
    def test_journal_with_mood(self):
        """Journal with mood tracking."""
        journal = JournalBuilder()
        journal.mood("happy", 8)
        
        result = journal.build()
        assert "Mood: happy" in result
        assert "(8/10)" in result
    
    def test_journal_with_gratitude(self):
        """Journal with gratitude entries."""
        journal = JournalBuilder()
        journal.gratitude("Health", "Family", "Work")
        
        result = journal.build()
        assert "Gratitude" in result
        assert "Health" in result
        assert "Family" in result


class TestEdgeCases:
    """Test edge cases and potential issues."""
    
    def test_empty_block(self):
        """Empty block returns empty string."""
        block = BlockBuilder("")
        result = block.build()
        assert result == ""
    
    def test_block_with_special_characters(self):
        """Block with special Logseq characters."""
        block = BlockBuilder("Block with [[link]] and #tag")
        result = block.build()
        assert "[[link]]" in result
        assert "#tag" in result
    
    def test_deeply_nested_structure(self):
        """Very deep nesting should work."""
        root = BlockBuilder("Root")
        current = root
        
        for i in range(10):
            child = BlockBuilder(f"Level {i+1}")
            current.child(child)
            current = child
        
        result = root.build()
        lines = result.split("\n")
        
        assert len(lines) == 11  # Root + 10 levels
        # Last line should have most indentation
        assert lines[-1].startswith("                    ")  # 10 * 2 spaces
    
    def test_block_with_unicode(self):
        """Block with unicode characters."""
        block = BlockBuilder("Hello 世界 🌍")
        result = block.build()
        assert "世界" in result
        assert "🌍" in result
    
    def test_code_block_with_special_syntax(self):
        """Code block with syntax that looks like Logseq markup."""
        code = CodeBlockBuilder("python")
        code.line("# This is not a [[link]]")
        code.line("tag = '#not-a-tag'")
        
        block = BlockBuilder(code.build())
        result = block.build()
        
        # Should preserve as-is within code block
        assert "# This is not a [[link]]" in result
        assert "tag = '#not-a-tag'" in result


class TestIntegrationScenarios:
    """Test realistic usage scenarios."""
    
    def test_meeting_notes_page(self):
        """Complete meeting notes page."""
        page = PageBuilder("Meeting Notes - 2025-01-15")
        page.property("date", "2025-01-15")
        page.property("attendees", "Alice, Bob, Charlie")
        
        page.heading(1, "Meeting Notes")
        page.heading(2, "Agenda")
        page.bullet_list("Project updates", "Q1 planning", "Team feedback")
        
        page.heading(2, "Action Items")
        page.add(TaskBuilder("Alice: Prepare Q1 roadmap").todo().high_priority())
        page.add(TaskBuilder("Bob: Review budget").todo())
        
        result = page.build()
        assert "Meeting Notes" in result
        assert "attendees:: Alice, Bob, Charlie" in result
        assert "TODO" in result
        assert "[#A]" in result
    
    def test_code_documentation_page(self):
        """Code documentation with examples."""
        page = PageBuilder("API Documentation")
        
        page.heading(1, "Authentication API")
        page.text("Use the following endpoint to authenticate:")
        
        code = page.code_block("bash")
        code.line("curl -X POST https://api.example.com/auth")
        code.line('  -H "Content-Type: application/json"')
        code.line('  -d \'{"username":"user","password":"pass"}\'')
        
        page.heading(2, "Response")
        response_code = page.code_block("json")
        response_code.line("{")
        response_code.line('  "token": "abc123",')
        response_code.line('  "expires": "2025-01-20"')
        response_code.line("}")
        
        result = page.build()
        assert "# Authentication API" in result
        assert "```bash" in result
        assert "```json" in result
        assert "curl -X POST" in result
    
    def test_project_page_with_tasks_and_notes(self):
        """Project page with mixed content."""
        page = PageBuilder("Project: Website Redesign")
        page.status("in-progress")
        page.property("deadline", "2025-02-01")
        
        page.heading(1, "Website Redesign Project")
        page.heading(2, "Overview")
        page.text("Complete redesign of company website.")
        
        page.heading(2, "Tasks")
        page.add(TaskBuilder("Design mockups").done())
        page.add(TaskBuilder("Frontend implementation").doing().high_priority())
        page.add(TaskBuilder("Backend integration").todo())
        page.add(TaskBuilder("User testing").later())
        
        page.heading(2, "Notes")
        page.text("Using React for frontend")
        page.text("Target: Mobile-first design")
        
        result = page.build()
        assert "DONE Design mockups" in result
        # Priority comes right after state: "DOING [#A] Frontend implementation"
        assert "DOING [#A] Frontend implementation" in result
        assert "LATER User testing" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
