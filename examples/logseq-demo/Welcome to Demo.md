- # Welcome to the Logseq Demo! 🎉
- This demo was generated on 2025-10-13 at 23:57:06 using the **Logseq Builder DSL**.
- ## What's New in This Demo
- 🏗️ **Type-safe content creation** - No more string templates!
- 🎯 **Fluent interface** - Readable and intuitive code
- 🧩 **Modular building blocks** - Compose complex content easily
- 🔍 **Complete feature coverage** - Every Logseq feature demonstrated
- ⚡ **Zero hardcoded strings** - Everything built programmatically
- ## Demo Pages
- Explore these demonstration pages:
- [[Task Management Demo]] - Programmatic task creation
- [[Block Types Showcase]] - All content types via builders
- [[Code Examples Demo]] - Language-aware code blocks
- [[Math Examples Demo]] - LaTeX math expressions
- [[Tables and Media Demo]] - Structured content
- [[Query Examples Demo]] - Dynamic content queries
- [[Workflow Demo]] - Process documentation
- ## Builder Usage Example
- Here's how this page was created:
- ```python
welcome = (PageBuilder('Welcome to Demo')
          .author('Demo Generator')
          .created()
          .heading(1, 'Welcome to the Logseq Demo! 🎉')
          .paragraph('This demo was generated...')
          .bullet_list(
              '🏗️ Type-safe content creation',
              '🎯 Fluent interface',
              '🧩 Modular building blocks'
          ))
```
- ---
- *Generated with the Logseq Builder DSL - no strings attached!* 🚀