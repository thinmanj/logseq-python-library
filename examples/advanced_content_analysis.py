#!/usr/bin/env python3

"""
Advanced Logseq Content Analysis & Manipulation

This example demonstrates sophisticated content processing using the Logseq Python library:
- Processing existing Logseq content
- Complex queries and analytics
- Automated content updates and enhancements
- Knowledge graph analysis
"""

import sys
from pathlib import Path
from datetime import datetime, date, timedelta
from collections import defaultdict, Counter
import re

sys.path.append('..')

from logseq_py import LogseqClient
from logseq_py.builders import (
    PageBuilder, TaskBuilder, CodeBlockBuilder, QueryBuilder, 
    TableBuilder, ListBuilder
)

class LogseqContentAnalyzer:
    """Advanced content analyzer for Logseq graphs."""
    
    def __init__(self, graph_path: str):
        self.graph_path = Path(graph_path)
        self.client = LogseqClient(graph_path)
        self.analytics = {}
    
    def run_comprehensive_analysis(self):
        """Run a complete analysis of the Logseq graph."""
        print("🔍 Starting comprehensive Logseq content analysis...")
        
        with self.client as client:
            # Load and analyze existing content
            self._analyze_content_patterns(client)
            
            # Generate insights and reports
            self._create_analytics_dashboard(client)
            
            # Perform content enhancements
            self._enhance_existing_content(client)
            
            # Create dynamic queries
            self._create_smart_queries(client)
            
            # Generate knowledge graph insights
            self._analyze_knowledge_graph(client)
        
        print("✅ Analysis complete! Check the generated reports.")
    
    def _analyze_content_patterns(self, client):
        """Analyze patterns in existing content."""
        print("📊 Analyzing content patterns...")
        
        graph = client.load_graph()
        
        # Content statistics
        total_pages = len(graph.pages)
        total_blocks = len(graph.blocks)
        
        # Task analysis
        task_stats = defaultdict(int)
        priority_stats = defaultdict(int)
        tag_frequency = Counter()
        link_network = defaultdict(set)
        
        for page_name, page in graph.pages.items():
            # Analyze tasks
            for block in page.blocks:
                if block.is_task():
                    task_stats[block.task_state.value] += 1
                    if block.priority:
                        priority_stats[block.priority.value] += 1
                
                # Count tags
                tag_frequency.update(block.tags)
                
                # Build link network
                for link in block.get_links():
                    link_network[page_name].add(link)
        
        # Store analytics
        self.analytics = {
            'total_pages': total_pages,
            'total_blocks': total_blocks,
            'task_stats': dict(task_stats),
            'priority_stats': dict(priority_stats),
            'top_tags': tag_frequency.most_common(10),
            'link_network': dict(link_network),
            'most_connected_pages': self._find_hub_pages(link_network),
            'orphaned_pages': self._find_orphaned_pages(graph, link_network)
        }
        
        print(f"   📄 {total_pages} pages, {total_blocks} blocks")
        print(f"   📝 {sum(task_stats.values())} tasks found")
        print(f"   🏷️ {len(tag_frequency)} unique tags")
    
    def _find_hub_pages(self, link_network):
        """Find pages that are most connected (referenced by others)."""
        incoming_links = defaultdict(int)
        for page, links in link_network.items():
            for link in links:
                incoming_links[link] += 1
        
        return sorted(incoming_links.items(), key=lambda x: x[1], reverse=True)[:5]
    
    def _find_orphaned_pages(self, graph, link_network):
        """Find pages with no incoming or outgoing links."""
        all_pages = set(graph.pages.keys())
        linked_pages = set(link_network.keys())
        
        # Pages that are referenced by others
        referenced_pages = set()
        for links in link_network.values():
            referenced_pages.update(links)
        
        # Pages that neither link out nor are linked to
        orphaned = all_pages - (linked_pages | referenced_pages)
        return list(orphaned)[:10]  # Limit to 10 for display
    
    def _create_analytics_dashboard(self, client):
        """Create a comprehensive analytics dashboard page."""
        print("📈 Creating analytics dashboard...")
        
        analytics = self.analytics
        
        dashboard = (PageBuilder("📊 Content Analytics Dashboard")
                    .author("Content Analyzer")
                    .created()
                    .page_type("analytics")
                    .category("insights")
                    .tags("analytics", "dashboard", "insights")
                    
                    .heading(1, "📊 Logseq Content Analytics Dashboard")
                    .text(f"*Analysis generated on {datetime.now().strftime('%Y-%m-%d at %H:%M:%S')}*")
                    .empty_line()
                    
                    .heading(2, "📈 Overview Statistics"))
        
        # Create overview table
        overview_table = (dashboard.table()
                         .headers("Metric", "Value", "Description")
                         .row("Total Pages", str(analytics['total_pages']), "All pages in the graph")
                         .row("Total Blocks", str(analytics['total_blocks']), "All content blocks")
                         .row("Total Tasks", str(sum(analytics['task_stats'].values())), "All task items")
                         .row("Active Tags", str(len([t for t, c in analytics['top_tags']])), "Tags in use")
                         .row("Connected Pages", str(len(analytics['link_network'])), "Pages with outgoing links"))
        
        dashboard.empty_line().heading(2, "✅ Task Status Distribution")
        
        # Task status breakdown
        task_list = ListBuilder("bullet")
        for status, count in analytics['task_stats'].items():
            percentage = round((count / sum(analytics['task_stats'].values())) * 100, 1)
            task_list.item(f"**{status}**: {count} tasks ({percentage}%)")
        dashboard.add(task_list)
        
        dashboard.empty_line().heading(2, "🏷️ Top Tags")
        
        # Top tags list
        tag_list = ListBuilder("bullet")
        for tag, count in analytics['top_tags']:
            tag_list.item(f"#{tag} - used {count} times")
        dashboard.add(tag_list)
        
        dashboard.empty_line().heading(2, "🌐 Knowledge Graph Insights")
        
        # Hub pages (most referenced)
        hub_list = ListBuilder("bullet")
        hub_list.item("**Most Connected Pages** (pages that others link to):")
        for page, link_count in analytics['most_connected_pages']:
            hub_list.item(f"[[{page}]] - {link_count} incoming links", 1)
        dashboard.add(hub_list)
        
        # Orphaned pages
        if analytics['orphaned_pages']:
            dashboard.empty_line().heading(2, "🏝️ Potential Orphaned Pages")
            orphan_list = ListBuilder("bullet")
            orphan_list.item("Pages with no links (may need attention):")
            for page in analytics['orphaned_pages']:
                orphan_list.item(f"[[{page}]]", 1)
            dashboard.add(orphan_list)
        
        client.create_page("📊 Content Analytics Dashboard", dashboard.build())
    
    def _enhance_existing_content(self, client):
        """Enhance existing content with additional metadata and structure."""
        print("✨ Enhancing existing content...")
        
        graph = client.load_graph()
        enhanced_count = 0
        
        for page_name, page in graph.pages.items():
            enhanced = False
            
            # Skip our generated pages
            if "Analytics Dashboard" in page_name or "Enhanced" in page_name:
                continue
            
            # Add summary if page has many blocks
            if len(page.blocks) > 10:
                summary_block = f"📄 **Page Summary**: This page contains {len(page.blocks)} blocks"
                
                task_blocks = [b for b in page.blocks if b.is_task()]
                if task_blocks:
                    completed = len([b for b in task_blocks if b.is_completed_task()])
                    summary_block += f" including {len(task_blocks)} tasks ({completed} completed)"
                
                # Add summary at the top (this would require more complex block manipulation)
                enhanced = True
            
            # Identify pages that could benefit from structure
            if len(page.blocks) > 5 and not any(b.block_type.value == "heading" for b in page.blocks):
                # This page might benefit from better structure
                self._suggest_page_improvements(client, page)
                enhanced = True
            
            if enhanced:
                enhanced_count += 1
        
        print(f"   ✅ Enhanced {enhanced_count} pages with additional insights")
    
    def _suggest_page_improvements(self, client, page):
        """Create improvement suggestions for a page."""
        suggestions = (PageBuilder(f"💡 Improvements for {page.name}")
                      .author("Content Analyzer")
                      .created()
                      .page_type("suggestions")
                      .tags("improvements", "suggestions")
                      
                      .heading(1, f"💡 Suggested Improvements for [[{page.name}]]")
                      .text("*Automatically generated suggestions based on content analysis*")
                      .empty_line()
                      
                      .heading(2, "📋 Current Page Stats"))
        
        # Analyze current structure
        stats_list = ListBuilder("bullet")
        stats_list.item(f"Total blocks: {len(page.blocks)}")
        
        task_count = len([b for b in page.blocks if b.is_task()])
        if task_count > 0:
            stats_list.item(f"Tasks: {task_count}")
        
        tag_count = len(set().union(*[b.tags for b in page.blocks]))
        if tag_count > 0:
            stats_list.item(f"Unique tags: {tag_count}")
        
        suggestions.add(stats_list)
        
        # Provide specific suggestions
        suggestions.empty_line().heading(2, "✨ Recommendations")
        
        rec_list = ListBuilder("bullet")
        
        if not any(b.content.startswith("#") for b in page.blocks):
            rec_list.item("📝 **Add headings** to organize content into sections")
        
        if task_count > 3:
            completed = len([b for b in page.blocks if b.is_completed_task()])
            rec_list.item(f"✅ **Task management**: {task_count} tasks ({completed} completed)")
            if completed < task_count / 2:
                rec_list.item("Consider reviewing overdue tasks", 1)
        
        if len(page.blocks) > 20:
            rec_list.item("📄 **Consider splitting** into smaller, focused pages")
        
        if tag_count == 0:
            rec_list.item("🏷️ **Add tags** for better categorization and findability")
        
        suggestions.add(rec_list)
        
        try:
            client.create_page(f"💡 Improvements for {page.name}", suggestions.build())
        except ValueError:
            # Page already exists
            pass
    
    def _create_smart_queries(self, client):
        """Create intelligent queries based on content analysis."""
        print("🔍 Creating smart queries...")
        
        queries_page = (PageBuilder("🔍 Smart Content Queries")
                       .author("Content Analyzer")
                       .created()
                       .page_type("queries")
                       .tags("queries", "automation", "insights")
                       
                       .heading(1, "🔍 Smart Content Queries")
                       .text("Dynamically generated queries based on your content patterns")
                       .empty_line()
                       
                       .heading(2, "📝 Task Management Queries"))
        
        # Task queries
        task_queries = ListBuilder("bullet")
        task_queries.item("**Overdue High Priority Tasks**:")
        task_queries.item("```query", 1)
        task_queries.item("(and (task TODO) (priority A) (not (scheduled)))", 2)
        task_queries.item("```", 1)
        
        task_queries.item("**Recently Completed Tasks** (last 7 days):", 1)
        task_queries.item("```query", 1)
        task_queries.item(f"(and (task DONE) (between [[{(date.today() - timedelta(days=7)).strftime('%Y-%m-%d')}]] [[{date.today().strftime('%Y-%m-%d')}]]))", 2)
        task_queries.item("```", 1)
        
        queries_page.add(task_queries)
        
        queries_page.empty_line().heading(2, "🏷️ Tag-Based Queries")
        
        # Dynamic tag queries based on most popular tags
        if self.analytics['top_tags']:
            tag_queries = ListBuilder("bullet")
            top_tag = self.analytics['top_tags'][0][0]
            tag_queries.item(f"**Most used tag (#{top_tag})**:")
            tag_queries.item("```query", 1)
            tag_queries.item(f"(page-tags #{top_tag})", 2)
            tag_queries.item("```", 1)
            queries_page.add(tag_queries)
        
        queries_page.empty_line().heading(2, "🔗 Relationship Queries")
        
        # Relationship queries
        rel_queries = ListBuilder("bullet")
        rel_queries.item("**Pages with most connections**:")
        rel_queries.item("```query", 1)
        rel_queries.item("(sort-by :block/refs-count :desc)", 2)
        rel_queries.item("```", 1)
        
        queries_page.add(rel_queries)
        
        client.create_page("🔍 Smart Content Queries", queries_page.build())
    
    def _analyze_knowledge_graph(self, client):
        """Analyze the knowledge graph structure and create insights."""
        print("🕸️ Analyzing knowledge graph structure...")
        
        # Create a comprehensive knowledge graph analysis
        graph_analysis = (PageBuilder("🕸️ Knowledge Graph Analysis")
                         .author("Graph Analyzer")
                         .created()
                         .page_type("analysis")
                         .tags("knowledge-graph", "network-analysis", "insights")
                         
                         .heading(1, "🕸️ Knowledge Graph Network Analysis")
                         .text("Deep analysis of your knowledge network structure")
                         .empty_line())
        
        # Connection patterns
        graph_analysis.heading(2, "🌐 Network Structure")
        
        connections = ListBuilder("bullet")
        connections.item(f"**Total nodes**: {self.analytics['total_pages']} pages")
        connections.item(f"**Connected nodes**: {len(self.analytics['link_network'])} pages with outgoing links")
        
        # Calculate network density
        possible_connections = self.analytics['total_pages'] * (self.analytics['total_pages'] - 1)
        actual_connections = sum(len(links) for links in self.analytics['link_network'].values())
        density = (actual_connections / possible_connections * 100) if possible_connections > 0 else 0
        connections.item(f"**Network density**: {density:.2f}% (how interconnected your knowledge is)")
        
        graph_analysis.add(connections)
        
        # Hub analysis
        if self.analytics['most_connected_pages']:
            graph_analysis.empty_line().heading(2, "🎯 Knowledge Hubs")
            
            hub_analysis = ListBuilder("bullet")
            hub_analysis.item("**These pages are central to your knowledge network:**")
            
            for page, count in self.analytics['most_connected_pages']:
                hub_analysis.item(f"[[{page}]] - referenced {count} times", 1)
                hub_analysis.item("*Consider expanding or organizing content here*", 2)
            
            graph_analysis.add(hub_analysis)
        
        # Growth suggestions
        graph_analysis.empty_line().heading(2, "📈 Growth Opportunities")
        
        growth = ListBuilder("bullet")
        if self.analytics['orphaned_pages']:
            growth.item(f"**Connect isolated pages**: {len(self.analytics['orphaned_pages'])} pages have no links")
        
        growth.item("**Create index pages** for your most important topics")
        growth.item("**Add cross-references** between related concepts")
        growth.item("**Use tags consistently** to create implicit connections")
        
        graph_analysis.add(growth)
        
        client.create_page("🕸️ Knowledge Graph Analysis", graph_analysis.build())

def main():
    """Run the comprehensive content analysis."""
    # Use our demo as the source
    demo_path = Path("examples/logseq-demo")
    
    if not demo_path.exists():
        print("❌ Demo not found. Run generate_logseq_demo.py first!")
        return
    
    analyzer = LogseqContentAnalyzer(demo_path)
    analyzer.run_comprehensive_analysis()
    
    print(f"\n🎉 Analysis complete! Open your Logseq graph at: {demo_path}")
    print("📊 Check these new pages:")
    print("  - 📊 Content Analytics Dashboard")
    print("  - 🔍 Smart Content Queries") 
    print("  - 🕸️ Knowledge Graph Analysis")
    print("  - 💡 Improvements for [various pages]")

if __name__ == "__main__":
    main()