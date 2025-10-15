#!/usr/bin/env python3
"""
Command-line interface for logseq-python.

Provides easy access to logseq-python functionality from the command line.
"""

import sys
import json
import logging
from pathlib import Path
from typing import Optional, List, Dict, Any

try:
    import click
    from rich.console import Console
    from rich.table import Table
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich.panel import Panel
    from rich.syntax import Syntax
    from rich.text import Text
except ImportError:
    print("CLI dependencies not installed. Install with: pip install 'logseq-python[cli]'")
    sys.exit(1)

from .pipeline import (
    create_pipeline, ProcessingContext, ProcessingStatus,
    create_content_filter, create_task_filter, create_and_filter,
    analyze_content, extract_from_block, generate_content
)
from .models import Block, Page
from .client import LogseqClient


console = Console()


@click.group()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
@click.option('--quiet', '-q', is_flag=True, help='Suppress output except errors')
@click.pass_context
def cli(ctx, verbose: bool, quiet: bool):
    """
    Logseq Python CLI - Tools for processing Logseq knowledge graphs.
    
    This CLI provides access to the logseq-python library functionality
    including content analysis, pipeline processing, and data extraction.
    """
    ctx.ensure_object(dict)
    
    # Setup logging
    if verbose:
        level = logging.DEBUG
    elif quiet:
        level = logging.ERROR
    else:
        level = logging.INFO
    
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    ctx.obj['verbose'] = verbose
    ctx.obj['quiet'] = quiet


@cli.group()
def analyze():
    """Analyze Logseq content using various analyzers."""
    pass


@analyze.command()
@click.argument('text')
@click.option('--analyzers', '-a', multiple=True, 
              help='Specific analyzers to use (sentiment, topics, summary, structure)')
@click.option('--output', '-o', type=click.Path(), help='Output file for results')
@click.option('--format', 'output_format', type=click.Choice(['json', 'table', 'text']), 
              default='text', help='Output format')
def text(text: str, analyzers: List[str], output: Optional[str], output_format: str):
    """Analyze a text string using content analyzers."""
    
    # Use all analyzers if none specified
    if not analyzers:
        analyzers = ['sentiment', 'topics', 'summary', 'structure']
    
    console.print(f"[blue]Analyzing text with {len(analyzers)} analyzers...[/blue]")
    
    try:
        results = analyze_content(text, list(analyzers))
        
        if output_format == 'json':
            output_data = json.dumps(results, indent=2, default=str)
            if output:
                Path(output).write_text(output_data)
                console.print(f"[green]Results saved to {output}[/green]")
            else:
                console.print(output_data)
        
        elif output_format == 'table':
            _display_analysis_table(results)
        
        else:  # text format
            _display_analysis_text(results)
            
    except Exception as e:
        console.print(f"[red]Error during analysis: {e}[/red]")
        sys.exit(1)


@analyze.command()
@click.argument('graph_path', type=click.Path(exists=True))
@click.option('--page', '-p', help='Analyze specific page')
@click.option('--filter', 'filter_expr', help='Filter expression for blocks')
@click.option('--analyzers', '-a', multiple=True, help='Analyzers to use')
@click.option('--output', '-o', type=click.Path(), help='Output file')
@click.option('--limit', type=int, default=100, help='Maximum blocks to analyze')
def graph(graph_path: str, page: Optional[str], filter_expr: Optional[str], 
          analyzers: List[str], output: Optional[str], limit: int):
    """Analyze content from a Logseq graph."""
    
    if not analyzers:
        analyzers = ['sentiment', 'topics', 'structure']
    
    try:
        client = LogseqClient(graph_path)
        
        # Load content
        if page:
            page_obj = client.get_page(page)
            if not page_obj or not page_obj.blocks:
                console.print(f"[red]Page '{page}' not found or has no blocks[/red]")
                return
            blocks = page_obj.blocks
        else:
            pages = client.get_all_pages()
            blocks = []
            for p in pages:
                if p.blocks:
                    blocks.extend(p.blocks)
            
            if limit:
                blocks = blocks[:limit]
        
        console.print(f"[blue]Analyzing {len(blocks)} blocks from graph...[/blue]")
        
        # Apply filter if specified
        if filter_expr:
            # Simple filter implementation - could be expanded
            if 'TODO' in filter_expr:
                blocks = [b for b in blocks if b.content and 'TODO' in b.content]
            elif 'http' in filter_expr:
                blocks = [b for b in blocks if b.content and 'http' in b.content]
        
        # Analyze blocks
        results = []
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
            task = progress.add_task("Analyzing blocks...", total=len(blocks))
            
            for block in blocks:
                if block.content:
                    block_results = analyze_content(block.content, list(analyzers))
                    results.append({
                        'block_id': getattr(block, 'id', None),
                        'content_preview': block.content[:100] + '...' if len(block.content) > 100 else block.content,
                        'analysis': block_results
                    })
                progress.advance(task)
        
        # Display results
        _display_graph_analysis_results(results, analyzers)
        
        # Save if requested
        if output:
            output_data = json.dumps(results, indent=2, default=str)
            Path(output).write_text(output_data)
            console.print(f"[green]Results saved to {output}[/green]")
            
    except Exception as e:
        console.print(f"[red]Error analyzing graph: {e}[/red]")
        sys.exit(1)


@cli.group()
def pipeline():
    """Run processing pipelines on Logseq content."""
    pass


@pipeline.command()
@click.argument('graph_path', type=click.Path(exists=True))
@click.option('--filter', help='Filter expression for content')
@click.option('--extractors', multiple=True, help='Content extractors to use')
@click.option('--analyzers', multiple=True, help='Analyzers to use')
@click.option('--generators', multiple=True, help='Generators to use')
@click.option('--output', '-o', type=click.Path(), help='Output directory for results')
@click.option('--resume', type=click.Path(), help='Resume from saved state file')
def run(graph_path: str, filter: Optional[str], extractors: List[str], 
        analyzers: List[str], generators: List[str], output: Optional[str], 
        resume: Optional[str]):
    """Run a complete processing pipeline on a Logseq graph."""
    
    # Set defaults
    if not extractors:
        extractors = ['url', 'youtube', 'github']
    if not analyzers:
        analyzers = ['sentiment', 'topics', 'summary']
    if not generators:
        generators = ['summary_page', 'insights_blocks']
    
    console.print(Panel(
        f"[bold]Pipeline Configuration[/bold]\n"
        f"Graph: {graph_path}\n"
        f"Extractors: {', '.join(extractors)}\n"
        f"Analyzers: {', '.join(analyzers)}\n"
        f"Generators: {', '.join(generators)}",
        title="Pipeline Setup"
    ))
    
    try:
        # Create context
        context = ProcessingContext(graph_path=graph_path)
        
        # Build pipeline
        from .pipeline.steps import (
            LoadContentStep, FilterBlocksStep, ExtractContentStep,
            AnalyzeContentStep, GenerateContentStep, ReportProgressStep
        )
        
        pipeline_builder = create_pipeline("cli_pipeline", "CLI-initiated pipeline")
        pipeline_builder.step(LoadContentStep(graph_path))
        
        # Add filter if specified
        if filter:
            if filter == 'tasks':
                pipeline_builder.step(FilterBlocksStep(create_task_filter()))
            elif filter.startswith('contains:'):
                text = filter[9:]  # Remove 'contains:' prefix
                pipeline_builder.step(FilterBlocksStep(create_content_filter(contains=text)))
        
        # Add processing steps
        pipeline_builder.step(ExtractContentStep(list(extractors)))
        pipeline_builder.step(AnalyzeContentStep(list(analyzers)))
        pipeline_builder.step(GenerateContentStep(list(generators)))
        pipeline_builder.step(ReportProgressStep())
        
        pipeline_obj = pipeline_builder.configure(continue_on_error=True).build()
        
        # Execute pipeline with progress tracking
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
            task = progress.add_task("Running pipeline...", total=len(pipeline_obj.steps))
            
            result_context = pipeline_obj.execute(context)
            
            progress.advance(task, len(pipeline_obj.steps))
        
        # Display results
        _display_pipeline_results(result_context)
        
        # Save results if output specified
        if output:
            output_path = Path(output)
            output_path.mkdir(exist_ok=True)
            
            # Save summary
            summary = result_context.get_status_summary()
            (output_path / 'pipeline_summary.json').write_text(
                json.dumps(summary, indent=2, default=str)
            )
            
            # Save detailed results
            if result_context.generated_content:
                (output_path / 'generated_content.json').write_text(
                    json.dumps(result_context.generated_content, indent=2, default=str)
                )
            
            console.print(f"[green]Pipeline results saved to {output_path}[/green]")
            
    except Exception as e:
        console.print(f"[red]Pipeline execution failed: {e}[/red]")
        if ctx.obj.get('verbose'):
            import traceback
            console.print(traceback.format_exc())
        sys.exit(1)


@pipeline.command()
@click.argument('graph_path', type=click.Path(exists=True))
@click.option('--output', '-o', type=click.Path(), help='Output file for report')
def info(graph_path: str, output: Optional[str]):
    """Get information about a Logseq graph."""
    
    try:
        client = LogseqClient(graph_path)
        pages = client.get_all_pages()
        
        # Gather statistics
        total_pages = len(pages)
        total_blocks = sum(len(p.blocks) if p.blocks else 0 for p in pages)
        pages_with_blocks = sum(1 for p in pages if p.blocks)
        
        # Content statistics
        task_blocks = 0
        code_blocks = 0
        blocks_with_urls = 0
        
        for page in pages:
            if page.blocks:
                for block in page.blocks:
                    if block.content:
                        if any(marker in block.content for marker in ['TODO', 'DOING', 'DONE']):
                            task_blocks += 1
                        if '```' in block.content:
                            code_blocks += 1
                        if 'http' in block.content:
                            blocks_with_urls += 1
        
        # Create info table
        table = Table(title=f"Logseq Graph Information: {Path(graph_path).name}")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("Total Pages", str(total_pages))
        table.add_row("Pages with Content", str(pages_with_blocks))
        table.add_row("Total Blocks", str(total_blocks))
        table.add_row("Task Blocks", str(task_blocks))
        table.add_row("Code Blocks", str(code_blocks))
        table.add_row("Blocks with URLs", str(blocks_with_urls))
        
        if total_blocks > 0:
            table.add_row("Avg Blocks/Page", f"{total_blocks/total_pages:.1f}")
        
        console.print(table)
        
        # Save if requested
        if output:
            info_data = {
                'graph_path': graph_path,
                'total_pages': total_pages,
                'pages_with_blocks': pages_with_blocks,
                'total_blocks': total_blocks,
                'task_blocks': task_blocks,
                'code_blocks': code_blocks,
                'blocks_with_urls': blocks_with_urls,
                'avg_blocks_per_page': total_blocks/total_pages if total_pages > 0 else 0
            }
            Path(output).write_text(json.dumps(info_data, indent=2))
            console.print(f"[green]Graph info saved to {output}[/green]")
            
    except Exception as e:
        console.print(f"[red]Error getting graph info: {e}[/red]")
        sys.exit(1)


@cli.command()
@click.argument('text')
@click.option('--extractors', multiple=True, help='Extractors to use')
@click.option('--format', 'output_format', type=click.Choice(['json', 'text']), 
              default='text', help='Output format')
def extract(text: str, extractors: List[str], output_format: str):
    """Extract content from URLs, YouTube links, etc. in text."""
    
    if not extractors:
        extractors = ['url', 'youtube', 'github', 'twitter']
    
    # Create a block from the text
    block = Block(content=text)
    
    console.print(f"[blue]Extracting content using {len(extractors)} extractors...[/blue]")
    
    try:
        results = extract_from_block(block, list(extractors))
        
        if output_format == 'json':
            console.print(json.dumps(results, indent=2, default=str))
        else:
            _display_extraction_results(results)
            
    except Exception as e:
        console.print(f"[red]Error during extraction: {e}[/red]")
        sys.exit(1)


# Helper functions for display

def _display_analysis_table(results: Dict[str, Any]):
    """Display analysis results in table format."""
    table = Table(title="Content Analysis Results")
    table.add_column("Analyzer", style="cyan")
    table.add_column("Results", style="green")
    
    for analyzer, result in results.items():
        if isinstance(result, dict):
            if analyzer == 'sentiment':
                sentiment = result.get('sentiment', 'unknown')
                polarity = result.get('polarity', 0)
                table.add_row(analyzer, f"{sentiment} (polarity: {polarity:.2f})")
            elif analyzer == 'topics':
                topics = [t['topic'] for t in result.get('topics', [])]
                table.add_row(analyzer, ", ".join(topics[:3]))
            elif analyzer == 'summary':
                summary = result.get('summary', '')
                preview = summary[:100] + '...' if len(summary) > 100 else summary
                table.add_row(analyzer, preview)
            else:
                table.add_row(analyzer, str(result))
        else:
            table.add_row(analyzer, str(result))
    
    console.print(table)


def _display_analysis_text(results: Dict[str, Any]):
    """Display analysis results in text format."""
    for analyzer, result in results.items():
        console.print(f"\n[bold blue]{analyzer.capitalize()} Analysis:[/bold blue]")
        
        if isinstance(result, dict):
            if analyzer == 'sentiment':
                sentiment = result.get('sentiment', 'unknown')
                polarity = result.get('polarity', 0)
                console.print(f"  Sentiment: {sentiment}")
                console.print(f"  Polarity: {polarity:.3f}")
                console.print(f"  Positive Score: {result.get('positive_score', 0)}")
                console.print(f"  Negative Score: {result.get('negative_score', 0)}")
            
            elif analyzer == 'topics':
                if result.get('topics'):
                    console.print("  Topics:")
                    for topic in result['topics']:
                        console.print(f"    - {topic['topic']}: {topic['score']}")
                
                if result.get('keywords'):
                    console.print("  Keywords:")
                    for kw in result['keywords'][:5]:  # Top 5
                        console.print(f"    - {kw['word']}: {kw['count']}")
            
            elif analyzer == 'summary':
                console.print(f"  Summary: {result.get('summary', 'N/A')}")
                console.print(f"  Compression: {result.get('compression_ratio', 0):.1%}")
            
            elif analyzer == 'structure':
                console.print(f"  Word Count: {result.get('word_count', 0)}")
                console.print(f"  Sentence Count: {result.get('sentence_count', 0)}")
                console.print(f"  Complexity: {result.get('readability', {}).get('complexity', 'unknown')}")
        
        else:
            console.print(f"  {result}")


def _display_graph_analysis_results(results: List[Dict], analyzers: List[str]):
    """Display results from graph analysis."""
    console.print(f"\n[bold green]Analysis complete![/bold green] Processed {len(results)} blocks.")
    
    # Show summary statistics
    if 'sentiment' in analyzers:
        sentiments = []
        for result in results:
            if 'sentiment' in result['analysis']:
                sentiments.append(result['analysis']['sentiment']['sentiment'])
        
        if sentiments:
            positive = sentiments.count('positive')
            negative = sentiments.count('negative')
            neutral = sentiments.count('neutral')
            
            console.print(f"\n[bold]Sentiment Summary:[/bold]")
            console.print(f"  Positive: {positive}")
            console.print(f"  Negative: {negative}")
            console.print(f"  Neutral: {neutral}")


def _display_pipeline_results(context):
    """Display pipeline execution results."""
    summary = context.get_status_summary()
    
    # Create results panel
    results_text = (
        f"[bold green]Pipeline Completed Successfully![/bold green]\n\n"
        f"[bold]Statistics:[/bold]\n"
        f"  Processed Items: {summary['processed_items']}/{summary['total_items']}\n"
        f"  Processing Time: {summary['elapsed_time']:.1f}s\n"
        f"  Success Rate: {summary['progress']:.1f}%\n"
        f"  Errors: {summary['errors_count']}\n\n"
    )
    
    if context.extracted_content:
        extracted_count = context.extracted_content.get('count', 0)
        results_text += f"  Content Extracted: {extracted_count} items\n"
    
    if context.analysis_results:
        analysis_count = sum(
            result.get('count', 0) for result in context.analysis_results.values()
            if isinstance(result, dict)
        )
        results_text += f"  Analyses Completed: {analysis_count}\n"
    
    if context.generated_content:
        generated_count = len(context.generated_content)
        results_text += f"  Content Generated: {generated_count} items\n"
    
    console.print(Panel(results_text, title="Pipeline Results"))


def _display_extraction_results(results: Dict[str, Any]):
    """Display content extraction results."""
    for extractor, result in results.items():
        console.print(f"\n[bold blue]{extractor.capitalize()} Extraction:[/bold blue]")
        
        if 'error' in result:
            console.print(f"  [red]Error: {result['error']}[/red]")
        elif isinstance(result, dict):
            if result.get('type') == 'youtube' and 'videos' in result:
                for video in result['videos']:
                    console.print(f"  Video: {video.get('title', 'N/A')}")
                    console.print(f"  Author: {video.get('author_name', 'N/A')}")
            elif result.get('type') == 'url' and 'content' in result:
                for item in result['content']:
                    console.print(f"  URL: {item.get('url', 'N/A')}")
                    console.print(f"  Title: {item.get('title', 'N/A')}")
            else:
                console.print(f"  {result}")


def main():
    """Main entry point for CLI."""
    cli()


if __name__ == '__main__':
    main()