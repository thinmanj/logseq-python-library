"""
Async Comprehensive Content Processor with Rate Limit Handling

Extends the comprehensive processor with async queue-based processing
that intelligently handles rate limits and processes content concurrently.
"""

import asyncio
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

from .comprehensive_processor import ComprehensiveContentProcessor
from .async_queue import AsyncRateLimitedQueue, TaskPriority
from ..models import Block, Page


class AsyncComprehensiveContentProcessor(ComprehensiveContentProcessor):
    """
    Async version of comprehensive processor with intelligent rate limit handling.
    
    Features:
    - Queue-based processing with priorities
    - Automatic retry on rate limits
    - Concurrent processing while waiting for rate-limited resources
    - Processes pages by type (videos, Twitter, PDFs)
    - Waits for all tasks before updating files
    """
    
    def __init__(self, graph_path: str, config: Dict[str, Any] = None):
        """Initialize the async comprehensive content processor.
        
        Args:
            graph_path: Path to the Logseq graph directory
            config: Configuration options including async settings
        """
        super().__init__(graph_path, config)
        
        # Async-specific config
        self.max_concurrent = self.config.get('max_concurrent', 10)
        self.retry_delay = self.config.get('retry_delay', 60)
        self.max_queue_size = self.config.get('max_queue_size', 1000)
        self.enable_async = self.config.get('enable_async', True)
        
        # Queue system
        self.queue: Optional[AsyncRateLimitedQueue] = None
        
        # Results storage (wait for all before updating)
        self.pending_updates: Dict[str, Dict[str, Any]] = {}
    
    def run(self) -> Dict[str, Any]:
        """Run the processor with async queue handling.
        
        Returns:
            Dictionary with processing results and statistics
        """
        if not self.enable_async:
            # Fall back to synchronous processing
            return super().run()
        
        # Run async version
        return asyncio.run(self.run_async())
    
    async def run_async(self) -> Dict[str, Any]:
        """Run the complete content processing pipeline asynchronously.
        
        Returns:
            Dictionary with processing results and statistics
        """
        self.logger.info(f"Starting async content processing for {self.graph_path}")
        
        try:
            # Validate graph path
            if not self.graph_path.exists():
                raise ValueError(f"Graph path does not exist: {self.graph_path}")
            
            # Create backup if enabled
            if self.backup_enabled and not self.dry_run:
                self._create_backup()
            
            # Initialize queue
            self.queue = AsyncRateLimitedQueue(
                max_concurrent=self.max_concurrent,
                default_retry_delay=self.retry_delay,
                max_queue_size=self.max_queue_size
            )
            
            # Step 1: Scan for content blocks
            content_blocks = self._scan_for_content_blocks()
            self.logger.info(f"Found {len(content_blocks)} blocks with content")
            
            # Step 2: Queue all content processing tasks
            await self._queue_content_tasks(content_blocks)
            
            # Step 3: Start workers and process
            self.logger.info(f"Starting {self.max_concurrent} workers...")
            await self.queue.start_workers()
            
            # Step 4: Wait for all tasks to complete
            self.logger.info("Waiting for all tasks to complete...")
            results = await self.queue.wait_completion()
            self.logger.info("All tasks completed")
            
            # Step 5: Process results and update files
            await self._process_results(results)
            
            # Step 6: Create topic pages from processed content
            if self.pending_updates:
                self._create_topic_pages_from_updates()
            
            # Step 7: Generate report
            return self._generate_async_report(results)
            
        except Exception as e:
            self.logger.error(f"Async pipeline failed: {e}")
            self.stats['errors'] += 1
            return {'success': False, 'error': str(e), 'stats': self.stats}
    
    async def _queue_content_tasks(self, content_blocks: List[Dict[str, Any]]):
        """Queue all content processing tasks by type and priority.
        
        Args:
            content_blocks: List of content blocks to process
        """
        video_count = 0
        twitter_count = 0
        pdf_count = 0
        
        self.logger.info(f"Queuing tasks from {len(content_blocks)} content blocks...")
        
        for i, block_info in enumerate(content_blocks, 1):
            if i % 100 == 0:
                self.logger.info(f"Processed {i}/{len(content_blocks)} blocks for queuing")
            
            urls = block_info['urls']
            
            # Queue video processing (high priority if has subtitles)
            for url in urls.get('video', []):
                task_id = f"video_{hash(url)}"
                await self.queue.add_task(
                    task_id=task_id,
                    task_type='video',
                    func=self._async_process_video,
                    url=url,
                    block=block_info['block'],
                    page=block_info['page'],
                    priority=TaskPriority.HIGH
                )
                video_count += 1
            
            # Queue Twitter processing (normal priority)
            for url in urls.get('twitter', []):
                task_id = f"twitter_{hash(url)}"
                await self.queue.add_task(
                    task_id=task_id,
                    task_type='twitter',
                    func=self._async_process_twitter,
                    url=url,
                    block=block_info['block'],
                    page=block_info['page'],
                    priority=TaskPriority.NORMAL
                )
                twitter_count += 1
            
            # Queue PDF processing (low priority)
            for url in urls.get('pdf', []):
                task_id = f"pdf_{hash(url)}"
                await self.queue.add_task(
                    task_id=task_id,
                    task_type='pdf',
                    func=self._async_process_pdf,
                    url=url,
                    block=block_info['block'],
                    page=block_info['page'],
                    priority=TaskPriority.LOW
                )
                pdf_count += 1
        
        self.logger.info(
            f"Queued {video_count} video, {twitter_count} Twitter, {pdf_count} PDF tasks "
            f"(total: {video_count + twitter_count + pdf_count})"
        )
    
    async def _async_process_video(
        self,
        url: str,
        block: Block,
        page: Page
    ) -> Optional[Dict[str, Any]]:
        """Async wrapper for video processing.
        
        Args:
            url: Video URL
            block: Block containing the URL
            page: Page containing the block
            
        Returns:
            Processed video data
        """
        # Use thread pool for sync operations
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self._process_video_url,
            url,
            block,
            page
        )
    
    async def _async_process_twitter(
        self,
        url: str,
        block: Block,
        page: Page
    ) -> Optional[Dict[str, Any]]:
        """Async wrapper for Twitter processing.
        
        Args:
            url: Twitter URL
            block: Block containing the URL
            page: Page containing the block
            
        Returns:
            Processed Twitter data
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self._process_twitter_url,
            url,
            block,
            page
        )
    
    async def _async_process_pdf(
        self,
        url: str,
        block: Block,
        page: Page
    ) -> Optional[Dict[str, Any]]:
        """Async wrapper for PDF processing.
        
        Args:
            url: PDF URL
            block: Block containing the URL
            page: Page containing the block
            
        Returns:
            Processed PDF data
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self._process_pdf_url,
            url,
            block,
            page
        )
    
    async def _process_results(self, results: Dict[str, Any]):
        """Process completed tasks and prepare updates.
        
        Args:
            results: Results from queue completion
        """
        completed_tasks = results['completed_tasks']
        failed_tasks = results['failed_tasks']
        
        self.logger.info(
            f"Processing {len(completed_tasks)} completed tasks, "
            f"{len(failed_tasks)} failed"
        )
        
        # Group results by page
        page_updates = {}
        
        for task in completed_tasks:
            if task.result:
                content_data = task.result
                page_name = content_data.get('source_page')
                
                if page_name not in page_updates:
                    page_updates[page_name] = []
                
                page_updates[page_name].append(content_data)
        
        # Store for later file updates
        self.pending_updates = page_updates
        
        # Update stats
        self.stats['videos_enhanced'] = sum(
            1 for t in completed_tasks if t.task_type == 'video'
        )
        self.stats['tweets_enhanced'] = sum(
            1 for t in completed_tasks if t.task_type == 'twitter'
        )
        self.stats['pdfs_enhanced'] = sum(
            1 for t in completed_tasks if t.task_type == 'pdf'
        )
    
    def _create_topic_pages_from_updates(self):
        """Create topic pages from pending updates.
        
        This runs after all tasks complete to ensure consistency.
        """
        processed_content = []
        
        for page_name, content_items in self.pending_updates.items():
            processed_content.append({
                'page_name': page_name,
                'content_items': content_items
            })
        
        # Use parent class method
        self._create_topic_pages(processed_content)
    
    def _generate_async_report(self, queue_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive report including async stats.
        
        Args:
            queue_results: Results from the async queue
            
        Returns:
            Complete processing report
        """
        base_report = self._generate_report()
        
        # Add async-specific stats
        base_report['async_stats'] = {
            'total_tasks': queue_results['stats']['total_tasks'],
            'completed': queue_results['stats']['completed'],
            'failed': queue_results['stats']['failed'],
            'rate_limited': queue_results['stats']['rate_limited'],
            'retried': queue_results['stats']['retried']
        }
        
        base_report['processing_mode'] = 'async'
        base_report['max_concurrent'] = self.max_concurrent
        
        return base_report


# Convenience function for running async processor
async def process_graph_async(
    graph_path: str,
    config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Convenience function to process a graph asynchronously.
    
    Args:
        graph_path: Path to Logseq graph
        config: Optional configuration
        
    Returns:
        Processing results and statistics
    """
    processor = AsyncComprehensiveContentProcessor(graph_path, config)
    return await processor.run_async()
