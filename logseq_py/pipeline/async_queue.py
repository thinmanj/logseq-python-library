"""
Async Queue System for Rate-Limited API Requests

Handles HTTP 429 responses with intelligent retry logic, respects Retry-After headers,
and manages concurrent processing while waiting for rate-limited resources.
"""

import asyncio
import logging
from typing import Dict, Any, Optional, Callable, Awaitable, List, TypeVar, Generic
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import time


T = TypeVar('T')


class TaskPriority(Enum):
    """Priority levels for queued tasks."""
    HIGH = 1
    NORMAL = 2
    LOW = 3


class TaskStatus(Enum):
    """Status of a queued task."""
    PENDING = "pending"
    PROCESSING = "processing"
    RATE_LIMITED = "rate_limited"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class QueuedTask(Generic[T]):
    """Represents a task in the processing queue."""
    
    task_id: str
    task_type: str  # 'video', 'twitter', 'pdf', 'subtitle'
    func: Callable[..., Awaitable[T]]
    args: tuple = field(default_factory=tuple)
    kwargs: Dict[str, Any] = field(default_factory=dict)
    priority: TaskPriority = TaskPriority.NORMAL
    status: TaskStatus = TaskStatus.PENDING
    retry_count: int = 0
    max_retries: int = 3
    retry_after: Optional[datetime] = None
    result: Optional[T] = None
    error: Optional[Exception] = None
    created_at: datetime = field(default_factory=datetime.now)
    
    def can_retry(self) -> bool:
        """Check if task can be retried."""
        return self.retry_count < self.max_retries
    
    def should_wait(self) -> bool:
        """Check if task should wait before retry."""
        if self.retry_after is None:
            return False
        return datetime.now() < self.retry_after


@dataclass
class RateLimitInfo:
    """Information about rate limiting for a resource."""
    
    resource: str  # 'youtube_subtitle', 'twitter_api', etc.
    is_limited: bool = False
    retry_after: Optional[datetime] = None
    request_count: int = 0
    last_request: Optional[datetime] = None
    
    def should_wait(self) -> bool:
        """Check if we should wait before making a request."""
        if not self.is_limited:
            return False
        if self.retry_after is None:
            return False
        return datetime.now() < self.retry_after
    
    def get_wait_time(self) -> float:
        """Get seconds to wait before next request."""
        if not self.should_wait():
            return 0.0
        delta = self.retry_after - datetime.now()
        return max(0.0, delta.total_seconds())


class AsyncRateLimitedQueue:
    """
    Async queue that handles rate-limited API requests intelligently.
    
    Features:
    - Parses Retry-After headers from HTTP 429 responses
    - Queues tasks by type and priority
    - Processes tasks concurrently while respecting rate limits
    - Automatically retries failed tasks
    - Collects all results before returning
    """
    
    def __init__(
        self,
        max_concurrent: int = 10,
        default_retry_delay: int = 60,
        max_queue_size: int = 1000
    ):
        """Initialize the async queue.
        
        Args:
            max_concurrent: Maximum number of concurrent tasks
            default_retry_delay: Default delay (seconds) when Retry-After not specified
            max_queue_size: Maximum queue size (prevents memory issues)
        """
        self.max_concurrent = max_concurrent
        self.default_retry_delay = default_retry_delay
        self.max_queue_size = max_queue_size
        
        self.logger = logging.getLogger(__name__)
        
        # Task queues by priority
        self.queues: Dict[TaskPriority, asyncio.Queue] = {
            TaskPriority.HIGH: asyncio.Queue(maxsize=max_queue_size),
            TaskPriority.NORMAL: asyncio.Queue(maxsize=max_queue_size),
            TaskPriority.LOW: asyncio.Queue(maxsize=max_queue_size)
        }
        
        # Rate limit tracking per resource
        self.rate_limits: Dict[str, RateLimitInfo] = {}
        
        # Task tracking
        self.tasks: Dict[str, QueuedTask] = {}
        self.completed_tasks: List[QueuedTask] = []
        
        # Worker control
        self.workers: List[asyncio.Task] = []
        self.is_running = False
        
        # Statistics
        self.stats = {
            'total_tasks': 0,
            'completed': 0,
            'failed': 0,
            'rate_limited': 0,
            'retried': 0
        }
    
    async def add_task(
        self,
        task_id: str,
        task_type: str,
        func: Callable[..., Awaitable[T]],
        *args,
        priority: TaskPriority = TaskPriority.NORMAL,
        max_retries: int = 3,
        **kwargs
    ) -> QueuedTask[T]:
        """Add a task to the queue.
        
        Args:
            task_id: Unique identifier for the task
            task_type: Type of task ('video', 'twitter', 'pdf', 'subtitle')
            func: Async function to execute
            *args: Positional arguments for func
            priority: Task priority level
            max_retries: Maximum retry attempts
            **kwargs: Keyword arguments for func
            
        Returns:
            QueuedTask object for tracking
        """
        task = QueuedTask(
            task_id=task_id,
            task_type=task_type,
            func=func,
            args=args,
            kwargs=kwargs,
            priority=priority,
            max_retries=max_retries
        )
        
        self.tasks[task_id] = task
        await self.queues[priority].put(task)
        self.stats['total_tasks'] += 1
        
        self.logger.debug(f"Added task {task_id} ({task_type}) with priority {priority.name}")
        return task
    
    async def start_workers(self, num_workers: Optional[int] = None):
        """Start worker tasks to process the queue.
        
        Args:
            num_workers: Number of workers (defaults to max_concurrent)
        """
        if self.is_running:
            self.logger.warning("Workers already running")
            return
        
        self.is_running = True
        num_workers = num_workers or self.max_concurrent
        
        self.logger.info(f"Starting {num_workers} worker tasks")
        
        for i in range(num_workers):
            worker = asyncio.create_task(self._worker(i))
            self.workers.append(worker)
    
    async def wait_completion(self) -> Dict[str, Any]:
        """Wait for all tasks to complete and return results.
        
        Returns:
            Dictionary with completion statistics and results
        """
        # Wait for all queues to be empty
        for priority_queue in self.queues.values():
            await priority_queue.join()
        
        # Stop workers
        self.is_running = False
        
        # Wait for workers to finish
        if self.workers:
            await asyncio.gather(*self.workers, return_exceptions=True)
            self.workers.clear()
        
        self.logger.info(f"All tasks completed: {self.stats}")
        
        return {
            'stats': self.stats.copy(),
            'completed_tasks': self.completed_tasks.copy(),
            'failed_tasks': [t for t in self.tasks.values() if t.status == TaskStatus.FAILED]
        }
    
    async def _worker(self, worker_id: int):
        """Worker coroutine that processes tasks from the queue.
        
        Args:
            worker_id: Unique identifier for this worker
        """
        self.logger.debug(f"Worker {worker_id} started")
        tasks_processed = 0
        
        while self.is_running:
            task = await self._get_next_task()
            
            if task is None:
                # No task available, wait a bit
                await asyncio.sleep(0.1)
                continue
            
            try:
                await self._process_task(task, worker_id)
                tasks_processed += 1
                
                # Log progress every 10 tasks
                if tasks_processed % 10 == 0:
                    completed = self.stats['completed']
                    total = self.stats['total_tasks']
                    percent = (completed / total * 100) if total > 0 else 0
                    self.logger.info(
                        f"Progress: {completed}/{total} ({percent:.1f}%) - "
                        f"Worker {worker_id} processed {tasks_processed} tasks"
                    )
            except Exception as e:
                self.logger.error(f"Worker {worker_id} error processing task {task.task_id}: {e}")
                task.status = TaskStatus.FAILED
                task.error = e
                self.stats['failed'] += 1
            finally:
                # Mark task as done for the queue
                self.queues[task.priority].task_done()
        
        self.logger.debug(f"Worker {worker_id} stopped after processing {tasks_processed} tasks")
    
    async def _get_next_task(self) -> Optional[QueuedTask]:
        """Get the next task from queues, respecting priority and rate limits.
        
        Returns:
            Next task to process, or None if no tasks available
        """
        # Try to get task from high priority first, then normal, then low
        for priority in [TaskPriority.HIGH, TaskPriority.NORMAL, TaskPriority.LOW]:
            try:
                task = self.queues[priority].get_nowait()
                
                # Check if task should wait due to rate limiting
                if task.should_wait():
                    wait_time = (task.retry_after - datetime.now()).total_seconds()
                    self.logger.debug(f"Task {task.task_id} waiting {wait_time:.1f}s due to rate limit")
                    # Put it back and try next
                    await self.queues[priority].put(task)
                    continue
                
                # Check if resource is rate limited
                rate_limit = self.rate_limits.get(task.task_type)
                if rate_limit and rate_limit.should_wait():
                    wait_time = rate_limit.get_wait_time()
                    self.logger.debug(f"Resource {task.task_type} rate limited, waiting {wait_time:.1f}s")
                    # Put task back and wait
                    await self.queues[priority].put(task)
                    await asyncio.sleep(min(wait_time, 1.0))  # Wait up to 1s before retry
                    continue
                
                return task
                
            except asyncio.QueueEmpty:
                continue
        
        return None
    
    async def _process_task(self, task: QueuedTask, worker_id: int):
        """Process a single task.
        
        Args:
            task: Task to process
            worker_id: ID of the worker processing this task
        """
        task.status = TaskStatus.PROCESSING
        self.logger.debug(f"Worker {worker_id} processing task {task.task_id} ({task.task_type})")
        
        try:
            # Execute the task function
            result = await task.func(*task.args, **task.kwargs)
            
            # Task succeeded
            task.status = TaskStatus.COMPLETED
            task.result = result
            self.completed_tasks.append(task)
            self.stats['completed'] += 1
            
            self.logger.debug(f"Task {task.task_id} completed successfully")
            
        except Exception as e:
            # Check if it's a rate limit error
            is_rate_limit = self._is_rate_limit_error(e)
            
            if is_rate_limit:
                await self._handle_rate_limit(task, e)
            elif task.can_retry():
                # Other error but can retry
                task.retry_count += 1
                task.status = TaskStatus.PENDING
                task.retry_after = datetime.now() + timedelta(seconds=5 * task.retry_count)
                await self.queues[task.priority].put(task)
                self.stats['retried'] += 1
                self.logger.warning(f"Task {task.task_id} failed, retry {task.retry_count}/{task.max_retries}")
            else:
                # Failed permanently
                task.status = TaskStatus.FAILED
                task.error = e
                self.stats['failed'] += 1
                self.logger.error(f"Task {task.task_id} failed permanently: {e}")
    
    def _is_rate_limit_error(self, error: Exception) -> bool:
        """Check if error is a rate limit error (HTTP 429).
        
        Args:
            error: Exception to check
            
        Returns:
            True if it's a rate limit error
        """
        error_str = str(error).lower()
        return (
            '429' in error_str or
            'too many requests' in error_str or
            'rate limit' in error_str or
            'quota exceeded' in error_str
        )
    
    async def _handle_rate_limit(self, task: QueuedTask, error: Exception):
        """Handle rate limit error with intelligent retry.
        
        Args:
            task: Task that was rate limited
            error: Rate limit exception
        """
        task.status = TaskStatus.RATE_LIMITED
        self.stats['rate_limited'] += 1
        
        # Try to extract Retry-After from error message or use default
        retry_delay = self._extract_retry_after(error)
        retry_after = datetime.now() + timedelta(seconds=retry_delay)
        
        task.retry_after = retry_after
        
        # Update resource rate limit info
        if task.task_type not in self.rate_limits:
            self.rate_limits[task.task_type] = RateLimitInfo(resource=task.task_type)
        
        rate_limit = self.rate_limits[task.task_type]
        rate_limit.is_limited = True
        rate_limit.retry_after = retry_after
        
        self.logger.warning(
            f"Task {task.task_id} rate limited, will retry after {retry_delay}s"
        )
        
        # Re-queue the task if it can retry
        if task.can_retry():
            task.retry_count += 1
            task.status = TaskStatus.PENDING
            await self.queues[task.priority].put(task)
            self.stats['retried'] += 1
        else:
            task.status = TaskStatus.FAILED
            task.error = error
            self.stats['failed'] += 1
            self.logger.error(f"Task {task.task_id} exceeded retry limit due to rate limiting")
    
    def _extract_retry_after(self, error: Exception) -> int:
        """Extract Retry-After delay from error message.
        
        Args:
            error: Exception that may contain Retry-After information
            
        Returns:
            Delay in seconds (uses default if not found)
        """
        import re
        
        error_str = str(error)
        
        # Try to find "Retry-After: <seconds>" pattern
        match = re.search(r'retry[- ]after[:\s]+(\d+)', error_str, re.IGNORECASE)
        if match:
            return int(match.group(1))
        
        # Try to find "wait <seconds>" pattern
        match = re.search(r'wait[:\s]+(\d+)', error_str, re.IGNORECASE)
        if match:
            return int(match.group(1))
        
        # Use default
        return self.default_retry_delay
