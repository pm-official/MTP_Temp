"""
Streamlit Frontend for Agentic Vagueness Detection System - ENHANCED
Includes cross-reference analysis across uploaded documents
"""

import streamlit as st
import sys
import os
from pathlib import Path
import json
import pandas as pd
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add src to path
sys.path.append(str(Path(__file__).parent.parent))

from preprocessing.pdf_to_text import PDFExtractor
from preprocessing.chunk_text import TextChunker
from embeddings.create_embeddings import EmbeddingManager, ReferenceDocumentStore
from detection.vagueness_detector import VaguenessDetector
from detection.qualifiers import VaguenessQualifiers
from rag.retriever import RAGRetriever
from rag.suggestion_agent import SuggestionAgent
from evaluation.expert_validation import ExpertValidator
from analysis.cross_reference import CrossReferenceAnalyzer

# Page configuration
st.set_page_config(
    page_title="Vagueness Detection System - Enhanced",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .vague-text {
        background-color: #ffebee;
        padding: 10px;
        border-left: 4px solid #f44336;
        margin: 10px 0;
    }
    .suggestion-box {
        background-color: #e8f5e9;
        padding: 10px;
        border-left: 4px solid #4caf50;
        margin: 10px 0;
    }
    .cross-ref-box {
        background-color: #e3f2fd;
        padding: 10px;
        border-left: 4px solid #2196f3;
        margin: 10px 0;
    }
    .metric-card {
        background-color: #f5f5f5;
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
    }
    .score-high {
        color: #4caf50;
        font-weight: bold;
    }
    .score-medium {
        color: #ff9800;
        font-weight: bold;
    }
    .score-low {
        color: #f44336;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize session state variables"""
    if 'embedding_manager' not in st.session_state:
        st.session_state.embedding_manager = None
    if 'detector' not in st.session_state:
        st.session_state.detector = None
    if 'retriever' not in st.session_state:
        st.session_state.retriever = None
    if 'suggestion_agent' not in st.session_state:
        st.session_state.suggestion_agent = None
    if 'cross_ref_analyzer' not in st.session_state:
        st.session_state.cross_ref_analyzer = None
    if 'tender_chunks' not in st.session_state:
        st.session_state.tender_chunks = []
    if 'detection_results' not in st.session_state:
        st.session_state.detection_results = []
    if 'reference_docs_loaded' not in st.session_state:
        st.session_state.reference_docs_loaded = False
    if 'uploaded_tender_files' not in st.session_state:
        st.session_state.uploaded_tender_files = []
    if 'extracted_documents' not in st.session_state:
        st.session_state.extracted_documents = []
    if 'all_tender_chunks' not in st.session_state:
        st.session_state.all_tender_chunks = []
    if 'tender_collection_ready' not in st.session_state:
        st.session_state.tender_collection_ready = False
    if 'config' not in st.session_state:
        st.session_state.config = {
            'api_key': '',
            'model': 'gemini-2.0-flash-lite',
            'chunk_size': 500,
            'overlap': 100,
            'threshold': 0.3,
            'enable_cross_ref': True
        }


def setup_sidebar():
    """Setup sidebar with configuration"""
    st.sidebar.title("⚙️ Configuration")
    
    # API Key input with unique key
    api_key = st.sidebar.text_input(
        "Gemini API Key",
        type="password",
        help="Enter your Google Gemini API key",
        key="api_key_input")
    
    # Model selection with unique key
    model = st.sidebar.selectbox(
        "Gemini Model",
        [
            "gemini-2.0-flash-lite",
            "gemini-2.5-flash",
            "gemini-2.5-flash-lite",
            "gemini-2.0-flash",
            "gemini-2.5-pro",
        ],
        index=0,
        help="gemini-2.0-flash-lite is fastest",
        key="model_select"
    )
    
    # Chunking parameters
    st.sidebar.subheader("Chunking Parameters")
    chunk_size = st.sidebar.slider("Chunk Size", 300, 1000, 500, 50, key="chunk_size_slider")
    overlap = st.sidebar.slider("Overlap", 50, 200, 100, 25, key="overlap_slider")
    
    # Detection parameters
    st.sidebar.subheader("Detection Parameters")
    threshold = st.sidebar.slider(
        "Vagueness Threshold",
        0.0, 1.0, 0.3, 0.05,
        help="Minimum score to flag as vague",
        key="threshold_slider"
    )
    
    # Cross-reference parameters
    st.sidebar.subheader("Cross-Reference Parameters")
    enable_cross_ref = st.sidebar.checkbox(
        "Enable Cross-Reference Analysis",
        value=True,
        help="Search for clarifying information across all documents",
        key="enable_cross_ref_checkbox"
    )
    
    return api_key, model, chunk_size, overlap, threshold, enable_cross_ref


def initialize_components(api_key, model):
    """Initialize all system components"""
    try:
        if not api_key:
            st.error("Please enter your Gemini API key in the sidebar")
            return False
        
        with st.spinner("Initializing system components..."):
            # Initialize embedding manager
            if st.session_state.embedding_manager is None:
                st.session_state.embedding_manager = EmbeddingManager()
            
            # Initialize detector
            if st.session_state.detector is None:
                st.session_state.detector = VaguenessDetector(api_key, model)
            
            # Initialize retriever
            if st.session_state.retriever is None:
                st.session_state.retriever = RAGRetriever(st.session_state.embedding_manager)
            
            # Initialize suggestion agent
            if st.session_state.suggestion_agent is None:
                st.session_state.suggestion_agent = SuggestionAgent(
                    api_key,
                    st.session_state.retriever,
                    model
                )
            
            # Initialize cross-reference analyzer
            if st.session_state.cross_ref_analyzer is None:
                st.session_state.cross_ref_analyzer = CrossReferenceAnalyzer(
                    api_key,
                    st.session_state.embedding_manager,
                    model
                )
        
        return True
    except Exception as e:
        st.error(f"Error initializing components: {str(e)}")
        return False


def process_reference_documents():
    """Tab 1: Process and embed reference documents"""
    st.header("📚 Reference Documents (IS Codes, CPWD Manuals)")
    
    st.info("""
    Upload reference documents (IS Codes, CPWD manuals, technical standards) that will be used 
    to provide context and suggestions for vague phrases found in tender documents.
    """)
    
    # File uploader for reference docs
    ref_files = st.file_uploader(
        "Upload Reference Documents (PDFs)",
        type=['pdf'],
        accept_multiple_files=True,
        key="ref_docs"
    )
    
    col1, col2 = st.columns([1, 4])
    
    with col1:
        if st.button("Process Reference Documents", type="primary"):
            if not ref_files:
                st.warning("Please upload at least one reference document")
                return
            
            if st.session_state.embedding_manager is None:
                st.error("System not initialized. Please enter API key in sidebar.")
                return
            
            process_references(ref_files)
    
    # Show status
    if st.session_state.reference_docs_loaded:
        st.success("✅ Reference documents are loaded and ready")
        
        stats = st.session_state.embedding_manager.get_collection_stats("reference_documents")
        st.metric("Total Reference Chunks", stats['count'])


def process_references(ref_files):
    """Process reference documents"""
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        status_text.text("⚡ Step 1/3: Fast-extracting text from PDFs...")
        
        extractor = PDFExtractor(use_parallel=True, max_workers=4)
        
        all_docs = []
        for i, uploaded_file in enumerate(ref_files):
            original_filename = uploaded_file.name
            status_text.text(f"⚡ Extracting ({i+1}/{len(ref_files)}): {original_filename}")
            
            # Save with original filename
            temp_path = f"temp_{original_filename}"
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            doc_data = extractor.extract_from_file(temp_path)
            if doc_data:
                # Ensure filename is set to original name
                doc_data['filename'] = original_filename
                all_docs.append(doc_data)
            
            os.remove(temp_path)
            progress_bar.progress((i + 1) / (len(ref_files) * 3))
        
        status_text.text("Step 2/3: Chunking documents...")
        chunker = TextChunker(chunk_size=500, overlap=100)
        
        all_chunks = []
        for doc in all_docs:
            chunks = chunker.chunk_document(doc, method='sentences')
            all_chunks.extend(chunks)
        
        progress_bar.progress(2/3)
        
        status_text.text("Step 3/3: Creating embeddings and storing...")
        ref_store = ReferenceDocumentStore(st.session_state.embedding_manager)
        ref_store.initialize(reset=True)
        ref_store.add_reference_docs(all_chunks)
        
        progress_bar.progress(1.0)
        st.session_state.reference_docs_loaded = True
        
        status_text.text("")
        st.success(f"✅ Processed {len(ref_files)} reference documents ({len(all_chunks)} chunks)!")
        
    except Exception as e:
        st.error(f"Error processing reference documents: {str(e)}")


def detect_vagueness_tab():
    """Tab 2: Upload tender documents and detect vagueness with cross-reference analysis"""
    st.header("🔍 Detect Vagueness in Tender Documents")
    
    st.info("""
    Upload tender/specification documents, select specific document and page range to analyze.
    **NEW:** Cross-reference analysis will search for clarifying information across all uploaded documents.
    """)
    
    if not st.session_state.reference_docs_loaded:
        st.warning("⚠️ Please process reference documents first (Tab 1)")
    
    # File uploader for tender docs
    tender_files = st.file_uploader(
        "Upload Tender Documents (PDFs) - Upload ALL documents in your tender package",
        type=['pdf'],
        accept_multiple_files=True,
        key="tender_docs",
        help="Upload all documents for cross-reference analysis"
    )
    
    # Step 1: Load documents
    if tender_files:
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📥 Load Documents", type="primary"):
                if st.session_state.detector is None:
                    st.error("System not initialized. Please enter API key in sidebar.")
                    return
                
                load_tender_documents(tender_files)
        
        with col2:
            if st.button("🗑️ Clear All"):
                st.session_state.detection_results = []
                st.session_state.tender_chunks = []
                st.session_state.uploaded_tender_files = []
                st.session_state.extracted_documents = []
                st.session_state.all_tender_chunks = []
                st.session_state.tender_collection_ready = False
                st.rerun()
    
    # Step 2: Select document and page range
    if st.session_state.extracted_documents:
        st.divider()
        st.subheader("📄 Select Document and Pages to Analyze")
        
        doc_options = [
            f"{i+1}. {doc['filename']} ({doc['total_pages']} pages)"
            for i, doc in enumerate(st.session_state.extracted_documents)
        ]
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            selected_doc_index = st.selectbox(
                "Select Document",
                range(len(doc_options)),
                format_func=lambda x: doc_options[x],
                key="selected_doc"
            )
        
        selected_doc = st.session_state.extracted_documents[selected_doc_index]
        total_pages = selected_doc['total_pages']
        
        st.markdown("**Select Page Range:**")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            page_selection_type = st.radio(
                "Selection Type",
                ["Single Page", "Page Range", "All Pages"],
                key="page_type"
            )
        
        with col2:
            if page_selection_type == "Single Page":
                page_num = st.number_input(
                    "Page Number",
                    min_value=1,
                    max_value=total_pages,
                    value=1,
                    key="single_page"
                )
                start_page = end_page = page_num
            elif page_selection_type == "Page Range":
                start_page = st.number_input(
                    "Start Page",
                    min_value=1,
                    max_value=total_pages,
                    value=1,
                    key="start_page"
                )
            else:
                start_page = 1
                end_page = total_pages
        
        with col3:
            if page_selection_type == "Page Range":
                end_page = st.number_input(
                    "End Page",
                    min_value=start_page,
                    max_value=total_pages,
                    value=min(start_page + 4, total_pages),
                    key="end_page"
                )
        
        if page_selection_type != "All Pages":
            pages_to_analyze = end_page - start_page + 1
        else:
            pages_to_analyze = total_pages
            
        st.info(f"📊 Will analyze **{pages_to_analyze} page(s)** from **{selected_doc['filename']}**")
        
        # Analyze button
        col1, col2 = st.columns([1, 4])
        
        with col1:
            if st.button("🔍 Analyze Selection", type="primary"):
                # Get enable_cross_ref from session state config
                enable_cross_ref = st.session_state.config.get('enable_cross_ref', True)
                analyze_selected_pages(
                    selected_doc,
                    start_page,
                    end_page,
                    enable_cross_ref
                )
    
    # Display results if available
    if st.session_state.detection_results:
        st.divider()
        display_detection_results()


def load_tender_documents(tender_files):
    """Load and extract text from tender documents"""
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        status_text.text("⚡ Fast-loading documents...")
        
        extractor = PDFExtractor(use_parallel=True, max_workers=4)
        
        all_docs = []
        all_chunks = []
        chunker = TextChunker(chunk_size=500, overlap=100)
        
        total_files = len(tender_files)
        
        for i, uploaded_file in enumerate(tender_files):
            # Use original filename for identification
            original_filename = uploaded_file.name
            file_id = f"{original_filename}_{uploaded_file.size}"
            
            existing_doc = None
            if st.session_state.extracted_documents:
                existing_doc = next(
                    (doc for doc in st.session_state.extracted_documents 
                     if doc.get('file_id') == file_id),
                    None
                )
            
            if existing_doc:
                status_text.text(f"✅ Using cached: {original_filename}")
                all_docs.append(existing_doc)
            else:
                status_text.text(f"⚡ Extracting ({i+1}/{total_files}): {original_filename}")
                
                # Save with original filename to preserve it
                temp_path = f"temp_{original_filename}"
                with open(temp_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                doc_data = extractor.extract_from_file(temp_path)
                if doc_data:
                    # Ensure filename is set to original name
                    doc_data['file_id'] = file_id
                    doc_data['filename'] = original_filename
                    all_docs.append(doc_data)
                
                os.remove(temp_path)
            
            progress_bar.progress((i + 1) / (total_files * 2))
        
        st.session_state.uploaded_tender_files = tender_files
        st.session_state.extracted_documents = all_docs
        
        # Create chunks from ALL documents for cross-reference search
        status_text.text("Creating tender document collection for cross-reference analysis...")
        
        for doc in all_docs:
            chunks = chunker.chunk_document(doc, method='sentences')
            all_chunks.extend(chunks)
        
        st.session_state.all_tender_chunks = all_chunks
        
        # Store in vector database for cross-reference search
        status_text.text("Building cross-reference search index...")
        tender_collection = st.session_state.embedding_manager.create_collection(
            "tender_documents",
            reset=True
        )
        st.session_state.embedding_manager.add_documents_to_collection(
            "tender_documents",
            all_chunks
        )
        st.session_state.tender_collection_ready = True
        
        progress_bar.progress(1.0)
        status_text.text("")
        
        st.success(f"✅ Loaded {len(all_docs)} documents with {len(all_chunks)} chunks for cross-reference analysis!")
        
        for i, doc in enumerate(all_docs):
            pages = doc['total_pages']
            has_text = doc.get('full_text', '').strip() != ''
            
            if not has_text:
                st.warning(f"{i+1}. **{doc['filename']}** - {pages} pages ⚠️ NO TEXT FOUND")
            else:
                st.write(f"{i+1}. **{doc['filename']}** - {pages} pages ⚡")
        
    except Exception as e:
        st.error(f"Error loading documents: {str(e)}")


def analyze_selected_pages(selected_doc, start_page, end_page, enable_cross_ref=True):
    """Analyze selected pages from a specific document"""
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        status_text.text(f"Step 1/3: Extracting pages {start_page} to {end_page}...")
        
        selected_pages = [
            page for page in selected_doc['pages']
            if start_page <= page['page_num'] <= end_page
        ]
        
        selected_text = "\n\n".join([page['text'] for page in selected_pages])
        
        progress_bar.progress(0.33)
        
        status_text.text("Step 2/3: Analyzing text for vagueness...")
        
        chunker = TextChunker(chunk_size=500, overlap=100)
        
        metadata = {
            'filename': selected_doc['filename'],
            'filepath': selected_doc['filepath'],
            'start_page': start_page,
            'end_page': end_page,
            'total_pages_analyzed': end_page - start_page + 1
        }
        
        chunks = chunker.chunk_by_sentences(selected_text, metadata)
        st.session_state.tender_chunks = chunks
        
        results = st.session_state.detector.detect_batch(chunks)
        
        progress_bar.progress(0.66)
        
        # Step 3: Cross-reference analysis
        if enable_cross_ref and st.session_state.tender_collection_ready:
            status_text.text("Step 3/3: Analyzing cross-references across all documents...")
            
            vague_results = [r for r in results if r.get('is_vague')]
            
            if vague_results and st.session_state.cross_ref_analyzer:
                analyzed_results = st.session_state.cross_ref_analyzer.batch_analyze_cross_references(
                    vague_results,
                    "tender_documents"
                )
                
                # Update results with cross-reference analysis
                for analyzed in analyzed_results:
                    for i, r in enumerate(results):
                        if r['chunk_id'] == analyzed['chunk_id']:
                            results[i] = analyzed
                            break
        
        st.session_state.detection_results = results
        progress_bar.progress(1.0)
        
        status_text.text("")
        
        vague_count = sum(1 for r in results if r.get('is_vague'))
        
        success_msg = f"""
        ✅ Analysis complete!
        - **Document:** {selected_doc['filename']}
        - **Pages Analyzed:** {start_page} to {end_page} ({end_page - start_page + 1} pages)
        - **Chunks Created:** {len(results)}
        - **Vague Chunks Found:** {vague_count}
        """
        
        if enable_cross_ref and vague_count > 0:
            xref_count = sum(1 for r in results if r.get('cross_reference_analysis', {}).get('has_cross_references', False))
            success_msg += f"\n        - **Chunks with Cross-References:** {xref_count}"
        
        st.success(success_msg)
        
    except Exception as e:
        st.error(f"Error analyzing pages: {str(e)}")


def display_detection_results():
    """Display detection results with cross-reference information"""
    st.subheader("📊 Analysis Results")
    
    results = st.session_state.detection_results
    vague_results = [r for r in results if r.get('is_vague')]
    
    if results and results[0].get('metadata'):
        metadata = results[0]['metadata']
        st.info(f"""
        **Analyzed:** {metadata.get('filename', 'Unknown')} | 
        **Pages:** {metadata.get('start_page', '?')} - {metadata.get('end_page', '?')} 
        ({metadata.get('total_pages_analyzed', '?')} pages)
        """)
    
    # Summary metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Total Chunks", len(results))
    
    with col2:
        st.metric("Vague Chunks", len(vague_results))
    
    with col3:
        vague_pct = (len(vague_results) / len(results) * 100) if results else 0
        st.metric("Vagueness Rate", f"{vague_pct:.1f}%")
    
    with col4:
        avg_score = sum(r.get('vagueness_score', 0) for r in vague_results) / len(vague_results) if vague_results else 0
        st.metric("Avg Vagueness Score", f"{avg_score:.2f}")
    
    with col5:
        xref_count = sum(1 for r in vague_results if r.get('cross_reference_analysis', {}).get('has_cross_references', False))
        st.metric("With Cross-Refs", xref_count)
    
    # Filter options
    st.subheader("🔎 Filter Results")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        show_all = st.checkbox("Show all chunks", value=False)
    
    with col2:
        min_score = st.slider("Minimum vagueness score", 0.0, 1.0, 0.3, 0.05)
    
    with col3:
        show_only_with_xref = st.checkbox("Show only with cross-references", value=False)
    
    # Display chunks
    st.subheader("📝 Detected Vague Phrases")
    
    display_results = results if show_all else vague_results
    display_results = [r for r in display_results if r.get('vagueness_score', 0) >= min_score]
    
    if show_only_with_xref:
        display_results = [r for r in display_results if r.get('cross_reference_analysis', {}).get('has_cross_references', False)]
    
    if not display_results:
        st.warning("No results match the current filter criteria.")
        return
    
    for i, result in enumerate(display_results):
        xref_indicator = "🔗" if result.get('cross_reference_analysis', {}).get('has_cross_references', False) else ""
        
        with st.expander(
            f"{xref_indicator} Chunk {result['chunk_id']} - Score: {result['vagueness_score']:.2f} "
            f"{'🚨' if result['vagueness_score'] > 0.7 else '⚠️' if result['vagueness_score'] > 0.5 else '⚡'}",
            expanded=(i < 3)
        ):
            display_chunk_detail(result)
    
    # Export options
    st.subheader("💾 Export Results")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Export as JSON"):
            export_json(vague_results)
    
    with col2:
        if st.button("Export as CSV"):
            export_csv(vague_results)


def display_chunk_detail(result):
    """Display detailed information about a chunk including cross-references"""
    # Original text
    st.markdown("**Original Text:**")
    st.markdown(f'<div class="vague-text">{result["text"]}</div>', unsafe_allow_html=True)
    
    # Vagueness analysis
    st.markdown("**Vagueness Analysis:**")
    
    gemini_analysis = result.get('gemini_analysis', {})
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Vague Phrases:**")
        for phrase in gemini_analysis.get('vague_phrases', []):
            st.write(f"- {phrase}")
    
    with col2:
        st.write("**Categories:**")
        for category in gemini_analysis.get('categories', []):
            st.write(f"- {category}")
    
    st.write("**Explanation:**")
    st.write(gemini_analysis.get('explanation', 'No explanation available'))
    
    # Cross-reference analysis (NEW)
    xref_analysis = result.get('cross_reference_analysis')
    
    if xref_analysis:
        st.divider()
        st.markdown("### 🔗 Cross-Reference Analysis")
        
        xref_score = xref_analysis.get('cross_reference_score', 0)
        score_class = 'score-high' if xref_score >= 0.6 else 'score-medium' if xref_score >= 0.4 else 'score-low'
        
        col1, col2 = st.columns([1, 3])
        
        with col1:
            st.markdown(f"**Cross-Ref Score:**")
            st.markdown(f'<span class="{score_class}">{xref_score:.2f}</span>', unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"**Summary:**")
            st.write(xref_analysis.get('summary', 'No summary available'))
        
        # Display phrase-level analysis
        phrase_analyses = xref_analysis.get('phrase_analyses', [])
        
        if phrase_analyses:
            st.markdown("**Detailed Analysis by Phrase:**")
            
            for idx, pa in enumerate(phrase_analyses):
                # Use a container with divider instead of nested expander
                st.markdown(f"---")
                st.markdown(f"### 📌 {pa['vague_phrase']} (Score: {pa['cross_reference_score']:.2f})")
                
                st.markdown(f"**Reasoning:** {pa['reasoning']['reasoning']}")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Related Chunks", pa['related_chunks_found'])
                with col2:
                    st.metric("Relevant Chunks", pa['relevant_chunks_found'])
                with col3:
                    interp = pa['reasoning']['interpretation'].replace('_', ' ').title()
                    st.metric("Interpretation", interp)
                
                # Display top relevant chunks
                top_chunks = pa.get('top_relevant_chunks', [])
                
                if top_chunks:
                    st.markdown("**📄 Relevant Information Found:**")
                    
                    for i, chunk in enumerate(top_chunks, 1):
                        st.markdown(f'<div class="cross-ref-box">', unsafe_allow_html=True)
                        st.markdown(f"**Source {i}:** {chunk['source_document']}")
                        st.markdown(f"**Type:** {chunk['clarification_type'].replace('_', ' ').title()}")
                        st.markdown(f"**Relevance:** {chunk['relevance_score']:.2f}")
                        st.markdown(f"**Key Information:** {chunk['key_information']}")
                        
                        # Show truncated text with option to see more
                        chunk_preview = chunk['chunk_text'][:200] + "..." if len(chunk['chunk_text']) > 200 else chunk['chunk_text']
                        st.markdown(f"**Text Preview:** {chunk_preview}")
                        
                        # Add button to show full text if needed
                        if len(chunk['chunk_text']) > 200:
                            show_full_key = f"show_full_{idx}_{i}"
                            if st.button(f"Show full text", key=show_full_key):
                                st.text_area("Full Text", chunk['chunk_text'], height=150, key=f"text_area_{idx}_{i}")
                        
                        st.markdown('</div>', unsafe_allow_html=True)


def generate_suggestions_tab():
    """Tab 3: Generate improvement suggestions"""
    st.header("💡 Generate Improvement Suggestions")
    
    st.info("""
    Generate specific, actionable suggestions for improving vague language based on reference standards.
    Cross-reference information will be included when available.
    """)
    
    if not st.session_state.detection_results:
        st.warning("⚠️ Please analyze tender documents first (Tab 2)")
        return
    
    if not st.session_state.reference_docs_loaded:
        st.warning("⚠️ Please process reference documents first (Tab 1)")
        return
    
    vague_results = [r for r in st.session_state.detection_results if r.get('is_vague')]
    
    st.write(f"Found {len(vague_results)} vague chunks to process")
    
    if st.button("Generate Suggestions", type="primary"):
        generate_all_suggestions(vague_results)
    
    display_suggestions()


def generate_all_suggestions(vague_results):
    """Generate suggestions for all vague chunks"""
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        status_text.text("Generating suggestions with AI...")
        
        processed_results = st.session_state.suggestion_agent.process_batch(vague_results)
        
        for result in processed_results:
            chunk_id = result['chunk_id']
            for i, stored_result in enumerate(st.session_state.detection_results):
                if stored_result['chunk_id'] == chunk_id:
                    st.session_state.detection_results[i] = result
                    break
        
        progress_bar.progress(1.0)
        status_text.text("")
        
        st.success(f"✅ Generated suggestions for {len(vague_results)} vague chunks")
        
    except Exception as e:
        st.error(f"Error generating suggestions: {str(e)}")


def display_suggestions():
    """Display generated suggestions"""
    results_with_suggestions = [
        r for r in st.session_state.detection_results 
        if r.get('suggestions')
    ]
    
    if not results_with_suggestions:
        return
    
    st.subheader("📋 Improvement Suggestions")
    
    for result in results_with_suggestions:
        with st.expander(
            f"Chunk {result['chunk_id']} - {len(result.get('suggestions', []))} suggestions",
            expanded=True
        ):
            display_suggestion_detail(result)


def display_suggestion_detail(result):
    """Display detailed suggestions for a chunk"""
    st.markdown("**Original Text:**")
    st.markdown(f'<div class="vague-text">{result["text"]}</div>', unsafe_allow_html=True)
    
    suggestions = result.get('suggestions', [])
    
    for i, sugg in enumerate(suggestions):
        st.markdown(f"### Suggestion {i+1}: {sugg['vague_phrase']}")
        
        doc_sugg = sugg.get('document_suggestions', {})
        
        with st.container():
            st.markdown("**📚 Recommended Documents:**")
            for doc in doc_sugg.get('suggested_documents', []):
                st.write(f"- {doc}")
            
            st.markdown("**🔍 Search Terms Used:**")
            st.write(", ".join(doc_sugg.get('search_terms', [])))
            
            st.markdown(f"**💭 Reasoning:** {doc_sugg.get('reasoning', '')}")
        
        st.markdown(f"**📖 Retrieved {sugg.get('retrieved_chunks_count', 0)} Reference Chunks**")
        
        improvement = sugg.get('suggestion', {})
        
        st.markdown("**✨ Improved Text:**")
        st.markdown(f'<div class="suggestion-box">{improvement.get("improved_text", "")}</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Specific Changes:**")
            for change in improvement.get('specific_changes', []):
                st.write(f"- {change}")
        
        with col2:
            st.markdown("**Standards Referenced:**")
            for std in improvement.get('standards_referenced', []):
                st.write(f"- {std}")
        
        st.markdown(f"**Explanation:** {improvement.get('explanation', '')}")
        
        st.divider()


def export_json(results):
    """Export results as JSON"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"vagueness_detection_{timestamp}.json"
    
    json_str = json.dumps(results, indent=2)
    
    st.download_button(
        label="Download JSON",
        data=json_str,
        file_name=filename,
        mime="application/json"
    )


def export_csv(results):
    """Export results as CSV"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"vagueness_detection_{timestamp}.csv"
    
    flat_results = []
    for r in results:
        xref = r.get('cross_reference_analysis', {})
        flat_results.append({
            'chunk_id': r.get('chunk_id'),
            'text': r.get('text'),
            'is_vague': r.get('is_vague'),
            'vagueness_score': r.get('vagueness_score'),
            'vague_phrases': ", ".join(r.get('gemini_analysis', {}).get('vague_phrases', [])),
            'categories': ", ".join(r.get('gemini_analysis', {}).get('categories', [])),
            'has_cross_references': xref.get('has_cross_references', False),
            'cross_reference_score': xref.get('cross_reference_score', 0),
            'cross_reference_summary': xref.get('summary', '')
        })
    
    df = pd.DataFrame(flat_results)
    csv = df.to_csv(index=False)
    
    st.download_button(
        label="Download CSV",
        data=csv,
        file_name=filename,
        mime="text/csv"
    )


def main():
    """Main application"""
    st.title("📄 Agentic Vagueness Detection System - Enhanced")
    st.markdown("*Automatically detect and improve vague language with cross-reference analysis*")
    
    initialize_session_state()
    
    # Setup sidebar ONCE at the start
    api_key, model, chunk_size, overlap, threshold, enable_cross_ref = setup_sidebar()
    
    # Store configuration in session state for access in tabs
    st.session_state.config = {
        'api_key': api_key,
        'model': model,
        'chunk_size': chunk_size,
        'overlap': overlap,
        'threshold': threshold,
        'enable_cross_ref': enable_cross_ref
    }
    
    if api_key:
        initialize_components(api_key, model)
    
    tab1, tab2, tab3 = st.tabs([
        "📚 Reference Documents",
        "🔍 Detect Vagueness + Cross-References",
        "💡 Generate Suggestions"
    ])
    
    with tab1:
        process_reference_documents()
    
    with tab2:
        detect_vagueness_tab()
    
    with tab3:
        generate_suggestions_tab()
    
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: gray; font-size: 12px;'>
        MTP Version 2 - Enhanced with Cross-Reference Analysis<br>
        Powered by Gemini AI and ChromaDB
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()