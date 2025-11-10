# MTP Version 2 - Agentic Vagueness Detection System

An intelligent system that automatically detects and explains vague, ambiguous, or poorly defined language in technical and tender documents using AI agents, RAG pipelines, and reference standards.

## 🌟 Features

- **Selective Document Analysis**: Choose specific documents and page ranges to analyze (NEW!)
- **Automatic Vagueness Detection**: Uses Gemini AI to identify vague, ambiguous language across 5 categories
- **RAG-Based Context Retrieval**: Searches reference documents (IS Codes, CPWD manuals) for precise definitions
- **AI-Powered Suggestions**: Generates specific, actionable improvements based on standards
- **Interactive Web Interface**: User-friendly Streamlit application with targeted analysis controls
- **Expert Validation**: Compare model outputs with expert ratings
- **Performance Optimized**: Analyze only what you need - single pages, page ranges, or full documents

## 📋 System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        User Interface (Streamlit)                │
└─────────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  Document    │     │  Vagueness   │     │     RAG      │
│  Processing  │     │   Detection  │     │  Suggestion  │
│    Agent     │     │    Agent     │     │    Engine    │
└──────────────┘     └──────────────┘     └──────────────┘
        │                     │                     │
        └─────────────────────┼─────────────────────┘
                              ▼
                    ┌──────────────────┐
                    │   Vector DB      │
                    │   (ChromaDB)     │
                    └──────────────────┘
```

## 🔍 Vagueness Categories

The system detects 5 types of vagueness:

1. **Abstractness & Subjective Language**: Subjective terms needing interpretation
   - Examples: "quality materials", "reasonable price", "user friendly"

2. **Ambiguous Modifiers & Comparative Phrases**: Fuzzy concepts without objective bounds
   - Examples: "faster than", "better performance", "approximately"

3. **Referent Ambiguity & Complex Noun Phrases**: Unclear actors or referents
   - Examples: "it should be done", "implementation of plan"

4. **Open-Ended / Non-Verifiable Terms**: Conditional phrasing creating loopholes
   - Examples: "if feasible", "where possible", "not limited to"

5. **Negative & Passive Structures**: Passive voice reducing clarity
   - Examples: "Payment will be issued", "should not exceed"

## 🚀 Installation

### Prerequisites

- Python 3.8 or higher
- Google Gemini API key

### Setup

1. **Clone the repository**
```bash
git clone <repository-url>
cd mtp_v2
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure API key**
   
   Create a `.env` file in the root directory:
   ```
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

   Or enter it directly in the Streamlit interface.

4. **Create necessary directories**
```bash
mkdir -p data/raw_docs data/reference_docs data/embeddings outputs/reports
```

## 📖 Usage

### Running the Streamlit Application

```bash
cd src/app
streamlit run streamlit_frontend.py
```

The application will open in your browser at `http://localhost:8501`

### Workflow

#### Step 1: Upload Reference Documents
1. Go to the "📚 Reference Documents" tab
2. Upload IS Codes, CPWD manuals, or other technical standards (PDF format)
3. Click "Process Reference Documents"
4. Wait for processing to complete

#### Step 2: Analyze Tender Documents
1. Go to the "🔍 Detect Vagueness" tab
2. Upload tender/specification documents (PDF format)
3. Click "Analyze Documents"
4. View detected vague phrases with scores and explanations

#### Step 3: Generate Suggestions
1. Go to the "💡 Generate Suggestions" tab
2. Click "Generate Suggestions"
3. Review AI-generated improvements based on reference standards
4. Export results as JSON or CSV

### Configuration Options

**Sidebar Settings:**
- **Gemini API Key**: Your Google Gemini API key
- **Model Selection**: Choose between gemini-1.5-pro (more accurate) or gemini-1.5-flash (faster)
- **Chunk Size**: Size of text segments (300-1000 characters)
- **Overlap**: Overlap between chunks (50-200 characters)
- **Vagueness Threshold**: Minimum score to flag as vague (0.0-1.0)

## 📁 Directory Structure

```
mtp_v2/
│
├── data/
│   ├── raw_docs/              # Input tender/specification PDFs
│   ├── reference_docs/        # IS codes, CPWD manuals, standards
│   └── embeddings/            # Saved ChromaDB vector stores
│
├── src/
│   ├── preprocessing/
│   │   ├── pdf_to_text.py    # PDF extraction
│   │   └── chunk_text.py     # Text chunking
│   │
│   ├── embeddings/
│   │   └── create_embeddings.py  # Vectorization & ChromaDB
│   │
│   ├── detection/
│   │   ├── vagueness_detector.py # Gemini-based detection
│   │   └── qualifiers.py     # Vagueness categories
│   │
│   ├── rag/
│   │   ├── retriever.py      # Semantic search
│   │   └── suggestion_agent.py   # Gemini + RAG suggestions
│   │
│   ├── evaluation/
│   │   └── expert_validation.py  # Expert comparison
│   │
│   └── app/
│       └── streamlit_frontend.py # Web interface
│
├── outputs/
│   ├── flagged_sentences.json
│   ├── expert_ratings.csv
│   └── reports/
│
├── requirements.txt
├── README.md
└── .env
```

## 🔧 API Usage

### Programmatic Usage

```python
import os
from dotenv import load_dotenv
from src.preprocessing.pdf_to_text import PDFExtractor
from src.preprocessing.chunk_text import TextChunker
from src.embeddings.create_embeddings import EmbeddingManager
from src.detection.vagueness_detector import VaguenessDetector
from src.rag.retriever import RAGRetriever
from src.rag.suggestion_agent import SuggestionAgent

# Load API key
load_dotenv()
api_key = os.getenv('GEMINI_API_KEY')

# Initialize components
embedding_manager = EmbeddingManager()
detector = VaguenessDetector(api_key)
retriever = RAGRetriever(embedding_manager)
suggestion_agent = SuggestionAgent(api_key, retriever)

# Process a document
extractor = PDFExtractor()
doc = extractor.extract_from_file("tender.pdf")

# Chunk the document
chunker = TextChunker()
chunks = chunker.chunk_document(doc)

# Detect vagueness
results = detector.detect_batch(chunks)

# Generate suggestions for vague chunks
vague_results = [r for r in results if r['is_vague']]
suggestions = suggestion_agent.process_batch(vague_results)

# Print results
for result in suggestions:
    print(f"Chunk {result['chunk_id']}: {result['vagueness_score']:.2f}")
    for sugg in result.get('suggestions', []):
        print(f"  - {sugg['vague_phrase']}")
        print(f"    Improved: {sugg['suggestion']['improved_text']}")
```

## 📊 Evaluation

### Creating Expert Rating Template

```python
from src.evaluation.expert_validation import ExpertValidator

validator = ExpertValidator()
validator.create_expert_rating_template(chunks, "expert_ratings.csv")
```

### Comparing with Expert Ratings

```python
# After experts fill in the ratings
validator.load_expert_ratings("expert_ratings_filled.csv")
validator.load_model_outputs("model_outputs.json")

# Calculate metrics
metrics = validator.calculate_metrics()
print(f"Precision: {metrics['precision']:.3f}")
print(f"Recall: {metrics['recall']:.3f}")
print(f"F1 Score: {metrics['f1_score']:.3f}")

# Generate report
report = validator.generate_report("evaluation_report.json")
```

## 🎯 Example Output

### Detection Result
```json
{
  "chunk_id": 12,
  "text": "The contractor shall use quality materials where possible.",
  "is_vague": true,
  "vagueness_score": 0.75,
  "gemini_analysis": {
    "is_vague": true,
    "vague_phrases": ["quality materials", "where possible"],
    "categories": ["Abstractness & Subjective Language", "Open-Ended Terms"],
    "severity": "high"
  }
}
```

### Suggestion Result
```json
{
  "vague_phrase": "quality materials",
  "document_suggestions": {
    "suggested_documents": ["IS 383:2016 - Coarse and Fine Aggregates", "IS 456:2000 - Plain and Reinforced Concrete"],
    "search_terms": ["material specifications", "aggregate quality", "IS 383"]
  },
  "suggestion": {
    "improved_text": "The contractor shall use aggregates conforming to IS 383:2016 and concrete meeting IS 456:2000 Grade M25 specifications.",
    "specific_changes": [
      "Replace 'quality materials' with specific IS code references",
      "Remove conditional 'where possible' clause"
    ],
    "standards_referenced": ["IS 383:2016", "IS 456:2000"]
  }
}
```

## 🛠️ Troubleshooting

### Common Issues

1. **API Key Error**
   - Ensure your Gemini API key is valid
   - Check that .env file is in the root directory
   - Verify the API key has sufficient quota

2. **ChromaDB Errors**
   - Delete the `data/embeddings` directory and re-process documents
   - Ensure write permissions in the data directory

3. **Memory Issues**
   - Reduce chunk size in sidebar settings
   - Process fewer documents at once
   - Use gemini-1.5-flash for faster, lighter processing

4. **PDF Extraction Errors**
   - Ensure PDFs are not password-protected
   - Try using different PDF files
   - Check that PDFs contain actual text (not scanned images)

## 🔄 Future Enhancements

- [ ] Multi-language support (Hindi, Marathi)
- [ ] Fine-tuned domain-specific model
- [ ] Automated severity scoring
- [ ] Batch processing API
- [ ] PDF highlighting in UI
- [ ] Integration with document management systems
- [ ] Real-time collaboration features

## 📝 License

This project is part of the MTP (Major Technical Project) Version 2.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## 📧 Contact

For questions or support, please contact the project maintainers.

---

**Built with:**
- Google Gemini AI
- ChromaDB
- Streamlit
- Sentence Transformers
- Python 3.8+
