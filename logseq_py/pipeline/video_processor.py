"""
Video Processing Pipeline for Logseq Enhancement

This module provides a comprehensive pipeline for processing video content in Logseq:
1. Scans all blocks for video URLs
2. Enhances blocks with {{video}} syntax
3. Extracts video metadata and subtitles  
4. Analyzes content for tagging
5. Creates tagged pages with source information
"""

import os
import re
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Set, Tuple
from datetime import datetime
from collections import defaultdict

from ..utils import LogseqUtils
from ..models import Block, Page
from ..builders import PageBuilder, BlockBuilder
from .core import PipelineStep, ProcessingContext
from .subtitle_extractor import YouTubeSubtitleExtractor, VideoContentAnalyzer


class VideoProcessingPipeline:
    """Main pipeline for processing video content in Logseq graphs."""
    
    def __init__(self, graph_path: str, config: Dict[str, Any] = None):
        """Initialize the video processing pipeline.
        
        Args:
            graph_path: Path to the Logseq graph directory
            config: Configuration options for the pipeline
        """
        self.graph_path = Path(graph_path)
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Configuration defaults
        self.dry_run = self.config.get('dry_run', False)
        self.youtube_api_key = self.config.get('youtube_api_key')
        self.tag_prefix = self.config.get('tag_prefix', 'video-topic')
        self.min_subtitle_length = self.config.get('min_subtitle_length', 100)
        self.max_tags_per_video = self.config.get('max_tags_per_video', 5)
        self.backup_enabled = self.config.get('backup_enabled', True)
        
        # Initialize subtitle extractor
        self.subtitle_extractor = YouTubeSubtitleExtractor(
            api_key=self.youtube_api_key
        )
        
        # Initialize text analyzer  
        self.text_analyzer = VideoContentAnalyzer(
            max_tags=self.max_tags_per_video
        )
        
        # Stats tracking
        self.stats = {
            'blocks_processed': 0,
            'videos_found': 0,
            'videos_enhanced': 0,
            'subtitles_extracted': 0,
            'tags_created': 0,
            'pages_created': 0,
            'errors': 0
        }
    
    def run(self) -> Dict[str, Any]:
        """Run the complete video processing pipeline.
        
        Returns:
            Dictionary with processing results and statistics
        """
        self.logger.info(f"Starting video processing pipeline for {self.graph_path}")
        
        try:
            # Validate graph path
            if not self.graph_path.exists():
                raise ValueError(f"Graph path does not exist: {self.graph_path}")
            
            # Create backup if enabled
            if self.backup_enabled and not self.dry_run:
                self._create_backup()
            
            # Step 1: Load and scan all pages for video content
            video_blocks = self._scan_for_video_blocks()
            self.logger.info(f"Found {len(video_blocks)} blocks with video content")
            
            # Step 2: Process each video block
            processed_videos = []
            for block_info in video_blocks:
                try:
                    result = self._process_video_block(block_info)
                    if result:
                        processed_videos.append(result)
                except Exception as e:
                    self.logger.error(f"Error processing video block: {e}")
                    self.stats['errors'] += 1
            
            # Step 3: Create tagged pages from processed content
            if processed_videos:
                self._create_tagged_pages(processed_videos)
            
            # Step 4: Generate summary report
            return self._generate_report()
            
        except Exception as e:
            self.logger.error(f"Pipeline failed: {e}")
            self.stats['errors'] += 1
            return {'success': False, 'error': str(e), 'stats': self.stats}
    
    def _scan_for_video_blocks(self) -> List[Dict[str, Any]]:
        """Scan all pages for blocks containing video URLs."""
        video_blocks = []
        
        # Scan main pages
        for md_file in self.graph_path.glob("*.md"):
            if md_file.name.startswith('.'):
                continue
            
            try:
                page = LogseqUtils.parse_markdown_file(md_file)
                for block in page.blocks:
                    video_urls = LogseqUtils.extract_video_urls(block.content)
                    if video_urls:
                        video_blocks.append({
                            'page': page,
                            'block': block,
                            'video_urls': video_urls,
                            'file_path': md_file
                        })
                        self.stats['videos_found'] += len(video_urls)
                    
                    self.stats['blocks_processed'] += 1
            
            except Exception as e:
                self.logger.warning(f"Error processing {md_file}: {e}")
                self.stats['errors'] += 1
        
        # Scan journal pages
        journals_path = self.graph_path / "journals"
        if journals_path.exists():
            for md_file in journals_path.glob("*.md"):
                try:
                    page = LogseqUtils.parse_markdown_file(md_file)
                    for block in page.blocks:
                        video_urls = LogseqUtils.extract_video_urls(block.content)
                        if video_urls:
                            video_blocks.append({
                                'page': page,
                                'block': block,
                                'video_urls': video_urls,
                                'file_path': md_file
                            })
                            self.stats['videos_found'] += len(video_urls)
                        
                        self.stats['blocks_processed'] += 1
                
                except Exception as e:
                    self.logger.warning(f"Error processing {md_file}: {e}")
                    self.stats['errors'] += 1
        
        return video_blocks
    
    def _process_video_block(self, block_info: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process a single video block to enhance it and extract content."""
        page = block_info['page']
        block = block_info['block']
        video_urls = block_info['video_urls']
        file_path = block_info['file_path']
        
        processed_data = {
            'page_name': page.name,
            'block_id': getattr(block, 'id', None),
            'file_path': file_path,
            'videos': []
        }
        
        # Process each video URL in the block
        for url in video_urls:
            try:
                video_data = self._process_single_video(url, block, page)
                if video_data:
                    processed_data['videos'].append(video_data)
            
            except Exception as e:
                self.logger.error(f"Error processing video {url}: {e}")
                self.stats['errors'] += 1
        
        # Update the block content if we have video data
        if processed_data['videos']:
            self._enhance_block_content(block_info, processed_data)
            return processed_data
        
        return None
    
    def _process_single_video(self, url: str, block: Block, page: Page) -> Optional[Dict[str, Any]]:
        """Process a single video URL to extract metadata and content."""
        self.logger.info(f"Processing video: {url}")
        
        # Get basic video information
        video_info = LogseqUtils.get_video_info(url, self.youtube_api_key)
        if not video_info:
            self.logger.warning(f"Could not extract video info for: {url}")
            return None
        
        video_data = {
            'url': url,
            'title': video_info.get('title'),
            'author': video_info.get('author_name'),
            'duration': video_info.get('duration'),
            'platform': video_info.get('platform', 'unknown'),
            'extracted_at': datetime.now().isoformat(),
            'subtitles': None,
            'tags': [],
            'source_page': page.name,
            'source_block_content': block.content[:200] + "..." if len(block.content) > 200 else block.content
        }
        
        # Extract subtitles if available (YouTube only for now)
        if 'youtube' in url.lower():
            try:
                subtitles = self.subtitle_extractor.extract_subtitles(url)
                if subtitles and len(subtitles) > self.min_subtitle_length:
                    video_data['subtitles'] = subtitles
                    
                    # Analyze subtitles for tags
                    tags = self.text_analyzer.extract_tags(subtitles, video_data['title'])
                    video_data['tags'] = tags
                    
                    self.stats['subtitles_extracted'] += 1
                    self.logger.info(f"Extracted {len(subtitles)} chars of subtitles and {len(tags)} tags")
            
            except Exception as e:
                self.logger.warning(f"Failed to extract subtitles for {url}: {e}")
        
        return video_data
    
    def _enhance_block_content(self, block_info: Dict[str, Any], processed_data: Dict[str, Any]):
        """Enhance the block content with {{video}} syntax and metadata."""
        if self.dry_run:
            self.logger.info("DRY RUN: Would enhance block content")
            return
        
        block = block_info['block']
        original_content = block.content
        enhanced_content = original_content
        
        # Replace each video URL with enhanced syntax
        for video_data in processed_data['videos']:
            url = video_data['url']
            title = video_data.get('title', 'Unknown Video')
            
            # Create enhanced video block
            video_block = f"{{{{video {url}}}}}\n**{title}**"
            
            if video_data.get('author'):
                video_block += f"\nBy: {video_data['author']}"
            
            if video_data.get('tags'):
                tags_str = ' '.join([f"#{self.tag_prefix}-{tag}" for tag in video_data['tags']])
                video_block += f"\nTags: {tags_str}"
            
            # Replace the URL with the enhanced block
            enhanced_content = enhanced_content.replace(url, video_block)
        
        # Update the block content
        block.content = enhanced_content
        
        # Write back to file
        self._update_page_file(block_info['file_path'], block_info['page'])
        
        self.stats['videos_enhanced'] += len(processed_data['videos'])
        self.logger.info(f"Enhanced block with {len(processed_data['videos'])} videos")
    
    def _create_tagged_pages(self, processed_videos: List[Dict[str, Any]]):
        """Create pages for each tag with source information."""
        # Collect all tags and their sources
        tag_sources = defaultdict(list)
        
        for video_group in processed_videos:
            for video_data in video_group['videos']:
                for tag in video_data.get('tags', []):
                    tag_sources[tag].append({
                        'video_title': video_data.get('title'),
                        'video_url': video_data['url'],
                        'source_page': video_data['source_page'],
                        'timestamp': video_data['extracted_at'],
                        'subtitles_preview': (video_data.get('subtitles', '')[:200] + "...") 
                                           if video_data.get('subtitles') else None
                    })
        
        # Create a page for each tag
        for tag, sources in tag_sources.items():
            self._create_tag_page(tag, sources)
    
    def _create_tag_page(self, tag: str, sources: List[Dict[str, Any]]):
        """Create a page for a specific tag with all its video sources."""
        page_name = f"{self.tag_prefix}-{tag}"
        page_path = self.graph_path / f"{page_name}.md"
        
        if self.dry_run:
            self.logger.info(f"DRY RUN: Would create page {page_name}")
            return
        
        # Build page content
        builder = PageBuilder(page_name)
        builder.property("type", "video-topic")
        builder.property("tag", tag)
        builder.property("created", datetime.now().strftime("%Y-%m-%d"))
        builder.property("video-count", len(sources))
        
        # Add heading
        builder.heading(1, f"Videos tagged with: {tag}")
        
        # Add description
        builder.text(f"This page contains all videos related to the topic: **{tag}**")
        builder.text(f"Found in {len(sources)} video(s) from your Logseq graph.")
        
        # Add each video source
        for i, source in enumerate(sources, 1):
            builder.heading(2, f"{i}. {source['video_title'] or 'Unknown Video'}")
            builder.text(f"**Source Page:** [[{source['source_page']}]]")
            builder.text(f"**Video URL:** {source['video_url']}")
            builder.text(f"**Processed:** {source['timestamp'][:10]}")  # Just the date
            
            if source['subtitles_preview']:
                builder.heading(3, "Content Preview")
                builder.quote(source['subtitles_preview'])
            
            builder.text("")  # Add space between entries
        
        # Write the page
        try:
            with open(page_path, 'w', encoding='utf-8') as f:
                f.write(builder.build())
            
            self.stats['pages_created'] += 1
            self.stats['tags_created'] += 1
            self.logger.info(f"Created tag page: {page_name}")
        
        except Exception as e:
            self.logger.error(f"Failed to create page {page_name}: {e}")
            self.stats['errors'] += 1
    
    def _update_page_file(self, file_path: Path, page: Page):
        """Update a page file with modified content."""
        try:
            # Reconstruct page content from blocks
            content_lines = []
            
            # Add page properties
            if page.properties:
                for key, value in page.properties.items():
                    content_lines.append(f"{key}:: {value}")
                content_lines.append("")  # Empty line after properties
            
            # Add blocks
            for block in page.blocks:
                # Add proper indentation based on block level
                indent = "  " * block.level if block.level > 0 else ""
                content_lines.append(f"{indent}- {block.content}")
            
            # Write back to file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(content_lines))
            
            self.logger.debug(f"Updated file: {file_path}")
        
        except Exception as e:
            self.logger.error(f"Failed to update file {file_path}: {e}")
            self.stats['errors'] += 1
    
    def _create_backup(self):
        """Create a backup of the graph before processing."""
        backup_name = f"logseq-backup-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        backup_path = self.graph_path.parent / backup_name
        
        try:
            import shutil
            shutil.copytree(self.graph_path, backup_path)
            self.logger.info(f"Created backup at: {backup_path}")
        except Exception as e:
            self.logger.warning(f"Failed to create backup: {e}")
    
    def _generate_report(self) -> Dict[str, Any]:
        """Generate a final processing report."""
        return {
            'success': True,
            'graph_path': str(self.graph_path),
            'processing_time': datetime.now().isoformat(),
            'stats': self.stats,
            'config': self.config
        }