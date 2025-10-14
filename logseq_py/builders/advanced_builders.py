"""
Advanced builders for complex Logseq content generation.

This module provides builders for queries, journal entries, workflows,
and comprehensive demo generation with high-level abstractions.
"""

from typing import List, Dict, Any, Optional, Union
from datetime import datetime, date, timedelta
from .core import ContentBuilder, format_date
from .page_builders import PageBuilder
from .content_types import TaskBuilder, CodeBlockBuilder, QuoteBuilder, TableBuilder


class QueryBuilder(ContentBuilder):
    """Builder for Logseq queries."""
    
    def __init__(self):
        super().__init__()
        self._conditions: List[str] = []
        self._query_type = "and"  # or "or"
    
    def and_query(self) -> 'QueryBuilder':
        """Set query type to AND."""
        self._query_type = "and"
        return self
    
    def or_query(self) -> 'QueryBuilder':
        """Set query type to OR."""
        self._query_type = "or"
        return self
    
    def property(self, key: str, value: str) -> 'QueryBuilder':
        """Add property condition."""
        self._conditions.append(f'(property {key} "{value}")')
        return self
    
    def task_state(self, *states: str) -> 'QueryBuilder':
        """Add task state condition."""
        state_conditions = []
        for state in states:
            state_conditions.append(f"(task {state})")
        if len(state_conditions) == 1:
            self._conditions.append(state_conditions[0])
        else:
            self._conditions.append(f'(or {" ".join(state_conditions)})')
        return self
    
    def todo(self) -> 'QueryBuilder':
        """Add TODO task condition."""
        return self.task_state("TODO")
    
    def doing(self) -> 'QueryBuilder':
        """Add DOING task condition."""
        return self.task_state("DOING")
    
    def done(self) -> 'QueryBuilder':
        """Add DONE task condition."""
        return self.task_state("DONE")
    
    def has_tag(self, tag: str) -> 'QueryBuilder':
        """Add tag condition."""
        self._conditions.append(f"[[{tag}]]")
        return self
    
    def between_dates(self, start: Union[str, date, datetime], end: Union[str, date, datetime]) -> 'QueryBuilder':
        """Add date range condition."""
        start_str = format_date(start) if not isinstance(start, str) else start
        end_str = format_date(end) if not isinstance(end, str) else end
        self._conditions.append(f"(between {start_str} {end_str})")
        return self
    
    def last_days(self, days: int) -> 'QueryBuilder':
        """Add last N days condition."""
        self._conditions.append(f"(between -{days}d today)")
        return self
    
    def this_week(self) -> 'QueryBuilder':
        """Add this week condition."""
        return self.last_days(7)
    
    def this_month(self) -> 'QueryBuilder':
        """Add this month condition."""
        return self.last_days(30)
    
    def page_reference(self, page_name: str) -> 'QueryBuilder':
        """Add page reference condition."""
        self._conditions.append(f"[[{page_name}]]")
        return self
    
    def namespace(self, namespace: str) -> 'QueryBuilder':
        """Add namespace condition."""
        self._conditions.append(f'(namespace "{namespace}")')
        return self
    
    def custom_condition(self, condition: str) -> 'QueryBuilder':
        """Add a custom query condition."""
        self._conditions.append(condition)
        return self
    
    def build(self) -> str:
        """Build the query."""
        if not self._conditions:
            return "{{query}}"
        
        if len(self._conditions) == 1:
            query_content = self._conditions[0]
        else:
            query_content = f'({self._query_type} {" ".join(self._conditions)})'
        
        return f"{{{{query {query_content}}}}}"


class JournalBuilder(PageBuilder):
    """Builder for journal entries."""
    
    def __init__(self, date_val: Union[str, date, datetime] = None):
        if date_val is None:
            date_val = datetime.now()
        
        # Format date for journal filename
        if isinstance(date_val, str):
            self._date_str = date_val
            self._date = datetime.strptime(date_val, "%Y-%m-%d").date()
        elif isinstance(date_val, datetime):
            self._date = date_val.date()
            self._date_str = self._date.strftime("%Y-%m-%d")
        else:  # date
            self._date = date_val
            self._date_str = date_val.strftime("%Y-%m-%d")
        
        # Journal pages use the date as filename
        super().__init__(f"journals_{self._date_str}")
        
        # Set journal-specific properties
        self.page_type("journal")
        self.created(self._date)
    
    def date(self, date_val: Union[str, date, datetime]) -> 'JournalBuilder':
        """Set journal date."""
        self.__init__(date_val)
        return self
    
    def daily_note(self, content: str) -> 'JournalBuilder':
        """Add a daily note entry."""
        self.heading(2, "Daily Notes")
        self.text(content)
        return self
    
    def mood(self, mood: str, rating: Optional[int] = None) -> 'JournalBuilder':
        """Add mood tracking."""
        mood_text = f"Mood: {mood}"
        if rating is not None:
            mood_text += f" ({rating}/10)"
        self.text(mood_text)
        self.tag("mood")
        return self
    
    def weather(self, description: str, temperature: Optional[str] = None) -> 'JournalBuilder':
        """Add weather information."""
        weather_text = f"Weather: {description}"
        if temperature:
            weather_text += f", {temperature}"
        self.text(weather_text)
        return self
    
    def gratitude(self, *items: str) -> 'JournalBuilder':
        """Add gratitude entries."""
        self.heading(3, "Gratitude")
        for item in items:
            self.text(f"- Grateful for: {item}")
        self.tag("gratitude")
        return self
    
    def reflection(self, content: str) -> 'JournalBuilder':
        """Add daily reflection."""
        self.heading(3, "Reflection")
        self.text(content)
        self.tag("reflection")
        return self
    
    def habit_tracker(self, **habits: bool) -> 'JournalBuilder':
        """Add habit tracking."""
        self.heading(3, "Habits")
        for habit, completed in habits.items():
            status = "✅" if completed else "❌"
            self.text(f"- {status} {habit}")
        self.tag("habits")
        return self
    
    def meeting_summary(self, title: str, attendees: List[str], notes: str) -> 'JournalBuilder':
        """Add meeting summary."""
        self.heading(3, f"Meeting: {title}")
        self.text(f"Attendees: {', '.join(attendees)}")
        self.text(f"Notes: {notes}")
        return self
    
    def work_log(self, *activities: str) -> 'JournalBuilder':
        """Add work activities log."""
        self.heading(3, "Work Log")
        for activity in activities:
            self.text(f"- {activity}")
        self.tag("work")
        return self
    
    def learning_log(self, topic: str, content: str, source: Optional[str] = None) -> 'JournalBuilder':
        """Add learning entry."""
        self.heading(3, f"Learning: {topic}")
        self.text(content)
        if source:
            self.text(f"Source: {source}")
        self.tag("learning")
        return self


class WorkflowBuilder(ContentBuilder):
    """Builder for workflow templates and process documentation."""
    
    def __init__(self, name: str):
        super().__init__()
        self._name = name
        self._steps: List[Dict[str, Any]] = []
        self._tools: List[str] = []
        self._prerequisites: List[str] = []
        self._outcomes: List[str] = []
    
    def step(self, title: str, description: str, tools: Optional[List[str]] = None) -> 'WorkflowBuilder':
        """Add a workflow step."""
        step_info = {
            "title": title,
            "description": description,
            "tools": tools or []
        }
        self._steps.append(step_info)
        return self
    
    def prerequisite(self, requirement: str) -> 'WorkflowBuilder':
        """Add a prerequisite."""
        self._prerequisites.append(requirement)
        return self
    
    def tool(self, tool_name: str) -> 'WorkflowBuilder':
        """Add a required tool."""
        self._tools.append(tool_name)
        return self
    
    def outcome(self, result: str) -> 'WorkflowBuilder':
        """Add an expected outcome."""
        self._outcomes.append(result)
        return self
    
    def build(self) -> str:
        """Build the workflow documentation."""
        lines = []
        
        # Title
        lines.append(f"# {self._name} Workflow")
        lines.append("")
        
        # Prerequisites
        if self._prerequisites:
            lines.append("## Prerequisites")
            for prereq in self._prerequisites:
                lines.append(f"- {prereq}")
            lines.append("")
        
        # Tools
        if self._tools:
            lines.append("## Required Tools")
            for tool in self._tools:
                lines.append(f"- {tool}")
            lines.append("")
        
        # Steps
        if self._steps:
            lines.append("## Process Steps")
            for i, step in enumerate(self._steps, 1):
                lines.append(f"### Step {i}: {step['title']}")
                lines.append(step['description'])
                if step['tools']:
                    lines.append("**Tools needed:**")
                    for tool in step['tools']:
                        lines.append(f"- {tool}")
                lines.append("")
        
        # Outcomes
        if self._outcomes:
            lines.append("## Expected Outcomes")
            for outcome in self._outcomes:
                lines.append(f"- {outcome}")
            lines.append("")
        
        return "\n".join(lines)


class DemoBuilder:
    """High-level builder for creating comprehensive Logseq demos."""
    
    def __init__(self, demo_name: str):
        self._demo_name = demo_name
        self._pages: List[PageBuilder] = []
        self._journal_entries: List[JournalBuilder] = []
        self._demo_config: Dict[str, Any] = {}
    
    def config(self, **settings) -> 'DemoBuilder':
        """Add demo configuration settings."""
        self._demo_config.update(settings)
        return self
    
    def welcome_page(self) -> PageBuilder:
        """Create and add a welcome page."""
        welcome = (PageBuilder(f"Welcome to {self._demo_name}")
                  .author("Demo Generator")
                  .created()
                  .page_type("documentation")
                  .heading(1, f"Welcome to {self._demo_name}! 🎉")
                  .text(f"This demo was generated on {datetime.now().strftime('%Y-%m-%d at %H:%M:%S')}."))
        
        self._pages.append(welcome)
        return welcome
    
    def task_demo_page(self) -> PageBuilder:
        """Create a comprehensive task management demo page."""
        page = (PageBuilder("Task Management Demo")
               .author("Demo Generator")
               .created()
               .page_type("demo")
               .category("productivity")
               .heading(1, "Task Management in Logseq")
               .text("This page demonstrates all task management features available in Logseq.")
               .empty_line()
               .heading(2, "Basic Task States"))
        
        # Add various task examples
        page.add(TaskBuilder("Basic task without any additional metadata").todo())
        page.add(TaskBuilder("Task currently in progress").doing())
        page.add(TaskBuilder("Completed task ✓").done())
        page.add(TaskBuilder("Task postponed for later").later())
        page.add(TaskBuilder("High priority task for immediate attention").now())
        
        page.empty_line().heading(2, "Tasks with Priorities")
        page.add(TaskBuilder("High priority task - most important").todo().high_priority())
        page.add(TaskBuilder("Medium priority task - normal importance").todo().medium_priority())
        page.add(TaskBuilder("Low priority task - when time permits").todo().low_priority())
        
        self._pages.append(page)
        return page
    
    def code_demo_page(self) -> PageBuilder:
        """Create a code examples demo page."""
        page = (PageBuilder("Code Examples Demo")
               .author("Demo Generator")
               .created()
               .page_type("demo")
               .category("development")
               .heading(1, "Code Block Examples")
               .text("This page demonstrates various code block formats.")
               .empty_line())
        
        # Python example
        page.heading(2, "Python Code")
        python_code = (page.code_block("python")
                      .comment("Fibonacci sequence generator")
                      .line("def fibonacci(n):")
                      .line("    if n <= 1:")
                      .line("        return n")
                      .line("    return fibonacci(n-1) + fibonacci(n-2)")
                      .blank_line()
                      .comment("Generate first 10 numbers")
                      .line("for i in range(10):")
                      .line("    print(f'F({i}) = {fibonacci(i)}')")
        )
        
        # JavaScript example
        page.empty_line().heading(2, "JavaScript Code")
        js_code = (page.code_block("javascript")
                  .comment("Async data fetching")
                  .line("const fetchUserData = async (userId) => {")
                  .line("  try {")
                  .line("    const response = await fetch(`/api/users/${userId}`);")
                  .line("    const userData = await response.json();")
                  .line("    return userData;")
                  .line("  } catch (error) {")
                  .line("    console.error('Failed to fetch user data:', error);")
                  .line("    throw error;")
                  .line("  }")
                  .line("};"))
        
        self._pages.append(page)
        return page
    
    def daily_journal(self, date_val: Union[str, date, datetime] = None) -> JournalBuilder:
        """Create a daily journal entry."""
        if date_val is None:
            date_val = datetime.now()
        
        journal = (JournalBuilder(date_val)
                  .daily_note("Started the day with energy and focus")
                  .mood("productive", 8)
                  .weather("sunny", "22°C")
                  .gratitude(
                      "Good health and energy",
                      "Supportive team members",
                      "Interesting projects to work on"
                  )
                  .habit_tracker(
                      exercise=True,
                      meditation=True,
                      reading=False,
                      journaling=True
                  )
                  .work_log(
                      "Reviewed and merged 3 pull requests",
                      "Attended team standup meeting",
                      "Started working on new feature implementation"
                  )
                  .learning_log(
                      "Python Design Patterns",
                      "Learned about the Builder pattern and how to implement fluent interfaces",
                      "Clean Code by Robert Martin"
                  ))
        
        self._journal_entries.append(journal)
        return journal
    
    def project_page(self, name: str, description: str, deadline: Optional[Union[str, date, datetime]] = None) -> PageBuilder:
        """Create a project page."""
        page = (PageBuilder(f"Project: {name}")
               .author("Demo Generator")
               .created()
               .page_type("project")
               .status("active")
               .heading(1, name)
               .text(description)
               .empty_line())
        
        if deadline:
            page.property("deadline", format_date(deadline))
        
        # Add project structure
        page.heading(2, "Goals")
        page.bullet_list(
            "Deliver high-quality solution on time",
            "Meet all specified requirements",
            "Maintain good code quality and documentation"
        )
        
        page.empty_line().heading(2, "Timeline")
        timeline_table = (page.table()
                         .headers("Phase", "Duration", "Status")
                         .row("Planning", "1 week", "✅ Complete")
                         .row("Development", "3 weeks", "🔄 In Progress")
                         .row("Testing", "1 week", "⏳ Pending")
                         .row("Deployment", "2 days", "⏳ Pending"))
        
        page.empty_line().heading(2, "Tasks")
        page.add(TaskBuilder("Define project requirements").done())
        page.add(TaskBuilder("Set up development environment").done())
        page.add(TaskBuilder("Implement core functionality").doing().high_priority())
        page.add(TaskBuilder("Write comprehensive tests").todo().medium_priority())
        page.add(TaskBuilder("Create deployment scripts").todo().low_priority())
        
        self._pages.append(page)
        return page
    
    def build_all(self) -> Dict[str, str]:
        """Build all demo pages and return as dictionary."""
        result = {}
        
        # Build pages
        for page in self._pages:
            page_name = page._title or "Untitled"
            result[page_name] = page.build()
        
        # Build journal entries
        for journal in self._journal_entries:
            journal_name = journal._title or f"journal_{journal._date_str}"
            result[journal_name] = journal.build()
        
        return result
    
    def add_sample_week(self, start_date: Optional[date] = None) -> 'DemoBuilder':
        """Add a week of sample journal entries."""
        if start_date is None:
            start_date = date.today() - timedelta(days=6)  # Start a week ago
        
        activities = [
            ("Monday", "Started new sprint, team planning session"),
            ("Tuesday", "Deep focus on feature implementation"),
            ("Wednesday", "Code review and bug fixes"),
            ("Thursday", "Team standup and client demo"),
            ("Friday", "Documentation and sprint retrospective"),
            ("Saturday", "Personal projects and learning"),
            ("Sunday", "Rest and preparation for next week")
        ]
        
        for i, (day, activity) in enumerate(activities):
            current_date = start_date + timedelta(days=i)
            journal = (JournalBuilder(current_date)
                      .daily_note(f"{day}: {activity}")
                      .mood("focused" if i < 5 else "relaxed", 7 + (i % 3))
                      .work_log(activity))
            self._journal_entries.append(journal)
        
        return self