- # Workflow Documentation via DSL
- This page demonstrates process documentation using WorkflowBuilder.
- # Code Review Process Workflow
- ## Prerequisites
- Pull request submitted
- All tests passing
- Code coverage meets threshold
- ## Required Tools
- GitHub/GitLab
- CI/CD pipeline
- Code analysis tools
- ## Process Steps
- ### Step 1: Initial Review
- Automated checks run and reviewer is assigned
- **Tools needed:**
- GitHub Actions
- Linting tools
- ### Step 2: Code Analysis
- Reviewer examines code for logic, style, and best practices
- **Tools needed:**
- IDE
- Code review checklist
- ### Step 3: Feedback & Discussion
- Comments are added and discussion happens
- **Tools needed:**
- GitHub comments
- Slack/Teams
- ### Step 4: Approval & Merge
- Code is approved and merged to main branch
- **Tools needed:**
- Git
- Deployment tools
- ## Expected Outcomes
- High-quality code in production
- Knowledge sharing among team
- Consistent coding standards
- ## Builder Usage
- The workflow above was created using:
- ```python
workflow = (WorkflowBuilder('Code Review Process')
           .prerequisite('Pull request submitted')
           .prerequisite('All tests passing')

           .tool('GitHub/GitLab')
           .tool('CI/CD pipeline')

           .step('Initial Review',
                'Automated checks run and reviewer assigned',
                ['GitHub Actions', 'Linting tools'])

           .step('Code Analysis',
                'Reviewer examines code for quality')

           .outcome('High-quality code in production')
           .outcome('Knowledge sharing among team'))
```