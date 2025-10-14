- # Logseq Block Types Showcase
- This page demonstrates every type of block supported in Logseq.
- ## Text Formatting Blocks
- ### Basic Text Block
- This is a standard bullet point block. It's the default block type in Logseq.
- Nested bullet point
	Deeply nested bullet point
		Even deeper nesting
- ### Numbered Lists
- First numbered item
- Second numbered item
- Third numbered item
	Nested numbered item
	Another nested item
- ## Heading Blocks
- # Heading Level 1
- ## Heading Level 2
- ### Heading Level 3
- #### Heading Level 4
- ##### Heading Level 5
- ###### Heading Level 6
- ## Code Blocks
- ### Python Code
- ```python
- def fibonacci(n):
	if n <= 1:
		return n
		return fibonacci(n-1) + fibonacci(n-2)
- # Generate first 10 Fibonacci numbers
- for i in range(10):
	print(f"F({i}) = {fibonacci(i)}")
- ```
- ### JavaScript Code
- ```javascript
- const fetchUserData = async (userId) => {
	try {
		const response = await fetch(`/api/users/${userId}`);
		const userData = await response.json();
		return userData;
	} catch (error) {
		console.error('Failed to fetch user data:', error);
		throw error;
	}
- };
- ```
- ### SQL Code
- ```sql
- SELECT u.name, u.email, COUNT(o.id) as order_count
- FROM users u
- LEFT JOIN orders o ON u.id = o.user_id
- WHERE u.created_at >= '2024-01-01'
- GROUP BY u.id, u.name, u.email
- ORDER BY order_count DESC
- LIMIT 10;
- ```
- ### Shell/Terminal Code
- ```bash
- #!/bin/bash
- # Deploy application script
- echo "Starting deployment..."
- # Build the application
- npm run build
- # Upload to server
- rsync -av dist/ user@server:/var/www/app/
- # Restart services
- ssh user@server 'sudo systemctl restart nginx'
- echo "Deployment completed successfully!"
- ```
- ## Mathematical Expressions
- ### Inline Math
- The quadratic formula is $x = rac{-b \pm \sqrt{b^2 - 4ac}}{2a}$
- ### Block Math Expressions
- $$
- E = mc^2
- $$
- $$
- \int_{-\infty}^{\infty} e^{-x^2} dx = \sqrt{\pi}
- $$
- $$
- egin{align}
- abla \cdot \mathbf{E} &= rac{ho}{\epsilon_0} \
- abla 	imes \mathbf{E} &= -rac{\partial \mathbf{B}}{\partial t} \
- abla \cdot \mathbf{B} &= 0 \
- abla 	imes \mathbf{B} &= \mu_0\mathbf{J} + \mu_0\epsilon_0rac{\partial \mathbf{E}}{\partial t}
- \end{align}
- $$
- ## Quote Blocks
- > This is a blockquote demonstrating how to highlight important text or citations.
- >
- > Blockquotes can span multiple lines and are great for:
- > - Highlighting key insights
- > - Citing external sources
- > - Creating visual emphasis
- > "The best way to predict the future is to create it." — Peter Drucker
- ## Advanced Block Types
- ### Collapsible/Toggle Blocks
- #### Click to expand: Project Details
- Project timeline: 3 months
- Budget allocation: $50,000
- Team members: 5 developers, 2 designers
- Key milestones:
	Month 1: Requirements and design
	Month 2: Development and testing
	Month 3: Deployment and optimization
- ### Tables
- | Feature | Basic Plan | Pro Plan | Enterprise |
- |---------|------------|----------|------------|
- | Storage | 10 GB | 100 GB | Unlimited |
- | Users | 5 | 50 | Unlimited |
- | Support | Email | Email + Chat | 24/7 Phone |
- | Price/month | $10 | $50 | $200 |
- ### Embedded Media
- #### YouTube Video Embed
- {{video https://www.youtube.com/watch?v=dQw4w9WgXcQ}}
- #### Twitter Tweet Embed
- {{twitter https://twitter.com/logseq/status/1234567890}}
- #### External Image
- ![Logseq Logo](https://logseq.com/logo.png)
- ### Drawing/Whiteboard Blocks
- {{drawing 123abc}}
- *Note: Drawing blocks require the Logseq app to create and edit*
- ## Interactive Elements
- ### Checkbox Lists
- [x] Completed task item
- [x] Another completed item
- [ ] Pending task item
- [ ] Another pending item
- ### Flash Cards
- #card
- #card
- ## Metadata and Property Blocks
- ### Block with Properties
- This block has custom properties attached
- :PROPERTIES:
- :CREATED: 2025-01-08
- :AUTHOR: Demo Generator
- :CATEGORY: Documentation
- :IMPORTANCE: High
- :END:
- ### Template Blocks
- **Date**: {{date}}
- **Attendees**:
- **Agenda**:
	-
- **Action Items**:
	-
- **Next Meeting**:
- ## Special Syntax Blocks
- ### Hiccup (HTML-like) Syntax
- [:div {:style {:background-color "#f0f8ff" :padding "10px" :border-radius "5px"}}
- [:h3 "Custom Styled Content"]
- [:p "This demonstrates Hiccup syntax for custom HTML elements"]]
- ### Query Blocks
- {{query (and (property type "meeting") (between -7d today))}}
- {{query (and [[project]] (task TODO DOING))}}
- ---
- *This showcase demonstrates the rich variety of content types you can create in Logseq!*
- #blocks #formatting #code #math #demo #reference