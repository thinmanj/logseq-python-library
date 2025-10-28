# ETL Automation Examples

Practical examples for automating Logseq data extraction, transformation, and loading.

## Table of Contents

1. [Daily Automation](#daily-automation)
2. [Weekly Reports](#weekly-reports)
3. [Meeting Workflows](#meeting-workflows)
4. [Research Digest](#research-digest)
5. [Personal CRM](#personal-crm)
6. [Task Management](#task-management)
7. [Learning Tracker](#learning-tracker)
8. [Backup & Export](#backup--export)

---

## 1. Daily Automation

### Morning Brief Script

Create a script that generates your daily brief every morning:

```python path=null start=null
#!/usr/bin/env python3
"""
daily_brief.py - Generate morning brief with today's tasks and schedule
"""

from datetime import date, timedelta
from pathlib import Path
from logseq_py.logseq_client import LogseqClient

GRAPH = Path.home() / "Documents/Logseq/Personal"

def generate_daily_brief():
    with LogseqClient(GRAPH) as client:
        graph = client.load_graph()
        
        today = date.today()
        page_name = f"Daily Brief {today}"
        
        # Get today's tasks
        tasks = graph.get_task_blocks()
        today_tasks = [t for t in tasks if not t.is_completed_task()]
        
        # Get scheduled items for today
        scheduled = graph.get_scheduled_blocks(today)
        
        # Get yesterday's journal for context
        yesterday_journals = [p for p in graph.get_journal_pages() 
                             if p.journal_date and p.journal_date.date() == today - timedelta(days=1)]
        
        # Build brief
        brief = f"""# Daily Brief: {today.strftime('%A, %B %d, %Y')}

## Priority Tasks ({len(today_tasks)})
"""
        
        for task in today_tasks[:10]:  # Top 10
            state = task.task_state.value if task.task_state else "TODO"
            priority = f"[{task.priority.value}]" if task.priority else ""
            brief += f"- {state} {priority} {task.content}\n"
        
        brief += f"\n## Scheduled Today ({len(scheduled)})\n"
        for item in scheduled:
            time = item.scheduled.time if item.scheduled and item.scheduled.time else ""
            brief += f"- {time} {item.content}\n"
        
        brief += "\n## Yesterday's Highlights\n"
        if yesterday_journals:
            for block in yesterday_journals[0].blocks[:5]:
                brief += f"- {block.content}\n"
        
        # Create the brief page
        client.create_page(page_name, brief)
        print(f"✓ Created {page_name}")

if __name__ == "__main__":
    generate_daily_brief()
```

**Schedule with cron** (runs at 6 AM daily):

```bash
# Edit crontab
crontab -e

# Add line:
0 6 * * * cd /path/to/logseq-python && python3 daily_brief.py
```

---

## 2. Weekly Reports

### Automated Weekly Review

```python path=null start=null
#!/usr/bin/env python3
"""
weekly_review.py - Generate comprehensive weekly review
"""

from datetime import date, timedelta
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from logseq_py.logseq_client import LogseqClient

GRAPH = Path.home() / "Documents/Logseq/Personal"
OUTPUT_DIR = Path.home() / "Dropbox/Reports"

def weekly_review():
    today = date.today()
    # Get last Sunday to Saturday
    days_since_sunday = (today.weekday() + 1) % 7
    end_date = today - timedelta(days=days_since_sunday)
    start_date = end_date - timedelta(days=6)
    
    with LogseqClient(GRAPH) as client:
        graph = client.load_graph()
        
        # Get journals in range
        journals = [j for j in graph.get_journal_pages()
                   if j.journal_date and start_date <= j.journal_date.date() <= end_date]
        
        # Get tasks
        all_tasks = graph.get_task_blocks()
        completed = [t for t in all_tasks if t.is_completed_task()]
        
        # Get top tags
        tag_counts = {}
        for j in journals:
            for tag in j.tags:
                tag_counts[tag] = tag_counts.get(tag, 0) + 1
        top_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # Build report
        report = f"""# Weekly Review: {start_date} to {end_date}

## Metrics
- Journal entries: {len(journals)}
- Tasks completed: {len(completed)}
- Active tags: {len(tag_counts)}

## Top Activities
"""
        for tag, count in top_tags:
            report += f"- #{tag} ({count} mentions)\n"
        
        report += "\n## Accomplishments\n"
        for task in completed[:20]:
            report += f"- ✓ {task.content}\n"
        
        # Save as both page and file
        page_name = f"Weekly Review {end_date}"
        client.create_page(page_name, report)
        
        # Export to file
        OUTPUT_DIR.mkdir(exist_ok=True)
        output_file = OUTPUT_DIR / f"weekly_{end_date}.md"
        output_file.write_text(report)
        
        print(f"✓ Created {page_name}")
        print(f"✓ Exported to {output_file}")

if __name__ == "__main__":
    weekly_review()
```

**Schedule for Sundays at 8 PM:**

```bash
0 20 * * 0 cd /path/to/logseq-python && python3 weekly_review.py
```

---

## 3. Meeting Workflows

### Pre-Meeting Template Application

```python path=null start=null
#!/usr/bin/env python3
"""
prepare_meeting.py - Create meeting page from template
"""

import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from logseq_py.logseq_client import LogseqClient

GRAPH = Path.home() / "Documents/Logseq/Work"

def prepare_meeting(topic, attendees):
    """Prepare a meeting page from template."""
    
    with LogseqClient(GRAPH) as client:
        template = client.get_page("template/Meeting Notes")
        if not template:
            print("Error: Template not found")
            return
        
        # Get template content
        content = template.to_markdown()
        
        # Substitute variables
        content = content.replace("{{topic}}", topic)
        content = content.replace("{{date}}", datetime.now().strftime("%Y-%m-%d"))
        content = content.replace("{{time}}", datetime.now().strftime("%H:%M"))
        
        # Add attendees
        for i, name in enumerate(attendees, 1):
            content = content.replace(f"{{{{attendee{i}}}}}", name)
        
        # Create page
        page_name = f"Meetings/{topic} - {datetime.now().strftime('%Y-%m-%d')}"
        client.create_page(page_name, content)
        
        print(f"✓ Created meeting page: {page_name}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Usage: python prepare_meeting.py 'Topic' 'Attendee1,Attendee2'")
        sys.exit(1)
    
    topic = sys.argv[1]
    attendees = sys.argv[2].split(',')
    
    prepare_meeting(topic, attendees)
```

**Usage:**

```bash
python prepare_meeting.py "Sprint Planning" "Alice,Bob,Charlie"
```

---

## 4. Research Digest

### Weekly Research Summary

```python path=null start=null
#!/usr/bin/env python3
"""
research_digest.py - Collect and summarize research content
"""

from datetime import date, timedelta
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from logseq_py.logseq_client import LogseqClient

GRAPH = Path.home() / "Documents/Logseq/Research"

def research_digest():
    """Generate weekly research digest from tagged content."""
    
    with LogseqClient(GRAPH) as client:
        graph = client.load_graph()
        
        # Get pages with research tags
        research_pages = []
        for page in graph.pages.values():
            if any(tag in page.tags for tag in ['research', 'paper', 'article']):
                research_pages.append(page)
        
        # Collect URLs and summaries
        urls = []
        summaries = []
        
        for page in research_pages:
            for block in page.blocks:
                # Extract URLs
                if 'http' in block.content:
                    urls.append((page.name, block.content))
                
                # Look for summary blocks
                if any(keyword in block.content.lower() 
                       for keyword in ['summary:', 'key points:', 'tldr:']):
                    summaries.append((page.name, block.content))
        
        # Build digest
        today = date.today()
        digest = f"""# Research Digest: Week of {today}

## New Resources ({len(urls)})
"""
        
        for page_name, content in urls[:20]:
            digest += f"- [[{page_name}]]: {content[:100]}...\n"
        
        digest += f"\n## Key Insights ({len(summaries)})\n"
        
        for page_name, summary in summaries[:10]:
            digest += f"\n### {page_name}\n{summary}\n"
        
        # Create digest page
        page_name = f"Research Digest {today}"
        client.create_page(page_name, digest)
        
        print(f"✓ Created {page_name}")
        print(f"  - {len(urls)} resources")
        print(f"  - {len(summaries)} summaries")

if __name__ == "__main__":
    research_digest()
```

---

## 5. Personal CRM

### Contact Follow-Up Tracker

```python path=null start=null
#!/usr/bin/env python3
"""
crm_tracker.py - Track when you last interacted with people
"""

from datetime import date, timedelta
from pathlib import Path
import sys
import re

sys.path.insert(0, str(Path(__file__).parent.parent))

from logseq_py.logseq_client import LogseqClient

GRAPH = Path.home() / "Documents/Logseq/Personal"

def extract_people_mentions(graph):
    """Extract all people mentions from journals."""
    
    people_last_seen = {}
    
    for journal in graph.get_journal_pages():
        if not journal.journal_date:
            continue
        
        for block in journal.blocks:
            # Find @mentions
            mentions = re.findall(r'@(\w+)', block.content)
            for person in mentions:
                if person not in people_last_seen or \
                   journal.journal_date.date() > people_last_seen[person]:
                    people_last_seen[person] = journal.journal_date.date()
    
    return people_last_seen

def generate_followup_report():
    """Generate follow-up report for people."""
    
    with LogseqClient(GRAPH) as client:
        graph = client.load_graph()
        
        people_last_seen = extract_people_mentions(graph)
        today = date.today()
        
        # Categorize by time since last contact
        overdue = []  # > 30 days
        soon = []     # 14-30 days
        recent = []   # < 14 days
        
        for person, last_date in people_last_seen.items():
            days_ago = (today - last_date).days
            
            if days_ago > 30:
                overdue.append((person, days_ago))
            elif days_ago > 14:
                soon.append((person, days_ago))
            else:
                recent.append((person, days_ago))
        
        # Build report
        report = f"""# Follow-Up Tracker: {today}

## Overdue (>30 days) - {len(overdue)}
"""
        
        for person, days in sorted(overdue, key=lambda x: x[1], reverse=True):
            report += f"- [[{person}]] - {days} days ago\n"
        
        report += f"\n## Coming Up (14-30 days) - {len(soon)}\n"
        
        for person, days in sorted(soon, key=lambda x: x[1], reverse=True):
            report += f"- [[{person}]] - {days} days ago\n"
        
        # Create page
        client.create_page("Follow-Up Tracker", report)
        print(f"✓ Updated Follow-Up Tracker")
        print(f"  - {len(overdue)} overdue")
        print(f"  - {len(soon)} coming up soon")

if __name__ == "__main__":
    generate_followup_report()
```

---

## 6. Task Management

### Task Export to External System

```python path=null start=null
#!/usr/bin/env python3
"""
sync_tasks.py - Export tasks to CSV for import into project management tools
"""

import csv
from datetime import date
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from logseq_py.logseq_client import LogseqClient

GRAPH = Path.home() / "Documents/Logseq/Work"
OUTPUT = Path.home() / "Dropbox/Tasks/logseq_tasks.csv"

def export_tasks():
    """Export active tasks to CSV for external systems."""
    
    with LogseqClient(GRAPH) as client:
        graph = client.load_graph()
        
        # Get active tasks
        tasks = [t for t in graph.get_task_blocks() if not t.is_completed_task()]
        
        # Group by project (from page name)
        by_project = {}
        for task in tasks:
            project = task.page_name.split('/')[0] if task.page_name and '/' in task.page_name else "General"
            if project not in by_project:
                by_project[project] = []
            by_project[project].append(task)
        
        # Write CSV
        OUTPUT.parent.mkdir(exist_ok=True)
        with open(OUTPUT, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Project', 'Status', 'Priority', 'Task', 'Due Date', 'Tags'])
            
            for project, project_tasks in sorted(by_project.items()):
                for task in project_tasks:
                    writer.writerow([
                        project,
                        task.task_state.value if task.task_state else 'TODO',
                        task.priority.value if task.priority else '',
                        task.content,
                        str(task.deadline.date) if task.deadline else '',
                        ','.join(task.tags)
                    ])
        
        print(f"✓ Exported {len(tasks)} tasks to {OUTPUT}")
        for project, project_tasks in sorted(by_project.items()):
            print(f"  - {project}: {len(project_tasks)}")

if __name__ == "__main__":
    export_tasks()
```

---

## 7. Learning Tracker

### Progress Report

```python path=null start=null
#!/usr/bin/env python3
"""
learning_progress.py - Track learning progress across topics
"""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from logseq_py.logseq_client import LogseqClient

GRAPH = Path.home() / "Documents/Logseq/Learning"

def learning_report():
    """Generate learning progress report."""
    
    with LogseqClient(GRAPH) as client:
        graph = client.load_graph()
        
        # Find learning-tagged pages
        learning_pages = [p for p in graph.pages.values() if 'learning' in p.tags]
        
        # Categorize by status
        in_progress = []
        completed = []
        planned = []
        
        for page in learning_pages:
            # Check for status property
            status = page.properties.get('status', '').lower()
            
            if 'complete' in status or 'done' in status:
                completed.append(page)
            elif 'progress' in status or 'active' in status:
                in_progress.append(page)
            else:
                planned.append(page)
        
        # Build report
        report = f"""# Learning Progress Report

## In Progress ({len(in_progress)})
"""
        
        for page in in_progress:
            topics = ', '.join(f"#{t}" for t in page.tags if t != 'learning')
            report += f"- [[{page.name}]] {topics}\n"
        
        report += f"\n## Completed ({len(completed)})\n"
        
        for page in completed:
            report += f"- ✓ [[{page.name}]]\n"
        
        report += f"\n## Planned ({len(planned)})\n"
        
        for page in planned:
            report += f"- [ ] [[{page.name}]]\n"
        
        # Create page
        client.create_page("Learning Progress", report)
        print(f"✓ Updated Learning Progress")
        print(f"  - {len(in_progress)} in progress")
        print(f"  - {len(completed)} completed")
        print(f"  - {len(planned)} planned")

if __name__ == "__main__":
    learning_report()
```

---

## 8. Backup & Export

### Automated Backup Script

```bash
#!/bin/bash
# backup_logseq.sh - Automated backup of Logseq graph

GRAPH="/Users/you/Documents/Logseq/Personal"
BACKUP_DIR="/Users/you/Backups/Logseq"
DATE=$(date +%Y-%m-%d)

# Create backup directory
mkdir -p "$BACKUP_DIR/$DATE"

# Copy graph files
rsync -av --exclude='.DS_Store' "$GRAPH/" "$BACKUP_DIR/$DATE/"

# Export to JSON
python3 -c "
from logseq_py.logseq_client import LogseqClient
client = LogseqClient('$GRAPH')
client.load_graph()
client.export_to_json('$BACKUP_DIR/$DATE/graph.json')
"

# Create archive
cd "$BACKUP_DIR"
tar -czf "$DATE.tar.gz" "$DATE"
rm -rf "$DATE"

# Keep only last 30 days
find "$BACKUP_DIR" -name "*.tar.gz" -mtime +30 -delete

echo "✓ Backup completed: $DATE.tar.gz"
```

**Schedule daily at midnight:**

```bash
0 0 * * * /path/to/backup_logseq.sh
```

---

## Usage Tips

1. **Test first**: Run scripts manually before scheduling with cron
2. **Check logs**: Redirect output to log files for debugging
   ```bash
   0 6 * * * /path/to/script.py >> /tmp/logseq_automation.log 2>&1
   ```
3. **Use absolute paths**: Always use full paths in cron jobs
4. **Virtual environments**: Activate venv in scripts if needed
5. **Error notifications**: Send email on failure
   ```bash
   0 6 * * * /path/to/script.py || mail -s "Script failed" you@example.com
   ```

## Advanced Ideas

- **Git integration**: Commit changes after each automation
- **Webhooks**: Trigger scripts from external events (e.g., GitHub, Slack)
- **API integration**: Push summaries to Notion, Roam, or other tools
- **Machine learning**: Analyze patterns and suggest optimizations
- **Voice input**: Transcribe voice memos and add to journals

For more examples, see `scripts/etl_examples.py`.
