# 🎯 Visual Workflow Guide - Selective Analysis

## 📊 New Analysis Workflow

```
┌─────────────────────────────────────────────────────────────┐
│                    STEP 1: UPLOAD FILES                      │
│                                                              │
│  [📁 Browse and select PDF files]                           │
│                                                              │
│  Selected Files:                                             │
│  ✓ tender_document_1.pdf (120 pages)                        │
│  ✓ specifications_2024.pdf (85 pages)                       │
│  ✓ contract_terms.pdf (45 pages)                            │
│                                                              │
│  [📥 Load Documents]  [🗑️ Clear All]                        │
│                                                              │
└─────────────────────────────────────────────────────────────┘
                            ↓
                    ✅ Documents Loaded
                    (No analysis yet!)
                            ↓
┌─────────────────────────────────────────────────────────────┐
│              STEP 2: SELECT DOCUMENT                         │
│                                                              │
│  Select Document:                                            │
│  ┌──────────────────────────────────────────────┐          │
│  │ 1. tender_document_1.pdf (120 pages)     [▼] │          │
│  └──────────────────────────────────────────────┘          │
│                                                              │
│  Available documents:                                        │
│  • tender_document_1.pdf (120 pages)                        │
│  • specifications_2024.pdf (85 pages)                       │
│  • contract_terms.pdf (45 pages)                            │
│                                                              │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│         STEP 3: CHOOSE PAGE RANGE (3 OPTIONS)                │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Selection Type:                                       │  │
│  │                                                       │  │
│  │  ○ Single Page        → Analyze ONE specific page    │  │
│  │  ● Page Range         → Analyze RANGE of pages       │  │
│  │  ○ All Pages          → Analyze ENTIRE document      │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  OPTION A: Single Page                                       │
│  ┌─────────────────┐                                        │
│  │ Page Number: 25 │                                        │
│  └─────────────────┘                                        │
│  → Will analyze ONLY page 25                                │
│                                                              │
│  OPTION B: Page Range                                        │
│  ┌─────────────┐  ┌─────────────┐                          │
│  │ Start: 10   │  │ End: 20     │                          │
│  └─────────────┘  └─────────────┘                          │
│  → Will analyze pages 10, 11, 12, ... 20 (11 pages)        │
│                                                              │
│  OPTION C: All Pages                                         │
│  → Will analyze ALL 120 pages                               │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ 📊 Will analyze 11 page(s) from                      │  │
│  │    tender_document_1.pdf                             │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  [🔍 Analyze Selection]                                      │
│                                                              │
└─────────────────────────────────────────────────────────────┘
                            ↓
                    ⏳ Processing...
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                  STEP 4: VIEW RESULTS                        │
│                                                              │
│  ✅ Analysis Complete!                                       │
│                                                              │
│  • Document: tender_document_1.pdf                          │
│  • Pages Analyzed: 10 to 20 (11 pages)                     │
│  • Chunks Created: 22                                       │
│  • Vague Chunks Found: 8                                    │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ 📊 Analysis Results                                   │  │
│  │                                                        │  │
│  │ Analyzed: tender_document_1.pdf | Pages: 10-20       │  │
│  │                                                        │  │
│  │ Total Chunks: 22    Vague Chunks: 8                  │  │
│  │ Vagueness Rate: 36.4%    Avg Score: 0.65             │  │
│  │                                                        │  │
│  │ 🔎 Filter Results                                     │  │
│  │ ☐ Show all chunks                                     │  │
│  │ Min vagueness score: ━━●━━━━━━━ 0.30                 │  │
│  │                                                        │  │
│  │ 📝 Detected Vague Phrases                             │  │
│  │                                                        │  │
│  │ ▼ Chunk 3 - Score: 0.75 🚨                           │  │
│  │ ▼ Chunk 7 - Score: 0.68 ⚠️                           │  │
│  │ ▼ Chunk 12 - Score: 0.52 ⚠️                          │  │
│  │ ▶ Chunk 15 - Score: 0.45 ⚡                          │  │
│  │                                                        │  │
│  │ [Export as JSON]  [Export as CSV]                    │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
└─────────────────────────────────────────────────────────────┘
                            ↓
              ✨ Analyze more pages or
              different document as needed!
```

## 🎯 Three Analysis Scenarios

### Scenario 1: Quick Check - Single Page
```
Use Case: Someone reported vague language on page 25
Action: Select "Single Page" → Enter 25
Result: Analyze only page 25 (fastest option)
Time: ~10 seconds
Cost: Minimal (1-2 chunks)
```

### Scenario 2: Section Review - Page Range
```
Use Case: Need to review "Payment Terms" section (pages 40-50)
Action: Select "Page Range" → Start: 40, End: 50
Result: Analyze 11 pages
Time: ~1 minute
Cost: Low (20-25 chunks)
```

### Scenario 3: Full Document - All Pages
```
Use Case: Complete audit of small document
Action: Select "All Pages"
Result: Analyze entire 45-page document
Time: ~3-5 minutes
Cost: Medium (90-100 chunks)
```

## 📈 Performance Comparison

### Large Document (100 pages)

**Old Method (Analyze All):**
```
┌─────────────────────────────────────┐
│ Upload → Analyze Everything         │
│                                     │
│ Processing: ████████████████  100% │
│ Time: 10 minutes                    │
│ Chunks: 200                         │
│ API Calls: 200                      │
│ Cost: High                          │
└─────────────────────────────────────┘
```

**New Method (Selective - Pages 10-15):**
```
┌─────────────────────────────────────┐
│ Upload → Select Pages 10-15         │
│                                     │
│ Processing: ██  6% of document      │
│ Time: 1 minute                      │
│ Chunks: 12                          │
│ API Calls: 12                       │
│ Cost: 94% lower!                    │
└─────────────────────────────────────┘
```

## 🔄 Multi-Document Workflow

### Analyzing Multiple Documents

```
Document 1: tender_main.pdf (120 pages)
├─ First: Analyze pages 1-10 (Introduction)
├─ Then: Analyze pages 50-60 (Payment Terms)
└─ Finally: Analyze pages 110-120 (Appendix)

Document 2: technical_specs.pdf (85 pages)
├─ First: Analyze page 25 (specific section)
└─ Then: Analyze pages 70-85 (Compliance)

Document 3: contract.pdf (45 pages)
└─ Analyze all pages (smaller document)

Total analyzed: 47 pages out of 250 (only 19%!)
Time saved: ~15 minutes
Cost saved: ~80%
```

## 💡 Smart Analysis Strategies

### Strategy 1: Critical Sections First
```
1. Load all tender documents
2. Identify critical sections (Payment, Penalties, Scope)
3. Analyze only those specific page ranges
4. Export results for review
5. Analyze additional sections if needed
```

### Strategy 2: Problem-Driven Analysis
```
1. Stakeholder reports issue on specific page
2. Load that document
3. Analyze single problematic page
4. If issues found, expand to surrounding pages
5. Repeat for other reported problems
```

### Strategy 3: Incremental Review
```
Week 1: Analyze pages 1-20 of all documents
Week 2: Analyze pages 21-40 of all documents
Week 3: Analyze pages 41-60 of all documents
...
Continuous: Build up complete analysis over time
```

## 🎨 UI Elements Explained

### Load Documents Button
```
[📥 Load Documents]
↓
• Extracts text from PDFs
• No AI analysis yet
• Fast operation (seconds)
• Prepares for selection
```

### Document Selector
```
[1. tender.pdf (120 pages) ▼]
↓
• Shows all loaded documents
• Displays page count
• Switch between documents easily
```

### Page Selection Types
```
○ Single Page    → Best for: Quick checks, specific issues
● Page Range     → Best for: Sections, chapters, ranges
○ All Pages      → Best for: Small docs, complete audits
```

### Analyze Selection Button
```
[🔍 Analyze Selection]
↓
• Runs Gemini AI analysis
• Only on selected pages
• Shows progress
• Displays results
```

## 🏆 Best Practices

### ✅ DO:
- Start with small page ranges to test
- Analyze critical sections first
- Use single page for quick verification
- Load all documents once, analyze selectively
- Export results after each analysis

### ❌ DON'T:
- Analyze all pages of large documents unnecessarily
- Process entire 100+ page docs at once
- Forget to select page range before analyzing
- Re-upload documents for each analysis

## 📊 Time & Cost Calculator

### Your Document: ___ pages

**Option 1: Analyze All Pages**
- Time: Pages ÷ 10 = ___ minutes
- Chunks: Pages × 2 = ___ chunks
- API Calls: ___ calls
- Cost: Approx $___ 

**Option 2: Selective (10 pages)**
- Time: ~1 minute
- Chunks: ~20 chunks
- API Calls: ~20 calls
- Cost: Approx $0.02

**Savings: ___%**

## 🎯 Quick Reference

| Action | Button/Control | Result |
|--------|---------------|---------|
| Upload PDFs | Browse Files | Files ready to load |
| Load text | 📥 Load Documents | Text extracted, ready to select |
| Choose document | Dropdown menu | Document selected |
| Single page | Radio + Number input | One page selected |
| Page range | Radio + Two number inputs | Range selected |
| All pages | Radio button | Entire doc selected |
| Start analysis | 🔍 Analyze Selection | AI processes selected pages |
| View results | Automatic | Results displayed below |
| Export | Export buttons | Save as JSON/CSV |
| Clear | 🗑️ Clear All | Reset everything |

---

**With selective analysis, you have complete control over what gets analyzed, when, and how much it costs!** 🎉
