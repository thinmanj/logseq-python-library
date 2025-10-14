- # Page Properties and Metadata via DSL
- This page demonstrates property management using PropertyBuilder.
- ## This Page's Properties
- The properties above were set using:
- ```python
- page = (PageBuilder('Page Properties DSL Demo')
	.author('DSL Demo Generator')
		.created()
			.page_type('documentation')
			.category('demo')
			.status('complete')
			.tags('properties', 'metadata', 'configuration')
			.property('version', '1.0.0')
			.property('complexity', 'intermediate'))
- ```
- ## Property Usage Patterns
- **.author()** - Set page author
- **.created()** - Set creation date (defaults to now)
- **.page_type()** - Set semantic page type
- **.tags()** - Add multiple tags at once
- **.property()** - Add custom key-value properties
- **.status()**, **.category()**, **.priority()** - Common properties