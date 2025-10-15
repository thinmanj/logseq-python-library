"""
Async Pipeline Framework

Provides asynchronous processing capabilities for high-performance content processing.
Extends the core pipeline system with async/await support for I/O operations.
"""

import asyncio
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, AsyncIterator, Callable, Union
from dataclasses import dataclass
from datetime import datetime
import logging
import uuid

from .core import ProcessingContext, ProcessingStatus


class AsyncPipelineStep(ABC):
    """Abstract base class for asynchronous pipeline steps."""
    
    def __init__(self, name: str, description: str = None):
        self.name = name
        self.description = description or name
        self.logger = logging.getLogger(f"async_pipeline.{name}")
    
    @abstractmethod
    async def execute(self, context: ProcessingContext) -> ProcessingContext:
        """Execute this pipeline step asynchronously."""
        pass
    
    async def can_execute(self, context: ProcessingContext) -> bool:
        """Check if this step can be executed with the current context."""
        return True
    
    def get_requirements(self) -> List[str]:
        """Get list of requirements/dependencies for this step."""
        return []
    
    async def validate_context(self, context: ProcessingContext) -> bool:
        """Validate that context has required data for this step."""
        return True
    
    async def on_start(self, context: ProcessingContext):
        """Called when step starts executing."""
        self.logger.info(f"Starting async step: {self.name}")
    
    async def on_complete(self, context: ProcessingContext):
        """Called when step completes successfully."""
        self.logger.info(f"Completed async step: {self.name}")
    
    async def on_error(self, context: ProcessingContext, error: Exception):
        """Called when step encounters an error."""
        self.logger.error(f"Error in async step {self.name}: {error}")
        context.add_error(error, step=self.name)


class AsyncPipeline:
    """Asynchronous pipeline orchestrator."""
    
    def __init__(self, name: str, description: str = None):
        self.name = name
        self.description = description or name
        self.steps: List[AsyncPipelineStep] = []
        self.logger = logging.getLogger(f"async_pipeline.{name}")
        
        # Configuration
        self.continue_on_error = True
        self.max_concurrent = 10
        self.batch_size = 100
        
        # Hooks
        self.on_pipeline_start: Optional[Callable] = None
        self.on_pipeline_complete: Optional[Callable] = None
        self.on_step_start: Optional[Callable] = None
        self.on_step_complete: Optional[Callable] = None
    
    def add_step(self, step: AsyncPipelineStep) -> 'AsyncPipeline':
        """Add a step to the pipeline."""
        self.steps.append(step)
        return self
    
    def add_steps(self, *steps: AsyncPipelineStep) -> 'AsyncPipeline':
        """Add multiple steps to the pipeline."""
        self.steps.extend(steps)
        return self
    
    async def execute(self, context: ProcessingContext) -> ProcessingContext:
        """Execute the pipeline asynchronously."""
        context.total_steps = len(self.steps)
        context.current_step = 0
        
        self.logger.info(f"Starting async pipeline '{self.name}' with {len(self.steps)} steps")
        
        # Pipeline start hook
        if self.on_pipeline_start:
            await self.on_pipeline_start(context)
        
        try:
            for i, step in enumerate(self.steps):
                context.current_step = i + 1
                
                self.logger.info(f"Executing async step {i+1}/{len(self.steps)}: {step.name}")
                
                # Step start hooks
                if self.on_step_start:
                    await self.on_step_start(step, context)
                await step.on_start(context)
                
                try:
                    # Validate step can execute
                    if not await step.can_execute(context):
                        self.logger.warning(f"Skipping step {step.name}: cannot execute")
                        continue
                    
                    if not await step.validate_context(context):
                        raise ValueError(f"Context validation failed for step {step.name}")
                    
                    # Execute step
                    context = await step.execute(context)
                    
                    # Step complete hooks
                    await step.on_complete(context)
                    if self.on_step_complete:
                        await self.on_step_complete(step, context)
                        
                except Exception as e:
                    # Handle step error
                    await step.on_error(context, e)
                    
                    if not self.continue_on_error:
                        raise
                    else:
                        self.logger.warning(f"Step {step.name} failed but continuing: {e}")
            
            # Pipeline complete hook
            if self.on_pipeline_complete:
                await self.on_pipeline_complete(context)
            
            self.logger.info(f"Async pipeline '{self.name}' completed successfully")
            
        except Exception as e:
            self.logger.error(f"Async pipeline '{self.name}' failed: {e}")
            context.add_error(e, step="async_pipeline")
            raise
        
        return context
    
    def configure(self, **kwargs) -> 'AsyncPipeline':
        """Configure pipeline options."""
        if 'continue_on_error' in kwargs:
            self.continue_on_error = kwargs['continue_on_error']
        if 'max_concurrent' in kwargs:
            self.max_concurrent = kwargs['max_concurrent']
        if 'batch_size' in kwargs:
            self.batch_size = kwargs['batch_size']
        return self


class AsyncBatchProcessor:
    """Processes items in batches with concurrency control."""
    
    def __init__(self, max_concurrent: int = 10, batch_size: int = 100):
        self.max_concurrent = max_concurrent
        self.batch_size = batch_size
        self.semaphore = asyncio.Semaphore(max_concurrent)
    
    async def process_items(self, 
                           items: List[Any],
                           processor: Callable,
                           progress_callback: Optional[Callable] = None) -> List[Any]:
        """Process items in batches with concurrency control."""
        results = []
        
        # Create batches
        batches = [items[i:i + self.batch_size] for i in range(0, len(items), self.batch_size)]
        
        for batch_idx, batch in enumerate(batches):
            # Process batch items concurrently
            tasks = []
            for item in batch:
                task = self._process_with_semaphore(processor, item)
                tasks.append(task)
            
            # Wait for batch completion
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Handle results and exceptions
            for result in batch_results:
                if isinstance(result, Exception):
                    # Log error but continue processing
                    logging.error(f"Item processing failed: {result}")
                    results.append(None)
                else:
                    results.append(result)
            
            # Progress callback
            if progress_callback:
                await progress_callback(batch_idx + 1, len(batches), len(results))
        
        return results
    
    async def _process_with_semaphore(self, processor: Callable, item: Any) -> Any:
        """Process single item with semaphore for concurrency control."""
        async with self.semaphore:
            if asyncio.iscoroutinefunction(processor):
                return await processor(item)
            else:
                # Run sync processor in thread pool
                loop = asyncio.get_event_loop()
                return await loop.run_in_executor(None, processor, item)


class AsyncProgressTracker:
    """Tracks progress of async operations with real-time updates."""
    
    def __init__(self, total_items: int = 0):
        self.total_items = total_items
        self.processed_items = 0
        self.start_time = datetime.now()
        self.callbacks: List[Callable] = []
    
    def add_callback(self, callback: Callable):
        """Add progress callback."""
        self.callbacks.append(callback)
    
    async def update_progress(self, processed: int):
        """Update progress and notify callbacks."""
        self.processed_items = processed
        
        # Calculate metrics
        elapsed = (datetime.now() - self.start_time).total_seconds()
        rate = processed / elapsed if elapsed > 0 else 0
        
        progress_data = {
            'processed': processed,
            'total': self.total_items,
            'percentage': (processed / self.total_items * 100) if self.total_items > 0 else 0,
            'rate': rate,
            'elapsed': elapsed,
            'eta': (self.total_items - processed) / rate if rate > 0 else 0
        }
        
        # Notify callbacks
        for callback in self.callbacks:
            if asyncio.iscoroutinefunction(callback):
                await callback(progress_data)
            else:
                callback(progress_data)


class AsyncPipelineBuilder:
    """Builder for constructing async pipelines fluently."""
    
    def __init__(self, name: str, description: str = None):
        self.pipeline = AsyncPipeline(name, description)
    
    def step(self, step: AsyncPipelineStep) -> 'AsyncPipelineBuilder':
        """Add a step to the pipeline."""
        self.pipeline.add_step(step)
        return self
    
    def configure(self, **kwargs) -> 'AsyncPipelineBuilder':
        """Configure pipeline options."""
        self.pipeline.configure(**kwargs)
        return self
    
    def build(self) -> AsyncPipeline:
        """Build and return the configured pipeline."""
        return self.pipeline


# Convenience functions
def create_async_pipeline(name: str, description: str = None) -> AsyncPipelineBuilder:
    """Create a new async pipeline builder."""
    return AsyncPipelineBuilder(name, description)


async def run_async_batch(items: List[Any], 
                         processor: Callable,
                         max_concurrent: int = 10,
                         batch_size: int = 100,
                         progress_callback: Optional[Callable] = None) -> List[Any]:
    """Convenience function to run batch processing."""
    batch_processor = AsyncBatchProcessor(max_concurrent, batch_size)
    return await batch_processor.process_items(items, processor, progress_callback)


# Async versions of core pipeline steps
class AsyncExtractContentStep(AsyncPipelineStep):
    """Async version of content extraction step."""
    
    def __init__(self, extractors: List[str] = None, max_concurrent: int = 10):
        super().__init__("async_extract_content", "Extract content asynchronously")
        self.extractors = extractors or ["url", "youtube", "github"]
        self.max_concurrent = max_concurrent
    
    async def execute(self, context: ProcessingContext) -> ProcessingContext:
        """Execute content extraction asynchronously."""
        extracted_items = []
        
        # Create extraction tasks
        async def extract_from_block(block):
            from .extractors import extract_from_block as sync_extract
            # Run in thread pool since extractors are sync
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, sync_extract, block, self.extractors)
        
        # Process blocks concurrently
        results = await run_async_batch(
            context.blocks,
            extract_from_block,
            max_concurrent=self.max_concurrent
        )
        
        # Collect results
        for block, result in zip(context.blocks, results):
            if result and not isinstance(result, Exception):
                for extractor_name, extracted in result.items():
                    if extracted and 'error' not in extracted:
                        extracted_items.append({
                            'block_id': getattr(block, 'id', None),
                            'extractor': extractor_name,
                            'content': extracted,
                            'timestamp': datetime.now().isoformat()
                        })
        
        context.extracted_content['items'] = extracted_items
        context.extracted_content['count'] = len(extracted_items)
        
        self.logger.info(f"Extracted {len(extracted_items)} content items asynchronously")
        return context


class AsyncAnalyzeContentStep(AsyncPipelineStep):
    """Async version of content analysis step."""
    
    def __init__(self, analyzers: List[str] = None, max_concurrent: int = 10):
        super().__init__("async_analyze_content", "Analyze content asynchronously") 
        self.analyzers = analyzers or ["sentiment", "topics", "summary"]
        self.max_concurrent = max_concurrent
    
    async def execute(self, context: ProcessingContext) -> ProcessingContext:
        """Execute content analysis asynchronously."""
        analysis_results = {}
        
        # Analyze blocks
        for analyzer_name in self.analyzers:
            async def analyze_block_content(block):
                if not block.content:
                    return None
                
                from .analyzers import analyze_content
                # Run in thread pool since analyzers are sync
                loop = asyncio.get_event_loop()
                return await loop.run_in_executor(None, analyze_content, block.content, [analyzer_name])
            
            # Process blocks concurrently
            results = await run_async_batch(
                context.blocks,
                analyze_block_content,
                max_concurrent=self.max_concurrent
            )
            
            # Collect results for this analyzer
            analyzer_results = []
            for block, result in zip(context.blocks, results):
                if result and analyzer_name in result:
                    analyzer_results.append({
                        'block_id': getattr(block, 'id', None),
                        'analysis': result[analyzer_name],
                        'timestamp': datetime.now().isoformat()
                    })
            
            analysis_results[analyzer_name] = {
                'results': analyzer_results,
                'count': len(analyzer_results)
            }
            
            self.logger.info(f"Analyzed {len(analyzer_results)} items with {analyzer_name} asynchronously")
        
        context.analysis_results.update(analysis_results)
        return context


class AsyncReportProgressStep(AsyncPipelineStep):
    """Async version of progress reporting step."""
    
    def __init__(self):
        super().__init__("async_report_progress", "Report pipeline progress asynchronously")
    
    async def execute(self, context: ProcessingContext) -> ProcessingContext:
        """Report current progress asynchronously."""
        summary = context.get_status_summary()
        
        self.logger.info("Async Pipeline Progress Report:")
        self.logger.info(f"  Pipeline: {context.pipeline_id}")
        self.logger.info(f"  Step: {summary['current_step']}/{summary['total_steps']}")
        self.logger.info(f"  Progress: {summary['progress']:.1f}%")
        self.logger.info(f"  Items: {summary['processed_items']}/{summary['total_items']}")
        self.logger.info(f"  Errors: {summary['errors_count']}")
        self.logger.info(f"  Elapsed: {summary['elapsed_time']:.1f}s")
        
        return context


# Example usage functions
async def run_async_analysis_pipeline(blocks: List, analyzers: List[str] = None) -> Dict[str, Any]:
    """Run async analysis pipeline on blocks."""
    context = ProcessingContext(graph_path="/tmp/async")
    context.blocks = blocks
    context.total_items = len(blocks)
    
    pipeline = (create_async_pipeline("async_analysis", "Async content analysis")
               .step(AsyncAnalyzeContentStep(analyzers, max_concurrent=20))
               .step(AsyncReportProgressStep())
               .configure(continue_on_error=True)
               .build())
    
    result_context = await pipeline.execute(context)
    return result_context.analysis_results


async def run_async_extraction_pipeline(blocks: List, extractors: List[str] = None) -> Dict[str, Any]:
    """Run async extraction pipeline on blocks."""
    context = ProcessingContext(graph_path="/tmp/async")
    context.blocks = blocks
    context.total_items = len(blocks)
    
    pipeline = (create_async_pipeline("async_extraction", "Async content extraction")
               .step(AsyncExtractContentStep(extractors, max_concurrent=15))
               .step(AsyncReportProgressStep())
               .configure(continue_on_error=True)
               .build())
    
    result_context = await pipeline.execute(context)
    return result_context.extracted_content