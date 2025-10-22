"""
Comprehensive Content Processing Pipeline for Logseq

Processes videos, X/Twitter posts, and PDFs with property-based topic organization.
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
from .enhanced_extractors import XTwitterExtractor, PDFExtractor, ContentAnalyzer


class ComprehensiveContentProcessor:
    """Main pipeline for processing video, X/Twitter, and PDF content in Logseq graphs."""
    
    def __init__(self, graph_path: str, config: Dict[str, Any] = None):
        """Initialize the comprehensive content processor.
        
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
        self.twitter_bearer_token = self.config.get('twitter_bearer_token')
        self.property_prefix = self.config.get('property_prefix', 'topic')
        self.min_subtitle_length = self.config.get('min_subtitle_length', 100)
        self.max_topics_per_item = self.config.get('max_topics_per_item', 3)
        self.backup_enabled = self.config.get('backup_enabled', True)
        self.process_videos = self.config.get('process_videos', True)
        self.process_twitter = self.config.get('process_twitter', True)
        self.process_pdfs = self.config.get('process_pdfs', True)
        
        # Initialize extractors
        self.subtitle_extractor = YouTubeSubtitleExtractor(
            api_key=self.youtube_api_key
        )
        
        self.twitter_extractor = XTwitterExtractor(
            bearer_token=self.twitter_bearer_token
        )
        
        self.pdf_extractor = PDFExtractor()
        
        # Initialize content analyzer  
        self.content_analyzer = ContentAnalyzer(
            max_topics=self.max_topics_per_item
        )
        
        # Stats tracking
        self.stats = {
            'blocks_processed': 0,
            'videos_found': 0,
            'videos_enhanced': 0,
            'tweets_found': 0,
            'tweets_enhanced': 0,
            'pdfs_found': 0,
            'pdfs_enhanced': 0,
            'subtitles_extracted': 0,
            'properties_added': 0,
            'topic_pages_created': 0,
            'errors': 0
        }
    
    def run(self) -> Dict[str, Any]:
        """Run the complete content processing pipeline.
        
        Returns:
            Dictionary with processing results and statistics
        """
        self.logger.info(f"Starting comprehensive content processing for {self.graph_path}")
        
        try:
            # Validate graph path
            if not self.graph_path.exists():
                raise ValueError(f"Graph path does not exist: {self.graph_path}")
            
            # Create backup if enabled
            if self.backup_enabled and not self.dry_run:
                self._create_backup()
            
            # Step 1: Load and scan all pages for content
            content_blocks = self._scan_for_content_blocks()
            self.logger.info(f"Found {len(content_blocks)} blocks with video, X/Twitter, or PDF content")
            
            # Step 2: Process each content block
            processed_content = []
            for block_info in content_blocks:
                try:
                    result = self._process_content_block(block_info)
                    if result:
                        processed_content.append(result)
                except Exception as e:
                    self.logger.error(f"Error processing content block: {e}")
                    self.stats['errors'] += 1
            
            # Step 3: Create topic pages from processed content
            if processed_content:
                self._create_topic_pages(processed_content)
            
            # Step 4: Generate summary report
            return self._generate_report()
            
        except Exception as e:
            self.logger.error(f"Pipeline failed: {e}")
            self.stats['errors'] += 1
            return {'success': False, 'error': str(e), 'stats': self.stats}
    
    def _scan_for_content_blocks(self) -> List[Dict[str, Any]]:
        """Scan all pages for blocks containing video, X/Twitter, or PDF URLs."""
        content_blocks = []
        
        # Scan main pages
        for md_file in self.graph_path.glob("*.md"):
            if md_file.name.startswith('.'):
                continue
            
            try:
                page = LogseqUtils.parse_markdown_file(md_file)
                for block in page.blocks:
                    block_urls = self._extract_all_urls(block.content)
                    if block_urls:
                        content_blocks.append({
                            'page': page,
                            'block': block,
                            'urls': block_urls,
                            'file_path': md_file
                        })
                        # Update stats based on URL types
                        self.stats['videos_found'] += len(block_urls.get('video', []))
                        self.stats['tweets_found'] += len(block_urls.get('twitter', []))
                        self.stats['pdfs_found'] += len(block_urls.get('pdf', []))
                    
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
                        block_urls = self._extract_all_urls(block.content)
                        if block_urls:
                            content_blocks.append({
                                'page': page,
                                'block': block,
                                'urls': block_urls,
                                'file_path': md_file
                            })
                            # Update stats based on URL types
                            self.stats['videos_found'] += len(block_urls.get('video', []))
                            self.stats['tweets_found'] += len(block_urls.get('twitter', []))
                            self.stats['pdfs_found'] += len(block_urls.get('pdf', []))
                        
                        self.stats['blocks_processed'] += 1
                
                except Exception as e:
                    self.logger.warning(f"Error processing {md_file}: {e}")
                    self.stats['errors'] += 1
        
        return content_blocks
    
    def _extract_all_urls(self, content: str) -> Dict[str, List[str]]:
        """Extract all supported URL types from content."""
        urls = {'video': [], 'twitter': [], 'pdf': []}
        
        if not content:
            return {}
        
        # Extract video URLs
        if self.process_videos:
            video_urls = LogseqUtils.extract_video_urls(content)
            urls['video'] = video_urls
        
        # Extract Twitter/X URLs
        if self.process_twitter:
            twitter_urls = self._extract_twitter_urls(content)
            urls['twitter'] = twitter_urls
        
        # Extract PDF URLs  
        if self.process_pdfs:
            pdf_urls = self._extract_pdf_urls(content)
            urls['pdf'] = pdf_urls
        
        # Return only if any URLs were found
        return {k: v for k, v in urls.items() if v}
    
    def _extract_twitter_urls(self, content: str) -> List[str]:
        """Extract Twitter/X URLs from content."""
        twitter_patterns = [
            r'https?://(?:twitter\.com|x\.com)/[^\s]+',
            r'https?://t\.co/[^\s]+'
        ]
        
        found_urls = []
        for pattern in twitter_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            found_urls.extend(matches)
        
        return found_urls
    
    def _extract_pdf_urls(self, content: str) -> List[str]:
        """Extract PDF URLs from content."""
        # General URL pattern
        url_pattern = r'https?://[^\s]+'
        urls = re.findall(url_pattern, content, re.IGNORECASE)
        
        pdf_urls = []
        for url in urls:
            if (url.lower().endswith('.pdf') or 
                '/pdf/' in url.lower() or 
                'filetype:pdf' in url.lower() or
                '.pdf?' in url.lower()):
                pdf_urls.append(url)
        
        return pdf_urls
    
    def _process_content_block(self, block_info: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process a content block with videos, tweets, or PDFs."""
        page = block_info['page']
        block = block_info['block']
        urls = block_info['urls']
        file_path = block_info['file_path']
        
        processed_data = {
            'page_name': page.name,
            'block_id': getattr(block, 'id', None),
            'file_path': file_path,
            'content_items': []
        }
        
        # Process video URLs
        for url in urls.get('video', []):
            try:
                content_data = self._process_video_url(url, block, page)
                if content_data:
                    processed_data['content_items'].append(content_data)
            except Exception as e:
                self.logger.error(f"Error processing video {url}: {e}")
                self.stats['errors'] += 1
        
        # Process Twitter URLs
        for url in urls.get('twitter', []):
            try:
                content_data = self._process_twitter_url(url, block, page)
                if content_data:
                    processed_data['content_items'].append(content_data)
            except Exception as e:
                self.logger.error(f"Error processing tweet {url}: {e}")
                self.stats['errors'] += 1
        
        # Process PDF URLs
        for url in urls.get('pdf', []):
            try:
                content_data = self._process_pdf_url(url, block, page)
                if content_data:
                    processed_data['content_items'].append(content_data)
            except Exception as e:
                self.logger.error(f"Error processing PDF {url}: {e}")
                self.stats['errors'] += 1
        
        # Update the block content if we have any processed items
        if processed_data['content_items']:
            self._enhance_content_block(block_info, processed_data)
            return processed_data
        
        return None
    
    def _process_video_url(self, url: str, block: Block, page: Page) -> Optional[Dict[str, Any]]:
        """Process a single video URL."""
        self.logger.info(f"Processing video: {url}")
        
        # Get video information
        video_info = LogseqUtils.get_video_info(url, self.youtube_api_key)
        if not video_info:
            self.logger.warning(f"Could not extract video info for: {url}")
            return None
        
        content_data = {
            'type': 'video',
            'url': url,
            'title': video_info.get('title'),
            'author': video_info.get('author_name'),
            'duration': video_info.get('duration'),
            'platform': video_info.get('platform', 'unknown'),
            'extracted_at': datetime.now().isoformat(),
            'topics': [],
            'source_page': page.name
        }
        
        # Extract subtitles if available (YouTube only)
        subtitle_content = None
        if 'youtube' in url.lower():
            try:
                subtitles = self.subtitle_extractor.extract_subtitles(url)
                if subtitles and len(subtitles) > self.min_subtitle_length:
                    subtitle_content = subtitles
                    self.stats['subtitles_extracted'] += 1
                    self.logger.info(f"Extracted {len(subtitles)} chars of subtitles")
            except Exception as e:
                self.logger.warning(f"Failed to extract subtitles for {url}: {e}")
        
        # Analyze content for topics
        analysis_text = subtitle_content or video_info.get('title', '')
        if analysis_text:
            topics = self.content_analyzer.extract_topics(
                analysis_text, 
                video_info.get('title'),
                'video'
            )
            content_data['topics'] = topics
        
        return content_data
    
    def _process_twitter_url(self, url: str, block: Block, page: Page) -> Optional[Dict[str, Any]]:
        """Process a single Twitter/X URL."""
        self.logger.info(f"Processing X/Twitter: {url}")
        
        # Get tweet information
        tweet_info = self.twitter_extractor.extract_tweet_info(url)
        if not tweet_info:
            self.logger.warning(f"Could not extract tweet info for: {url}")
            return None
        
        content_data = {
            'type': 'twitter',
            'url': url,
            'title': tweet_info.get('title'),
            'author': tweet_info.get('author'),
            'username': tweet_info.get('username'),
            'content': tweet_info.get('content'),
            'platform': 'x-twitter',
            'extracted_at': datetime.now().isoformat(),
            'topics': [],
            'source_page': page.name
        }
        
        # Analyze content for topics
        analysis_text = tweet_info.get('content') or tweet_info.get('title', '')
        if analysis_text:
            topics = self.content_analyzer.extract_topics(
                analysis_text,
                tweet_info.get('title'),
                'x-twitter'
            )
            content_data['topics'] = topics
        
        return content_data
    
    def _process_pdf_url(self, url: str, block: Block, page: Page) -> Optional[Dict[str, Any]]:
        """Process a single PDF URL."""
        self.logger.info(f"Processing PDF: {url}")
        
        # Get PDF information
        pdf_info = self.pdf_extractor.extract_pdf_info(url)
        if not pdf_info:
            self.logger.warning(f"Could not extract PDF info for: {url}")
            return None
        
        content_data = {
            'type': 'pdf',
            'url': url,
            'title': pdf_info.get('title'),
            'author': pdf_info.get('author'),
            'pages': pdf_info.get('num_pages'),
            'size_mb': pdf_info.get('size_mb'),
            'platform': 'pdf',
            'extracted_at': datetime.now().isoformat(),
            'topics': [],
            'source_page': page.name
        }
        
        # Analyze content for topics
        analysis_text = (pdf_info.get('content_preview') or 
                        pdf_info.get('subject') or 
                        pdf_info.get('title', ''))
        if analysis_text:
            topics = self.content_analyzer.extract_topics(
                analysis_text,
                pdf_info.get('title'),
                'pdf'
            )
            content_data['topics'] = topics
        
        return content_data
    
    def _enhance_content_block(self, block_info: Dict[str, Any], processed_data: Dict[str, Any]):
        """Enhance the block content with structured syntax and properties."""
        if self.dry_run:
            self.logger.info("DRY RUN: Would enhance block content")
            return
        
        block = block_info['block']
        original_content = block.content
        enhanced_content = original_content
        
        # Initialize block properties if needed
        if not hasattr(block, 'properties') or block.properties is None:
            block.properties = {}
        
        # Check if this block has already been processed (has topic properties)
        existing_topics = [k for k in block.properties.keys() if k.startswith(self.property_prefix)]
        if existing_topics:
            self.logger.info("Block already processed, skipping")
            return
        
        # Process each content item
        for item in processed_data['content_items']:
            url = item['url']
            title = item.get('title', 'Unknown')
            content_type = item['type']
            
            # Check if URL is already wrapped (skip if already has {{...}} around it)
            if f"{{{{{content_type} {url}}}}}" in original_content:
                self.logger.info(f"URL {url} already wrapped, skipping")
                continue
            
            # Check if URL is wrapped with any other syntax
            if re.search(r'\{\{[^}]*' + re.escape(url) + r'[^}]*\}\}', original_content):
                self.logger.info(f"URL {url} already has custom wrapper, skipping")
                continue
            
            # Create enhanced content block with proper hierarchy
            # Main block contains the URL wrapper, sub-blocks contain metadata
            if content_type == 'video':
                wrapper = f"{{{{video {url}}}}}"  # Main block
                details = []
                if title:
                    details.append(f"  **{title}**")
                if item.get('author'):
                    details.append(f"  By: {item['author']}")
                if item.get('duration'):
                    details.append(f"  Duration: {item['duration']}")
                enhanced_block = wrapper
                if details:
                    enhanced_block += "\n" + "\n".join(details)
                self.stats['videos_enhanced'] += 1
                
            elif content_type == 'twitter':
                wrapper = f"{{{{tweet {url}}}}}"  # Main block
                details = []
                if title:
                    details.append(f"  **{title}**")
                if item.get('username'):
                    details.append(f"  By: {item['username']}")
                if item.get('content'):
                    # Truncate long content
                    content_preview = item['content'][:200] + "..." if len(item['content']) > 200 else item['content']
                    details.append(f"  {content_preview}")
                enhanced_block = wrapper
                if details:
                    enhanced_block += "\n" + "\n".join(details)
                self.stats['tweets_enhanced'] += 1
                
            elif content_type == 'pdf':
                wrapper = f"{{{{pdf {url}}}}}"  # Main block
                details = []
                if title:
                    details.append(f"  **{title}**")
                if item.get('author'):
                    details.append(f"  Author: {item['author']}")
                if item.get('pages'):
                    details.append(f"  Pages: {item['pages']}")
                if item.get('size_mb'):
                    details.append(f"  Size: {item['size_mb']} MB")
                enhanced_block = wrapper
                if details:
                    enhanced_block += "\n" + "\n".join(details)
                self.stats['pdfs_enhanced'] += 1
            
            # Replace the URL with the enhanced block (only plain URL, not already wrapped)
            enhanced_content = enhanced_content.replace(url, enhanced_block)
            
            # Add topic properties (instead of tags)
            if item.get('topics'):
                for i, topic in enumerate(item['topics']):
                    prop_key = f"{self.property_prefix}-{i+1}"
                    block.properties[prop_key] = topic
                    self.stats['properties_added'] += 1
        
        # Update the block content
        block.content = enhanced_content
        
        # Write back to file
        self._update_page_file(block_info['file_path'], block_info['page'])
        
        self.logger.info(f"Enhanced block with {len(processed_data['content_items'])} items")
    
    def _create_topic_pages(self, processed_content: List[Dict[str, Any]]):
        """Create pages for each topic with source information."""
        # Collect all topics and their sources
        topic_sources = defaultdict(list)
        
        for content_group in processed_content:
            for item in content_group['content_items']:
                for topic in item.get('topics', []):
                    topic_sources[topic].append({
                        'title': item.get('title'),
                        'url': item['url'],
                        'type': item['type'],
                        'source_page': item['source_page'],
                        'timestamp': item['extracted_at'],
                        'author': item.get('author') or item.get('username')
                    })
        
        # Create a page for each topic
        for topic, sources in topic_sources.items():
            self._create_topic_page(topic, sources)
    
    def _create_topic_page(self, topic: str, sources: List[Dict[str, Any]]):
        """Create a page for a specific topic with all its content sources."""
        page_name = f"{self.property_prefix}-{topic}"
        page_path = self.graph_path / f"{page_name}.md"
        
        if self.dry_run:
            self.logger.info(f"DRY RUN: Would create page {page_name}")
            return
        
        # Build page content
        builder = PageBuilder(page_name)
        builder.property("type", "content-topic")
        builder.property("topic", topic)
        builder.property("created", datetime.now().strftime("%Y-%m-%d"))
        builder.property("item-count", len(sources))
        
        # Count by content type
        type_counts = defaultdict(int)
        for source in sources:
            type_counts[source['type']] += 1
        
        for content_type, count in type_counts.items():
            builder.property(f"{content_type}-count", count)
        
        # Add heading
        builder.heading(1, f"Content tagged with: {topic}")
        
        # Add description
        builder.text(f"This page contains all content related to the topic: **{topic}**")
        builder.text(f"Found in {len(sources)} item(s) from your Logseq graph.")
        
        # Group sources by type
        sources_by_type = defaultdict(list)
        for source in sources:
            sources_by_type[source['type']].append(source)
        
        # Add each content type section
        for content_type, type_sources in sources_by_type.items():
            builder.heading(2, f"{content_type.title()} Content ({len(type_sources)} items)")
            
            for i, source in enumerate(type_sources, 1):
                builder.heading(3, f"{i}. {source['title'] or 'Unknown'}")
                builder.text(f"**Source Page:** [[{source['source_page']}]]")
                builder.text(f"**URL:** {source['url']}")
                if source.get('author'):
                    builder.text(f"**Author:** {source['author']}")
                builder.text(f"**Processed:** {source['timestamp'][:10]}")
                builder.text("")  # Add space between entries
        
        # Write the page
        try:
            with open(page_path, 'w', encoding='utf-8') as f:
                f.write(builder.build())
            
            self.stats['topic_pages_created'] += 1
            self.logger.info(f"Created topic page: {page_name}")
        
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
            
            # Add blocks with their properties
            for block in page.blocks:
                # Add block properties if any
                if hasattr(block, 'properties') and block.properties:
                    for prop_key, prop_value in block.properties.items():
                        content_lines.append(f"{prop_key}:: {prop_value}")
                
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