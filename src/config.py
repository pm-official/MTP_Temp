"""
Configuration settings for the Vagueness Detection System
"""

import os
from pathlib import Path

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent

# Data directories
DATA_DIR = PROJECT_ROOT / "data"
RAW_DOCS_DIR = DATA_DIR / "raw_docs"
REFERENCE_DOCS_DIR = DATA_DIR / "reference_docs"
EMBEDDINGS_DIR = DATA_DIR / "embeddings"

# Output directories
OUTPUTS_DIR = PROJECT_ROOT / "outputs"
REPORTS_DIR = OUTPUTS_DIR / "reports"

# Ensure directories exist
for directory in [RAW_DOCS_DIR, REFERENCE_DOCS_DIR, EMBEDDINGS_DIR, OUTPUTS_DIR, REPORTS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Model settings
DEFAULT_EMBEDDING_MODEL = "all-MiniLM-L6-v2"
DEFAULT_GEMINI_MODEL = "gemini-1.5-pro"
GEMINI_MODEL_FLASH = "gemini-1.5-flash"

# Chunking settings
DEFAULT_CHUNK_SIZE = 500
DEFAULT_OVERLAP = 100
MIN_CHUNK_SIZE = 300
MAX_CHUNK_SIZE = 1000

# Detection settings
DEFAULT_VAGUENESS_THRESHOLD = 0.3
MIN_THRESHOLD = 0.0
MAX_THRESHOLD = 1.0

# RAG settings
DEFAULT_N_RESULTS = 5
MAX_N_RESULTS = 10

# ChromaDB settings
REFERENCE_COLLECTION_NAME = "reference_documents"
TENDER_COLLECTION_NAME = "tender_documents"

# API settings
GEMINI_API_KEY_ENV = "GEMINI_API_KEY"

# Logging
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Vagueness qualifier categories
QUALIFIER_CATEGORIES = {
    "abstractness_subjective": "Abstractness & Subjective Language",
    "ambiguous_modifiers": "Ambiguous Modifiers & Comparative Phrases",
    "referent_ambiguity": "Referent Ambiguity & Complex Noun Phrases",
    "open_ended_terms": "Open-Ended / Non-Verifiable Terms & Loopholes",
    "negative_passive": "Negative & Passive Structures"
}

# Severity levels
SEVERITY_LEVELS = {
    "low": 0.3,
    "medium": 0.5,
    "high": 0.7
}

# File formats
SUPPORTED_DOCUMENT_FORMATS = ['.pdf']
EXPORT_FORMATS = ['json', 'csv', 'xlsx']

# UI settings
STREAMLIT_PAGE_TITLE = "Vagueness Detection System"
STREAMLIT_PAGE_ICON = "📄"
STREAMLIT_LAYOUT = "wide"

# Processing settings
BATCH_SIZE = 100  # For embedding creation
MAX_CONCURRENT_REQUESTS = 5  # For API calls

# Cache settings
ENABLE_CACHE = True
CACHE_EXPIRY_HOURS = 24
