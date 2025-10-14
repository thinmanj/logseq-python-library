#!/usr/bin/env python3

"""
Advanced Logseq Content Processing with Updates

This example demonstrates:
- Loading and analyzing existing Logseq content 
- Identifying content patterns and insights
- Making smart updates based on analysis
- Adding contextual cross-references and connections
- Creating dynamic content based on existing data
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta
import re

# Add the parent directory to path to import our library
sys.path.append(str(Path(__file__).parent.parent))

from logseq_py import LogseqClient, LogseqGraph

def process_and_enhance_content():
    """Process existing content and enhance it intelligently."""
    print("🚀 Advanced Logseq Content Processing & Enhancement")
    print("=" * 60)
    
    # Initialize client with demo content
    demo_path = Path("logseq-demo")
    if not demo_path.exists():
        print("❌ Demo content not found. Run generate_logseq_demo.py first!")
        return
    
    client = LogseqClient(str(demo_path))
    graph = LogseqGraph(str(demo_path))
    
    print("📊 Loading and analyzing existing content...")
    
    # 1. Analyze task distribution
    task_analysis = analyze_task_patterns(graph)
    print(f"   Found {task_analysis['total_tasks']} tasks across {task_analysis['pages_with_tasks']} pages")
    
    # 2. Identify knowledge gaps
    knowledge_gaps = identify_knowledge_gaps(graph)
    print(f"   Identified {len(knowledge_gaps)} potential knowledge gaps")
    
    # 3. Find orphaned pages
    orphaned_pages = find_orphaned_pages(graph)
    print(f"   Found {len(orphaned_pages)} orphaned pages")
    
    # 4. Create enhancement suggestions
    enhancements = create_enhancement_suggestions(task_analysis, knowledge_gaps, orphaned_pages)
    
    # 5. Apply smart updates
    print("\n🔧 Applying intelligent content enhancements...")
    apply_smart_enhancements(client, enhancements)
    
    # 6. Create dynamic summary dashboard
    print("\n📋 Creating dynamic dashboard...")
    create_dynamic_dashboard(client, task_analysis, knowledge_gaps)
    
    # 7. Add contextual cross-references
    print("\n🔗 Adding contextual cross-references...")
    add_contextual_links(client, graph)
    
    print("\n✅ Content processing and enhancement complete!")
    print("\n📈 Enhancement Summary:")
    for enhancement_type, count in enhancements.items():
        if isinstance(count, int):
            print(f"   {enhancement_type}: {count} items")

def analyze_task_patterns(graph):
    """Analyze task distribution and patterns."""
    task_analysis = {
        'total_tasks': 0,
        'pages_with_tasks': 0,
        'status_distribution': {},
        'priority_distribution': {},
        'task_density': {}
    }
    
    for page in graph.pages.values():
        page_tasks = 0
        for block in page.blocks:
            if hasattr(block, 'task_status') and block.task_status:
                task_analysis['total_tasks'] += 1
                page_tasks += 1
                
                # Count status distribution
                status = block.task_status
                task_analysis['status_distribution'][status] = task_analysis['status_distribution'].get(status, 0) + 1
                
                # Count priority distribution
                if hasattr(block, 'priority') and block.priority:
                    priority = block.priority
                    task_analysis['priority_distribution'][priority] = task_analysis['priority_distribution'].get(priority, 0) + 1
        
        if page_tasks > 0:
            task_analysis['pages_with_tasks'] += 1
            task_analysis['task_density'][page.title] = page_tasks
    
    return task_analysis

def identify_knowledge_gaps(graph):
    """Identify potential knowledge gaps and improvement opportunities."""
    gaps = []
    
    # Find pages with many outgoing links but no incoming links
    for page in graph.pages.values():
        outgoing_count = len(page.linked_references)
        incoming_count = len([p for p in graph.pages.values() 
                            if page.title in [ref.strip('[]') for ref in p.linked_references]])
        
        if outgoing_count > 3 and incoming_count == 0:
            gaps.append({
                'type': 'isolated_hub',
                'page': page.title,
                'description': f'Page with {outgoing_count} outgoing links but no incoming references'
            })
    
    # Find frequently referenced pages that might need more content
    page_references = {}
    for page in graph.pages.values():
        for ref in page.linked_references:
            clean_ref = ref.strip('[]')
            page_references[clean_ref] = page_references.get(clean_ref, 0) + 1
    
    for page_title, ref_count in page_references.items():
        if ref_count > 2 and page_title in graph.pages:
            page = graph.pages[page_title]
            if len(page.blocks) < 5:  # Very short page
                gaps.append({
                    'type': 'under_developed',
                    'page': page_title,
                    'description': f'Frequently referenced ({ref_count} times) but minimal content'
                })
    
    return gaps

def find_orphaned_pages(graph):
    """Find pages with no incoming or outgoing links."""
    orphaned = []
    
    for page in graph.pages.values():
        if not page.linked_references:  # No outgoing links
            # Check for incoming links
            incoming_count = len([p for p in graph.pages.values() 
                                if page.title in [ref.strip('[]') for ref in p.linked_references]])
            
            if incoming_count == 0:
                orphaned.append(page.title)
    
    return orphaned

def create_enhancement_suggestions(task_analysis, knowledge_gaps, orphaned_pages):
    """Create intelligent enhancement suggestions."""
    suggestions = {
        'task_improvements': 0,
        'knowledge_connections': len(knowledge_gaps),
        'orphan_integrations': len(orphaned_pages),
        'cross_references': 0
    }
    
    # Suggest task improvements
    incomplete_ratio = (task_analysis['total_tasks'] - task_analysis['status_distribution'].get('DONE', 0)) / max(task_analysis['total_tasks'], 1)
    if incomplete_ratio > 0.8:
        suggestions['task_improvements'] = 1
    
    return suggestions

def apply_smart_enhancements(client, enhancements):
    """Apply intelligent enhancements to the content."""
    
    # 1. Add task management tips if high incomplete ratio
    if enhancements['task_improvements'] > 0:
        create_task_management_guide(client)
    
    # 2. Create knowledge connection suggestions
    if enhancements['knowledge_connections'] > 0:
        create_knowledge_bridge_page(client)
    
    # 3. Create integration suggestions for orphaned pages
    if enhancements['orphan_integrations'] > 0:
        create_content_integration_guide(client)

def create_task_management_guide(client):
    """Create a task management improvement guide."""
    guide_content = """# 📋 Task Management Enhancement Guide

*Generated based on analysis of your current task distribution*

## 🎯 Key Insights

Your current task completion rate suggests room for improvement. Here are some strategies:

## 📈 Improvement Strategies

- ### Priority Matrix
  - Use [#A], [#B], [#C] priorities consistently
  - Focus on high-priority items first
  
- ### Status Workflow
  - TODO → DOING → DONE (basic flow)
  - Use LATER for items without urgency
  - Use WAITING for blocked items

- ### Daily Review
  - Review TODO items each morning
  - Move stale items to LATER or CANCELLED
  - Celebrate DONE items

## 📊 Recommended Queries

Query to find high priority TODO items:
```query
{:title "High Priority Tasks"
 :query [:find (pull ?h [*])
         :where
         [?h :block/marker ?marker]
         [(contains? #{"TODO" "DOING"} ?marker)]
         [?h :block/priority "A"]]}
```

## 🔗 Related Pages

- [[Task Management Demo]]
- [[Project Management Workflows]]
"""
    
    client.create_page("Task Management Enhancement Guide", guide_content)

def create_knowledge_bridge_page(client):
    """Create a page to bridge knowledge gaps."""
    bridge_content = """# 🌉 Knowledge Bridge Connections

*Suggested connections to strengthen your knowledge graph*

## 🎯 Purpose

This page helps identify and create meaningful connections between isolated knowledge areas.

## 🔗 Suggested Connections

Based on content analysis, consider linking these related concepts:

- ### Development Projects
  - Link coding examples to specific projects
  - Connect project pages to relevant documentation

- ### Learning Integration  
  - Connect theoretical concepts to practical examples
  - Link tutorials to project applications

## 📊 Content Integration Tips

- **Cross-reference related topics**: Use [[page links]] to connect ideas
- **Tag consistently**: Use similar tags for related content  
- **Create summary pages**: Aggregate related content periodically
- **Use queries**: Create dynamic views of connected content

## 🔄 Regular Maintenance

- Weekly: Review and add missing connections
- Monthly: Clean up orphaned pages
- Quarterly: Restructure major knowledge areas
"""
    
    client.create_page("Knowledge Bridge Connections", bridge_content)

def create_content_integration_guide(client):
    """Create guide for integrating orphaned content."""
    guide_content = """# 🔗 Content Integration Guide

*Strategies for connecting isolated pages to your knowledge graph*

## 🎯 Integration Strategies

### For Project Pages
- Link to related technologies and tools
- Connect to learning resources
- Reference similar projects

### For Tutorial Pages  
- Link to practical applications
- Connect to related concepts
- Reference prerequisites and next steps

### For Reference Pages
- Connect to examples and use cases
- Link to related documentation
- Tag with relevant categories

## 📋 Integration Checklist

- [ ] Add at least 2-3 outgoing links per page
- [ ] Include relevant tags
- [ ] Reference from related existing pages
- [ ] Add to appropriate index or summary pages

## 🔄 Maintenance Process

1. **Identify**: Find pages with few connections
2. **Analyze**: Understand the content and context
3. **Connect**: Add relevant links and references  
4. **Review**: Periodically check and improve connections
"""
    
    client.create_page("Content Integration Guide", guide_content)

def create_dynamic_dashboard(client, task_analysis, knowledge_gaps):
    """Create a dynamic dashboard with real-time insights."""
    
    # Calculate some metrics
    total_tasks = task_analysis['total_tasks']
    done_tasks = task_analysis['status_distribution'].get('DONE', 0)
    completion_rate = (done_tasks / total_tasks * 100) if total_tasks > 0 else 0
    
    dashboard_content = f"""# 📊 Knowledge Graph Dashboard

*Live dashboard - Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}*

## 📈 Current Metrics

| Metric | Value | Status |
|--------|-------|---------|
| Total Tasks | {total_tasks} | {"🟢" if total_tasks > 10 else "🟡"} |
| Completion Rate | {completion_rate:.1f}% | {"🟢" if completion_rate > 70 else "🟡" if completion_rate > 40 else "🔴"} |
| Knowledge Gaps | {len(knowledge_gaps)} | {"🟢" if len(knowledge_gaps) < 3 else "🟡"} |

## ⚡ Quick Actions

### Today's Focus
```query
{{:title "Today's Priority Tasks"
 :query [:find (pull ?h [*])
         :where
         [?h :block/marker ?marker]
         [(contains? #{{"TODO" "DOING"}} ?marker)]
         [?h :block/priority "A"]]}}
```

### Recent Progress
```query
{{:title "Recently Completed"
 :query [:find (pull ?h [*])
         :where
         [?h :block/marker "DONE"]
         [?h :block/updated-at ?d]
         [(> ?d (- (js/Date.now) (* 7 24 3600 1000)))]]}}
```

## 🎯 Improvement Opportunities

{"### Task Management" if total_tasks > done_tasks * 3 else ""}
{"- Consider breaking down large tasks into smaller ones" if total_tasks > done_tasks * 3 else ""}
{"- Review and update task priorities regularly" if total_tasks > done_tasks * 3 else ""}

{"### Knowledge Connections" if len(knowledge_gaps) > 2 else ""}
{"- Add more cross-references between related topics" if len(knowledge_gaps) > 2 else ""}
{"- Create summary pages for major topics" if len(knowledge_gaps) > 2 else ""}

## 🔗 Quick Navigation

- [[Task Management Enhancement Guide]]
- [[Knowledge Bridge Connections]]  
- [[Content Integration Guide]]

---
*This dashboard is automatically updated when you run content analysis*
"""
    
    client.create_page("Knowledge Graph Dashboard", dashboard_content)

def add_contextual_links(client, graph):
    """Add contextual cross-references between related pages."""
    
    # Find pages with similar tags or topics
    tag_groups = {}
    for page in graph.pages.values():
        for tag in page.tags:
            if tag not in tag_groups:
                tag_groups[tag] = []
            tag_groups[tag].append(page.title)
    
    # Add cross-references for pages with shared tags
    connections_added = 0
    for tag, pages in tag_groups.items():
        if len(pages) > 1:
            for i, page1 in enumerate(pages):
                for page2 in pages[i+1:]:
                    # Add bidirectional references
                    try:
                        # Add reference from page1 to page2
                        client.add_block_to_page(
                            page1, 
                            f"- Related: [[{page2}]] (shared topic: #{tag})"
                        )
                        connections_added += 1
                    except:
                        pass  # Page might not exist or connection might already exist
    
    print(f"   Added {connections_added} contextual connections")

if __name__ == "__main__":
    process_and_enhance_content()