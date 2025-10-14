author:: DSL Demo
created:: 2025-10-13
type:: example
tags:: dsl, demo, builders

# Welcome to the DSL!
This page demonstrates the new builder patterns.

## Task Management
Tasks created with TaskBuilder:
TODO [#A] Learn the new DSL
DOING [#B] Create example content
:PROPERTIES:
:EFFORT: 2hh
:END:
TODO [#C] Share with the team @email

## Code Example
```python
# Example of using the DSL
page = (PageBuilder('My Page')
       .author('Me')
       .heading(1, 'Hello World!')
       .text('Content here'))

task = TaskBuilder('Do something').todo().high_priority()
page.add(task)
```

## Quote Example
> The best way to predict the future is to create it.
> — Peter Drucker

## Table Example
| Feature | Status | Priority |
|---|---|---|
| Core DSL | ✅ Complete | High |
| Advanced Features | 🔄 In Progress | Medium |
| Documentation | 📝 Planned | Low |

---

*Generated with the Logseq Builder DSL!* 🚀