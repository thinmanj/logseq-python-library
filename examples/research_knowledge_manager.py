#!/usr/bin/env python3

"""
Research Knowledge Management System

This example demonstrates realistic knowledge management workflows:
- Processing research papers and notes
- Creating literature reviews
- Tracking reading progress
- Generating citation networks
- Building concept maps
"""

import sys
import json
from pathlib import Path
from datetime import datetime, date, timedelta
from collections import defaultdict, Counter
import re

sys.path.append('..')

from logseq_py import LogseqClient
from logseq_py.builders import (
    PageBuilder, TaskBuilder, CodeBlockBuilder, QueryBuilder, 
    TableBuilder, ListBuilder, QuoteBuilder
)

class ResearchKnowledgeManager:
    """Manages research content and generates insights."""
    
    def __init__(self, graph_path: str):
        self.graph_path = Path(graph_path)
        self.client = LogseqClient(graph_path)
    
    def setup_research_system(self):
        """Set up a comprehensive research knowledge management system."""
        print("📚 Setting up research knowledge management system...")
        
        with self.client as client:
            # Create sample research content
            self._create_research_papers(client)
            
            # Create reading lists and progress tracking
            self._create_reading_management(client)
            
            # Generate literature review tools
            self._create_literature_review_tools(client)
            
            # Create citation network analysis
            self._create_citation_network(client)
            
            # Build concept mapping
            self._create_concept_maps(client)
            
            # Create research project tracking
            self._create_project_tracking(client)
        
        print("✅ Research system setup complete!")
    
    def _create_research_papers(self, client):
        """Create sample research papers with realistic academic content."""
        print("📄 Creating sample research papers...")
        
        papers = [
            {
                "title": "Machine Learning in Natural Language Processing: A Survey",
                "authors": ["Smith, J.", "Johnson, A.", "Williams, M."],
                "year": 2023,
                "journal": "Journal of Artificial Intelligence",
                "tags": ["machine-learning", "nlp", "survey", "deep-learning"],
                "concepts": ["transformer-architecture", "attention-mechanisms", "bert", "gpt"],
                "abstract": "This paper provides a comprehensive survey of machine learning techniques in natural language processing, covering recent advances in transformer architectures and their applications.",
                "key_findings": [
                    "Transformer models have revolutionized NLP tasks",
                    "Self-attention mechanisms enable better long-range dependencies",
                    "Pre-trained models significantly improve downstream task performance"
                ],
                "related_work": ["Attention Is All You Need", "BERT: Pre-training Bidirectional Transformers"],
                "notes": "Excellent overview paper. Key insights on attention mechanisms particularly relevant to my work."
            },
            {
                "title": "Ethical Considerations in AI Development",
                "authors": ["Brown, L.", "Davis, K."],
                "year": 2023,
                "journal": "AI Ethics Quarterly",
                "tags": ["ai-ethics", "bias", "fairness", "responsible-ai"],
                "concepts": ["algorithmic-bias", "fairness-metrics", "explainable-ai"],
                "abstract": "An examination of ethical challenges in AI development, focusing on bias detection and mitigation strategies.",
                "key_findings": [
                    "Bias can be introduced at multiple stages of ML pipeline",
                    "Fairness metrics often conflict with each other",
                    "Explainability vs. performance trade-offs are significant"
                ],
                "related_work": ["Fairness through Awareness", "The Ethical Algorithm"],
                "notes": "Important considerations for any AI system deployment. Need to implement these checks."
            },
            {
                "title": "Quantum Computing Applications in Optimization",
                "authors": ["Wilson, R.", "Taylor, S.", "Anderson, P."],
                "year": 2024,
                "journal": "Quantum Information Science",
                "tags": ["quantum-computing", "optimization", "algorithms"],
                "concepts": ["quantum-annealing", "variational-algorithms", "qaoa"],
                "abstract": "Explores practical applications of quantum computing in solving complex optimization problems.",
                "key_findings": [
                    "Quantum advantage demonstrated for specific optimization classes",
                    "NISQ devices show promise for near-term applications",
                    "Hybrid classical-quantum approaches most practical currently"
                ],
                "related_work": ["Quantum Approximate Optimization Algorithm", "Variational Quantum Eigensolver"],
                "notes": "Fascinating potential, but still early stage for practical applications."
            }
        ]
        
        for paper_data in papers:
            self._create_paper_page(client, paper_data)
    
    def _create_paper_page(self, client, paper_data):
        """Create a detailed page for a research paper."""
        title = paper_data["title"]
        
        paper_page = (PageBuilder(f"📄 {title}")
                     .author("Research Manager")
                     .created()
                     .page_type("research-paper")
                     .category("literature")
                     .tags(*paper_data["tags"])
                     .property("year", paper_data["year"])
                     .property("journal", paper_data["journal"])
                     .property("authors", ", ".join(paper_data["authors"]))
                     .property("status", "read")
                     
                     .heading(1, f"📄 {title}")
                     .text(f"**Authors**: {', '.join(paper_data['authors'])}")
                     .text(f"**Journal**: {paper_data['journal']} ({paper_data['year']})")
                     .text(f"**Tags**: {' '.join(f'#{tag}' for tag in paper_data['tags'])}")
                     .empty_line()
                     
                     .heading(2, "📝 Abstract")
                     .text(paper_data["abstract"])
                     .empty_line()
                     
                     .heading(2, "🔍 Key Findings"))
        
        # Add key findings as bullet list
        findings_list = ListBuilder("bullet")
        for finding in paper_data["key_findings"]:
            findings_list.item(finding)
        paper_page.add(findings_list)
        
        # Add concepts section
        paper_page.empty_line().heading(2, "💡 Key Concepts")
        concepts_list = ListBuilder("bullet")
        for concept in paper_data["concepts"]:
            concepts_list.item(f"[[{concept}]] #{concept.replace('-', '_')}")
        paper_page.add(concepts_list)
        
        # Add related work
        paper_page.empty_line().heading(2, "📚 Related Work")
        related_list = ListBuilder("bullet")
        for related in paper_data["related_work"]:
            related_list.item(f"[[📄 {related}]]")
        paper_page.add(related_list)
        
        # Add personal notes section
        paper_page.empty_line().heading(2, "📝 Personal Notes")
        
        notes_quote = paper_page.quote()
        notes_quote.line(paper_data["notes"])
        notes_quote.line("")
        notes_quote.line(f"*Reviewed on {date.today().strftime('%Y-%m-%d')}*")
        
        # Add reading status task
        paper_page.empty_line().heading(2, "✅ Reading Progress")
        paper_page.add(TaskBuilder("Review and summarize key points").done())
        paper_page.add(TaskBuilder("Add to literature review").todo().medium_priority())
        paper_page.add(TaskBuilder("Identify connections with other papers").todo().low_priority())
        
        client.create_page(f"📄 {title}", paper_page.build())
    
    def _create_reading_management(self, client):
        """Create reading lists and progress tracking systems."""
        print("📚 Creating reading management system...")
        
        # Current reading list
        reading_list = (PageBuilder("📚 Research Reading List")
                       .author("Research Manager")
                       .created()
                       .page_type("reading-list")
                       .tags("reading", "research", "todo")
                       
                       .heading(1, "📚 Research Reading List")
                       .text("Organized reading pipeline for research papers")
                       .empty_line()
                       
                       .heading(2, "🎯 Currently Reading"))
        
        current_list = ListBuilder("bullet")
        current_list.item("[[📄 Machine Learning in Natural Language Processing: A Survey]] - 80% complete")
        current_list.item("[[📄 Ethical Considerations in AI Development]] - Started notes section", 1)
        reading_list.add(current_list)
        
        reading_list.empty_line().heading(2, "📋 Priority Queue")
        
        # High priority papers to read
        priority_list = ListBuilder("bullet")
        priority_list.item("**High Priority**:")
        priority_list.item("[[📄 Quantum Computing Applications in Optimization]] - Relevant to current project", 1)
        priority_list.item("[[📄 Attention Is All You Need]] - Foundational transformer paper", 1)
        priority_list.item("**Medium Priority**:", 1)
        priority_list.item("[[📄 BERT: Pre-training Bidirectional Transformers]] - Follow-up to attention paper", 2)
        priority_list.item("[[📄 The Ethical Algorithm]] - Ethics deep dive", 2)
        reading_list.add(priority_list)
        
        # Add reading statistics
        reading_list.empty_line().heading(2, "📊 Reading Statistics")
        
        stats_table = (reading_list.table()
                      .headers("Metric", "This Month", "Total")
                      .row("Papers Read", "3", "47")
                      .row("Papers Noted", "2", "38") 
                      .row("Concepts Learned", "15", "234")
                      .row("Hours Reading", "12.5", "156.2"))
        
        # Add smart queries for reading management
        reading_list.empty_line().heading(2, "🔍 Smart Queries")
        
        queries_list = ListBuilder("bullet")
        queries_list.item("**Papers to Review**:")
        queries_list.item("```query", 1)
        queries_list.item("(and (page-property :page-type \"research-paper\") (task TODO))", 2)
        queries_list.item("```", 1)
        
        queries_list.item("**Recently Added Papers** (last 30 days):")
        queries_list.item("```query", 1)
        queries_list.item(f"(and (page-property :page-type \"research-paper\") (between [[{(date.today() - timedelta(days=30)).strftime('%Y-%m-%d')}]] [[{date.today().strftime('%Y-%m-%d')}]]))", 2)
        queries_list.item("```", 1)
        
        reading_list.add(queries_list)
        
        client.create_page("📚 Research Reading List", reading_list.build())
    
    def _create_literature_review_tools(self, client):
        """Create tools for generating literature reviews."""
        print("📝 Creating literature review tools...")
        
        lit_review = (PageBuilder("📝 Literature Review: AI & Ethics")
                     .author("Research Manager")
                     .created()
                     .page_type("literature-review")
                     .tags("literature-review", "ai-ethics", "survey")
                     
                     .heading(1, "📝 Literature Review: AI & Ethics")
                     .text("Comprehensive review of current research on AI ethics and fairness")
                     .empty_line()
                     
                     .heading(2, "🎯 Research Question")
                     .text("How can we develop and deploy AI systems that are both performant and ethically responsible?")
                     .empty_line()
                     
                     .heading(2, "📚 Key Papers"))
        
        # Organize papers by theme
        themes_list = ListBuilder("bullet")
        themes_list.item("**Bias Detection & Mitigation**:")
        themes_list.item("[[📄 Ethical Considerations in AI Development]] - Comprehensive framework for bias detection", 1)
        themes_list.item("[[📄 Fairness through Awareness]] - Mathematical foundations of fairness metrics", 1)
        
        themes_list.item("**Explainable AI**:")
        themes_list.item("[[📄 The Ethical Algorithm]] - Trade-offs between explainability and performance", 1)
        themes_list.item("[[📄 Interpreting Machine Learning Models]] - Practical approaches to model interpretation", 1)
        
        themes_list.item("**Practical Implementation**:")
        themes_list.item("[[📄 Building Fair AI Systems]] - Industry case studies and lessons learned", 1)
        lit_review.add(themes_list)
        
        # Add synthesis section
        lit_review.empty_line().heading(2, "🔗 Synthesis & Gaps")
        
        synthesis_list = ListBuilder("bullet")
        synthesis_list.item("**Common Themes**:")
        synthesis_list.item("Bias can emerge at any stage of the ML pipeline", 1)
        synthesis_list.item("Multiple fairness definitions often conflict", 1)
        synthesis_list.item("Trade-offs between fairness, accuracy, and interpretability", 1)
        
        synthesis_list.item("**Research Gaps**:")
        synthesis_list.item("Limited real-world deployment studies", 1)
        synthesis_list.item("Lack of standardized evaluation frameworks", 1)
        synthesis_list.item("Insufficient interdisciplinary collaboration", 1)
        
        lit_review.add(synthesis_list)
        
        # Add future work section
        lit_review.empty_line().heading(2, "🚀 Future Research Directions")
        
        future_list = ListBuilder("bullet")
        future_list.item("Develop automated bias detection tools")
        future_list.item("Create standardized fairness benchmarks")
        future_list.item("Study long-term societal impacts")
        future_list.item("Bridge technical and policy communities")
        
        lit_review.add(future_list)
        
        client.create_page("📝 Literature Review: AI & Ethics", lit_review.build())
    
    def _create_citation_network(self, client):
        """Create citation network analysis."""
        print("🕸️ Creating citation network analysis...")
        
        citation_network = (PageBuilder("🕸️ Citation Network Analysis")
                          .author("Research Manager")  
                          .created()
                          .page_type("analysis")
                          .tags("citations", "network-analysis", "research-mapping")
                          
                          .heading(1, "🕸️ Research Citation Network")
                          .text("Visual analysis of paper relationships and citation patterns")
                          .empty_line()
                          
                          .heading(2, "🎯 Key Influencers"))
        
        influencers_list = ListBuilder("bullet")
        influencers_list.item("**Most Cited Papers in My Collection**:")
        influencers_list.item("[[📄 Attention Is All You Need]] - 47,000+ citations, foundational transformer work", 1)
        influencers_list.item("[[📄 BERT: Pre-training Bidirectional Transformers]] - 25,000+ citations", 1)
        influencers_list.item("[[📄 Fairness through Awareness]] - 3,200+ citations", 1)
        
        influencers_list.item("**Emerging Hot Topics**:")
        influencers_list.item("Quantum machine learning applications", 1)
        influencers_list.item("Federated learning privacy", 1)
        influencers_list.item("AI governance frameworks", 1)
        
        citation_network.add(influencers_list)
        
        # Citation relationships
        citation_network.empty_line().heading(2, "🔗 Citation Relationships")
        
        relationships_table = (citation_network.table()
                             .headers("Paper A", "Paper B", "Relationship", "Strength")
                             .row("[[📄 Machine Learning in Natural Language Processing: A Survey]]", 
                                  "[[📄 Attention Is All You Need]]", "Cites", "High")
                             .row("[[📄 Ethical Considerations in AI Development]]", 
                                  "[[📄 Fairness through Awareness]]", "Builds on", "Medium")
                             .row("[[📄 Quantum Computing Applications in Optimization]]", 
                                  "[[📄 Variational Quantum Eigensolver]]", "Extends", "High"))
        
        # Research clusters
        citation_network.empty_line().heading(2, "🎨 Research Clusters")
        
        clusters_list = ListBuilder("bullet")
        clusters_list.item("**Natural Language Processing Cluster**:")
        clusters_list.item("Core: Transformer architectures, attention mechanisms", 1)
        clusters_list.item("Papers: 8 | Avg. Citation: 15,000 | Growth: High", 1)
        
        clusters_list.item("**AI Ethics Cluster**:")
        clusters_list.item("Core: Fairness, bias detection, explainability", 1)
        clusters_list.item("Papers: 5 | Avg. Citation: 2,800 | Growth: Very High", 1)
        
        clusters_list.item("**Quantum Computing Cluster**:")
        clusters_list.item("Core: Quantum algorithms, optimization applications", 1)
        clusters_list.item("Papers: 3 | Avg. Citation: 450 | Growth: Emerging", 1)
        
        citation_network.add(clusters_list)
        
        client.create_page("🕸️ Citation Network Analysis", citation_network.build())
    
    def _create_concept_maps(self, client):
        """Create concept mapping pages."""
        print("🗺️ Creating concept maps...")
        
        # Transformer architecture concept map
        transformer_map = (PageBuilder("🗺️ Concept Map: Transformer Architecture")
                          .author("Research Manager")
                          .created()
                          .page_type("concept-map")
                          .tags("transformers", "architecture", "concept-map")
                          
                          .heading(1, "🗺️ Transformer Architecture Concepts")
                          .text("Hierarchical breakdown of transformer model components")
                          .empty_line()
                          
                          .heading(2, "🏗️ Architecture Overview"))
        
        # Create hierarchical concept structure
        arch_list = ListBuilder("bullet")
        arch_list.item("**[[transformer-architecture]]** - Core model design")
        arch_list.item("**[[attention-mechanisms]]** - Key innovation", 1)
        arch_list.item("[[self-attention]] - Attention within sequence", 2)
        arch_list.item("[[multi-head-attention]] - Parallel attention computation", 2)
        arch_list.item("[[scaled-dot-product-attention]] - Mathematical formulation", 2)
        
        arch_list.item("**[[encoder-decoder-structure]]** - Model organization", 1)
        arch_list.item("[[encoder-stack]] - Input processing layers", 2)
        arch_list.item("[[decoder-stack]] - Output generation layers", 2)
        arch_list.item("[[feed-forward-networks]] - Position-wise processing", 2)
        
        arch_list.item("**[[positional-encoding]]** - Sequence order information", 1)
        arch_list.item("[[sinusoidal-encoding]] - Original approach", 2)
        arch_list.item("[[learned-positional-embeddings]] - Trainable alternative", 2)
        
        transformer_map.add(arch_list)
        
        # Add concept relationships
        transformer_map.empty_line().heading(2, "🔗 Concept Relationships")
        
        relations_table = (transformer_map.table()
                          .headers("Concept A", "Relationship", "Concept B", "Description")
                          .row("[[attention-mechanisms]]", "enables", "[[self-attention]]", "Core mechanism")
                          .row("[[multi-head-attention]]", "parallelizes", "[[self-attention]]", "Multiple attention heads")
                          .row("[[encoder-stack]]", "feeds into", "[[decoder-stack]]", "Information flow")
                          .row("[[positional-encoding]]", "adds to", "[[input-embeddings]]", "Position information"))
        
        client.create_page("🗺️ Concept Map: Transformer Architecture", transformer_map.build())
    
    def _create_project_tracking(self, client):
        """Create research project tracking system."""
        print("🎯 Creating project tracking system...")
        
        project = (PageBuilder("🎯 Research Project: Ethical NLP Systems")
                  .author("Research Manager")
                  .created()
                  .page_type("research-project")
                  .tags("research-project", "nlp", "ethics")
                  .property("status", "active")
                  .property("start-date", "2024-01-15")
                  .property("deadline", "2024-06-30")
                  .property("funding", "NSF Grant #12345")
                  
                  .heading(1, "🎯 Research Project: Ethical NLP Systems")
                  .text("Developing bias-aware natural language processing models")
                  .empty_line()
                  
                  .heading(2, "🎯 Project Objectives"))
        
        objectives_list = ListBuilder("bullet")
        objectives_list.item("Develop automated bias detection for NLP models")
        objectives_list.item("Create fairness-aware training algorithms")  
        objectives_list.item("Build evaluation framework for ethical NLP")
        objectives_list.item("Publish findings in top-tier venues")
        
        project.add(objectives_list)
        
        # Research phases
        project.empty_line().heading(2, "📅 Research Phases")
        
        phases_table = (project.table()
                       .headers("Phase", "Timeline", "Status", "Key Deliverables")
                       .row("Literature Review", "Jan-Feb 2024", "✅ Complete", "Survey paper draft")
                       .row("Method Development", "Mar-Apr 2024", "🔄 In Progress", "Bias detection algorithm")
                       .row("Experimental Validation", "May 2024", "⏳ Pending", "Benchmark results")
                       .row("Paper Writing", "Jun 2024", "⏳ Pending", "Conference submission"))
        
        # Current tasks
        project.empty_line().heading(2, "✅ Current Tasks")
        
        project.add(TaskBuilder("Complete bias detection algorithm implementation").doing().high_priority()
                   .scheduled("2024-04-15").effort("2w"))
        project.add(TaskBuilder("Run experiments on benchmark datasets").todo().high_priority()
                   .scheduled("2024-04-30").effort("1w"))
        project.add(TaskBuilder("Draft methodology section").todo().medium_priority()
                   .effort("3d"))
        project.add(TaskBuilder("Prepare conference presentation slides").later().low_priority())
        
        # Related papers
        project.empty_line().heading(2, "📚 Related Literature")
        
        papers_list = ListBuilder("bullet")
        papers_list.item("**Core References**:")
        papers_list.item("[[📄 Ethical Considerations in AI Development]] - Bias detection framework", 1)
        papers_list.item("[[📄 Machine Learning in Natural Language Processing: A Survey]] - NLP overview", 1)
        
        papers_list.item("**Methodological Papers**:")
        papers_list.item("[[📄 Fairness through Awareness]] - Mathematical foundations", 1)
        papers_list.item("[[📄 Building Fair AI Systems]] - Implementation guidelines", 1)
        
        project.add(papers_list)
        
        client.create_page("🎯 Research Project: Ethical NLP Systems", project.build())

def main():
    """Set up the research knowledge management system."""
    demo_path = Path("examples/logseq-demo")
    
    if not demo_path.exists():
        print("❌ Demo not found. Run generate_logseq_demo.py first!")
        return
    
    research_manager = ResearchKnowledgeManager(demo_path)
    research_manager.setup_research_system()
    
    print(f"\n🎉 Research system ready! Open your Logseq graph at: {demo_path}")
    print("📚 New research pages created:")
    print("  - 📚 Research Reading List")
    print("  - 📄 [Research Papers] (3 sample papers)")
    print("  - 📝 Literature Review: AI & Ethics")
    print("  - 🕸️ Citation Network Analysis")
    print("  - 🗺️ Concept Map: Transformer Architecture")
    print("  - 🎯 Research Project: Ethical NLP Systems")

if __name__ == "__main__":
    main()