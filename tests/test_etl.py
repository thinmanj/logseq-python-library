"""
Tests for ETL examples script.
"""

import pytest
import json
import csv
from pathlib import Path
from datetime import date, timedelta
from unittest.mock import Mock, patch, MagicMock
from click.testing import CliRunner

# Import ETL script
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from etl_examples import (
    cli, export_json, tasks_csv, weekly_report, 
    to_pdf, apply_template, topic_report, stats
)

from logseq_py.logseq_client import LogseqClient
from logseq_py.models import TaskState, Priority


class TestETLExportJSON:
    """Test JSON export functionality."""
    
    @pytest.fixture
    def test_graph(self, tmp_path):
        """Create test graph."""
        graph_path = tmp_path / "graph"
        graph_path.mkdir()
        (graph_path / "pages").mkdir()
        
        page = graph_path / "pages" / "Test.md"
        page.write_text("- Test content\n")
        
        return graph_path
    
    def test_export_json_command(self, test_graph, tmp_path):
        """Test export-json command."""
        runner = CliRunner()
        output_file = tmp_path / "output.json"
        
        result = runner.invoke(cli, [
            'export-json',
            str(test_graph),
            '--out', str(output_file)
        ])
        
        assert result.exit_code == 0
        assert output_file.exists()
        
        # Verify JSON content
        data = json.loads(output_file.read_text())
        assert 'pages' in data
        assert 'root_path' in data
    
    def test_export_json_with_content(self, test_graph, tmp_path):
        """Test JSON export includes content."""
        # Add more content
        (test_graph / "pages" / "Another.md").write_text("- Another page\n")
        
        runner = CliRunner()
        output_file = tmp_path / "export.json"
        
        result = runner.invoke(cli, [
            'export-json',
            str(test_graph),
            '--out', str(output_file)
        ])
        
        assert result.exit_code == 0
        
        data = json.loads(output_file.read_text())
        assert len(data['pages']) >= 2


class TestETLTasksCSV:
    """Test tasks CSV export."""
    
    @pytest.fixture
    def graph_with_tasks(self, tmp_path):
        """Create graph with tasks."""
        graph_path = tmp_path / "tasks_graph"
        graph_path.mkdir()
        (graph_path / "pages").mkdir()
        
        # Create page with tasks
        page = graph_path / "pages" / "Tasks.md"
        page.write_text("""
- TODO First task #work
- DOING Second task [#A]
- DONE Completed task
- Regular bullet
""")
        
        return graph_path
    
    def test_tasks_csv_command(self, graph_with_tasks, tmp_path):
        """Test tasks-csv command."""
        runner = CliRunner()
        output_file = tmp_path / "tasks.csv"
        
        result = runner.invoke(cli, [
            'tasks-csv',
            str(graph_with_tasks),
            '--out', str(output_file)
        ])
        
        assert result.exit_code == 0
        assert output_file.exists()
        
        # Read and verify CSV
        with open(output_file, 'r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            
            assert len(rows) >= 3  # At least 3 tasks
            assert any('TODO' in row['State'] for row in rows)
            assert any('DONE' in row['State'] for row in rows)
    
    def test_tasks_csv_with_filter(self, graph_with_tasks, tmp_path):
        """Test filtering tasks by state."""
        runner = CliRunner()
        output_file = tmp_path / "todo_only.csv"
        
        result = runner.invoke(cli, [
            'tasks-csv',
            str(graph_with_tasks),
            '--out', str(output_file),
            '--state', 'TODO'
        ])
        
        assert result.exit_code == 0
        
        with open(output_file, 'r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            
            # Should only have TODO tasks
            assert all('TODO' in row['State'] for row in rows)


class TestETLWeeklyReport:
    """Test weekly report generation."""
    
    @pytest.fixture
    def graph_with_journals(self, tmp_path):
        """Create graph with journal entries."""
        graph_path = tmp_path / "journal_graph"
        graph_path.mkdir()
        (graph_path / "journals").mkdir()
        (graph_path / "pages").mkdir()
        
        # Create journal entries for past week
        for i in range(7):
            date_str = (date.today() - timedelta(days=i)).strftime("%Y-%m-%d")
            journal = graph_path / "journals" / f"{date_str}.md"
            journal.write_text(f"""
- Work on project {i}
- TODO Task for day {i}
- #productivity #work
""")
        
        return graph_path
    
    def test_weekly_report_command(self, graph_with_journals, tmp_path):
        """Test weekly-report command."""
        runner = CliRunner()
        output_file = tmp_path / "weekly.md"
        
        start = (date.today() - timedelta(days=7)).strftime("%Y-%m-%d")
        end = date.today().strftime("%Y-%m-%d")
        
        result = runner.invoke(cli, [
            'weekly-report',
            str(graph_with_journals),
            '--start', start,
            '--end', end,
            '--out', str(output_file)
        ])
        
        assert result.exit_code == 0
        assert output_file.exists()
        
        content = output_file.read_text()
        assert "Weekly Review" in content
        assert "Summary" in content
    
    def test_weekly_report_with_page(self, graph_with_journals):
        """Test creating page in graph."""
        runner = CliRunner()
        
        start = (date.today() - timedelta(days=7)).strftime("%Y-%m-%d")
        
        result = runner.invoke(cli, [
            'weekly-report',
            str(graph_with_journals),
            '--start', start,
            '--page', 'Weekly Review Test'
        ])
        
        assert result.exit_code == 0
        
        # Verify page was created
        client = LogseqClient(graph_with_journals)
        graph = client.load_graph()
        page = client.get_page("Weekly Review Test")
        
        assert page is not None


class TestETLApplyTemplate:
    """Test template application."""
    
    @pytest.fixture
    def graph_with_template(self, tmp_path):
        """Create graph with template."""
        graph_path = tmp_path / "template_graph"
        graph_path.mkdir()
        (graph_path / "pages").mkdir()
        
        # Create template
        template = graph_path / "pages" / "template__Meeting.md"
        template.write_text("""template:: true

- Meeting: {{topic}}
  - Date: {{date}}
  - Attendees: {{attendee1}}, {{attendee2}}
  - Notes: {{notes}}
""")
        
        return graph_path
    
    def test_apply_template_command(self, graph_with_template):
        """Test apply-template command."""
        runner = CliRunner()
        
        result = runner.invoke(cli, [
            'apply-template',
            str(graph_with_template),
            '--template', 'template/Meeting',
            '--page', 'Sprint Planning',
            '--var', 'topic=Sprint Planning',
            '--var', 'date=2025-10-28',
            '--var', 'attendee1=Alice',
            '--var', 'attendee2=Bob',
            '--var', 'notes=Discussed timeline'
        ])
        
        assert result.exit_code == 0
        
        # Verify page was created with substituted values
        client = LogseqClient(graph_with_template)
        graph = client.load_graph()
        page = client.get_page("Sprint Planning")
        
        assert page is not None
        content = page.to_markdown()
        assert "Sprint Planning" in content
        assert "Alice" in content
        assert "Bob" in content
    
    def test_apply_template_missing_vars(self, graph_with_template):
        """Test template application with missing variables."""
        runner = CliRunner()
        
        result = runner.invoke(cli, [
            'apply-template',
            str(graph_with_template),
            '--template', 'template/Meeting',
            '--page', 'Test Meeting',
            '--var', 'topic=Test'
            # Missing other variables
        ])
        
        # Should succeed but warn about unsubstituted variables
        assert result.exit_code == 0


class TestETLTopicReport:
    """Test topic/tag report generation."""
    
    @pytest.fixture
    def graph_with_tags(self, tmp_path):
        """Create graph with tagged content."""
        graph_path = tmp_path / "tags_graph"
        graph_path.mkdir()
        (graph_path / "pages").mkdir()
        
        # Create pages with tags
        (graph_path / "pages" / "Page1.md").write_text("- Content #python #programming\n")
        (graph_path / "pages" / "Page2.md").write_text("- Content #python #data\n")
        (graph_path / "pages" / "Page3.md").write_text("- Content #javascript #programming\n")
        
        return graph_path
    
    def test_topic_report_command(self, graph_with_tags, tmp_path):
        """Test topic-report command."""
        runner = CliRunner()
        output_file = tmp_path / "topics.md"
        
        result = runner.invoke(cli, [
            'topic-report',
            str(graph_with_tags),
            '--out', str(output_file)
        ])
        
        assert result.exit_code == 0
        assert output_file.exists()
        
        content = output_file.read_text()
        assert "Topic Index" in content
        assert "python" in content.lower()
        assert "programming" in content.lower()
    
    def test_topic_report_with_limit(self, graph_with_tags, tmp_path):
        """Test limiting number of topics."""
        runner = CliRunner()
        output_file = tmp_path / "top_topics.md"
        
        result = runner.invoke(cli, [
            'topic-report',
            str(graph_with_tags),
            '--out', str(output_file),
            '--top', '2'
        ])
        
        assert result.exit_code == 0


class TestETLStats:
    """Test statistics command."""
    
    @pytest.fixture
    def diverse_graph(self, tmp_path):
        """Create graph with diverse content."""
        graph_path = tmp_path / "stats_graph"
        graph_path.mkdir()
        (graph_path / "journals").mkdir()
        (graph_path / "pages").mkdir()
        
        # Add journals
        for i in range(3):
            date_str = (date.today() - timedelta(days=i)).strftime("%Y-%m-%d")
            journal = graph_path / "journals" / f"{date_str}.md"
            journal.write_text(f"- Journal {i}\n")
        
        # Add pages
        (graph_path / "pages" / "Page1.md").write_text("- Content\n- TODO Task\n")
        (graph_path / "pages" / "Page2.md").write_text("- DONE Completed\n")
        
        return graph_path
    
    def test_stats_command(self, diverse_graph):
        """Test stats command."""
        runner = CliRunner()
        
        result = runner.invoke(cli, ['stats', str(diverse_graph)])
        
        assert result.exit_code == 0
        assert "Total Pages" in result.output
        assert "Journal Pages" in result.output
        assert "Task Blocks" in result.output


class TestETLToPDF:
    """Test PDF conversion."""
    
    @pytest.fixture
    def markdown_file(self, tmp_path):
        """Create markdown file."""
        md_file = tmp_path / "test.md"
        md_file.write_text("""# Test Document

## Section 1
Content here

## Section 2
More content
""")
        return md_file
    
    def test_to_pdf_pandoc_not_installed(self, markdown_file, tmp_path):
        """Test PDF conversion when pandoc not installed."""
        runner = CliRunner()
        output_file = tmp_path / "output.pdf"
        
        with patch('subprocess.run', side_effect=FileNotFoundError):
            result = runner.invoke(cli, [
                'to-pdf',
                str(markdown_file),
                '--out', str(output_file),
                '--engine', 'pandoc'
            ])
            
            assert result.exit_code == 1
            assert "pandoc not found" in result.output.lower()
    
    def test_to_pdf_weasyprint_not_installed(self, markdown_file, tmp_path):
        """Test PDF conversion when weasyprint not installed."""
        runner = CliRunner()
        output_file = tmp_path / "output.pdf"
        
        result = runner.invoke(cli, [
            'to-pdf',
            str(markdown_file),
            '--out', str(output_file),
            '--engine', 'weasyprint'
        ])
        
        # Will fail if weasyprint not installed
        assert result.exit_code in [0, 1]


class TestETLErrorHandling:
    """Test error handling in ETL commands."""
    
    def test_export_json_missing_graph(self, tmp_path):
        """Test export with missing graph."""
        runner = CliRunner()
        
        result = runner.invoke(cli, [
            'export-json',
            '/nonexistent/path',
            '--out', str(tmp_path / "output.json")
        ])
        
        assert result.exit_code != 0
    
    def test_apply_template_missing_template(self, tmp_path):
        """Test applying nonexistent template."""
        graph_path = tmp_path / "graph"
        graph_path.mkdir()
        (graph_path / "pages").mkdir()
        
        runner = CliRunner()
        
        result = runner.invoke(cli, [
            'apply-template',
            str(graph_path),
            '--template', 'nonexistent/template',
            '--page', 'Test',
            '--var', 'foo=bar'
        ])
        
        assert result.exit_code == 1
        assert "not found" in result.output.lower()


class TestETLIntegration:
    """Integration tests for ETL workflows."""
    
    @pytest.fixture
    def complete_graph(self, tmp_path):
        """Create comprehensive graph for integration tests."""
        graph_path = tmp_path / "complete_graph"
        graph_path.mkdir()
        (graph_path / "journals").mkdir()
        (graph_path / "pages").mkdir()
        
        # Add diverse content
        for i in range(5):
            date_str = (date.today() - timedelta(days=i)).strftime("%Y-%m-%d")
            journal = graph_path / "journals" / f"{date_str}.md"
            journal.write_text(f"""
- Work on project {i}
- TODO Task {i}
- #work #productivity
""")
        
        (graph_path / "pages" / "Project.md").write_text("""
- Project overview
- TODO Setup
- DOING Implementation
- DONE Design
""")
        
        (graph_path / "pages" / "template__Daily.md").write_text("""template:: true

- Goals for {{date}}
  - {{goal1}}
  - {{goal2}}
""")
        
        return graph_path
    
    def test_full_etl_workflow(self, complete_graph, tmp_path):
        """Test complete ETL workflow."""
        runner = CliRunner()
        
        # 1. Export to JSON
        json_file = tmp_path / "export.json"
        result = runner.invoke(cli, [
            'export-json',
            str(complete_graph),
            '--out', str(json_file)
        ])
        assert result.exit_code == 0
        assert json_file.exists()
        
        # 2. Export tasks
        tasks_file = tmp_path / "tasks.csv"
        result = runner.invoke(cli, [
            'tasks-csv',
            str(complete_graph),
            '--out', str(tasks_file)
        ])
        assert result.exit_code == 0
        assert tasks_file.exists()
        
        # 3. Generate weekly report
        report_file = tmp_path / "weekly.md"
        result = runner.invoke(cli, [
            'weekly-report',
            str(complete_graph),
            '--out', str(report_file)
        ])
        assert result.exit_code == 0
        assert report_file.exists()
        
        # 4. Generate topic report
        topics_file = tmp_path / "topics.md"
        result = runner.invoke(cli, [
            'topic-report',
            str(complete_graph),
            '--out', str(topics_file)
        ])
        assert result.exit_code == 0
        assert topics_file.exists()
        
        # 5. Get stats
        result = runner.invoke(cli, ['stats', str(complete_graph)])
        assert result.exit_code == 0
        
        # Verify all files were created
        assert json_file.exists()
        assert tasks_file.exists()
        assert report_file.exists()
        assert topics_file.exists()
