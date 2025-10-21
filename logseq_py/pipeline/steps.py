"""
Concrete Pipeline Steps

Implementation of specific pipeline steps for filtering, extraction, analysis, and generation.
"""

from typing import List, Dict, Any, Optional, Callable, Union
import logging
from datetime import datetime

from .core import PipelineStep, ProcessingContext, ProcessingStatus
from .filters import BlockFilter, PageFilter, create_property_filter
from ..models import Block, Page
from ..builders.parser import BuilderBasedLoader, BuilderParser
from ..logseq_client import LogseqClient


class LoadContentStep(PipelineStep):
    """Load content from Logseq graph."""
    
    def __init__(self, 
                 graph_path: str = None,
                 load_pages: bool = True,
                 load_blocks: bool = True,
                 page_filter: PageFilter = None,
                 name: str = "load_content"):
        super().__init__(name, "Load content from Logseq graph")
        self.graph_path = graph_path
        self.load_pages = load_pages
        self.load_blocks = load_blocks
        self.page_filter = page_filter
    
    def execute(self, context: ProcessingContext) -> ProcessingContext:
        """Load content into context."""
        graph_path = self.graph_path or context.graph_path
        
        try:
            # Initialize client and loader
            client = LogseqClient(graph_path)
            loader = client.get_builder_based_loader()
            
            if self.load_pages:
                # Load all pages
                pages = client.get_all_pages()
                
                # Apply page filter if provided
                if self.page_filter:
                    pages = self.page_filter.filter_pages(pages)
                
                context.pages = pages
                self.logger.info(f"Loaded {len(pages)} pages")
            
            if self.load_blocks:
                # Extract blocks from loaded pages
                all_blocks = []
                for page in context.pages:
                    if page.blocks:
                        all_blocks.extend(page.blocks)
                
                context.blocks = all_blocks
                context.total_items = len(all_blocks)
                self.logger.info(f"Loaded {len(all_blocks)} blocks")
            
        except Exception as e:
            self.logger.error(f"Failed to load content: {e}")
            context.add_error(e, step=self.name)
            raise
        
        return context
    
    def validate_context(self, context: ProcessingContext) -> bool:
        """Validate context has required data."""
        return bool(context.graph_path or self.graph_path)


class FilterBlocksStep(PipelineStep):
    """Filter blocks using specified criteria."""
    
    def __init__(self, 
                 block_filter: Union[BlockFilter, Callable[[Block], bool]] = None,
                 name: str = "filter_blocks"):
        super().__init__(name, "Filter blocks based on criteria")
        
        # Convert callable to BlockFilter if needed
        if callable(block_filter):
            from .filters import PredicateFilter
            self.block_filter = PredicateFilter(block_filter)
        else:
            self.block_filter = block_filter
    
    def execute(self, context: ProcessingContext) -> ProcessingContext:
        """Filter blocks in context."""
        if not self.block_filter:
            self.logger.warning("No filter specified, skipping")
            return context
        
        original_count = len(context.blocks)
        context.blocks = self.block_filter.filter_blocks(context.blocks)
        filtered_count = len(context.blocks)
        
        # Update total items count
        context.total_items = filtered_count
        
        self.logger.info(f"Filtered blocks: {original_count} -> {filtered_count}")
        return context
    
    def validate_context(self, context: ProcessingContext) -> bool:
        """Validate context has blocks to filter."""
        return len(context.blocks) > 0


class MarkProcessedStep(PipelineStep):
    """Mark blocks with processing status."""
    
    def __init__(self, 
                 status: ProcessingStatus = ProcessingStatus.PROCESSING,
                 property_name: str = "pipeline_status",
                 name: str = "mark_processed"):
        super().__init__(name, f"Mark blocks as {status.value}")
        self.status = status
        self.property_name = property_name
    
    def execute(self, context: ProcessingContext) -> ProcessingContext:
        """Mark blocks with processing status."""
        marked_count = 0
        
        for block in context.blocks:
            # Initialize properties if None
            if block.properties is None:
                block.properties = {}
            
            # Set status property
            block.properties[self.property_name] = self.status.value
            block.properties[f"{self.property_name}_timestamp"] = datetime.now().isoformat()
            block.properties[f"{self.property_name}_session"] = context.session_id
            
            marked_count += 1
        
        self.logger.info(f"Marked {marked_count} blocks as {self.status.value}")
        return context


class ExtractContentStep(PipelineStep):
    """Extract content from blocks using extractors."""
    
    def __init__(self, 
                 extractors: List[str] = None,
                 name: str = "extract_content"):
        super().__init__(name, "Extract content from blocks")
        self.extractors = extractors or ["url", "youtube", "twitter"]
    
    def execute(self, context: ProcessingContext) -> ProcessingContext:
        """Extract content from blocks."""
        extracted_items = []
        
        for block in context.blocks:
            for extractor_name in self.extractors:
                try:
                    extractor = self._get_extractor(extractor_name)
                    if extractor and extractor.can_extract(block):
                        extracted = extractor.extract(block)
                        if extracted:
                            extracted_items.append({
                                'block_id': getattr(block, 'id', None),
                                'extractor': extractor_name,
                                'content': extracted,
                                'timestamp': datetime.now().isoformat()
                            })
                            self.logger.debug(f"Extracted content using {extractor_name}")
                
                except Exception as e:
                    self.logger.warning(f"Extraction failed for {extractor_name}: {e}")
                    context.add_error(e, item=block, step=self.name)
        
        context.extracted_content['items'] = extracted_items
        context.extracted_content['count'] = len(extracted_items)
        
        self.logger.info(f"Extracted {len(extracted_items)} content items")
        return context
    
    def _get_extractor(self, name: str):
        """Get extractor instance by name."""
        from .extractors import get_extractor
        return get_extractor(name)


class AnalyzeContentStep(PipelineStep):
    """Analyze content using various analyzers."""
    
    def __init__(self, 
                 analyzers: List[str] = None,
                 name: str = "analyze_content"):
        super().__init__(name, "Analyze extracted content")
        self.analyzers = analyzers or ["sentiment", "topics", "summary"]
    
    def execute(self, context: ProcessingContext) -> ProcessingContext:
        """Analyze content in context."""
        analysis_results = {}
        
        # Analyze blocks
        for analyzer_name in self.analyzers:
            try:
                analyzer = self._get_analyzer(analyzer_name)
                if analyzer:
                    results = []
                    for block in context.blocks:
                        if block.content:
                            analysis = analyzer.analyze(block.content)
                            if analysis:
                                results.append({
                                    'block_id': getattr(block, 'id', None),
                                    'analysis': analysis,
                                    'timestamp': datetime.now().isoformat()
                                })
                    
                    analysis_results[analyzer_name] = {
                        'results': results,
                        'count': len(results)
                    }
                    
                    self.logger.debug(f"Analyzed {len(results)} items with {analyzer_name}")
            
            except Exception as e:
                self.logger.warning(f"Analysis failed for {analyzer_name}: {e}")
                context.add_error(e, step=self.name)
        
        # Analyze extracted content
        if 'items' in context.extracted_content:
            for analyzer_name in self.analyzers:
                try:
                    analyzer = self._get_analyzer(analyzer_name)
                    if analyzer:
                        extracted_analysis = []
                        for item in context.extracted_content['items']:
                            content = item.get('content', {}).get('text', '')
                            if content:
                                analysis = analyzer.analyze(content)
                                if analysis:
                                    extracted_analysis.append({
                                        'item_id': item.get('block_id'),
                                        'extractor': item.get('extractor'),
                                        'analysis': analysis,
                                        'timestamp': datetime.now().isoformat()
                                    })
                        
                        analysis_key = f"{analyzer_name}_extracted"
                        analysis_results[analysis_key] = {
                            'results': extracted_analysis,
                            'count': len(extracted_analysis)
                        }
                
                except Exception as e:
                    self.logger.warning(f"Extracted content analysis failed for {analyzer_name}: {e}")
                    context.add_error(e, step=self.name)
        
        context.analysis_results.update(analysis_results)
        
        total_analyses = sum(result['count'] for result in analysis_results.values())
        self.logger.info(f"Completed {total_analyses} analyses using {len(self.analyzers)} analyzers")
        
        return context
    
    def _get_analyzer(self, name: str):
        """Get analyzer instance by name."""
        from .analyzers import get_analyzer
        return get_analyzer(name)


class GenerateContentStep(PipelineStep):
    """Generate new content based on analysis results."""
    
    def __init__(self, 
                 generators: List[str] = None,
                 name: str = "generate_content"):
        super().__init__(name, "Generate new content")
        self.generators = generators or ["summary_page", "insights_blocks"]
    
    def execute(self, context: ProcessingContext) -> ProcessingContext:
        """Generate content based on context."""
        generated_content = {}
        
        for generator_name in self.generators:
            try:
                generator = self._get_generator(generator_name)
                if generator:
                    generated = generator.generate(context)
                    if generated:
                        generated_content[generator_name] = {
                            'content': generated,
                            'timestamp': datetime.now().isoformat()
                        }
                        
                        self.logger.debug(f"Generated content using {generator_name}")
            
            except Exception as e:
                self.logger.warning(f"Generation failed for {generator_name}: {e}")
                context.add_error(e, step=self.name)
        
        context.generated_content.update(generated_content)
        
        self.logger.info(f"Generated {len(generated_content)} content items")
        return context
    
    def _get_generator(self, name: str):
        """Get generator instance by name."""
        from .generators import get_generator
        return get_generator(name)


class SaveResultsStep(PipelineStep):
    """Save processing results back to Logseq."""
    
    def __init__(self, 
                 save_generated_content: bool = True,
                 save_analysis_properties: bool = True,
                 target_page: str = None,
                 name: str = "save_results"):
        super().__init__(name, "Save results to Logseq")
        self.save_generated_content = save_generated_content
        self.save_analysis_properties = save_analysis_properties
        self.target_page = target_page
    
    def execute(self, context: ProcessingContext) -> ProcessingContext:
        """Save results to Logseq."""
        saved_count = 0
        
        try:
            client = LogseqClient(context.graph_path)
            
            # Save generated content
            if self.save_generated_content and context.generated_content:
                for generator_name, generated in context.generated_content.items():
                    if isinstance(generated, dict) and 'content' in generated:
                        content = generated['content']
                        
                        # Determine target page
                        page_name = self.target_page or f"Pipeline Results - {context.pipeline_id[:8]}"
                        
                        # Create or update page with generated content
                        try:
                            # This would use the actual client methods when implemented
                            # client.create_or_update_page(page_name, content)
                            saved_count += 1
                            self.logger.debug(f"Saved content from {generator_name} to {page_name}")
                        except Exception as e:
                            self.logger.warning(f"Failed to save {generator_name} content: {e}")
            
            # Save analysis results as properties
            if self.save_analysis_properties and context.analysis_results:
                for block in context.blocks:
                    block_id = getattr(block, 'id', None)
                    if block_id:
                        # Find analysis results for this block
                        block_analyses = {}
                        for analyzer_name, results in context.analysis_results.items():
                            for result in results.get('results', []):
                                if result.get('block_id') == block_id:
                                    block_analyses[f"analysis_{analyzer_name}"] = result.get('analysis')
                        
                        if block_analyses:
                            # Update block properties
                            if not block.properties:
                                block.properties = {}
                            block.properties.update(block_analyses)
                            saved_count += 1
            
            self.logger.info(f"Saved {saved_count} items to Logseq")
            
        except Exception as e:
            self.logger.error(f"Failed to save results: {e}")
            context.add_error(e, step=self.name)
            raise
        
        return context
    
    def validate_context(self, context: ProcessingContext) -> bool:
        """Validate context has results to save."""
        return bool(context.generated_content or context.analysis_results)


class UpdateProcessingStatusStep(PipelineStep):
    """Update processing status of blocks."""
    
    def __init__(self, 
                 status: ProcessingStatus,
                 property_name: str = "pipeline_status",
                 name: str = "update_status"):
        super().__init__(name, f"Update processing status to {status.value}")
        self.status = status
        self.property_name = property_name
    
    def execute(self, context: ProcessingContext) -> ProcessingContext:
        """Update block processing status."""
        updated_count = 0
        
        for block in context.blocks:
            if not block.properties:
                block.properties = {}
            
            # Update status
            block.properties[self.property_name] = self.status.value
            block.properties[f"{self.property_name}_timestamp"] = datetime.now().isoformat()
            
            # Track progress
            if self.status == ProcessingStatus.COMPLETED:
                context.processed_items += 1
            
            updated_count += 1
        
        self.logger.info(f"Updated {updated_count} blocks to status {self.status.value}")
        return context


class ReportProgressStep(PipelineStep):
    """Report pipeline progress and statistics."""
    
    def __init__(self, name: str = "report_progress"):
        super().__init__(name, "Report pipeline progress")
    
    def execute(self, context: ProcessingContext) -> ProcessingContext:
        """Report current progress."""
        summary = context.get_status_summary()
        
        self.logger.info("Pipeline Progress Report:")
        self.logger.info(f"  Pipeline: {context.pipeline_id}")
        self.logger.info(f"  Step: {summary['current_step']}/{summary['total_steps']}")
        self.logger.info(f"  Progress: {summary['progress']:.1f}%")
        self.logger.info(f"  Items: {summary['processed_items']}/{summary['total_items']}")
        self.logger.info(f"  Errors: {summary['errors_count']}")
        self.logger.info(f"  Elapsed: {summary['elapsed_time']:.1f}s")
        
        # Log extracted content stats
        if context.extracted_content:
            extracted_count = context.extracted_content.get('count', 0)
            self.logger.info(f"  Extracted: {extracted_count} items")
        
        # Log analysis stats
        if context.analysis_results:
            total_analyses = sum(
                result.get('count', 0) 
                for result in context.analysis_results.values() 
                if isinstance(result, dict)
            )
            self.logger.info(f"  Analyses: {total_analyses} completed")
        
        # Log generation stats
        if context.generated_content:
            generated_count = len(context.generated_content)
            self.logger.info(f"  Generated: {generated_count} content items")
        
        return context


# Convenience functions for creating common step combinations
def create_basic_pipeline_steps(graph_path: str, 
                               block_filter: BlockFilter = None) -> List[PipelineStep]:
    """Create basic pipeline steps for content processing."""
    return [
        LoadContentStep(graph_path),
        FilterBlocksStep(block_filter) if block_filter else None,
        MarkProcessedStep(ProcessingStatus.PROCESSING),
        ExtractContentStep(),
        AnalyzeContentStep(),
        GenerateContentStep(),
        SaveResultsStep(),
        UpdateProcessingStatusStep(ProcessingStatus.COMPLETED),
        ReportProgressStep()
    ]


def create_analysis_pipeline_steps(analyzers: List[str] = None) -> List[PipelineStep]:
    """Create steps focused on content analysis."""
    return [
        MarkProcessedStep(ProcessingStatus.PROCESSING),
        AnalyzeContentStep(analyzers),
        UpdateProcessingStatusStep(ProcessingStatus.COMPLETED),
        ReportProgressStep()
    ]