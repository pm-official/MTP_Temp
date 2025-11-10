"""
PDF to Text Extraction Module
OPTIMIZED: Fast text extraction using PyMuPDF (fitz) with parallel processing
"""

try:
    import fitz  # PyMuPDF - much faster than pdfplumber
    PYMUPDF_AVAILABLE = True
except ImportError:
    import pdfplumber
    PYMUPDF_AVAILABLE = False
    
import os
from typing import Dict, List
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import lru_cache

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PDFExtractor:
    """Extract text from PDF files - OPTIMIZED VERSION"""
    
    def __init__(self, use_parallel=True, max_workers=4):
        """
        Initialize PDF extractor
        
        Args:
            use_parallel: Use parallel processing for multiple pages
            max_workers: Number of parallel workers
        """
        self.extracted_texts = {}
        self.use_parallel = use_parallel
        self.max_workers = max_workers
        
        if PYMUPDF_AVAILABLE:
            logger.info("Using PyMuPDF (fast mode)")
        else:
            logger.info("Using pdfplumber (slower - consider installing PyMuPDF: pip install PyMuPDF)")
    
    def extract_from_file(self, pdf_path: str) -> Dict[str, any]:
        """
        Extract text from a single PDF file - OPTIMIZED
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Dictionary containing filename, full text, and page-wise text
        """
        try:
            filename = os.path.basename(pdf_path)
            logger.info(f"Extracting text from: {filename}")
            
            if PYMUPDF_AVAILABLE:
                return self._extract_with_pymupdf(pdf_path, filename)
            else:
                return self._extract_with_pdfplumber(pdf_path, filename)
                
        except Exception as e:
            logger.error(f"Error extracting text from {pdf_path}: {str(e)}")
            return None
    
    def _extract_with_pymupdf(self, pdf_path: str, filename: str) -> Dict:
        """
        Fast extraction using PyMuPDF (3-10x faster than pdfplumber)
        """
        page_texts = []
        full_text = ""
        
        # Open PDF with PyMuPDF
        doc = fitz.open(pdf_path)
        
        try:
            # For small PDFs, extract sequentially
            if len(doc) < 10 or not self.use_parallel:
                for page_num in range(len(doc)):
                    page = doc[page_num]
                    page_text = page.get_text("text")  # Fast text extraction
                    
                    if page_text and page_text.strip():
                        page_texts.append({
                            'page_num': page_num + 1,
                            'text': page_text
                        })
                        full_text += f"\n--- Page {page_num + 1} ---\n{page_text}"
            
            # For large PDFs, use parallel processing
            else:
                page_texts = self._extract_pages_parallel(doc)
                full_text = "\n".join([
                    f"--- Page {p['page_num']} ---\n{p['text']}" 
                    for p in page_texts
                ])
            
        finally:
            doc.close()
        
        result = {
            'filename': filename,
            'filepath': pdf_path,
            'full_text': full_text,
            'pages': page_texts,
            'total_pages': len(page_texts)
        }
        
        logger.info(f"✅ Extracted {len(page_texts)} pages from {filename} (fast mode)")
        return result
    
    def _extract_pages_parallel(self, doc) -> List[Dict]:
        """
        Extract pages in parallel for faster processing
        """
        page_texts = [None] * len(doc)
        
        def extract_single_page(page_num):
            page = doc[page_num]
            text = page.get_text("text")
            return page_num, text
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                executor.submit(extract_single_page, i): i 
                for i in range(len(doc))
            }
            
            for future in as_completed(futures):
                page_num, text = future.result()
                if text and text.strip():
                    page_texts[page_num] = {
                        'page_num': page_num + 1,
                        'text': text
                    }
        
        # Filter out None values
        return [p for p in page_texts if p is not None]
    
    def _extract_with_pdfplumber(self, pdf_path: str, filename: str) -> Dict:
        """
        Fallback extraction using pdfplumber (slower)
        """
        page_texts = []
        full_text = ""
        
        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages, 1):
                page_text = page.extract_text()
                if page_text:
                    page_texts.append({
                        'page_num': page_num,
                        'text': page_text
                    })
                    full_text += f"\n--- Page {page_num} ---\n{page_text}"
        
        result = {
            'filename': filename,
            'filepath': pdf_path,
            'full_text': full_text,
            'pages': page_texts,
            'total_pages': len(page_texts)
        }
        
        logger.info(f"Extracted {len(page_texts)} pages from {filename}")
        return result
    
    def extract_from_directory(self, directory_path: str) -> List[Dict]:
        """
        Extract text from all PDFs in a directory
        
        Args:
            directory_path: Path to directory containing PDFs
            
        Returns:
            List of dictionaries containing extracted text from each PDF
        """
        extracted_docs = []
        
        if not os.path.exists(directory_path):
            logger.error(f"Directory not found: {directory_path}")
            return extracted_docs
        
        pdf_files = [f for f in os.listdir(directory_path) if f.lower().endswith('.pdf')]
        logger.info(f"Found {len(pdf_files)} PDF files in {directory_path}")
        
        for pdf_file in pdf_files:
            pdf_path = os.path.join(directory_path, pdf_file)
            result = self.extract_from_file(pdf_path)
            if result:
                extracted_docs.append(result)
        
        return extracted_docs


def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Simple function to extract text from a PDF
    
    Args:
        pdf_path: Path to PDF file
        
    Returns:
        Extracted text as string
    """
    extractor = PDFExtractor()
    result = extractor.extract_from_file(pdf_path)
    return result['full_text'] if result else ""


if __name__ == "__main__":
    # Test the extractor
    extractor = PDFExtractor()
    
    # Test with a single file
    test_pdf = "../data/raw_docs/sample.pdf"
    if os.path.exists(test_pdf):
        result = extractor.extract_from_file(test_pdf)
        print(f"Extracted {result['total_pages']} pages")
        print(f"First 500 characters:\n{result['full_text'][:500]}")
