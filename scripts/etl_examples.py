#!/usr/bin/env python3
"""
ETL Examples for Logseq Python

This script demonstrates various ETL (Extract, Transform, Load) operations:
- Export graph to JSON/CSV
- Generate reports (weekly reviews, task summaries)
- Convert to PDF (via Pandoc)
- Apply templates with variable substitution
- Create topic/tag indexes

Usage:
    python scripts/etl_examples.py export-json /path/to/graph --out graph.json
    python scripts/etl_examples.py tasks-csv /path/to/graph --out tasks.csv
    python scripts/etl_examples.py weekly-report /path/to/graph --start 2025-10-20 --end 2025-10-26
    python scripts/etl_examples.py to-pdf input.md --out output.pdf
    python scripts/etl_examples.py apply-template /path/to/graph --template "template/Meeting" --page "Meeting Notes" --var topic="Demo"
"""

import sys
import json
import csv
import subprocess
from pathlib import Path
from datetime import datetime, date, timedelta
from typing import Optional, List, Dict, Any

import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from logseq_py.logseq_client import LogseqClient
from logseq_py.models import Block, Page

console = Console()


@click.group()
def cli():
    """ETL tools for Logseq graphs."""
    pass


@cli.command()
@click.argument('graph_path', type=click.Path(exists=True))
@click.option('--out', '-o', default='graph_export.json', help='Output JSON file')
def export_json(graph_path: str, out: str):
    """Export entire graph to JSON."""
    console.print(f"[blue]Loading graph from {graph_path}...[/blue]")
    
    with LogseqClient(graph_path) as client:
        graph = client.load_graph()
        
        console.print(f"[green]Loaded {len(graph.pages)} pages[/green]")
        
        # Export using built-in method
        client.export_to_json(out)
        
        console.print(f"[green]✓ Exported to {out}[/green]")


@cli.command()
@click.argument('graph_path', type=click.Path(exists=True))
@click.option('--out', '-o', default='tasks.csv', help='Output CSV file')
@click.option('--state', multiple=True, help='Filter by state (TODO, DOING, DONE)')
def tasks_csv(graph_path: str, out: str, state: List[str]):
    """Export all tasks to CSV."""
    console.print(f"[blue]Extracting tasks from {graph_path}...[/blue]")
    
    with LogseqClient(graph_path) as client:
        graph = client.load_graph()
        
        # Get all task blocks
        all_tasks = graph.get_task_blocks()
        
        # Filter by state if specified
        if state:
            state_upper = [s.upper() for s in state]
            tasks = [t for t in all_tasks if t.task_state and t.task_state.value in state_upper]
        else:
            tasks = all_tasks
        
        console.print(f"[green]Found {len(tasks)} tasks[/green]")
        
        # Write to CSV
        with open(out, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Page', 'State', 'Priority', 'Content', 'Tags', 'Scheduled', 'Deadline'])
            
            for task in tasks:
                writer.writerow([
                    task.page_name or '',
                    task.task_state.value if task.task_state else '',
                    task.priority.value if task.priority else '',
                    task.content,
                    ', '.join(task.tags) if task.tags else '',
                    str(task.scheduled.date) if task.scheduled else '',
                    str(task.deadline.date) if task.deadline else ''
                ])
        
        console.print(f"[green]✓ Exported to {out}[/green]")


@cli.command()
@click.argument('graph_path', type=click.Path(exists=True))
@click.option('--start', help='Start date (YYYY-MM-DD)', default=None)
@click.option('--end', help='End date (YYYY-MM-DD)', default=None)
@click.option('--out', '-o', default=None, help='Output markdown file')
@click.option('--page', help='Create/update this page name in graph')
def weekly_report(graph_path: str, start: Optional[str], end: Optional[str], 
                 out: Optional[str], page: Optional[str]):
    """Generate a weekly review report."""
    
    # Parse dates
    if not start:
        # Default to last 7 days
        end_date = date.today()
        start_date = end_date - timedelta(days=7)
    else:
        start_date = datetime.strptime(start, '%Y-%m-%d').date()
        end_date = datetime.strptime(end, '%Y-%m-%d').date() if end else date.today()
    
    console.print(f"[blue]Generating report for {start_date} to {end_date}...[/blue]")
    
    with LogseqClient(graph_path) as client:
        graph = client.load_graph()
        
        # Get journal pages in range
        journals = graph.get_journal_pages()
        journals_in_range = [
            j for j in journals 
            if j.journal_date and start_date <= j.journal_date.date() <= end_date
        ]
        
        console.print(f"[green]Found {len(journals_in_range)} journal entries[/green]")
        
        # Collect tasks
        all_tasks = graph.get_task_blocks()
        completed_tasks = [t for t in all_tasks if t.is_completed_task()]
        active_tasks = [t for t in all_tasks if t.is_task() and not t.is_completed_task()]
        
        # Collect tags
        all_tags = set()
        for j in journals_in_range:
            all_tags.update(j.tags)
        
        # Build report
        report_lines = [
            f"# Weekly Review: {start_date} to {end_date}",
            "",
            f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "",
            "## Summary",
            "",
            f"- **Journal Entries:** {len(journals_in_range)}",
            f"- **Completed Tasks:** {len(completed_tasks)}",
            f"- **Active Tasks:** {len(active_tasks)}",
            f"- **Tags Used:** {len(all_tags)}",
            "",
            "## Daily Highlights",
            ""
        ]
        
        # Add highlights from each journal
        for journal in sorted(journals_in_range, key=lambda j: j.journal_date):
            if journal.journal_date:
                date_str = journal.journal_date.strftime('%Y-%m-%d (%A)')
                report_lines.append(f"### {date_str}")
                report_lines.append("")
                
                # Get first few blocks
                for block in journal.blocks[:5]:
                    report_lines.append(f"- {block.content}")
                
                if len(journal.blocks) > 5:
                    report_lines.append(f"- ... ({len(journal.blocks) - 5} more blocks)")
                
                report_lines.append("")
        
        # Add tasks section
        report_lines.extend([
            "## Completed Tasks",
            ""
        ])
        
        for task in completed_tasks[:20]:  # Top 20
            report_lines.append(f"- ✓ {task.content}")
        
        if len(completed_tasks) > 20:
            report_lines.append(f"- ... ({len(completed_tasks) - 20} more)")
        
        report_lines.extend([
            "",
            "## Active Tasks",
            ""
        ])
        
        for task in active_tasks[:20]:
            state = task.task_state.value if task.task_state else "TODO"
            report_lines.append(f"- {state} {task.content}")
        
        if len(active_tasks) > 20:
            report_lines.append(f"- ... ({len(active_tasks) - 20} more)")
        
        # Add tags
        report_lines.extend([
            "",
            "## Tags",
            "",
            ", ".join(sorted(all_tags)),
            "",
            "---",
            "",
            "*Generated by logseq-python ETL*"
        ])
        
        report_md = "\n".join(report_lines)
        
        # Save to file if requested
        if out:
            Path(out).write_text(report_md, encoding='utf-8')
            console.print(f"[green]✓ Saved to {out}[/green]")
        
        # Create page in graph if requested
        if page:
            try:
                existing = client.get_page(page)
                if existing:
                    console.print(f"[yellow]Page '{page}' exists, updating...[/yellow]")
                
                # Convert to Logseq block format
                blocks_md = "\n".join(f"- {line}" if not line.startswith('#') and line.strip() else line 
                                     for line in report_lines if line.strip())
                
                client.create_page(page, blocks_md)
                console.print(f"[green]✓ Created/updated page '{page}'[/green]")
            except Exception as e:
                console.print(f"[red]Error creating page: {e}[/red]")
        
        if not out and not page:
            console.print(report_md)


@cli.command()
@click.argument('input_md', type=click.Path(exists=True))
@click.option('--out', '-o', required=True, help='Output PDF file')
@click.option('--engine', default='pandoc', help='PDF engine (pandoc, weasyprint)')
def to_pdf(input_md: str, out: str, engine: str):
    """Convert Markdown to PDF (requires pandoc or weasyprint)."""
    
    if engine == 'pandoc':
        console.print(f"[blue]Converting {input_md} to PDF using Pandoc...[/blue]")
        
        try:
            result = subprocess.run(
                ['pandoc', input_md, '-o', out, '--pdf-engine=xelatex'],
                check=True,
                capture_output=True,
                text=True
            )
            console.print(f"[green]✓ PDF created: {out}[/green]")
        except FileNotFoundError:
            console.print("[red]Error: pandoc not found. Install from https://pandoc.org/[/red]")
            sys.exit(1)
        except subprocess.CalledProcessError as e:
            console.print(f"[red]Pandoc error: {e.stderr}[/red]")
            sys.exit(1)
    
    elif engine == 'weasyprint':
        try:
            import markdown
            from weasyprint import HTML
            
            console.print(f"[blue]Converting {input_md} to PDF using WeasyPrint...[/blue]")
            
            # Convert MD to HTML
            md_text = Path(input_md).read_text(encoding='utf-8')
            html_text = markdown.markdown(md_text)
            
            # Add basic styling
            styled_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <style>
                    body {{ font-family: sans-serif; margin: 2cm; }}
                    h1, h2, h3 {{ color: #333; }}
                    code {{ background: #f4f4f4; padding: 2px 4px; }}
                </style>
            </head>
            <body>
                {html_text}
            </body>
            </html>
            """
            
            HTML(string=styled_html).write_pdf(out)
            console.print(f"[green]✓ PDF created: {out}[/green]")
        
        except ImportError:
            console.print("[red]Error: weasyprint not installed. Install with: pip install weasyprint markdown[/red]")
            sys.exit(1)
    
    else:
        console.print(f"[red]Unknown engine: {engine}[/red]")
        sys.exit(1)


@cli.command()
@click.argument('graph_path', type=click.Path(exists=True))
@click.option('--template', required=True, help='Template page name (e.g., template/Meeting Notes)')
@click.option('--page', required=True, help='Target page to create/update')
@click.option('--var', 'variables', multiple=True, help='Variables in key=value format')
def apply_template(graph_path: str, template: str, page: str, variables: List[str]):
    """Apply a template to a page with variable substitution."""
    
    console.print(f"[blue]Applying template '{template}' to '{page}'...[/blue]")
    
    # Parse variables
    var_dict = {}
    for v in variables:
        if '=' in v:
            key, value = v.split('=', 1)
            var_dict[key] = value
    
    console.print(f"[cyan]Variables: {var_dict}[/cyan]")
    
    with LogseqClient(graph_path) as client:
        graph = client.load_graph()
        
        # Get template
        template_page = client.get_page(template)
        if not template_page:
            console.print(f"[red]Template '{template}' not found[/red]")
            sys.exit(1)
        
        # Extract content
        template_content = template_page.to_markdown()
        
        # Substitute variables
        result_content = template_content
        for key, value in var_dict.items():
            result_content = result_content.replace(f"{{{{{key}}}}}", value)
        
        # Check for unsubstituted variables
        import re
        remaining = re.findall(r'\{\{([^}]+)\}\}', result_content)
        if remaining:
            console.print(f"[yellow]Warning: Unsubstituted variables: {remaining}[/yellow]")
        
        # Create/update target page
        client.create_page(page, result_content)
        
        console.print(f"[green]✓ Applied template to '{page}'[/green]")


@cli.command()
@click.argument('graph_path', type=click.Path(exists=True))
@click.option('--out', '-o', help='Output markdown file')
@click.option('--page', help='Create/update this page in graph')
@click.option('--top', default=50, help='Number of top tags to include')
def topic_report(graph_path: str, out: Optional[str], page: Optional[str], top: int):
    """Generate a topic/tag index report."""
    
    console.print(f"[blue]Generating topic report from {graph_path}...[/blue]")
    
    with LogseqClient(graph_path) as client:
        graph = client.load_graph()
        
        # Collect tag usage
        tag_counts = {}
        for page_obj in graph.pages.values():
            for tag in page_obj.tags:
                tag_counts[tag] = tag_counts.get(tag, 0) + 1
        
        console.print(f"[green]Found {len(tag_counts)} unique tags[/green]")
        
        # Sort by count
        sorted_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)
        
        # Build report
        report_lines = [
            "# Topic Index",
            "",
            f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            f"**Total Tags:** {len(tag_counts)}",
            f"**Total Tag Uses:** {sum(tag_counts.values())}",
            "",
            f"## Top {min(top, len(sorted_tags))} Tags",
            ""
        ]
        
        for tag, count in sorted_tags[:top]:
            report_lines.append(f"- [[{tag}]] ({count} pages)")
        
        report_lines.extend([
            "",
            "## Alphabetical Index",
            ""
        ])
        
        # Group by first letter
        by_letter = {}
        for tag, count in sorted(tag_counts.items()):
            first_letter = tag[0].upper() if tag else '?'
            if first_letter not in by_letter:
                by_letter[first_letter] = []
            by_letter[first_letter].append((tag, count))
        
        for letter in sorted(by_letter.keys()):
            report_lines.append(f"### {letter}")
            report_lines.append("")
            for tag, count in by_letter[letter]:
                report_lines.append(f"- [[{tag}]] ({count})")
            report_lines.append("")
        
        report_lines.extend([
            "---",
            "",
            "*Generated by logseq-python ETL*"
        ])
        
        report_md = "\n".join(report_lines)
        
        # Save to file
        if out:
            Path(out).write_text(report_md, encoding='utf-8')
            console.print(f"[green]✓ Saved to {out}[/green]")
        
        # Create page
        if page:
            client.create_page(page, report_md)
            console.print(f"[green]✓ Created/updated page '{page}'[/green]")
        
        if not out and not page:
            console.print(report_md)


@cli.command()
@click.argument('graph_path', type=click.Path(exists=True))
def stats(graph_path: str):
    """Display graph statistics."""
    
    with LogseqClient(graph_path) as client:
        graph = client.load_graph()
        stats = graph.get_statistics()
        
        table = Table(title=f"Graph Statistics: {Path(graph_path).name}")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("Total Pages", str(stats['total_pages']))
        table.add_row("Regular Pages", str(stats['regular_pages']))
        table.add_row("Journal Pages", str(stats['journal_pages']))
        table.add_row("Total Blocks", str(stats['total_blocks']))
        table.add_row("Total Tags", str(stats['total_tags']))
        table.add_row("Total Links", str(stats['total_links']))
        table.add_row("Task Blocks", str(stats['task_blocks']))
        table.add_row("Completed Tasks", str(stats['completed_tasks']))
        table.add_row("Code Blocks", str(stats['code_blocks']))
        table.add_row("Query Blocks", str(stats['query_blocks']))
        
        console.print(table)


if __name__ == '__main__':
    cli()
