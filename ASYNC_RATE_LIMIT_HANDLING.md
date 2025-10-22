### Async Rate Limit Handling System

## Overview

The async queue system intelligently handles HTTP 429 rate limit errors by queuing tasks, extracting retry-after information, and processing other content while waiting for rate-limited resources.

## Architecture

### Components

1. **AsyncRateLimitedQueue** (`async_queue.py`)
   - Priority-based task queuing
   - Automatic rate limit detection
   - Retry-After header parsing
   - Concurrent worker management

2. **AsyncComprehensiveContentProcessor** (`async_comprehensive_processor.py`)
   - Extends base comprehensive processor
   - Queues content by type and priority
   - Waits for all tasks before updating files
   - Falls back to sync mode if disabled

### How It Works

```
[Content Blocks] → [Queue by Type/Priority] → [Workers Process Concurrently]
                                                       ↓
                                          [Rate Limit Detection]
                                                       ↓
                                          [Re-queue with Delay]
                                                       ↓
                                          [Wait for All] → [Update Files]
```

## Features

### 1. Intelligent Rate Limit Detection

```python
# Detects rate limit errors automatically
if '429' in error or 'too many requests' in error:
    extract_retry_after(error)  # Parse delay from error message
    queue_task_with_delay(task)  # Re-queue with proper timing
```

### 2. Retry-After Header Parsing

```python
# Extracts delay from error messages:
"HTTP 429: Too Many Requests. Retry-After: 60"  → 60 seconds
"Rate limit exceeded, wait 120 seconds"          → 120 seconds
"YouTube is blocking requests"                   → 60 seconds (default)
```

### 3. Priority-Based Processing

```python
TaskPriority.HIGH    # Videos (subtitle extraction is time-sensitive)
TaskPriority.NORMAL  # Twitter posts
TaskPriority.LOW     # PDF documents
```

### 4. Concurrent Processing

While waiting for rate-limited resources, the system processes other content types:

```
Time 0s:   Start 10 video tasks
Time 5s:   Videos hit rate limit (wait 60s)
Time 5s:   Switch to Twitter tasks (continue working)
Time 30s:  Process PDF tasks
Time 65s:  Resume video processing
```

## Usage

### Basic Usage

```python
from logseq_py.pipeline.async_comprehensive_processor import AsyncComprehensiveContentProcessor

config = {
    'enable_async': True,
    'max_concurrent': 10,
    'retry_delay': 60,
    'max_queue_size': 1000
}

processor = AsyncComprehensiveContentProcessor('/path/to/graph', config)
results = processor.run()  # Automatically uses async
```

### Configuration Options

```python
config = {
    # Async settings
    'enable_async': True,           # Enable async processing
    'max_concurrent': 10,            # Max concurrent tasks
    'retry_delay': 60,               # Default retry delay (seconds)
    'max_queue_size': 1000,          # Max tasks in queue
    
    # Existing settings still work
    'dry_run': False,
    'youtube_api_key': None,
    'process_videos': True,
    'process_twitter': True,
    'process_pdfs': True
}
```

### Direct Async API

```python
import asyncio
from logseq_py.pipeline.async_comprehensive_processor import process_graph_async

async def main():
    results = await process_graph_async('/path/to/graph', config)
    print(f"Completed: {results['async_stats']['completed']}")
    print(f"Rate limited: {results['async_stats']['rate_limited']}")
    print(f"Retried: {results['async_stats']['retried']}")

asyncio.run(main())
```

## Rate Limit Handling Flow

### Step 1: Task Queuing

```python
# Content scanned and queued by priority
await queue.add_task(
    task_id="video_12345",
    task_type="video",
    func=process_video,
    priority=TaskPriority.HIGH,
    max_retries=3
)
```

### Step 2: Worker Processing

```python
# 10 workers process tasks concurrently
# Worker 1: Processing video (subtitle extraction)
# Worker 2: Processing Twitter post
# Worker 3: Processing PDF
# ... etc
```

### Step 3: Rate Limit Detection

```python
try:
    result = await extract_subtitles(video_url)
except Exception as e:
    if is_rate_limit_error(e):
        # Extract retry delay
        retry_after = extract_retry_after(e)  # 60 seconds
        task.retry_after = now() + timedelta(seconds=retry_after)
        
        # Mark resource as rate-limited
        rate_limits['subtitle'].is_limited = True
        rate_limits['subtitle'].retry_after = retry_after
        
        # Re-queue task
        await queue.put(task)
```

### Step 4: Smart Re-queuing

```python
async def get_next_task():
    for priority in [HIGH, NORMAL, LOW]:
        task = await queue.get()
        
        # Check if task should wait
        if task.should_wait():
            await queue.put(task)  # Put back
            continue
        
        # Check if resource is rate-limited
        if rate_limits[task.type].should_wait():
            await queue.put(task)  # Put back
            await asyncio.sleep(1)  # Wait a bit
            continue
        
        return task  # This task is ready
```

### Step 5: Concurrent Processing

```python
# While subtitle extraction is rate-limited (60s wait)
# Process other content types:
- Process 20 Twitter posts (30s)
- Process 5 PDFs (25s)
- Check if subtitles can resume (5s remaining)
- Resume subtitle extraction (60s elapsed)
```

### Step 6: Wait for Completion

```python
# All tasks complete (or failed after max retries)
await queue.wait_completion()

# Now safe to update files
for page_name, updates in pending_updates.items():
    update_page_file(page_name, updates)
```

## Statistics and Monitoring

### Async Stats

```python
results = processor.run()

print(results['async_stats'])
# {
#     'total_tasks': 150,
#     'completed': 145,
#     'failed': 2,
#     'rate_limited': 45,  # Times rate limit was hit
#     'retried': 48        # Successful retries
# }
```

### Per-Task Status

```python
# Check individual task status
for task in results['completed_tasks']:
    print(f"{task.task_id}: {task.status.value}")
    print(f"  Retries: {task.retry_count}")
    print(f"  Duration: {task.completed_at - task.created_at}")
```

## Best Practices

### 1. Start with Reasonable Concurrency

```python
# For first-time processing large graphs
config = {'max_concurrent': 5}  # Conservative

# For incremental updates
config = {'max_concurrent': 15}  # More aggressive
```

### 2. Monitor Rate Limiting

```python
if results['async_stats']['rate_limited'] > 10:
    print("High rate limiting detected")
    print("Consider:")
    print("- Reducing max_concurrent")
    print("- Increasing retry_delay")
    print("- Using YouTube API key")
```

### 3. Process in Batches

```python
# Instead of processing entire graph at once
# Process by date range or tags

config = {
    'enable_async': True,
    'max_concurrent': 10,
    # Add custom filters in your code
}
```

### 4. Graceful Degradation

```python
# System continues even with rate limits
# Failed tasks after max retries are reported
# Partial success is better than complete failure

if results['success']:
    completed = results['async_stats']['completed']
    failed = results['async_stats']['failed']
    print(f"Processed {completed}/{completed+failed} items")
```

## Comparison: Sync vs Async

### Synchronous Processing (Old)

```
Video 1 → Rate Limited → STOP (60s wait)
          ↓
          All processing paused
          ↓
After 60s: Resume Video 1
Video 2 → Rate Limited → STOP (60s wait)
...
Total Time: ~10 minutes for 10 videos
```

### Asynchronous Processing (New)

```
Video 1, 2, 3 (parallel)  → Video 1 rate limited
  ↓                            ↓
Continue with Video 2, 3    Queue Video 1 (60s)
  ↓                            ↓
Process Twitter 1-10        Resume Video 1 after 60s
  ↓                            ↓
Process PDF 1-5             All done!
  ↓
Total Time: ~2 minutes for 10 videos + 10 Twitter + 5 PDFs
```

**Speedup**: 5-10x faster for mixed content with rate limits

## Troubleshooting

### Issue: All tasks failing immediately

```python
# Check if enable_async is True
config = {'enable_async': True}

# Check logs for error patterns
logging.basicConfig(level=logging.DEBUG)
```

### Issue: Tasks stuck in queue

```python
# Increase worker count
config = {'max_concurrent': 20}

# Check for deadlocks in task dependencies
# (Tasks should be independent)
```

### Issue: Too many retries

```python
# Increase retry delay
config = {'retry_delay': 120}  # 2 minutes

# Reduce concurrent requests
config = {'max_concurrent': 5}
```

### Issue: Memory usage high

```python
# Reduce queue size
config = {'max_queue_size': 500}

# Process in smaller batches
# (Split graph into sections)
```

## Technical Details

### Rate Limit Information Storage

```python
@dataclass
class RateLimitInfo:
    resource: str              # 'video', 'twitter', 'pdf'
    is_limited: bool          # Currently rate-limited?
    retry_after: datetime     # When can we retry?
    request_count: int        # Total requests made
    last_request: datetime    # Last request time
```

### Task Status Lifecycle

```
PENDING → PROCESSING → COMPLETED
   ↓           ↓
   ↓      RATE_LIMITED → (back to PENDING with delay)
   ↓           ↓
   ↓      retry_count++
   ↓           ↓
   ↓      (retry until max_retries)
   ↓           ↓
   └──────→ FAILED
```

### Concurrency Model

- **Workers**: Independent coroutines that pull tasks from queue
- **Queue**: Priority-based (HIGH → NORMAL → LOW)
- **Executor**: Thread pool for CPU-bound operations
- **Event Loop**: Manages all async operations

## Future Enhancements

Potential improvements:

1. **Adaptive concurrency**: Automatically adjust based on rate limit frequency
2. **Resource pooling**: Share rate limit info across processor instances
3. **Persistent queue**: Save queue state to resume after crashes
4. **Real-time monitoring**: WebSocket API for live progress updates
5. **Distributed processing**: Process across multiple machines

## Related Files

- `logseq_py/pipeline/async_queue.py` - Queue implementation
- `logseq_py/pipeline/async_comprehensive_processor.py` - Async processor
- `logseq_py/pipeline/comprehensive_processor.py` - Base processor
- `SUBTITLE_EXTRACTION.md` - Subtitle rate limiting details
