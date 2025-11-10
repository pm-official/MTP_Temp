"""
Example Script - Programmatic Usage of Vagueness Detection System
Demonstrates how to use the system without the Streamlit UI
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add src to path
sys.path.append(str(Path(__file__).parent / 'src'))

from preprocessing.pdf_to_text import PDFExtractor
from preprocessing.chunk_text import TextChunker
from embeddings.create_embeddings import EmbeddingManager, ReferenceDocumentStore
from detection.vagueness_detector import VaguenessDetector
from rag.retriever import RAGRetriever
from rag.suggestion_agent import SuggestionAgent
from utils import save_json, format_result_summary


def main():
    """
    Example workflow for detecting vagueness and generating suggestions
    """
    
    # Load environment variables
    load_dotenv()
    api_key = os.getenv('GEMINI_API_KEY')
    
    if not api_key:
        print("Error: GEMINI_API_KEY not found in environment variables")
        print("Please set it in your .env file or environment")
        return
    
    print("="*60)
    print("Vagueness Detection System - Programmatic Example")
    print("="*60)
    
    # ==================== STEP 1: Initialize Components ====================
    print("\n[1/6] Initializing components...")
    
    embedding_manager = EmbeddingManager()
    detector = VaguenessDetector(api_key, model_name="gemini-1.5-flash")
    retriever = RAGRetriever(embedding_manager)
    suggestion_agent = SuggestionAgent(api_key, retriever, model_name="gemini-1.5-flash")
    
    print("✓ Components initialized")
    
    # ==================== STEP 2: Process Reference Documents ====================
    print("\n[2/6] Processing reference documents...")
    
    # Check if reference documents exist
    reference_dir = Path("data/reference_docs")
    ref_pdfs = list(reference_dir.glob("*.pdf"))
    
    if not ref_pdfs:
        print("⚠️  No reference documents found in data/reference_docs/")
        print("   Skipping reference document processing")
        print("   (Suggestions will be generated without reference context)")
    else:
        print(f"   Found {len(ref_pdfs)} reference documents")
        
        # Extract text from reference documents
        extractor = PDFExtractor()
        ref_docs = []
        
        for pdf_path in ref_pdfs[:3]:  # Process first 3 for demo
            print(f"   Processing: {pdf_path.name}")
            doc_data = extractor.extract_from_file(str(pdf_path))
            if doc_data:
                ref_docs.append(doc_data)
        
        # Chunk reference documents
        chunker = TextChunker(chunk_size=500, overlap=100)
        ref_chunks = []
        
        for doc in ref_docs:
            chunks = chunker.chunk_document(doc)
            ref_chunks.extend(chunks)
        
        print(f"   Created {len(ref_chunks)} reference chunks")
        
        # Store in vector database
        ref_store = ReferenceDocumentStore(embedding_manager)
        ref_store.initialize(reset=True)
        ref_store.add_reference_docs(ref_chunks)
        
        print("✓ Reference documents processed and stored")
    
    # ==================== STEP 3: Process Tender Document ====================
    print("\n[3/6] Processing tender document...")
    
    # Check for tender documents
    tender_dir = Path("data/raw_docs")
    tender_pdfs = list(tender_dir.glob("*.pdf"))
    
    if not tender_pdfs:
        print("⚠️  No tender documents found in data/raw_docs/")
        print("   Creating a sample text for demonstration...")
        
        # Use sample text instead
        sample_text = """
        The contractor shall use quality materials where possible for all construction work.
        All concrete work must be completed to a reasonable standard within the project timeline.
        Payment will be issued upon satisfactory completion of work.
        The project should be completed faster than previous similar projects.
        Materials should not be sourced from non-approved vendors.
        Implementation of the safety plan will begin when feasible.
        """
        
        # Create sample chunks
        chunker = TextChunker(chunk_size=300, overlap=50)
        tender_chunks = chunker.chunk_by_sentences(sample_text, {
            'filename': 'sample_text',
            'source': 'demo'
        })
        
        print(f"   Created {len(tender_chunks)} chunks from sample text")
        
    else:
        print(f"   Found {len(tender_pdfs)} tender documents")
        
        # Process first tender document
        tender_path = tender_pdfs[0]
        print(f"   Processing: {tender_path.name}")
        
        extractor = PDFExtractor()
        tender_doc = extractor.extract_from_file(str(tender_path))
        
        # Chunk tender document
        chunker = TextChunker(chunk_size=500, overlap=100)
        tender_chunks = chunker.chunk_document(tender_doc)
        
        print(f"   Created {len(tender_chunks)} tender chunks")
    
    print("✓ Tender document processed")
    
    # ==================== STEP 4: Detect Vagueness ====================
    print("\n[4/6] Detecting vagueness...")
    
    # Limit to first 5 chunks for demo
    sample_chunks = tender_chunks[:5]
    
    detection_results = detector.detect_batch(sample_chunks)
    
    # Get summary
    summary = format_result_summary(detection_results)
    
    print(f"✓ Vagueness detection complete")
    print(f"   Total chunks analyzed: {summary['total_chunks']}")
    print(f"   Vague chunks found: {summary['vague_chunks']}")
    print(f"   Vagueness rate: {summary['vagueness_rate']:.1f}%")
    
    # ==================== STEP 5: Generate Suggestions ====================
    print("\n[5/6] Generating suggestions...")
    
    # Filter vague results
    vague_results = [r for r in detection_results if r.get('is_vague')]
    
    if not vague_results:
        print("   No vague chunks found - skipping suggestion generation")
    else:
        print(f"   Generating suggestions for {len(vague_results)} vague chunks...")
        
        # Generate suggestions (limit to first 2 for demo)
        results_with_suggestions = suggestion_agent.process_batch(vague_results[:2])
        
        print("✓ Suggestions generated")
    
    # ==================== STEP 6: Save Results ====================
    print("\n[6/6] Saving results...")
    
    # Save detection results
    output_dir = Path("outputs")
    output_dir.mkdir(exist_ok=True)
    
    detection_output = output_dir / "detection_results.json"
    save_json(detection_results, str(detection_output))
    print(f"   Saved detection results to: {detection_output}")
    
    if vague_results and len(vague_results) > 0:
        suggestions_output = output_dir / "suggestions.json"
        save_json(results_with_suggestions if 'results_with_suggestions' in locals() else vague_results, 
                 str(suggestions_output))
        print(f"   Saved suggestions to: {suggestions_output}")
    
    # ==================== Display Sample Results ====================
    print("\n" + "="*60)
    print("SAMPLE RESULTS")
    print("="*60)
    
    if vague_results:
        sample_result = vague_results[0]
        
        print(f"\n📝 Sample Vague Text:")
        print(f"   {sample_result['text']}")
        
        print(f"\n⚠️  Vagueness Score: {sample_result['vagueness_score']:.2f}")
        
        analysis = sample_result.get('gemini_analysis', {})
        print(f"\n🔍 Vague Phrases:")
        for phrase in analysis.get('vague_phrases', []):
            print(f"   - {phrase}")
        
        print(f"\n📊 Categories:")
        for category in analysis.get('categories', []):
            print(f"   - {category}")
        
        print(f"\n💡 Explanation:")
        print(f"   {analysis.get('explanation', 'N/A')}")
        
        # Display suggestion if available
        if 'results_with_suggestions' in locals() and results_with_suggestions:
            suggestions = results_with_suggestions[0].get('suggestions', [])
            if suggestions:
                first_sugg = suggestions[0]
                print(f"\n✨ Suggested Improvement:")
                print(f"   {first_sugg['suggestion'].get('improved_text', 'N/A')}")
    
    print("\n" + "="*60)
    print("✓ Example completed successfully!")
    print("="*60)
    print("\nNext steps:")
    print("1. Check the outputs/ directory for saved results")
    print("2. Add your own reference documents to data/reference_docs/")
    print("3. Add tender documents to data/raw_docs/")
    print("4. Run this script again or use the Streamlit app")


if __name__ == "__main__":
    main()
