"""
Performance Comparison Demo
Shows the difference between old (analyze all) vs new (selective) approach
"""

import time
from datetime import timedelta


def format_time(seconds):
    """Format seconds into readable time"""
    return str(timedelta(seconds=int(seconds)))


def calculate_metrics(pages, chunks_per_page=2, seconds_per_chunk=3):
    """Calculate processing metrics"""
    total_chunks = pages * chunks_per_page
    total_time = total_chunks * seconds_per_chunk
    api_calls = total_chunks
    estimated_cost = total_chunks * 0.001  # $0.001 per call estimate
    
    return {
        'pages': pages,
        'chunks': total_chunks,
        'time_seconds': total_time,
        'time_formatted': format_time(total_time),
        'api_calls': api_calls,
        'cost': estimated_cost
    }


def print_comparison():
    """Print comparison between old and new approaches"""
    
    print("=" * 70)
    print("PERFORMANCE COMPARISON: Old vs New Approach")
    print("=" * 70)
    
    # Scenario: 100-page document
    doc_pages = 100
    
    print(f"\nScenario: Analyzing a {doc_pages}-page tender document\n")
    
    # OLD APPROACH: Analyze all pages
    print("🔴 OLD APPROACH: Analyze Everything At Once")
    print("-" * 70)
    old_metrics = calculate_metrics(doc_pages)
    
    print(f"Pages Analyzed:     {old_metrics['pages']} pages (ALL)")
    print(f"Chunks Created:     {old_metrics['chunks']} chunks")
    print(f"Processing Time:    {old_metrics['time_formatted']}")
    print(f"API Calls:          {old_metrics['api_calls']} calls")
    print(f"Estimated Cost:     ${old_metrics['cost']:.2f}")
    print(f"User Control:       ❌ None - processes everything")
    print(f"Flexibility:        ❌ All or nothing")
    
    print("\n" + "=" * 70)
    
    # NEW APPROACH: Selective analysis
    selected_pages = 5  # Analyze only 5 pages
    
    print("\n🟢 NEW APPROACH: Selective Analysis (5 pages)")
    print("-" * 70)
    new_metrics = calculate_metrics(selected_pages)
    
    print(f"Pages Analyzed:     {new_metrics['pages']} pages (Selected: 10-15)")
    print(f"Chunks Created:     {new_metrics['chunks']} chunks")
    print(f"Processing Time:    {new_metrics['time_formatted']}")
    print(f"API Calls:          {new_metrics['api_calls']} calls")
    print(f"Estimated Cost:     ${new_metrics['cost']:.2f}")
    print(f"User Control:       ✅ Full - choose any pages")
    print(f"Flexibility:        ✅ Single page, range, or all")
    
    # Calculate improvements
    time_saved = old_metrics['time_seconds'] - new_metrics['time_seconds']
    time_saved_pct = (time_saved / old_metrics['time_seconds']) * 100
    
    cost_saved = old_metrics['cost'] - new_metrics['cost']
    cost_saved_pct = (cost_saved / old_metrics['cost']) * 100
    
    print("\n" + "=" * 70)
    print("📊 IMPROVEMENTS")
    print("=" * 70)
    print(f"Time Saved:         {format_time(time_saved)} ({time_saved_pct:.1f}% faster)")
    print(f"Cost Saved:         ${cost_saved:.2f} ({cost_saved_pct:.1f}% cheaper)")
    print(f"API Calls Saved:    {old_metrics['api_calls'] - new_metrics['api_calls']} calls")
    print(f"Efficiency Gain:    {old_metrics['pages'] / new_metrics['pages']:.1f}x better")
    
    # Multiple scenarios
    print("\n" + "=" * 70)
    print("📈 DIFFERENT SCENARIOS")
    print("=" * 70)
    
    scenarios = [
        ("Single page check", 1),
        ("Small section", 5),
        ("Medium section", 10),
        ("Large section", 20),
        ("Half document", 50),
        ("Full document", 100)
    ]
    
    print(f"\n{'Scenario':<20} {'Pages':<10} {'Time':<15} {'Cost':<10} {'vs Full Doc':<15}")
    print("-" * 70)
    
    full_doc_time = calculate_metrics(doc_pages)['time_seconds']
    
    for scenario_name, pages in scenarios:
        metrics = calculate_metrics(pages)
        time_ratio = (pages / doc_pages) * 100
        
        print(f"{scenario_name:<20} {pages:<10} {metrics['time_formatted']:<15} "
              f"${metrics['cost']:<9.2f} {time_ratio:.1f}% of full")
    
    # Real-world example
    print("\n" + "=" * 70)
    print("🌟 REAL-WORLD EXAMPLE")
    print("=" * 70)
    print("""
Task: Review payment terms section in a 150-page contract

OLD APPROACH:
- Must analyze entire 150-page document
- Time: ~25 minutes
- Cost: ~$0.30
- Can't skip irrelevant sections
- ❌ Inefficient

NEW APPROACH:
- Identify payment terms section: pages 75-85 (11 pages)
- Select page range: 75 to 85
- Click "Analyze Selection"
- Time: ~2 minutes
- Cost: ~$0.02
- ✅ Direct to what matters

RESULT: 92% time saved, 93% cost saved!
""")
    
    # Multiple documents example
    print("\n" + "=" * 70)
    print("📚 MULTIPLE DOCUMENTS STRATEGY")
    print("=" * 70)
    print("""
You have: 5 tender documents (100 pages each = 500 total pages)

SMART APPROACH:
1. Load all 5 documents (1 minute)
2. Analyze critical sections only:
   - Doc 1: Pages 10-15 (payment terms)
   - Doc 2: Pages 30-35 (penalties) 
   - Doc 3: Pages 50-55 (scope)
   - Doc 4: Pages 20-25 (timeline)
   - Doc 5: Pages 40-45 (compliance)

Total pages analyzed: 30 pages (6% of total)
Time: ~3 minutes
Cost: ~$0.06

vs OLD APPROACH:
Analyze all 500 pages
Time: ~83 minutes  
Cost: ~$1.00

SAVINGS: 97% time saved, 94% cost saved!
""")
    
    print("\n" + "=" * 70)
    print("✨ CONCLUSION")
    print("=" * 70)
    print("""
The new selective analysis feature makes the system practical for:
✅ Large documents (100+ pages)
✅ Multiple documents  
✅ Quick spot checks
✅ Budget-conscious projects
✅ Time-sensitive reviews
✅ Incremental analysis

You now have COMPLETE CONTROL over:
- Which document to analyze
- Which pages to process
- How much to spend
- How long it takes

Perfect for real-world tender document analysis! 🎉
""")


if __name__ == "__main__":
    print_comparison()
    
    # Interactive calculator
    print("\n" + "=" * 70)
    print("💡 CALCULATE YOUR OWN SAVINGS")
    print("=" * 70)
    
    try:
        total_pages = int(input("\nHow many pages is your document? "))
        pages_to_analyze = int(input("How many pages do you want to analyze? "))
        
        if pages_to_analyze > total_pages:
            print("Error: Can't analyze more pages than document has!")
        else:
            print("\n" + "-" * 70)
            
            full_metrics = calculate_metrics(total_pages)
            selective_metrics = calculate_metrics(pages_to_analyze)
            
            print(f"\nFull Document ({total_pages} pages):")
            print(f"  Time: {full_metrics['time_formatted']}")
            print(f"  Cost: ${full_metrics['cost']:.2f}")
            
            print(f"\nYour Selection ({pages_to_analyze} pages):")
            print(f"  Time: {selective_metrics['time_formatted']}")
            print(f"  Cost: ${selective_metrics['cost']:.2f}")
            
            time_saved = full_metrics['time_seconds'] - selective_metrics['time_seconds']
            cost_saved = full_metrics['cost'] - selective_metrics['cost']
            
            time_saved_pct = (time_saved / full_metrics['time_seconds']) * 100
            cost_saved_pct = (cost_saved / full_metrics['cost']) * 100
            
            print(f"\nYou save:")
            print(f"  ⏱️  {format_time(time_saved)} ({time_saved_pct:.1f}%)")
            print(f"  💰 ${cost_saved:.2f} ({cost_saved_pct:.1f}%)")
            print("\n✨ Use selective analysis for maximum efficiency!")
            
    except (ValueError, KeyboardInterrupt):
        print("\n\nThanks for checking out the comparison!")
    
    print("\n" + "=" * 70)
    print("Run the Streamlit app to try selective analysis now!")
    print("Command: python run.py")
    print("=" * 70)
