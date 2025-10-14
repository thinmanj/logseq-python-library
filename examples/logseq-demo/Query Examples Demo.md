- # Dynamic Queries via DSL
- This page demonstrates dynamic content queries using QueryBuilder.
- ## Task Queries
- All TODO tasks:
- {{query (task TODO)}}
- High priority tasks (TODO or DOING):
- {{query (and (or (task TODO) (task DOING)) (property priority "A"))}}
- ## Date-based Queries
- Tasks from this week:
- {{query (and (or (task TODO) (task DONE)) (between -7d today))}}
- Items from last 30 days:
- {{query (between -30d today)}}
- ## Property-based Queries
- Demo pages:
- {{query (property type "demo")}}
- Pages by specific author:
- {{query (property author "Demo Generator")}}
- ## Complex Combined Queries
- Demo pages created this month:
- {{query (and (property type "demo") (property author "Demo Generator") (between -30d today))}}
- ## Builder Usage
- Queries above were created using:
- ```python
# Simple task query
todo_query = DSLQueryBuilder().todo()

# Complex combined query
complex_query = (DSLQueryBuilder()
                .and_query()
                .property('type', 'demo')
                .property('author', 'Demo Generator')
                .this_month())

# Add to page
page.text(complex_query.build())
```