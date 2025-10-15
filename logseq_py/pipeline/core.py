"""
Core Pipeline Framework

Provides the foundation for building flexible, multi-step processing pipelines
that can process Logseq content with state tracking and resumable execution.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Iterator, Callable, Union
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import logging
import uuid
from pathlib import Path

from ..models import Block, Page
from ..builders.parser import BuilderParser


class ProcessingStatus(Enum):
    """Status of processing for blocks and content."""
    UNPROCESSED = "unprocessed"
    PROCESSING = "processing"  
    COMPLETED = "completed"
    ERROR = "error"
    SKIPPED = "skipped"


@dataclass
class ProcessingContext:
    """Context object that carries state through pipeline steps."""
    
    # Core data
    graph_path: str
    pipeline_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    
    # Processing state
    current_step: int = 0
    total_steps: int = 0
    start_time: datetime = field(default_factory=datetime.now)
    
    # Data storage
    blocks: List[Block] = field(default_factory=list)
    pages: List[Page] = field(default_factory=list)
    extracted_content: Dict[str, Any] = field(default_factory=dict)
    analysis_results: Dict[str, Any] = field(default_factory=dict)
    generated_content: Dict[str, Any] = field(default_factory=dict)
    
    # Configuration
    properties: Dict[str, Any] = field(default_factory=dict)
    filters: Dict[str, Any] = field(default_factory=dict)
    
    # Progress tracking
    processed_items: int = 0
    total_items: int = 0
    errors: List[Dict[str, Any]] = field(default_factory=list)
    
    def add_error(self, error: Exception, item: Any = None, step: str = None):
        """Add an error to the context."""
        self.errors.append({
            'error': str(error),
            'type': type(error).__name__,
            'item': str(item) if item else None,
            'step': step,
            'timestamp': datetime.now().isoformat()
        })
    
    def get_progress(self) -> float:
        """Get current processing progress as percentage."""
        if self.total_items == 0:
            return 0.0
        return (self.processed_items / self.total_items) * 100
    
    def get_status_summary(self) -> Dict[str, Any]:
        """Get summary of processing status."""
        return {
            'pipeline_id': self.pipeline_id,
            'session_id': self.session_id,
            'current_step': self.current_step,
            'total_steps': self.total_steps,
            'progress': self.get_progress(),
            'processed_items': self.processed_items,
            'total_items': self.total_items,
            'errors_count': len(self.errors),
            'elapsed_time': (datetime.now() - self.start_time).total_seconds(),
            'status': 'completed' if self.current_step >= self.total_steps else 'processing'
        }


class PipelineStep(ABC):
    """Abstract base class for pipeline steps."""
    
    def __init__(self, name: str, description: str = None):
        self.name = name
        self.description = description or name
        self.logger = logging.getLogger(f"pipeline.{name}")
    
    @abstractmethod
    def execute(self, context: ProcessingContext) -> ProcessingContext:
        """Execute this pipeline step with the given context."""
        pass
    
    def can_execute(self, context: ProcessingContext) -> bool:
        """Check if this step can be executed with the current context."""
        return True
    
    def get_requirements(self) -> List[str]:
        """Get list of requirements/dependencies for this step."""
        return []
    
    def validate_context(self, context: ProcessingContext) -> bool:
        """Validate that context has required data for this step."""
        return True
    
    def on_start(self, context: ProcessingContext):
        """Called when step starts executing."""
        self.logger.info(f"Starting step: {self.name}")
    
    def on_complete(self, context: ProcessingContext):
        """Called when step completes successfully."""
        self.logger.info(f"Completed step: {self.name}")
    
    def on_error(self, context: ProcessingContext, error: Exception):
        """Called when step encounters an error."""
        self.logger.error(f"Error in step {self.name}: {error}")
        context.add_error(error, step=self.name)


class Pipeline:
    """Main pipeline orchestrator that executes steps in sequence."""
    
    def __init__(self, name: str, description: str = None):
        self.name = name
        self.description = description or name
        self.steps: List[PipelineStep] = []
        self.logger = logging.getLogger(f"pipeline.{name}")
        
        # Configuration
        self.continue_on_error = True
        self.save_intermediate_state = True
        
        # Hooks
        self.on_pipeline_start: Optional[Callable] = None
        self.on_pipeline_complete: Optional[Callable] = None
        self.on_step_start: Optional[Callable] = None
        self.on_step_complete: Optional[Callable] = None
    
    def add_step(self, step: PipelineStep) -> 'Pipeline':
        """Add a step to the pipeline."""
        self.steps.append(step)
        return self
    
    def add_steps(self, *steps: PipelineStep) -> 'Pipeline':
        """Add multiple steps to the pipeline."""
        self.steps.extend(steps)
        return self
    
    def insert_step(self, index: int, step: PipelineStep) -> 'Pipeline':
        """Insert a step at a specific position."""
        self.steps.insert(index, step)
        return self
    
    def remove_step(self, step_name: str) -> 'Pipeline':
        """Remove a step by name."""
        self.steps = [s for s in self.steps if s.name != step_name]
        return self
    
    def get_step(self, step_name: str) -> Optional[PipelineStep]:
        """Get a step by name."""
        for step in self.steps:
            if step.name == step_name:
                return step
        return None
    
    def validate_pipeline(self) -> List[str]:
        """Validate pipeline configuration and return any issues."""
        issues = []
        
        if not self.steps:
            issues.append("Pipeline has no steps")
        
        # Check for duplicate step names
        step_names = [s.name for s in self.steps]
        duplicates = set([x for x in step_names if step_names.count(x) > 1])
        if duplicates:
            issues.append(f"Duplicate step names: {duplicates}")
        
        # Check step requirements
        available_steps = set(step_names)
        for step in self.steps:
            missing_reqs = set(step.get_requirements()) - available_steps
            if missing_reqs:
                issues.append(f"Step '{step.name}' missing requirements: {missing_reqs}")
        
        return issues
    
    def execute(self, context: ProcessingContext, 
                start_from: int = 0, 
                end_at: Optional[int] = None) -> ProcessingContext:
        """Execute the pipeline with given context."""
        
        # Validate pipeline
        issues = self.validate_pipeline()
        if issues:
            raise ValueError(f"Pipeline validation failed: {issues}")
        
        # Setup context
        context.total_steps = len(self.steps)
        context.current_step = start_from
        
        if end_at is None:
            end_at = len(self.steps)
        
        self.logger.info(f"Starting pipeline '{self.name}' with {len(self.steps)} steps")
        
        # Pipeline start hook
        if self.on_pipeline_start:
            self.on_pipeline_start(context)
        
        try:
            # Execute steps
            for i in range(start_from, min(end_at, len(self.steps))):
                step = self.steps[i]
                context.current_step = i + 1
                
                self.logger.info(f"Executing step {i+1}/{len(self.steps)}: {step.name}")
                
                # Step start hooks
                if self.on_step_start:
                    self.on_step_start(step, context)
                step.on_start(context)
                
                try:
                    # Validate step can execute
                    if not step.can_execute(context):
                        self.logger.warning(f"Skipping step {step.name}: cannot execute")
                        continue
                    
                    if not step.validate_context(context):
                        raise ValueError(f"Context validation failed for step {step.name}")
                    
                    # Execute step
                    context = step.execute(context)
                    
                    # Step complete hooks
                    step.on_complete(context)
                    if self.on_step_complete:
                        self.on_step_complete(step, context)
                        
                except Exception as e:
                    # Handle step error
                    step.on_error(context, e)
                    
                    if not self.continue_on_error:
                        raise
                    else:
                        self.logger.warning(f"Step {step.name} failed but continuing: {e}")
                
                # Save intermediate state if configured
                if self.save_intermediate_state:
                    self._save_intermediate_state(context, i)
            
            # Pipeline complete hook
            if self.on_pipeline_complete:
                self.on_pipeline_complete(context)
            
            self.logger.info(f"Pipeline '{self.name}' completed successfully")
            
        except Exception as e:
            self.logger.error(f"Pipeline '{self.name}' failed: {e}")
            context.add_error(e, step="pipeline")
            raise
        
        return context
    
    def resume_from_step(self, context: ProcessingContext, step_name: str) -> ProcessingContext:
        """Resume pipeline execution from a specific step."""
        step_index = None
        for i, step in enumerate(self.steps):
            if step.name == step_name:
                step_index = i
                break
        
        if step_index is None:
            raise ValueError(f"Step '{step_name}' not found in pipeline")
        
        return self.execute(context, start_from=step_index)
    
    def _save_intermediate_state(self, context: ProcessingContext, step_index: int):
        """Save intermediate processing state (can be overridden)."""
        # Default implementation - log progress
        self.logger.debug(f"Completed step {step_index + 1}: {context.get_progress():.1f}% done")
    
    def get_pipeline_info(self) -> Dict[str, Any]:
        """Get information about this pipeline."""
        return {
            'name': self.name,
            'description': self.description,
            'steps_count': len(self.steps),
            'steps': [
                {
                    'name': step.name,
                    'description': step.description,
                    'requirements': step.get_requirements()
                }
                for step in self.steps
            ]
        }


class PipelineBuilder:
    """Builder for constructing pipelines fluently."""
    
    def __init__(self, name: str, description: str = None):
        self.pipeline = Pipeline(name, description)
    
    def step(self, step: PipelineStep) -> 'PipelineBuilder':
        """Add a step to the pipeline."""
        self.pipeline.add_step(step)
        return self
    
    def filter_blocks(self, filter_func: Callable, name: str = "filter_blocks") -> 'PipelineBuilder':
        """Add a block filtering step."""
        from .steps import FilterBlocksStep
        return self.step(FilterBlocksStep(filter_func, name))
    
    def extract_content(self, extractors: List[str] = None, name: str = "extract_content") -> 'PipelineBuilder':
        """Add content extraction step."""
        from .steps import ExtractContentStep
        return self.step(ExtractContentStep(extractors, name))
    
    def analyze_content(self, analyzers: List[str] = None, name: str = "analyze_content") -> 'PipelineBuilder':
        """Add content analysis step."""
        from .steps import AnalyzeContentStep  
        return self.step(AnalyzeContentStep(analyzers, name))
    
    def generate_content(self, generators: List[str] = None, name: str = "generate_content") -> 'PipelineBuilder':
        """Add content generation step."""
        from .steps import GenerateContentStep
        return self.step(GenerateContentStep(generators, name))
    
    def configure(self, **kwargs) -> 'PipelineBuilder':
        """Configure pipeline options."""
        if 'continue_on_error' in kwargs:
            self.pipeline.continue_on_error = kwargs['continue_on_error']
        if 'save_intermediate_state' in kwargs:
            self.pipeline.save_intermediate_state = kwargs['save_intermediate_state']
        return self
    
    def build(self) -> Pipeline:
        """Build and return the configured pipeline."""
        return self.pipeline


# Convenience function for creating pipelines
def create_pipeline(name: str, description: str = None) -> PipelineBuilder:
    """Create a new pipeline builder."""
    return PipelineBuilder(name, description)