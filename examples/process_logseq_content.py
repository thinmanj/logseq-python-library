#!/usr/bin/env python3

"""
Logseq Content Processing Example

This example demonstrates realistic content processing using our demo:
- Reading and analyzing existing Logseq content
- Extracting insights and patterns
- Creating dynamic content updates
- Generating smart summaries and reports
"""

import re
from pathlib import Path
from datetime import datetime, date
from collections import Counter, defaultdict

def analyze_logseq_content():
    """Analyze the existing demo content and create interesting reports."""
    print("🔍 Analyzing Logseq demo content...")
    
    demo_path = Path("logseq-demo")
    if not demo_path.exists():
        print("❌ Demo not found. Run generate_logseq_demo.py first!")
        return
    
    # Read all markdown files
    content_analysis = {
        'pages': [],
        'total_blocks': 0,
        'tasks': [],
        'links': [],
        'tags': [],
        'code_blocks': [],
        'queries': []
    }
    
    print("📄 Processing markdown files...")
    
    for md_file in demo_path.glob("**/*.md"):
        if '.logseq' in str(md_file) or 'journals' in md_file.parent.name or '/logseq/' in str(md_file):
            continue  # Skip system files and process journals separately
            
        print(f"   Reading: {md_file.name}")
        
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        page_info = analyze_page_content(md_file.name, content)
        content_analysis['pages'].append(page_info)
        
        # Aggregate data
        content_analysis['total_blocks'] += page_info['block_count']
        content_analysis['tasks'].extend(page_info['tasks'])
        content_analysis['links'].extend(page_info['links'])
        content_analysis['tags'].extend(page_info['tags'])
        content_analysis['code_blocks'].extend(page_info['code_blocks'])
        content_analysis['queries'].extend(page_info['queries'])
    
    # Process journals
    journals_path = demo_path / "journals"
    if journals_path.exists():
        print("📅 Processing journal entries...")
        journal_analysis = analyze_journals(journals_path)
        content_analysis['journals'] = journal_analysis
    
    # Generate reports
    create_content_reports(demo_path, content_analysis)
    
    print("✅ Content analysis complete!")

def analyze_page_content(filename, content):
    """Analyze a single page's content."""
    lines = content.split('\n')
    
    analysis = {
        'filename': filename,
        'title': extract_title(content),
        'block_count': len([l for l in lines if l.strip().startswith('-')]),
        'tasks': extract_tasks(content),
        'links': extract_links(content),
        'tags': extract_tags(content),
        'headings': extract_headings(content),
        'code_blocks': extract_code_blocks(content),
        'queries': extract_queries(content),
        'properties': extract_properties(content),
        'word_count': len(content.split())
    }
    
    return analysis

def extract_title(content):
    """Extract page title from content."""
    lines = content.split('\n')
    for line in lines:
        if line.strip().startswith('# '):
            return line.strip()[2:]
        elif line.strip().startswith('- # '):
            return line.strip()[4:]
    return "Untitled"

def extract_tasks(content):
    """Extract all tasks from content."""
    tasks = []
    task_pattern = r'- (TODO|DOING|DONE|LATER|NOW|WAITING|CANCELLED|DELEGATED)\s+([^\n]+)'
    
    matches = re.findall(task_pattern, content)
    for status, task_text in matches:
        # Extract priority
        priority = None
        priority_match = re.search(r'\[#([ABC])\]', task_text)
        if priority_match:
            priority = priority_match.group(1)
            task_text = re.sub(r'\[#[ABC]\]\s*', '', task_text)
        
        tasks.append({
            'status': status,
            'text': task_text.strip(),
            'priority': priority
        })
    
    return tasks

def extract_links(content):
    """Extract all page links."""
    link_pattern = r'\[\[([^\]]+)\]\]'
    return re.findall(link_pattern, content)

def extract_tags(content):
    """Extract all hashtags."""
    tag_pattern = r'#([a-zA-Z0-9_-]+)'
    return re.findall(tag_pattern, content)

def extract_headings(content):
    """Extract all headings with their levels."""
    headings = []
    heading_pattern = r'^- (#{1,6})\s+(.+)$'
    
    for line in content.split('\n'):
        match = re.match(heading_pattern, line.strip())
        if match:
            level = len(match.group(1))
            text = match.group(2).strip()
            headings.append({'level': level, 'text': text})
    
    return headings

def extract_code_blocks(content):
    """Extract all code blocks."""
    code_blocks = []
    in_code_block = False
    current_block = {'language': None, 'lines': []}
    
    for line in content.split('\n'):
        line = line.strip()
        if line.startswith('```'):
            if not in_code_block:
                # Starting code block
                in_code_block = True
                language = line[3:].strip() if len(line) > 3 else 'text'
                current_block = {'language': language, 'lines': []}
            else:
                # Ending code block
                in_code_block = False
                if current_block['lines']:
                    code_blocks.append(current_block)
        elif in_code_block:
            current_block['lines'].append(line)
    
    return code_blocks

def extract_queries(content):
    """Extract Logseq queries."""
    queries = []
    in_query = False
    current_query = []
    
    for line in content.split('\n'):
        line = line.strip()
        if line == '```query':
            in_query = True
            current_query = []
        elif line == '```' and in_query:
            in_query = False
            if current_query:
                queries.append(' '.join(current_query))
        elif in_query:
            current_query.append(line)
    
    return queries

def extract_properties(content):
    """Extract page properties."""
    properties = {}
    lines = content.split('\n')
    
    for line in lines[:10]:  # Properties are usually at the top
        line = line.strip()
        if '::' in line and not line.startswith('-'):
            key, value = line.split('::', 1)
            properties[key.strip()] = value.strip()
    
    return properties

def analyze_journals(journals_path):
    """Analyze journal entries."""
    journals = []
    
    for journal_file in sorted(journals_path.glob("*.md")):
        print(f"   Reading journal: {journal_file.name}")
        
        with open(journal_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract date from filename (YYYY_MM_DD.md format)
        date_match = re.match(r'(\d{4})_(\d{2})_(\d{2})\.md', journal_file.name)
        if date_match:
            year, month, day = date_match.groups()
            journal_date = f"{year}-{month}-{day}"
        else:
            journal_date = "unknown"
        
        journal_info = {
            'date': journal_date,
            'filename': journal_file.name,
            'habits': extract_habits(content),
            'gratitude': extract_gratitude(content),
            'mood': extract_mood(content),
            'work_entries': extract_work_log(content),
            'learning': extract_learning(content)
        }
        
        journals.append(journal_info)
    
    return journals

def extract_habits(content):
    """Extract habit tracking from journal."""
    habits = {}
    lines = content.split('\n')
    
    in_habits = False
    for line in lines:
        line = line.strip()
        if '### Habits' in line:
            in_habits = True
            continue
        elif line.startswith('###') and in_habits:
            break
        elif in_habits and line.startswith('-'):
            # Parse habit entries like "- ✅ exercise"
            if '✅' in line:
                habit = line.replace('-', '').replace('✅', '').strip()
                habits[habit] = True
            elif '❌' in line:
                habit = line.replace('-', '').replace('❌', '').strip()
                habits[habit] = False
    
    return habits

def extract_gratitude(content):
    """Extract gratitude entries."""
    gratitude = []
    lines = content.split('\n')
    
    in_gratitude = False
    for line in lines:
        line = line.strip()
        if '### Gratitude' in line:
            in_gratitude = True
            continue
        elif line.startswith('###') and in_gratitude:
            break
        elif in_gratitude and line.startswith('- Grateful for:'):
            entry = line.replace('- Grateful for:', '').strip()
            gratitude.append(entry)
    
    return gratitude

def extract_mood(content):
    """Extract mood information."""
    mood_pattern = r'Mood: ([^(]+)\s*\((\d+)/10\)'
    match = re.search(mood_pattern, content)
    if match:
        return {'mood': match.group(1).strip(), 'rating': int(match.group(2))}
    return None

def extract_work_log(content):
    """Extract work log entries."""
    work_entries = []
    lines = content.split('\n')
    
    in_work = False
    for line in lines:
        line = line.strip()
        if '### Work Log' in line:
            in_work = True
            continue
        elif line.startswith('###') and in_work:
            break
        elif in_work and line.startswith('-'):
            entry = line[1:].strip()
            work_entries.append(entry)
    
    return work_entries

def extract_learning(content):
    """Extract learning entries."""
    learning_pattern = r'### Learning: ([^\n]+)\n([^\n]+)'
    matches = re.findall(learning_pattern, content)
    
    learning_entries = []
    for topic, description in matches:
        learning_entries.append({
            'topic': topic.strip(),
            'description': description.strip()
        })
    
    return learning_entries

def create_content_reports(demo_path, analysis):
    """Create comprehensive content reports."""
    print("📊 Creating content analysis reports...")
    
    # Create main analysis report
    create_analysis_dashboard(demo_path, analysis)
    
    # Create task analysis report
    create_task_analysis(demo_path, analysis)
    
    # Create knowledge network report
    create_knowledge_network(demo_path, analysis)
    
    # Create journal insights
    if 'journals' in analysis:
        create_journal_insights(demo_path, analysis['journals'])

def create_analysis_dashboard(demo_path, analysis):
    """Create main analysis dashboard."""
    report_content = f"""📊 Content Analysis Dashboard
author:: Content Analyzer
created:: {datetime.now().strftime('%Y-%m-%d')}
page-type:: analysis
tags:: analysis, dashboard, insights

# 📊 Logseq Content Analysis Dashboard

*Analysis generated on {datetime.now().strftime('%Y-%m-%d at %H:%M:%S')}*

## 📈 Overview Statistics

| Metric | Value | Details |
|--------|-------|---------|
| Total Pages | {len(analysis['pages'])} | Excluding journals and system files |
| Total Blocks | {analysis['total_blocks']} | All bullet points and content blocks |
| Total Tasks | {len(analysis['tasks'])} | All TODO/DOING/DONE items |
| Unique Links | {len(set(analysis['links']))} | Internal page references |
| Unique Tags | {len(set(analysis['tags']))} | Hashtag references |
| Code Blocks | {len(analysis['code_blocks'])} | Programming examples |
| Smart Queries | {len(analysis['queries'])} | Dynamic content queries |

## ✅ Task Analysis

### Task Status Distribution
"""
    
    # Analyze task status
    task_status = Counter(task['status'] for task in analysis['tasks'])
    for status, count in task_status.most_common():
        percentage = round((count / len(analysis['tasks'])) * 100, 1) if analysis['tasks'] else 0
        report_content += f"- **{status}**: {count} tasks ({percentage}%)\\n"
    
    # Priority analysis
    priority_counts = Counter(task['priority'] for task in analysis['tasks'] if task['priority'])
    if priority_counts:
        report_content += "\\n### Priority Distribution\\n"
        for priority, count in sorted(priority_counts.items()):
            report_content += f"- **Priority {priority}**: {count} tasks\\n"
    
    # Popular tags
    tag_counts = Counter(analysis['tags'])
    if tag_counts:
        report_content += "\\n## 🏷️ Most Used Tags\\n"
        for tag, count in tag_counts.most_common(10):
            report_content += f"- #{tag} - used {count} times\\n"
    
    # Code languages
    languages = [block['language'] for block in analysis['code_blocks'] if block['language']]
    if languages:
        lang_counts = Counter(languages)
        report_content += "\\n## 💻 Programming Languages\\n"
        for lang, count in lang_counts.most_common():
            report_content += f"- **{lang}**: {count} code blocks\\n"
    
    # Page analysis
    report_content += "\\n## 📄 Page Analysis\\n"
    for page in sorted(analysis['pages'], key=lambda p: p['word_count'], reverse=True)[:5]:
        report_content += f"- **[[{page['title']}]]**: {page['word_count']} words, {page['block_count']} blocks\\n"
        if page['tasks']:
            report_content += f"  - {len(page['tasks'])} tasks\\n"
    
    # Write report
    report_path = demo_path / "📊 Content Analysis Report.md"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    print(f"   ✅ Created: {report_path.name}")

def create_task_analysis(demo_path, analysis):
    """Create detailed task analysis."""
    if not analysis['tasks']:
        return
    
    report_content = f"""📝 Task Analysis Report
author:: Task Analyzer
created:: {datetime.now().strftime('%Y-%m-%d')}
page-type:: task-analysis
tags:: tasks, productivity, analysis

# 📝 Comprehensive Task Analysis

*Analysis of {len(analysis['tasks'])} tasks across your Logseq graph*

## 🎯 Task Overview

### Status Breakdown
"""
    
    status_counts = Counter(task['status'] for task in analysis['tasks'])
    total_tasks = len(analysis['tasks'])
    
    for status in ['TODO', 'DOING', 'DONE', 'LATER', 'NOW', 'WAITING', 'CANCELLED', 'DELEGATED']:
        count = status_counts.get(status, 0)
        percentage = round((count / total_tasks) * 100, 1) if total_tasks > 0 else 0
        
        status_emoji = {
            'TODO': '⏳', 'DOING': '🔄', 'DONE': '✅', 'LATER': '📅',
            'NOW': '🚨', 'WAITING': '⏸️', 'CANCELLED': '❌', 'DELEGATED': '👥'
        }
        
        emoji = status_emoji.get(status, '📋')
        report_content += f"- {emoji} **{status}**: {count} tasks ({percentage}%)\\n"
    
    # Priority analysis
    priority_tasks = [t for t in analysis['tasks'] if t['priority']]
    if priority_tasks:
        report_content += "\\n### Priority Analysis\\n"
        priority_counts = Counter(task['priority'] for task in priority_tasks)
        
        for priority in ['A', 'B', 'C']:
            count = priority_counts.get(priority, 0)
            percentage = round((count / len(priority_tasks)) * 100, 1) if priority_tasks else 0
            report_content += f"- **Priority {priority}** (High/Medium/Low): {count} tasks ({percentage}%)\\n"
    
    # Productivity insights
    report_content += "\\n## 📈 Productivity Insights\\n"
    
    completed_tasks = [t for t in analysis['tasks'] if t['status'] == 'DONE']
    active_tasks = [t for t in analysis['tasks'] if t['status'] in ['TODO', 'DOING', 'NOW']]
    
    if total_tasks > 0:
        completion_rate = round((len(completed_tasks) / total_tasks) * 100, 1)
        report_content += f"- **Completion Rate**: {completion_rate}% ({len(completed_tasks)}/{total_tasks})\\n"
    
    if active_tasks:
        report_content += f"- **Active Tasks**: {len(active_tasks)} tasks need attention\\n"
    
    # High priority active tasks
    high_priority_active = [t for t in active_tasks if t['priority'] == 'A']
    if high_priority_active:
        report_content += f"- **High Priority Active**: {len(high_priority_active)} urgent tasks\\n"
        report_content += "\\n### 🚨 High Priority Tasks Needing Attention\\n"
        for task in high_priority_active[:5]:
            report_content += f"- [{task['status']}] {task['text']}\\n"
    
    # Task examples by status
    report_content += "\\n## 📋 Task Examples\\n"
    
    for status in ['DOING', 'TODO', 'DONE']:
        status_tasks = [t for t in analysis['tasks'] if t['status'] == status]
        if status_tasks:
            report_content += f"\\n### {status} Tasks\\n"
            for task in status_tasks[:3]:
                priority_str = f" [#{task['priority']}]" if task['priority'] else ""
                report_content += f"- {task['status']}{priority_str} {task['text']}\\n"
    
    # Write report
    report_path = demo_path / "📝 Task Analysis Report.md"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    print(f"   ✅ Created: {report_path.name}")

def create_knowledge_network(demo_path, analysis):
    """Create knowledge network analysis."""
    links = analysis['links']
    if not links:
        return
    
    # Analyze link network
    link_counts = Counter(links)
    pages_with_links = set(links)
    
    report_content = f"""🕸️ Knowledge Network Analysis
author:: Network Analyzer
created:: {datetime.now().strftime('%Y-%m-%d')}
page-type:: network-analysis
tags:: network, connections, knowledge-graph

# 🕸️ Knowledge Network Analysis

*Analysis of {len(links)} links creating your knowledge network*

## 🌐 Network Overview

- **Total Links**: {len(links)}
- **Unique Pages Referenced**: {len(pages_with_links)}
- **Average Links per Reference**: {round(len(links) / len(pages_with_links), 1) if pages_with_links else 0}

## 🎯 Most Referenced Pages

The following pages are most frequently linked to (knowledge hubs):

"""
    
    for page, count in link_counts.most_common(10):
        report_content += f"- **[[{page}]]** - referenced {count} times\\n"
        if count > 3:
            report_content += f"  - *High-value content hub - consider expanding*\\n"
    
    # Page analysis
    report_content += "\\n## 📄 Page Connectivity Analysis\\n"
    
    for page_info in analysis['pages']:
        outgoing_links = len(page_info['links'])
        if outgoing_links > 0:
            report_content += f"- **{page_info['title']}**: {outgoing_links} outgoing links\\n"
    
    # Tag network
    if analysis['tags']:
        tag_counts = Counter(analysis['tags'])
        report_content += "\\n## 🏷️ Tag Network\\n"
        
        report_content += "### Most Used Tags\\n"
        for tag, count in tag_counts.most_common(10):
            report_content += f"- #{tag} - used {count} times\\n"
    
    # Network insights
    report_content += "\\n## 🔍 Network Insights\\n"
    
    # Find potential connection opportunities
    isolated_pages = [p for p in analysis['pages'] if not p['links']]
    if isolated_pages:
        report_content += f"- **Isolated Pages**: {len(isolated_pages)} pages have no outgoing links\\n"
        report_content += "  - Consider adding connections to build knowledge network\\n"
    
    high_connectivity = [p for p in analysis['pages'] if len(p['links']) > 5]
    if high_connectivity:
        report_content += f"- **Highly Connected**: {len(high_connectivity)} pages have 5+ outgoing links\\n"
        report_content += "  - These are your knowledge connectors\\n"
    
    # Write report
    report_path = demo_path / "🕸️ Knowledge Network Analysis.md"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    print(f"   ✅ Created: {report_path.name}")

def create_journal_insights(demo_path, journals):
    """Create journal insights report."""
    if not journals:
        return
    
    report_content = f"""📔 Journal Insights
author:: Journal Analyzer  
created:: {datetime.now().strftime('%Y-%m-%d')}
page-type:: journal-analysis
tags:: journals, habits, reflection, insights

# 📔 Journal Analysis & Insights

*Analysis of {len(journals)} journal entries*

## 📅 Journal Overview

- **Total Entries**: {len(journals)}
- **Date Range**: {journals[0]['date']} to {journals[-1]['date']}
- **Consistency**: {len(journals)} consecutive days tracked

## 🎯 Habit Tracking Analysis

"""
    
    # Analyze habits across all journal entries
    all_habits = {}
    mood_data = []
    
    for journal in journals:
        if journal['habits']:
            for habit, completed in journal['habits'].items():
                if habit not in all_habits:
                    all_habits[habit] = {'completed': 0, 'total': 0}
                all_habits[habit]['total'] += 1
                if completed:
                    all_habits[habit]['completed'] += 1
        
        if journal['mood']:
            mood_data.append(journal['mood']['rating'])
    
    # Habit success rates
    if all_habits:
        report_content += "### Habit Success Rates\\n"
        for habit, data in sorted(all_habits.items(), key=lambda x: x[1]['completed']/x[1]['total'], reverse=True):
            success_rate = round((data['completed'] / data['total']) * 100, 1)
            emoji = "✅" if success_rate >= 80 else "⚠️" if success_rate >= 50 else "❌"
            report_content += f"- {emoji} **{habit}**: {success_rate}% ({data['completed']}/{data['total']})\\n"
    
    # Mood analysis
    if mood_data:
        avg_mood = round(sum(mood_data) / len(mood_data), 1)
        max_mood = max(mood_data)
        min_mood = min(mood_data)
        
        report_content += f"\\n## 😊 Mood Analysis\\n"
        report_content += f"- **Average Mood**: {avg_mood}/10\\n"
        report_content += f"- **Best Day**: {max_mood}/10\\n"
        report_content += f"- **Challenging Day**: {min_mood}/10\\n"
        
        # Mood trend
        if len(mood_data) >= 3:
            recent_avg = round(sum(mood_data[-3:]) / 3, 1)
            early_avg = round(sum(mood_data[:3]) / 3, 1)
            
            if recent_avg > early_avg:
                report_content += f"- **Trend**: Improving mood (recent: {recent_avg}, early: {early_avg})\\n"
            elif recent_avg < early_avg:
                report_content += f"- **Trend**: Declining mood (recent: {recent_avg}, early: {early_avg})\\n"
            else:
                report_content += f"- **Trend**: Stable mood\\n"
    
    # Learning insights
    all_learning = []
    for journal in journals:
        all_learning.extend(journal.get('learning', []))
    
    if all_learning:
        report_content += f"\\n## 📚 Learning Highlights\\n"
        for learning in all_learning[-5:]:  # Show last 5 learnings
            report_content += f"- **{learning['topic']}**: {learning['description']}\\n"
    
    # Gratitude themes
    all_gratitude = []
    for journal in journals:
        all_gratitude.extend(journal.get('gratitude', []))
    
    if all_gratitude:
        report_content += f"\\n## 🙏 Gratitude Themes\\n"
        report_content += f"- **Total Gratitude Entries**: {len(all_gratitude)}\\n"
        report_content += "- **Recent Gratitude**:\\n"
        for gratitude in all_gratitude[-5:]:
            report_content += f"  - {gratitude}\\n"
    
    # Work patterns
    all_work = []
    for journal in journals:
        all_work.extend(journal.get('work_entries', []))
    
    if all_work:
        report_content += f"\\n## 💼 Work Patterns\\n"
        report_content += f"- **Total Work Entries**: {len(all_work)}\\n"
        report_content += f"- **Average per Day**: {round(len(all_work) / len(journals), 1)}\\n"
    
    # Insights and recommendations
    report_content += "\\n## 🔍 Insights & Recommendations\\n"
    
    if all_habits:
        best_habit = max(all_habits.items(), key=lambda x: x[1]['completed']/x[1]['total'])
        worst_habit = min(all_habits.items(), key=lambda x: x[1]['completed']/x[1]['total'])
        
        report_content += f"- **Strongest Habit**: {best_habit[0]} - keep it up!\\n"
        report_content += f"- **Growth Opportunity**: {worst_habit[0]} - needs attention\\n"
    
    if mood_data and avg_mood < 7:
        report_content += "- **Mood Focus**: Consider activities that boost well-being\\n"
    
    report_content += "- **Journaling Consistency**: Great job maintaining daily entries!\\n"
    
    # Write report
    report_path = demo_path / "📔 Journal Insights.md"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    print(f"   ✅ Created: {report_path.name}")

if __name__ == "__main__":
    analyze_logseq_content()
    
    print("\\n🎉 Content analysis complete!")
    print("📊 Generated reports:")
    print("  - 📊 Content Analysis Report")
    print("  - 📝 Task Analysis Report") 
    print("  - 🕸️ Knowledge Network Analysis")
    print("  - 📔 Journal Insights")
    print("\\n💡 These reports demonstrate sophisticated content processing:")
    print("  - Pattern recognition in existing content")
    print("  - Statistical analysis and insights")
    print("  - Dynamic content generation")
    print("  - Multi-file content aggregation")