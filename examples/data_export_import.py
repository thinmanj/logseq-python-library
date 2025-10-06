#!/usr/bin/env python3
"""
Data export and import example for the Logseq Python library.

This example demonstrates:
1. Exporting graph data to JSON
2. Analyzing exported data
3. Creating backups
4. Data transformation workflows
"""

import sys
import os
import json
from datetime import date, datetime
from pathlib import Path

# Add the parent directory to Python path so we can import logseq_py
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from logseq_py import LogseqClient


def main():
    # Replace with your actual Logseq graph path
    graph_path = "/path/to/your/logseq/graph"
    
    if not os.path.exists(graph_path):
        print(f"Graph path '{graph_path}' not found.")
        print("Please update the graph_path variable with your actual Logseq graph directory.")
        return
    
    print("📤 Logseq Python Library - Data Export/Import Example")
    print("=" * 60)
    
    client = LogseqClient(graph_path)
    client.load_graph()
    
    # Create exports directory
    exports_dir = Path("exports")
    exports_dir.mkdir(exist_ok=True)
    
    print("1️⃣  Full Graph Export")
    print("-" * 30)
    
    # Export entire graph to JSON
    export_path = exports_dir / f"logseq_export_{date.today().isoformat()}.json"
    print(f"📁 Exporting graph to: {export_path}")
    
    client.export_to_json(export_path)
    
    # Check file size
    file_size = export_path.stat().st_size
    print(f"✅ Export completed! File size: {file_size / 1024:.1f} KB")
    print()
    
    print("2️⃣  Analyzing Exported Data")
    print("-" * 30)
    
    # Load and analyze the exported JSON
    with open(export_path, 'r', encoding='utf-8') as f:
        exported_data = json.load(f)
    
    stats = exported_data['statistics']
    print(f"📊 Exported graph statistics:")
    print(f"   📄 Total pages: {stats['total_pages']}")
    print(f"   📓 Journal pages: {stats['journal_pages']}")
    print(f"   📖 Regular pages: {stats['regular_pages']}")
    print(f"   📝 Total blocks: {stats['total_blocks']}")
    print(f"   🏷️  Unique tags: {stats['total_tags']}")
    print(f"   🔗 Unique links: {stats['total_links']}")
    print()
    
    # Analyze pages
    pages = exported_data['pages']
    print(f"📄 Page analysis:")
    
    # Find largest pages (by block count)
    page_sizes = [(name, len(data['blocks'])) for name, data in pages.items()]
    page_sizes.sort(key=lambda x: x[1], reverse=True)
    
    print(f"   📈 Top 5 largest pages (by block count):")
    for page_name, block_count in page_sizes[:5]:
        print(f"      {page_name}: {block_count} blocks")
    print()
    
    # Find pages with most tags
    page_tags = [(name, len(data['tags'])) for name, data in pages.items()]
    page_tags.sort(key=lambda x: x[1], reverse=True)
    
    print(f"   🏷️  Top 5 most tagged pages:")
    for page_name, tag_count in page_tags[:5]:
        if tag_count > 0:
            page_data = pages[page_name]
            tags_str = ", ".join(page_data['tags'][:3])
            if len(page_data['tags']) > 3:
                tags_str += f" (+{len(page_data['tags']) - 3} more)"
            print(f"      {page_name}: {tag_count} tags ({tags_str})")
    print()
    
    print("3️⃣  Creating Targeted Exports")
    print("-" * 30)
    
    # Export only journal pages
    journal_pages = {
        name: data for name, data in pages.items() 
        if data['is_journal']
    }
    
    journal_export_path = exports_dir / f"journals_export_{date.today().isoformat()}.json"
    journal_export_data = {
        "export_type": "journals_only",
        "export_date": datetime.now().isoformat(),
        "pages": journal_pages,
        "statistics": {
            "total_journal_pages": len(journal_pages),
            "date_range": {
                "earliest": min([data['journal_date'] for data in journal_pages.values() if data['journal_date']]),
                "latest": max([data['journal_date'] for data in journal_pages.values() if data['journal_date']])
            }
        }
    }
    
    with open(journal_export_path, 'w', encoding='utf-8') as f:
        json.dump(journal_export_data, f, indent=2, ensure_ascii=False)
    
    print(f"📓 Exported {len(journal_pages)} journal pages to: {journal_export_path}")
    
    # Export pages with specific tags
    tagged_pages = {
        name: data for name, data in pages.items() 
        if any(tag in ['project', 'important', 'todo'] for tag in data['tags'])
    }
    
    tagged_export_path = exports_dir / f"tagged_pages_export_{date.today().isoformat()}.json"
    tagged_export_data = {
        "export_type": "tagged_pages",
        "export_date": datetime.now().isoformat(),
        "filter_tags": ['project', 'important', 'todo'],
        "pages": tagged_pages,
        "statistics": {
            "total_tagged_pages": len(tagged_pages),
            "tag_distribution": {}
        }
    }
    
    # Calculate tag distribution
    tag_dist = {}
    for data in tagged_pages.values():
        for tag in data['tags']:
            tag_dist[tag] = tag_dist.get(tag, 0) + 1
    tagged_export_data['statistics']['tag_distribution'] = tag_dist
    
    with open(tagged_export_path, 'w', encoding='utf-8') as f:
        json.dump(tagged_export_data, f, indent=2, ensure_ascii=False)
    
    print(f"🏷️  Exported {len(tagged_pages)} tagged pages to: {tagged_export_path}")
    print()
    
    print("4️⃣  Creating Data Reports")
    print("-" * 30)
    
    # Generate a comprehensive report
    report_path = exports_dir / f"logseq_report_{date.today().isoformat()}.md"
    
    report_content = f"""# Logseq Graph Report
Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Graph path: {graph_path}

## 📊 Overview Statistics
- **Total Pages**: {stats['total_pages']}
- **Journal Pages**: {stats['journal_pages']}
- **Regular Pages**: {stats['regular_pages']}
- **Total Blocks**: {stats['total_blocks']}
- **Unique Tags**: {stats['total_tags']}
- **Unique Links**: {stats['total_links']}

## 📈 Top Pages by Block Count
"""
    
    for i, (page_name, block_count) in enumerate(page_sizes[:10], 1):
        report_content += f"{i}. **{page_name}** - {block_count} blocks\\n"
    
    report_content += "\\n## 🏷️ Most Common Tags\\n"
    
    # Count all tags across all pages
    all_tags = {}
    for data in pages.values():
        for tag in data['tags']:
            all_tags[tag] = all_tags.get(tag, 0) + 1
    
    sorted_tags = sorted(all_tags.items(), key=lambda x: x[1], reverse=True)
    for i, (tag, count) in enumerate(sorted_tags[:20], 1):
        report_content += f"{i}. **#{tag}** - {count} occurrences\\n"
    
    report_content += "\\n## 🔗 Most Linked Pages\\n"
    
    # Count backlinks
    link_counts = {}
    for data in pages.values():
        for link in data['links']:
            link_counts[link] = link_counts.get(link, 0) + 1
    
    sorted_links = sorted(link_counts.items(), key=lambda x: x[1], reverse=True)
    for i, (page_name, count) in enumerate(sorted_links[:10], 1):
        report_content += f"{i}. **{page_name}** - {count} incoming links\\n"
    
    # Add journal analysis if there are journal pages
    if journal_pages:
        report_content += "\\n## 📓 Journal Analysis\\n"
        
        # Calculate journal streak and gaps
        journal_dates = sorted([
            datetime.fromisoformat(data['journal_date'].replace('Z', '+00:00')).date()
            for data in journal_pages.values() 
            if data['journal_date']
        ])
        
        if journal_dates:
            report_content += f"- **First journal entry**: {journal_dates[0]}\\n"
            report_content += f"- **Latest journal entry**: {journal_dates[-1]}\\n"
            report_content += f"- **Total journal days**: {len(journal_dates)}\\n"
            
            # Calculate gaps
            total_days = (journal_dates[-1] - journal_dates[0]).days + 1
            gaps = total_days - len(journal_dates)
            consistency = (len(journal_dates) / total_days) * 100
            report_content += f"- **Journal consistency**: {consistency:.1f}% ({gaps} gap days)\\n"
    
    report_content += f"""
## 🗂️ Export Files Created
- Full export: `{export_path.name}`
- Journal export: `{journal_export_path.name}`
- Tagged pages export: `{tagged_export_path.name}`
- This report: `{report_path.name}`

---
*Report generated by Logseq Python Library*
"""
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    print(f"📋 Generated comprehensive report: {report_path}")
    print()
    
    print("5️⃣  Data Transformation Example")
    print("-" * 30)
    
    # Transform data for external use (e.g., for a website or other tools)
    # Extract all unique tags and their descriptions
    tag_info = {}
    for page_name, data in pages.items():
        for tag in data['tags']:
            if tag not in tag_info:
                tag_info[tag] = {
                    'name': tag,
                    'pages': [],
                    'total_blocks': 0,
                    'first_seen': None,
                    'last_seen': None
                }
            
            tag_info[tag]['pages'].append(page_name)
            tag_info[tag]['total_blocks'] += len(data['blocks'])
            
            # Track dates (simplified)
            if data.get('created_at'):
                created_date = data['created_at']
                if not tag_info[tag]['first_seen'] or created_date < tag_info[tag]['first_seen']:
                    tag_info[tag]['first_seen'] = created_date
                if not tag_info[tag]['last_seen'] or created_date > tag_info[tag]['last_seen']:
                    tag_info[tag]['last_seen'] = created_date
    
    # Clean up tag info
    for tag_data in tag_info.values():
        tag_data['page_count'] = len(tag_data['pages'])
        tag_data['pages'] = tag_data['pages'][:10]  # Limit to first 10 pages
    
    tag_export_path = exports_dir / f"tag_index_{date.today().isoformat()}.json"
    with open(tag_export_path, 'w', encoding='utf-8') as f:
        json.dump({
            'export_date': datetime.now().isoformat(),
            'total_tags': len(tag_info),
            'tags': dict(sorted(tag_info.items(), key=lambda x: x[1]['page_count'], reverse=True))
        }, f, indent=2, ensure_ascii=False)
    
    print(f"🏷️  Created tag index with {len(tag_info)} tags: {tag_export_path}")
    print()
    
    print("✅ Export Operations Summary")
    print("-" * 30)
    print(f"📁 All files saved to: {exports_dir.absolute()}")
    print(f"📊 Files created:")
    for file_path in exports_dir.glob("*"):
        if file_path.is_file() and file_path.name.startswith(('logseq_', 'journals_', 'tagged_', 'tag_')):
            size_kb = file_path.stat().st_size / 1024
            print(f"   {file_path.name} ({size_kb:.1f} KB)")
    
    print()
    print("🎉 Data export example completed!")
    print("💡 These exports can be used for:")
    print("   - Creating backups")
    print("   - Analyzing your knowledge graph")
    print("   - Migrating to other tools")
    print("   - Building external applications")
    print("   - Generating reports and insights")


if __name__ == "__main__":
    main()