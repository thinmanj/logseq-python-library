- # Tables and Media via DSL
- This page demonstrates structured content using TableBuilder and MediaBuilder.
- ## Project Timeline Table
- | Phase | Duration | Status | Owner |
- |---|:---:|:---:|---|
- | Planning | 1 week | ✅ Complete | Alice |
- | Development | 3 weeks | 🔄 In Progress | Bob |
- | Testing | 1 week | ⏳ Pending | Charlie |
- | Deployment | 2 days | ⏳ Pending | Diana |
- ## Feature Comparison Table
- | Feature | Basic Plan | Pro Plan | Enterprise |
- |---|:---:|:---:|:---:|
- | Storage | 10 GB | 100 GB | Unlimited |
- | Users | 5 | 50 | Unlimited |
- | Support | Email | Email + Chat | 24/7 Phone |
- | Price/month | $10 | $50 | $200 |
- ## Media Embeds
- Media embeds using MediaBuilder:
- ![Logseq Logo](https://logseq.com/logo.png "Official Logseq Logo")
- {{video https://www.youtube.com/watch?v=dQw4w9WgXcQ}}
- {{pdf https://example.com/document.pdf#1}}
- ## Builder Code
- Tables and media were created using:
- ```python
# Create table with headers and alignment
table = (page.table()
        .headers('Phase', 'Duration', 'Status', 'Owner')
        .alignment('left', 'center', 'center', 'left')
        .row('Planning', '1 week', '✅ Complete', 'Alice')
        .row('Development', '3 weeks', '🔄 In Progress', 'Bob'))

# Add various media types
media = (page.media()
        .image('https://example.com/logo.png', 'Logo')
        .youtube('https://youtube.com/watch?v=...')
        .pdf('https://example.com/doc.pdf', page=1))
```