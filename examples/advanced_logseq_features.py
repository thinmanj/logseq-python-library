#!/usr/bin/env python3
"""
Advanced Logseq Features Example

This example demonstrates all the advanced Logseq features supported by the library:
- Task management (TODO states, priorities, scheduling)
- Advanced content types (code, math, queries)
- Namespaces and templates
- Block references and embeds
- Whiteboards and annotations
- Workflow automation
"""

import sys
import os
from datetime import date, datetime, timedelta

# Add the parent directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from logseq_py import (
    LogseqClient, TaskState, Priority, BlockType,
    Template, Annotation, WhiteboardElement
)


def main():
    # Replace with your actual Logseq graph path
    graph_path = "/path/to/your/logseq/graph"
    
    if not os.path.exists(graph_path):
        print(f"Graph path '{graph_path}' not found.")
        print("Please update the graph_path variable with your actual Logseq graph directory.")
        return
    
    print("🚀 Advanced Logseq Features Demo")
    print("=" * 50)
    
    client = LogseqClient(graph_path)
    client.load_graph()
    
    # === 1. TASK MANAGEMENT ===
    print("\\n1️⃣  TASK MANAGEMENT")
    print("-" * 30)
    
    # Find all tasks
    all_tasks = client.query().blocks().is_task().execute()
    print(f"📋 Total tasks in graph: {len(all_tasks)}")
    
    # Tasks by state
    for state in TaskState:
        tasks = client.query().blocks().has_task_state(state).execute()
        if tasks:
            print(f"   {state.value}: {len(tasks)} tasks")
    
    # High priority tasks
    priority_a_tasks = client.query().blocks().has_priority(Priority.A).execute()
    print(f"🔥 High priority (A) tasks: {len(priority_a_tasks)}")
    
    # Scheduled tasks for today
    today = date.today()
    today_tasks = client.query().blocks().has_scheduled_date(today).execute()
    print(f"📅 Tasks scheduled for today: {len(today_tasks)}")
    
    # Overdue tasks
    overdue_tasks = client.query().blocks().has_deadline().custom_filter(
        lambda block: block.deadline and block.deadline.date < today
    ).execute()
    print(f"⚠️  Overdue tasks: {len(overdue_tasks)}")
    
    # === 2. ADVANCED CONTENT TYPES ===
    print("\\n2️⃣  ADVANCED CONTENT TYPES")
    print("-" * 30)
    
    # Code blocks
    code_blocks = client.query().blocks().is_code_block().execute()
    print(f"💻 Total code blocks: {len(code_blocks)}")
    
    # Code blocks by language
    languages = {}
    for block in code_blocks:
        lang = block.code_language or "unknown"
        languages[lang] = languages.get(lang, 0) + 1
    
    print("   Code languages:")
    for lang, count in sorted(languages.items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"      {lang}: {count} blocks")
    
    # Math blocks
    math_blocks = client.query().blocks().has_math_content().execute()
    print(f"🔢 Math/LaTeX blocks: {len(math_blocks)}")
    
    # Query blocks
    query_blocks = client.query().blocks().has_query().execute()
    print(f"🔍 Query blocks: {len(query_blocks)}")
    
    # Headings by level
    print("📝 Headings by level:")
    for level in range(1, 7):
        headings = client.query().blocks().is_heading(level).execute()
        if headings:
            print(f"   H{level}: {len(headings)} headings")
    
    # === 3. NAMESPACES AND ORGANIZATION ===
    print("\\n3️⃣  NAMESPACES AND ORGANIZATION")
    print("-" * 30)
    
    # Get all namespaces
    namespaces = client.graph.get_all_namespaces()
    print(f"📁 Total namespaces: {len(namespaces)}")
    
    for namespace in namespaces[:10]:  # Show first 10
        pages_in_ns = client.query().pages().in_namespace(namespace).execute()
        print(f"   {namespace}/: {len(pages_in_ns)} pages")
    
    # Template pages
    template_pages = client.query().pages().is_template().execute()
    print(f"📄 Template pages: {len(template_pages)}")
    
    # Whiteboard pages
    whiteboard_pages = client.query().pages().is_whiteboard().execute()
    print(f"🎨 Whiteboard pages: {len(whiteboard_pages)}")
    
    # === 4. BLOCK RELATIONSHIPS ===
    print("\\n4️⃣  BLOCK RELATIONSHIPS")
    print("-" * 30)
    
    # Blocks with references to other blocks
    ref_blocks = client.query().blocks().has_block_references().execute()
    print(f"🔗 Blocks with references: {len(ref_blocks)}")
    
    # Blocks with embedded content
    embed_blocks = client.query().blocks().has_embeds().execute()
    print(f"📎 Blocks with embeds: {len(embed_blocks)}")
    
    # Show some examples
    if ref_blocks:
        print("   Reference examples:")
        for block in ref_blocks[:3]:
            refs = list(block.referenced_blocks)[:2]  # Show first 2 refs
            print(f"      {block.content[:50]}... -> {refs}")
    
    # === 5. WORKFLOW INSIGHTS ===
    print("\\n5️⃣  WORKFLOW INSIGHTS")
    print("-" * 30)
    
    workflow_summary = client.graph.get_workflow_summary()
    print(f"📊 Workflow Summary:")
    print(f"   Total tasks: {workflow_summary['total_tasks']}")
    print(f"   Scheduled: {workflow_summary['scheduled_tasks']}")
    print(f"   With deadlines: {workflow_summary['tasks_with_deadline']}")
    
    print("   Task states:")
    for state, count in workflow_summary['task_states'].items():
        if count > 0:
            print(f"      {state}: {count}")
    
    # === 6. PAGE ANALYSIS ===
    print("\\n6️⃣  PAGE ANALYSIS")
    print("-" * 30)
    
    # Most complex pages (by block count)
    all_pages = list(client.graph.pages.values())
    complex_pages = sorted(all_pages, key=lambda p: len(p.blocks), reverse=True)[:5]
    
    print("📚 Most complex pages:")
    for page in complex_pages:
        outline = page.get_page_outline()
        print(f"   {page.name}:")
        print(f"      {outline['blocks']['total']} blocks")
        print(f"      {outline['tasks']['total']} tasks ({outline['tasks']['completed']} done)")
        print(f"      {len(outline['headings'])} headings")
    
    # Pages with most tasks
    task_pages = [(page, len(page.get_task_blocks())) 
                  for page in all_pages if page.get_task_blocks()]
    task_pages.sort(key=lambda x: x[1], reverse=True)
    
    print("\\n✅ Pages with most tasks:")
    for page, task_count in task_pages[:5]:
        completed = len(page.get_completed_tasks())
        completion_rate = (completed / task_count * 100) if task_count > 0 else 0
        print(f"   {page.name}: {task_count} tasks ({completion_rate:.1f}% complete)")
    
    # === 7. ADVANCED QUERIES ===
    print("\\n7️⃣  ADVANCED QUERY EXAMPLES")
    print("-" * 30)
    
    # Complex query: High priority tasks due this week
    next_week = today + timedelta(days=7)
    urgent_tasks = (client.query()
                   .blocks()
                   .is_task()
                   .has_priority(Priority.A)
                   .custom_filter(lambda block: 
                       block.deadline and 
                       today <= block.deadline.date <= next_week)
                   .sort_by('deadline')
                   .execute())
    
    print(f"🚨 Urgent tasks (Priority A, due within 7 days): {len(urgent_tasks)}")
    for task in urgent_tasks[:3]:
        deadline_str = task.deadline.date.strftime("%Y-%m-%d") if task.deadline else "No deadline"
        print(f"   - {task.content[:50]}... (Due: {deadline_str})")
    
    # Find pages with incomplete tasks
    incomplete_task_pages = (client.query()
                           .pages()
                           .custom_filter(lambda page:
                               len(page.get_task_blocks()) > len(page.get_completed_tasks()))
                           .sort_by('name')
                           .execute())
    
    print(f"\\n📋 Pages with incomplete tasks: {len(incomplete_task_pages)}")
    
    # === 8. GRAPH INSIGHTS ===
    print("\\n8️⃣  COMPREHENSIVE GRAPH INSIGHTS")
    print("-" * 30)
    
    insights = client.graph.get_graph_insights()
    
    print("🔍 Graph Overview:")
    print(f"   Pages: {insights['total_pages']}")
    print(f"   Blocks: {insights['total_blocks']}")
    print(f"   Namespaces: {insights['namespaces']}")
    print(f"   Templates: {insights['templates']}")
    print(f"   Whiteboards: {insights['whiteboards']}")
    
    print("\\n📈 Most Connected Pages:")
    for page_name, connection_count in insights['most_connected_pages'][:5]:
        print(f"   {page_name}: {connection_count} backlinks")
    
    print("\\n🏷️  Most Used Tags:")
    for tag, usage_count in insights['most_used_tags'][:10]:
        print(f"   #{tag}: {usage_count} pages")
    
    # === 9. CONTENT ANALYSIS ===
    print("\\n9️⃣  CONTENT ANALYSIS")
    print("-" * 30)
    
    # Collapsed blocks
    collapsed_blocks = client.query().blocks().is_collapsed().execute()
    print(f"👁️  Collapsed blocks: {len(collapsed_blocks)}")
    
    # Blocks with annotations
    annotated_blocks = client.query().blocks().has_annotations().execute()
    print(f"📝 Blocks with annotations: {len(annotated_blocks)}")
    
    # Journal pages with tasks
    journal_with_tasks = (client.query()
                         .pages()
                         .is_journal()
                         .custom_filter(lambda page: len(page.get_task_blocks()) > 0)
                         .sort_by('journal_date', desc=True)
                         .limit(5)
                         .execute())
    
    print(f"📓 Recent journal entries with tasks: {len(journal_with_tasks)}")
    for journal in journal_with_tasks:
        task_count = len(journal.get_task_blocks())
        date_str = journal.journal_date.strftime("%Y-%m-%d") if journal.journal_date else "Unknown"
        print(f"   {date_str}: {task_count} tasks")
    
    # === 10. PRODUCTIVITY METRICS ===
    print("\\n🔟 PRODUCTIVITY METRICS")
    print("-" * 30)
    
    # Calculate completion rates
    total_tasks = len(all_tasks)
    completed_tasks = len(client.query().blocks().is_completed_task().execute())
    completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
    
    print(f"📊 Overall task completion rate: {completion_rate:.1f}%")
    print(f"   Completed: {completed_tasks}/{total_tasks}")
    
    # Tasks created vs completed (rough estimate based on recent activity)
    recent_tasks = (client.query()
                   .blocks()
                   .is_task()
                   .created_after(today - timedelta(days=30))
                   .execute())
    
    recent_completed = (client.query()
                       .blocks()
                       .is_completed_task()
                       .updated_after(today - timedelta(days=30))
                       .execute())
    
    print(f"\\n📈 Last 30 days:")
    print(f"   New tasks: ~{len(recent_tasks)}")
    print(f"   Tasks completed: ~{len(recent_completed)}")
    
    print("\\n🎉 Advanced features analysis completed!")
    print("This demonstrates the comprehensive Logseq feature support in the library.")


if __name__ == "__main__":
    main()