- # Code Block Examples via DSL
- This page demonstrates language-aware code generation using CodeBlockBuilder.
- ## Python Code with Comments
- ```python
# Fibonacci sequence generator with memoization
def fibonacci(n, memo={}):
    if n in memo:
        return memo[n]
    if n <= 1:
        return n

    memo[n] = fibonacci(n-1, memo) + fibonacci(n-2, memo)
    return memo[n]

# Generate and display first 10 numbers
for i in range(10):
    print(f'F({i}) = {fibonacci(i)}')
```
- ## JavaScript with Async/Await
- ```javascript
// Modern API fetching with error handling
const fetchUserData = async (userId) => {
  try {
    const response = await fetch(`/api/users/${userId}`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const userData = await response.json();
    return userData;
  } catch (error) {
    console.error('Failed to fetch user data:', error);
    throw error;
  }
};
```
- ## SQL Query
- ```sql
-- Complex query with joins and aggregation
SELECT 
    u.name,
    u.email,
    COUNT(o.id) as order_count,
    AVG(o.total_amount) as avg_order_value
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
WHERE u.created_at >= '2024-01-01'
GROUP BY u.id, u.name, u.email
HAVING COUNT(o.id) > 0
ORDER BY order_count DESC, avg_order_value DESC
LIMIT 10;
```
- ## Builder Code Example
- The code blocks above were generated using:
- ```python
# Language-aware code generation
python_code = (page.code_block('python')
              .comment('Fibonacci sequence generator')
              .line('def fibonacci(n, memo={}):') 
              .line('    if n in memo:')
              .line('        return memo[n]')
              .blank_line())

# Automatic comment formatting per language
js_code = (page.code_block('javascript')
          .comment('Modern API fetching')  # Uses // comments
          .line('const fetchUserData = async (userId) => {'))
```