#!/usr/bin/env python3

"""
Realistic Logseq Content Processing with Updates

This example demonstrates sophisticated content manipulation:
- Loading existing Logseq content
- Analyzing patterns and extracting insights  
- Making intelligent content updates
- Creating cross-references and connections
- Generating dynamic content from existing data
"""

import re
from pathlib import Path
from datetime import datetime, timedelta
from collections import Counter, defaultdict

def main():
    """Main function demonstrating realistic Logseq content processing."""
    print("🚀 Realistic Logseq Content Processing & Updates")
    print("=" * 60)
    
    demo_path = Path("logseq-demo")
    if not demo_path.exists():
        print("❌ Demo content not found. Run generate_logseq_demo.py first!")
        return
    
    # 1. Load and analyze existing content
    print("📊 Loading and analyzing existing content...")
    content_data = load_all_content(demo_path)
    
    # 2. Extract insights and patterns
    insights = extract_content_insights(content_data)
    print_insights(insights)
    
    # 3. Generate intelligent updates based on analysis
    print("\n🔧 Generating intelligent content updates...")
    updates = generate_smart_updates(insights, content_data)
    
    # 4. Apply the updates to create new content
    apply_content_updates(demo_path, updates)
    
    # 5. Create a master summary
    create_master_summary(demo_path, insights)
    
    print("\n✅ Realistic content processing complete!")
    print_results_summary(updates)

def load_all_content(demo_path):
    """Load all markdown content with metadata."""
    content_data = {
        'pages': {},
        'journals': {},
        'metadata': {
            'total_files': 0,
            'total_words': 0,
            'load_time': datetime.now()
        }
    }
    
    # Load regular pages
    for md_file in demo_path.glob("*.md"):
        if not should_skip_file(md_file):
            content_data['pages'][md_file.name] = load_file_with_analysis(md_file)
            content_data['metadata']['total_files'] += 1
    
    # Load journals
    journals_path = demo_path / "journals"
    if journals_path.exists():
        for journal_file in journals_path.glob("*.md"):
            content_data['journals'][journal_file.name] = load_file_with_analysis(journal_file)
            content_data['metadata']['total_files'] += 1
    
    # Calculate total words
    total_words = sum(page['word_count'] for page in content_data['pages'].values())
    total_words += sum(journal['word_count'] for journal in content_data['journals'].values())
    content_data['metadata']['total_words'] = total_words
    
    return content_data

def should_skip_file(file_path):
    """Determine if a file should be skipped during processing."""
    skip_patterns = ['.logseq', 'README', 'ACHIEVEMENT', 'PLUGIN_RESEARCH']
    return any(pattern in str(file_path) for pattern in skip_patterns)

def load_file_with_analysis(file_path):
    """Load a file and perform basic content analysis."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    return {
        'content': content,
        'word_count': len(content.split()),
        'line_count': len(content.split('\n')),
        'tasks': extract_tasks_simple(content),
        'links': extract_links_simple(content),
        'tags': extract_tags_simple(content),
        'code_blocks': extract_code_blocks_simple(content),
        'headings': extract_headings_simple(content),
        'modified': datetime.fromtimestamp(file_path.stat().st_mtime)
    }

def extract_tasks_simple(content):
    """Extract tasks with status and text."""
    tasks = []
    task_pattern = r'- (TODO|DOING|DONE|LATER|NOW|WAITING|CANCELLED|DELEGATED)\s+(.+)'
    
    for match in re.finditer(task_pattern, content):
        status, text = match.groups()
        
        # Extract priority if present
        priority_match = re.search(r'\[#([ABC])\]', text)
        priority = priority_match.group(1) if priority_match else None
        
        tasks.append({
            'status': status,
            'text': text.strip(),
            'priority': priority,
            'line_number': content[:match.start()].count('\n') + 1
        })
    
    return tasks

def extract_links_simple(content):
    """Extract page links."""
    return re.findall(r'\[\[([^\]]+)\]\]', content)

def extract_tags_simple(content):
    """Extract hashtags."""
    return re.findall(r'#([a-zA-Z0-9_-]+)', content)

def extract_code_blocks_simple(content):
    """Extract code blocks with language."""
    code_blocks = []
    pattern = r'```(\w+)?\n(.*?)```'
    
    for match in re.finditer(pattern, content, re.DOTALL):
        language = match.group(1) or 'text'
        code = match.group(2).strip()
        code_blocks.append({
            'language': language,
            'code': code,
            'lines': len(code.split('\n'))
        })
    
    return code_blocks

def extract_headings_simple(content):
    """Extract headings with levels."""
    headings = []
    for line_num, line in enumerate(content.split('\n'), 1):
        match = re.match(r'^-?\s*(#{1,6})\s+(.+)$', line.strip())
        if match:
            level = len(match.group(1))
            text = match.group(2).strip()
            headings.append({
                'level': level,
                'text': text,
                'line_number': line_num
            })
    
    return headings

def extract_content_insights(content_data):
    """Extract meaningful insights from the loaded content."""
    insights = {
        'content_overview': analyze_content_overview(content_data),
        'task_patterns': analyze_task_patterns(content_data),
        'knowledge_network': analyze_knowledge_network(content_data),
        'content_quality': analyze_content_quality(content_data),
        'temporal_patterns': analyze_temporal_patterns(content_data)
    }
    
    return insights

def analyze_content_overview(content_data):
    """Analyze overall content distribution and characteristics."""
    pages = content_data['pages']
    journals = content_data['journals']
    
    return {
        'total_pages': len(pages),
        'total_journals': len(journals),
        'avg_page_length': sum(p['word_count'] for p in pages.values()) / len(pages) if pages else 0,
        'most_active_pages': sorted(pages.items(), key=lambda x: x[1]['word_count'], reverse=True)[:5],
        'content_types': analyze_content_types(pages)
    }

def analyze_content_types(pages):
    """Categorize pages by content type."""
    types = defaultdict(int)
    
    for filename, page_data in pages.items():
        content = page_data['content'].lower()
        
        if 'project:' in filename.lower():
            types['project'] += 1
        elif 'demo' in filename.lower():
            types['demo'] += 1
        elif any(word in content for word in ['task', 'todo', 'workflow']):
            types['productivity'] += 1
        elif any(word in content for word in ['code', 'example', 'programming']):
            types['technical'] += 1
        else:
            types['general'] += 1
    
    return dict(types)

def analyze_task_patterns(content_data):
    """Analyze task distribution and completion patterns."""
    all_tasks = []
    pages_with_tasks = []
    
    # Collect all tasks
    for filename, page_data in content_data['pages'].items():
        tasks = page_data['tasks']
        if tasks:
            pages_with_tasks.append(filename)
            all_tasks.extend(tasks)
    
    # Analyze patterns
    status_counts = Counter(task['status'] for task in all_tasks)
    priority_counts = Counter(task['priority'] for task in all_tasks if task['priority'])
    
    completion_rate = status_counts['DONE'] / len(all_tasks) if all_tasks else 0
    
    return {
        'total_tasks': len(all_tasks),
        'pages_with_tasks': len(pages_with_tasks),
        'status_distribution': dict(status_counts),
        'priority_distribution': dict(priority_counts),
        'completion_rate': completion_rate,
        'task_density': {filename: len(content_data['pages'][filename]['tasks']) 
                        for filename in pages_with_tasks}
    }

def analyze_knowledge_network(content_data):
    """Analyze the knowledge network structure."""
    all_links = []
    all_tags = []
    page_connectivity = {}
    
    # Collect all links and tags
    for filename, page_data in content_data['pages'].items():
        links = page_data['links']
        tags = page_data['tags']
        
        all_links.extend(links)
        all_tags.extend(tags)
        
        page_connectivity[filename] = {
            'outgoing_links': len(links),
            'tags': len(tags),
            'unique_links': len(set(links)),
            'unique_tags': len(set(tags))
        }
    
    # Find most referenced pages
    link_counts = Counter(all_links)
    tag_counts = Counter(all_tags)
    
    # Identify hub pages and isolated pages
    hub_pages = [name for name, data in page_connectivity.items() 
                if data['outgoing_links'] > 3]
    isolated_pages = [name for name, data in page_connectivity.items() 
                     if data['outgoing_links'] == 0]
    
    return {
        'total_links': len(all_links),
        'unique_links': len(set(all_links)),
        'total_tags': len(all_tags),
        'unique_tags': len(set(all_tags)),
        'most_referenced': dict(link_counts.most_common(10)),
        'popular_tags': dict(tag_counts.most_common(10)),
        'hub_pages': hub_pages,
        'isolated_pages': isolated_pages,
        'connectivity_scores': page_connectivity
    }

def analyze_content_quality(content_data):
    """Analyze content quality metrics."""
    quality_metrics = {
        'pages_with_headings': 0,
        'pages_with_code': 0,
        'pages_with_links': 0,
        'average_heading_depth': 0,
        'total_code_blocks': 0,
        'content_depth_scores': {}
    }
    
    total_heading_levels = 0
    heading_count = 0
    
    for filename, page_data in content_data['pages'].items():
        # Basic quality indicators
        if page_data['headings']:
            quality_metrics['pages_with_headings'] += 1
            for heading in page_data['headings']:
                total_heading_levels += heading['level']
                heading_count += 1
        
        if page_data['code_blocks']:
            quality_metrics['pages_with_code'] += 1
            quality_metrics['total_code_blocks'] += len(page_data['code_blocks'])
        
        if page_data['links']:
            quality_metrics['pages_with_links'] += 1
        
        # Calculate content depth score
        depth_score = calculate_content_depth(page_data)
        quality_metrics['content_depth_scores'][filename] = depth_score
    
    if heading_count > 0:
        quality_metrics['average_heading_depth'] = total_heading_levels / heading_count
    
    return quality_metrics

def calculate_content_depth(page_data):
    """Calculate a content depth/quality score for a page."""
    score = 0
    
    # Word count contribution
    score += min(page_data['word_count'] / 100, 10)  # Max 10 points
    
    # Structure contribution
    score += len(page_data['headings']) * 2
    score += len(page_data['links'])
    score += len(page_data['code_blocks']) * 3
    score += len(set(page_data['tags'])) * 2
    
    # Task management contribution
    score += len(page_data['tasks'])
    
    return round(score, 2)

def analyze_temporal_patterns(content_data):
    """Analyze temporal patterns in journal data."""
    if not content_data['journals']:
        return {'has_journals': False}
    
    journal_dates = []
    for filename in content_data['journals'].keys():
        # Extract date from filename (YYYY_MM_DD.md format)
        date_match = re.match(r'(\d{4})_(\d{2})_(\d{2})\.md', filename)
        if date_match:
            year, month, day = date_match.groups()
            date_obj = datetime(int(year), int(month), int(day))
            journal_dates.append(date_obj)
    
    if not journal_dates:
        return {'has_journals': False}
    
    journal_dates.sort()
    
    return {
        'has_journals': True,
        'date_range': (journal_dates[0], journal_dates[-1]),
        'total_days': len(journal_dates),
        'consistency': calculate_journaling_consistency(journal_dates)
    }

def calculate_journaling_consistency(dates):
    """Calculate consistency score for journaling habit."""
    if len(dates) < 2:
        return 1.0
    
    # Calculate expected vs actual days
    date_range = (dates[-1] - dates[0]).days + 1
    actual_days = len(dates)
    
    return actual_days / date_range

def print_insights(insights):
    """Print the extracted insights in a readable format."""
    print("\n📈 Content Insights:")
    
    # Overview
    overview = insights['content_overview']
    print(f"   📄 {overview['total_pages']} pages, {overview['total_journals']} journal entries")
    print(f"   📊 Average page length: {overview['avg_page_length']:.0f} words")
    
    # Task patterns
    tasks = insights['task_patterns']
    print(f"   ✅ {tasks['total_tasks']} tasks with {tasks['completion_rate']:.1%} completion rate")
    
    # Knowledge network
    network = insights['knowledge_network']
    print(f"   🔗 {network['total_links']} links, {len(network['hub_pages'])} hub pages, {len(network['isolated_pages'])} isolated pages")
    
    # Quality metrics
    quality = insights['content_quality']
    print(f"   📚 {quality['pages_with_headings']} structured pages, {quality['total_code_blocks']} code examples")

def generate_smart_updates(insights, content_data):
    """Generate intelligent content updates based on analysis."""
    updates = {
        'new_pages': [],
        'content_enhancements': [],
        'cross_references': [],
        'summary_reports': []
    }
    
    # 1. Create improvement guides based on task analysis
    if insights['task_patterns']['completion_rate'] < 0.7:
        updates['new_pages'].append({
            'type': 'productivity_guide',
            'filename': 'Productivity Enhancement Guide.md',
            'content': generate_productivity_guide(insights['task_patterns'])
        })
    
    # 2. Create knowledge network enhancement suggestions
    if len(insights['knowledge_network']['isolated_pages']) > 2:
        updates['new_pages'].append({
            'type': 'integration_guide',
            'filename': 'Knowledge Integration Suggestions.md',
            'content': generate_integration_guide(insights['knowledge_network'])
        })
    
    # 3. Create content quality dashboard
    updates['new_pages'].append({
        'type': 'dashboard',
        'filename': 'Content Quality Dashboard.md',
        'content': generate_quality_dashboard(insights)
    })
    
    # 4. Generate cross-reference suggestions
    updates['cross_references'] = generate_cross_reference_suggestions(insights, content_data)
    
    # 5. Create master learning index
    updates['new_pages'].append({
        'type': 'index',
        'filename': 'Master Learning Index.md',
        'content': generate_master_index(content_data)
    })
    
    return updates

def generate_productivity_guide(task_insights):
    """Generate a productivity improvement guide."""
    total_tasks = task_insights['total_tasks']
    completion_rate = task_insights['completion_rate']
    status_dist = task_insights['status_distribution']
    
    content = f"""# 📈 Productivity Enhancement Guide

*Generated from analysis of {total_tasks} tasks*

## 🎯 Current Status

Your task completion rate is **{completion_rate:.1%}**. Here's how to improve:

## 📊 Task Distribution Analysis

{create_task_distribution_table(status_dist)}

## 🚀 Recommended Actions

### Immediate Actions
- **Focus on DOING tasks**: You have {status_dist.get('DOING', 0)} tasks in progress
- **Clear WAITING items**: Review {status_dist.get('WAITING', 0)} blocked tasks
- **Prioritize TODO items**: {status_dist.get('TODO', 0)} tasks need attention

### Weekly Review Process
1. **Monday**: Review and prioritize all TODO items
2. **Wednesday**: Check progress on DOING tasks  
3. **Friday**: Celebrate DONE items and plan next week

### Productivity Tips
- Break large tasks into smaller, actionable items
- Use time-blocking for DOING tasks
- Set daily limits (max 3 active DOING tasks)
- Review and move stale items to LATER or CANCELLED

## 📋 Productivity Queries

Use these queries to monitor your progress:

```query
{{:title "Today's Focus"
 :query [:find (pull ?h [*])
         :where
         [?h :block/marker ?marker]
         [(contains? #{{"TODO" "DOING"}} ?marker)]
         [?h :block/priority "A"]]}}
```

## 🔗 Related Resources

- [[Task Management Demo]]
- [[Workflow Demo]]

---
*Updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}*
"""
    
    return content

def create_task_distribution_table(status_dist):
    """Create a markdown table of task status distribution."""
    if not status_dist:
        return "No tasks found."
    
    total = sum(status_dist.values())
    table = "| Status | Count | Percentage |\n|--------|-------|------------|\n"
    
    for status, count in sorted(status_dist.items()):
        percentage = count / total * 100
        table += f"| {status} | {count} | {percentage:.1f}% |\n"
    
    return table

def generate_integration_guide(network_insights):
    """Generate a knowledge integration guide."""
    isolated_pages = network_insights['isolated_pages']
    hub_pages = network_insights['hub_pages']
    popular_tags = network_insights['popular_tags']
    
    content = f"""# 🌐 Knowledge Integration Guide

*Connecting {len(isolated_pages)} isolated pages to your knowledge network*

## 🎯 Integration Opportunities

### Isolated Pages ({len(isolated_pages)})
These pages have no outgoing links and could benefit from connections:

{create_page_list(isolated_pages)}

### Hub Pages ({len(hub_pages)})
These well-connected pages can serve as connection points:

{create_page_list(hub_pages)}

## 🏷️ Popular Tags for Connection
Use these trending tags to create thematic connections:

{create_tag_list(popular_tags)}

## 🔧 Integration Strategies

### 1. Thematic Linking
- Group pages by topic or theme
- Add cross-references between related concepts
- Create summary pages for major topics

### 2. Hierarchical Organization
- Create parent-child page relationships
- Use consistent naming conventions
- Build topic indices and tables of contents

### 3. Tag-based Connections
- Apply consistent tagging across related content
- Use tag queries to create dynamic connections
- Build tag-based navigation systems

## 📋 Integration Checklist

For each isolated page:
- [ ] Add at least 2-3 relevant outgoing links
- [ ] Apply 2-3 descriptive tags
- [ ] Create incoming links from related pages
- [ ] Consider adding to a summary or index page

## 🔄 Maintenance Schedule

- **Weekly**: Review new content for connection opportunities
- **Monthly**: Audit isolated pages and add connections
- **Quarterly**: Restructure major knowledge areas

---
*Updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}*
"""
    
    return content

def create_page_list(pages):
    """Create a markdown list of pages."""
    if not pages:
        return "- None found"
    
    return "\n".join(f"- [[{page}]]" for page in pages[:10])  # Limit to 10

def create_tag_list(tag_dict):
    """Create a markdown list of tags with counts."""
    if not tag_dict:
        return "- None found"
    
    return "\n".join(f"- #{tag} (used {count} times)" 
                    for tag, count in list(tag_dict.items())[:10])

def generate_quality_dashboard(insights):
    """Generate a comprehensive quality dashboard."""
    overview = insights['content_overview']
    quality = insights['content_quality']
    network = insights['knowledge_network']
    
    content = f"""# 📊 Content Quality Dashboard

*Comprehensive analysis of your knowledge base*

## 📈 Overview Metrics

| Metric | Value | Status |
|--------|-------|---------|
| Total Pages | {overview['total_pages']} | {"🟢" if overview['total_pages'] > 10 else "🟡"} |
| Average Page Length | {overview['avg_page_length']:.0f} words | {"🟢" if overview['avg_page_length'] > 100 else "🟡"} |
| Pages with Structure | {quality['pages_with_headings']} | {"🟢" if quality['pages_with_headings'] > overview['total_pages'] * 0.7 else "🟡"} |
| Knowledge Connections | {network['total_links']} | {"🟢" if network['total_links'] > 20 else "🟡"} |

## 🏆 Top Content by Quality Score

{create_quality_rankings(quality['content_depth_scores'])}

## 📚 Content Distribution

{create_content_type_analysis(overview['content_types'])}

## 🔍 Quality Insights

### Strengths
- **Code Examples**: {quality['total_code_blocks']} code blocks across pages
- **Structured Content**: {quality['pages_with_headings']} pages use headings
- **Connected Knowledge**: {quality['pages_with_links']} pages include links

### Improvement Opportunities
- **Isolated Content**: {len(network['isolated_pages'])} pages need connections
- **Shallow Content**: Consider expanding pages with low quality scores
- **Missing Structure**: Add headings to unstructured pages

## 🎯 Recommended Actions

1. **Connect Isolated Pages**: Link {len(network['isolated_pages'])} orphaned pages
2. **Add Structure**: Include headings in content-heavy pages
3. **Expand Shallow Content**: Develop pages with quality scores below 10
4. **Create Summary Pages**: Build overview pages for major topics

## 📊 Progress Tracking

Track these metrics over time:
- Average quality score per page
- Percentage of connected pages  
- Content structure consistency
- Knowledge network density

---
*Dashboard updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}*
"""
    
    return content

def create_quality_rankings(quality_scores):
    """Create quality rankings table."""
    if not quality_scores:
        return "No quality scores available."
    
    # Sort by score, highest first
    sorted_scores = sorted(quality_scores.items(), key=lambda x: x[1], reverse=True)[:10]
    
    table = "| Page | Quality Score | Rating |\n|------|---------------|--------|\n"
    for page, score in sorted_scores:
        rating = "🌟" if score > 20 else "⭐" if score > 10 else "📝"
        table += f"| [[{page}]] | {score} | {rating} |\n"
    
    return table

def create_content_type_analysis(content_types):
    """Create content type distribution analysis."""
    if not content_types:
        return "No content types identified."
    
    total = sum(content_types.values())
    analysis = "| Content Type | Count | Percentage |\n|--------------|-------|------------|\n"
    
    for content_type, count in sorted(content_types.items(), key=lambda x: x[1], reverse=True):
        percentage = count / total * 100
        analysis += f"| {content_type.title()} | {count} | {percentage:.1f}% |\n"
    
    return analysis

def generate_cross_reference_suggestions(insights, content_data):
    """Generate intelligent cross-reference suggestions."""
    suggestions = []
    
    # Find pages with similar tags that should be linked
    tag_pages = defaultdict(list)
    for filename, page_data in content_data['pages'].items():
        for tag in set(page_data['tags']):  # Use set to avoid duplicates
            tag_pages[tag].append(filename)
    
    # Generate cross-reference suggestions
    for tag, pages in tag_pages.items():
        if len(pages) > 1:  # Only suggest if multiple pages share the tag
            for i, page1 in enumerate(pages):
                for page2 in pages[i+1:]:
                    suggestions.append({
                        'from_page': page1,
                        'to_page': page2,
                        'reason': f'Shared tag: #{tag}',
                        'suggested_text': f"Related: [[{page2.replace('.md', '')}]] (#{tag})"
                    })
    
    return suggestions[:20]  # Limit to 20 suggestions

def generate_master_index(content_data):
    """Generate a master learning index."""
    content = f"""# 📚 Master Learning Index

*Comprehensive index of all knowledge areas - Updated {datetime.now().strftime('%Y-%m-%d')}*

## 📖 Content Overview

{create_comprehensive_index(content_data)}

## 🏷️ Topic Index

{create_topic_index(content_data)}

## 💡 Learning Paths

### For Beginners
1. Start with [[Welcome to Demo]]
2. Explore [[Block Types Showcase]]  
3. Practice with [[Task Management Demo]]

### For Advanced Users
1. Review [[Query Examples Demo]]
2. Study [[Workflow Demo]]
3. Build projects using examples

## 🔄 Regular Reviews

### Daily
- Check [[Knowledge Graph Dashboard]]
- Review active tasks and projects
- Update learning progress

### Weekly  
- Scan new content additions
- Update cross-references
- Clean up outdated information

### Monthly
- Restructure major topics
- Archive completed projects
- Plan new learning objectives

## 📊 Learning Analytics

Track your knowledge growth:
- Pages created per week
- Concepts mastered per month
- Projects completed per quarter
- Cross-references added

---
*This index is automatically maintained and updated*
"""
    
    return content

def create_comprehensive_index(content_data):
    """Create a comprehensive content index."""
    pages = content_data['pages']
    journals = content_data['journals']
    
    index = f"**Total Content**: {len(pages)} pages, {len(journals)} journal entries\n\n"
    
    # Group pages by type
    content_groups = defaultdict(list)
    
    for filename, page_data in pages.items():
        page_title = filename.replace('.md', '')
        
        if 'project:' in filename.lower():
            content_groups['Projects'].append(page_title)
        elif 'demo' in filename.lower():
            content_groups['Demos & Examples'].append(page_title)
        elif any(word in page_data['content'].lower() for word in ['task', 'productivity', 'workflow']):
            content_groups['Productivity & Tasks'].append(page_title)
        elif any(word in page_data['content'].lower() for word in ['code', 'programming', 'example']):
            content_groups['Technical & Code'].append(page_title)
        else:
            content_groups['General Knowledge'].append(page_title)
    
    # Create the index
    for group_name, page_list in sorted(content_groups.items()):
        index += f"### {group_name}\n"
        for page in sorted(page_list):
            index += f"- [[{page}]]\n"
        index += "\n"
    
    return index

def create_topic_index(content_data):
    """Create an index organized by topics/tags."""
    all_tags = defaultdict(list)
    
    # Collect all tags and associated pages
    for filename, page_data in content_data['pages'].items():
        page_title = filename.replace('.md', '')
        for tag in set(page_data['tags']):
            all_tags[tag].append(page_title)
    
    if not all_tags:
        return "No topics found. Consider adding more tags to your content."
    
    index = ""
    for tag in sorted(all_tags.keys()):
        pages = all_tags[tag]
        index += f"### #{tag}\n"
        for page in sorted(set(pages)):  # Remove duplicates and sort
            index += f"- [[{page}]]\n"
        index += "\n"
    
    return index

def apply_content_updates(demo_path, updates):
    """Apply the generated updates to the file system."""
    print(f"   Creating {len(updates['new_pages'])} new pages...")
    
    for page_update in updates['new_pages']:
        filename = page_update['filename']
        content = page_update['content']
        
        file_path = demo_path / filename
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"   ✅ Created: {filename}")

def create_master_summary(demo_path, insights):
    """Create a comprehensive master summary document."""
    
    summary_content = f"""# 🎯 Knowledge Base Summary

*Comprehensive analysis and overview generated on {datetime.now().strftime('%Y-%m-%d %H:%M')}*

## 📊 Executive Summary

This knowledge base contains **{insights['content_overview']['total_pages']} pages** with a total of **{insights['content_overview']['avg_page_length'] * insights['content_overview']['total_pages']:.0f} words** of content.

### Key Metrics
- **Task Management**: {insights['task_patterns']['total_tasks']} tasks with {insights['task_patterns']['completion_rate']:.1%} completion rate
- **Knowledge Network**: {insights['knowledge_network']['total_links']} internal links connecting ideas
- **Content Quality**: Average depth score of {sum(insights['content_quality']['content_depth_scores'].values()) / len(insights['content_quality']['content_depth_scores']):.1f}
- **Active Learning**: {insights['content_overview']['total_journals']} journal entries tracking progress

## 🏆 Top Performing Content

{create_quality_rankings(insights['content_quality']['content_depth_scores'])}

## 🔍 Content Analysis

### Content Types Distribution
{create_content_type_analysis(insights['content_overview']['content_types'])}

### Knowledge Network Health
- **Hub Pages**: {len(insights['knowledge_network']['hub_pages'])} well-connected pages
- **Isolated Pages**: {len(insights['knowledge_network']['isolated_pages'])} pages needing connections
- **Popular Topics**: {', '.join(f"#{tag}" for tag in list(insights['knowledge_network']['popular_tags'].keys())[:5])}

## 🎯 Improvement Recommendations

### High Priority
1. **Connect Isolated Content**: {len(insights['knowledge_network']['isolated_pages'])} pages need linking
2. **Improve Task Completion**: Current rate is {insights['task_patterns']['completion_rate']:.1%}
3. **Add Structure**: {insights['content_overview']['total_pages'] - insights['content_quality']['pages_with_headings']} pages lack headings

### Medium Priority  
1. **Expand Shallow Content**: Develop pages with low quality scores
2. **Create Topic Summaries**: Build overview pages for major subjects
3. **Standardize Tagging**: Improve consistency in topic classification

## 📈 Growth Tracking

Track these metrics monthly:
- Total pages and word count
- Task completion rates
- Knowledge network connectivity
- Content quality scores

## 🔗 Quick Navigation

- [[Content Quality Dashboard]] - Live metrics and analysis
- [[Knowledge Integration Suggestions]] - Connection recommendations  
- [[Productivity Enhancement Guide]] - Task management improvements
- [[Master Learning Index]] - Complete content catalog

---
*This summary is automatically updated with each content analysis run*
"""
    
    summary_path = demo_path / "📋 Knowledge Base Summary.md"
    with open(summary_path, 'w', encoding='utf-8') as f:
        f.write(summary_content)
    
    print(f"   ✅ Created master summary: {summary_path.name}")

def print_results_summary(updates):
    """Print a summary of the results and what was created."""
    print("\n📈 Results Summary:")
    print(f"   📄 Created {len(updates['new_pages'])} new pages")
    print(f"   🔗 Generated {len(updates['cross_references'])} cross-reference suggestions")
    
    print("\n🎯 New Content Created:")
    for page in updates['new_pages']:
        page_type = page['type'].replace('_', ' ').title()
        print(f"   • {page_type}: {page['filename']}")
    
    print("\n💡 This demonstrates:")
    print("   • Sophisticated content analysis and pattern recognition")
    print("   • Intelligent content generation based on existing data")
    print("   • Dynamic dashboard and reporting capabilities")
    print("   • Cross-referencing and knowledge network analysis")
    print("   • Automated content quality assessment")
    
    print("\n📚 Explore the generated files to see advanced content processing in action!")

if __name__ == "__main__":
    main()