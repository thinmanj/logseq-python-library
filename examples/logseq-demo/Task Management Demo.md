- # Task Management with DSL Builders
- This page demonstrates programmatic task creation using the TaskBuilder DSL.
- ## Basic Task States
- Created using fluent TaskBuilder interface:
- TODO Basic task without any additional metadata
- DOING Task currently in progress
- DONE Completed task ✓
- LATER Task postponed for later
- NOW High priority task for immediate attention
- WAITING Task waiting for external dependency
- CANCELLED Task that was cancelled
- DELEGATED Task assigned to someone else
- ## Tasks with Priorities
- [#A] TODO High priority task - most important
- [#B] TODO Medium priority task - normal importance
- [#C] TODO Low priority task - when time permits
- [#A] DOING Critical task in progress right now
- [#A] DONE Completed high priority task ✓
- ## Scheduled and Deadline Tasks
- TODO Review quarterly reports
- SCHEDULED: <2025-01-15>
- :PROPERTIES:
- :EFFORT: 2h
- :END:
- [#A] TODO Submit project proposal
- DEADLINE: <2025-01-20>
- :PROPERTIES:
- :ASSIGNED: John Doe
- :END:
- TODO Weekly team meeting
- SCHEDULED: <2025-01-08>
- :PROPERTIES:
- :REPEAT: Weekly
- :END:
- ## GTD-Style Context Tasks
- [#B] TODO Call client about project requirements @phone @office
- TODO Buy groceries after work @errands @car
- TODO Read research papers @home @evening @lowenergy
- TODO Review code changes @computer @focused
- :PROPERTIES:
- :EFFORT: 1hh
- :END:
- ## Project Tasks with Properties
- [#A] TODO Implement new feature #development #frontend
- :PROPERTIES:
- :PROJECT: WebApp Redesign
- :EFFORT: 4hh
- :ASSIGNED: Alice Johnson
- :END:
- DOING Code review for PR #123 @computer
- :PROPERTIES:
- :EFFORT: 1hh
- :URGENCY: High
- :COMPLEXITY: Medium
- :END:
- ## Hierarchical Task Organization
- Example of nested task structure using custom blocks:
- [#A] 📋 **Project: Website Redesign**\n  - 🎨 Frontend Development\n    - TODO Design new homepage layout \n    - DOING Implement responsive navigation \n    - TODO Add dark mode support \n  - ⚙️ Backend Development\n    - TODO Upgrade database schema \n    - TODO Implement new API endpoints \n    - DONE Set up automated testing  ✓\n  - 🧪 Testing & QA\n    - TODO Write unit tests for new features \n    - TODO Perform cross-browser testing \n    - TODO Load testing with realistic data
- ## Builder Code Example
- The tasks above were created using code like this:
- ```python
# Create a high-priority task with scheduling and context
task = (TaskBuilder('Review quarterly reports')
        .todo()
        .scheduled('2025-01-15')
        .effort(2)
        .high_priority()
        .context('office', 'computer')
        .tag('review', 'quarterly'))

# Add to page
page.add(task)
```