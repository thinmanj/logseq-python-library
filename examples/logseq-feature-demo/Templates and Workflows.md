- # Templates and Workflows
- Logseq templates help automate repetitive content creation and standardize workflows.
- ## Basic Templates
- ### Daily Note Template
- **Date**: {{date}}
- **Weather**:
- **Mood**: ⭐⭐⭐⭐⭐
- **Goals for Today**:
	-
	-
	-
- **Accomplishments**:
	-
- **Tomorrow's Priority**:
	-
- **Gratitude**:
	-
- **Notes**:
	-
- #daily #journal
- ### Meeting Notes Template
- **Meeting**:
- **Date**: {{date}}
- **Time**: {{time}}
- **Attendees**:
- **Location/Platform**:
- **Agenda**:
	1.
	2.
	3.
- **Discussion Notes**:
	-
- **Decisions Made**:
	-
- **Action Items**:
	[ ]
	[ ]
	[ ]
- **Next Steps**:
	-
- **Next Meeting**:
- #meeting #notes
- ### Project Planning Template
- **Project Name**:
- **Project Lead**:
- **Start Date**: {{date}}
- **Target Completion**:
- **Budget**: $
- **Team Members**:
	-
- **Objectives**:
	-
- **Success Criteria**:
	-
- **Deliverables**:
	[ ]
	[ ]
	[ ]
- **Timeline**:
	**Phase 1** (Dates):
	**Phase 2** (Dates):
	**Phase 3** (Dates):
- **Risks & Mitigation**:
	**Risk**: | **Mitigation**:
- **Resources Needed**:
	-
- **Stakeholders**:
	-
- #project #planning
- ## Workflow Templates
- ### Code Review Template
- **PR/MR Title**:
- **Author**:
- **Reviewer**:
- **Date**: {{date}}
- **Repository**:
- **Branch**:
- **Changes Overview**:
	-
- **Review Checklist**:
	[ ] Code follows style guidelines
	[ ] Functions are well-documented
	[ ] Tests are included and pass
	[ ] No security vulnerabilities
	[ ] Performance considerations addressed
	[ ] Error handling is appropriate
- **Feedback**:
	**Strengths**:
	**Areas for Improvement**:
	**Suggestions**:
- **Decision**: ✅ Approve | 🔄 Request Changes | ❌ Reject
- **Next Steps**:
	-
- #code-review #development
- ### Book/Article Review Template
- **Title**:
- **Author**:
- **Type**: Book | Article | Paper | Video
- **Date Started**: {{date}}
- **Date Completed**:
- **Rating**: ⭐⭐⭐⭐⭐
- **Source/Link**:
- **Categories**:
- **Key Takeaways**:
	-
	-
	-
- **Important Quotes**:
	>
- **Action Items**:
	[ ]
	[ ]
- **Related Resources**:
	-
- **Would Recommend**: Yes | No | Maybe
- **Notes**:
	-
- #reading #review #learning
- ### Problem-Solving Template
- **Problem Statement**:
- **Date Identified**: {{date}}
- **Priority**: Low | Medium | High | Critical
- **Impact**:
- **Root Cause Analysis**:
	**Symptoms**:
	**Potential Causes**:
		-
		-
	**Root Cause**:
- **Solution Options**:
	**Option A**:
		Pros:
		Cons:
		Effort:
	**Option B**:
		Pros:
		Cons:
		Effort:
- **Recommended Solution**:
- **Implementation Plan**:
	[ ] Step 1:
	[ ] Step 2:
	[ ] Step 3:
- **Success Metrics**:
- **Follow-up Date**:
- **Lessons Learned**:
- #problem-solving #analysis
- ## Advanced Template Features
- ### Conditional Content Templates
- {{#if urgent}}
- 🚨 **URGENT MEETING** 🚨
- {{/if}}
- **Meeting Type**: {{meeting-type}}
- {{#if meeting-type == "standup"}}
- **Sprint**: {{sprint-name}}
- **Burn-down**: {{burn-down}}
- {{/if}}
- {{#if meeting-type == "retrospective"}}
- **Sprint Completed**: {{completed-sprint}}
- **What Went Well**:
- **What Could Improve**:
- **Action Items**:
- {{/if}}
- ### Dynamic Date Templates
- **Week of**: {{date:YYYY-MM-DD}} to {{date+7d:YYYY-MM-DD}}
- **Week Number**: {{date:WW}}
- **Month**: {{date:MMMM YYYY}}
- ### Variable Substitution Templates
- **Project**: {{project-name}}
- **Status Update**: {{date:MMMM Do, YYYY}}
- **Progress**: {{progress-percent}}% complete
- **Budget Used**: ${{budget-used}} of ${{total-budget}}
- **Team**: {{team-members}}
- ## Workflow Automation
- ### Task Creation Workflows
- When creating a task with high priority:
- Automatically add to [[High Priority Tasks]] page
- Set reminder for tomorrow
- Notify relevant team members
- Add to current sprint if in development context
- ### Content Publishing Workflow
- For blog posts and articles:
- Draft → [[Content Drafts]]
- Review → [[Content Review Queue]]
- Edit → [[Content Editing]]
- Publish → [[Published Content]]
- Promote → [[Content Marketing]]
- ### Meeting Follow-up Workflow
- After every meeting:
- Extract action items automatically
- Create individual task blocks for each action item
- Assign to responsible parties
- Set due dates based on meeting context
- Add to project backlogs if applicable
- ## Template Management
- ### Template Organization
- **Daily Templates**: Daily notes, standups, check-ins
- **Meeting Templates**: Various meeting types and contexts
- **Project Templates**: Planning, status, retrospectives
- **Content Templates**: Writing, reviewing, publishing
- **Personal Templates**: Habits, goals, reflections
- ### Template Versioning
- Keep track of template changes:
- v1.0: Initial meeting template
- v1.1: Added action items section
- v1.2: Enhanced with stakeholder tracking
- v2.0: Major restructure for better workflow
- ### Template Sharing
- Share templates across teams:
- Export template definitions
- Create template libraries
- Document template usage guidelines
- Train team members on template adoption
- ---
- *Use templates to standardize processes and accelerate content creation!*
- #templates #workflows #automation #productivity #standards