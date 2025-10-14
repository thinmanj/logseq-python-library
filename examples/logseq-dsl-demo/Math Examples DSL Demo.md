- # Mathematical Expressions via DSL
- This page demonstrates LaTeX math generation using MathBuilder.
- ## Inline Math
- $x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a}$
- The quadratic formula is $x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a}$
- ## Block Math Expressions
- $$
- E = mc^2
- $$
- $$
- \int_{-\infty}^{\infty} e^{-x^2}  = \sqrt{\pi}
- $$
- ## Maxwell's Equations
- $$
- \begin{align} \nabla \cdot \mathbf{E} &= \frac{\rho}{\epsilon_0} \\ \nabla \times \mathbf{E} &= -\frac{\partial \mathbf{B}}{\partial t} \\ \nabla \cdot \mathbf{B} &= 0 \\ \nabla \times \mathbf{B} &= \mu_0\mathbf{J} + \mu_0\epsilon_0\frac{\partial \mathbf{E}}{\partial t} \end{align}
- $$
- ## Builder Usage
- Mathematical expressions were created using:
- ```python
- # Inline math
- inline_math = page.math(inline=True).expression('x = \\frac{-b \\pm \\sqrt{b^2 - 4ac}}{2a}')
- # Block math with integrals
- gaussian = (page.math()
	.integral('e^{-x^2}', '-\\infty', '\\infty')
		.expression(' = \\sqrt{\\pi}'))
- # Complex multi-line expressions
- maxwell = (page.math()
	.expression('\\begin{align}')
		.expression('\\nabla \\cdot \\mathbf{E} &= \\frac{\\rho}{\\epsilon_0}')
			.expression('\\end{align}'))
- ```