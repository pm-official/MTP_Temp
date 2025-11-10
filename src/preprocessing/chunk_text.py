"""
Text Chunking Module
Chunks text into uniform segments for better token-level context alignment
"""

import re
from typing import List, Dict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TextChunker:
    """Chunk text into manageable segments"""
    
    def __init__(self, chunk_size: int = 500, overlap: int = 100):
        """
        Initialize chunker
        
        Args:
            chunk_size: Target size for each chunk (in characters)
            overlap: Overlap between consecutive chunks
        """
        self.chunk_size = chunk_size
        self.overlap = overlap
    
    def chunk_by_sentences(self, text: str, doc_metadata: Dict = None) -> List[Dict]:
        """
        Chunk text by sentences with overlap
        
        Args:
            text: Input text to chunk
            doc_metadata: Metadata about the source document
            
        Returns:
            List of chunk dictionaries
        """
        # Split into sentences
        sentences = self._split_into_sentences(text)
        
        # Create unique prefix from filename
        filename = doc_metadata.get('filename', 'unknown') if doc_metadata else 'unknown'
        # Remove extension and sanitize for ID
        base_name = filename.rsplit('.', 1)[0].replace(' ', '_').replace('-', '_')
        
        chunks = []
        current_chunk = []
        current_length = 0
        chunk_id = 0
        
        for i, sentence in enumerate(sentences):
            sentence_length = len(sentence)
            
            # If adding this sentence exceeds chunk_size, save current chunk
            if current_length + sentence_length > self.chunk_size and current_chunk:
                chunk_text = ' '.join(current_chunk)
                # Create unique chunk ID with filename prefix
                unique_id = f"{base_name}_chunk_{chunk_id}"
                chunks.append({
                    'chunk_id': unique_id,
                    'text': chunk_text,
                    'start_sentence': i - len(current_chunk),
                    'end_sentence': i - 1,
                    'metadata': doc_metadata or {}
                })
                chunk_id += 1
                
                # Keep overlap sentences
                overlap_sentences = self._get_overlap_sentences(current_chunk)
                current_chunk = overlap_sentences
                current_length = sum(len(s) for s in current_chunk)
            
            current_chunk.append(sentence)
            current_length += sentence_length
        
        # Add the last chunk
        if current_chunk:
            chunk_text = ' '.join(current_chunk)
            unique_id = f"{base_name}_chunk_{chunk_id}"
            chunks.append({
                'chunk_id': unique_id,
                'text': chunk_text,
                'start_sentence': len(sentences) - len(current_chunk),
                'end_sentence': len(sentences) - 1,
                'metadata': doc_metadata or {}
            })
        
        logger.info(f"Created {len(chunks)} chunks from text")
        return chunks
    
    def chunk_by_paragraphs(self, text: str, doc_metadata: Dict = None) -> List[Dict]:
        """
        Chunk text by paragraphs
        
        Args:
            text: Input text to chunk
            doc_metadata: Metadata about the source document
            
        Returns:
            List of chunk dictionaries
        """
        # Create unique prefix from filename
        filename = doc_metadata.get('filename', 'unknown') if doc_metadata else 'unknown'
        # Remove extension and sanitize for ID
        base_name = filename.rsplit('.', 1)[0].replace(' ', '_').replace('-', '_')
        
        # Split by double newlines (paragraphs)
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        
        chunks = []
        for i, para in enumerate(paragraphs):
            if len(para) > 50:  # Ignore very short paragraphs
                unique_id = f"{base_name}_para_{i}"
                chunks.append({
                    'chunk_id': unique_id,
                    'text': para,
                    'paragraph_num': i,
                    'metadata': doc_metadata or {}
                })
        
        logger.info(f"Created {len(chunks)} paragraph-based chunks")
        return chunks
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """
        Split text into sentences
        
        Args:
            text: Input text
            
        Returns:
            List of sentences
        """
        # Simple sentence splitter (can be improved with nltk)
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _get_overlap_sentences(self, sentences: List[str]) -> List[str]:
        """
        Get sentences for overlap based on overlap parameter
        
        Args:
            sentences: List of sentences
            
        Returns:
            List of sentences to keep for overlap
        """
        overlap_chars = 0
        overlap_sentences = []
        
        for sentence in reversed(sentences):
            overlap_chars += len(sentence)
            overlap_sentences.insert(0, sentence)
            if overlap_chars >= self.overlap:
                break
        
        return overlap_sentences
    
    def chunk_document(self, doc_data: Dict, method: str = 'sentences') -> List[Dict]:
        """
        Chunk a document with its metadata
        
        Args:
            doc_data: Document data from PDFExtractor
            method: Chunking method ('sentences' or 'paragraphs')
            
        Returns:
            List of chunks with metadata
        """
        metadata = {
            'filename': doc_data.get('filename', ''),
            'filepath': doc_data.get('filepath', ''),
            'total_pages': doc_data.get('total_pages', 0)
        }
        
        text = doc_data.get('full_text', '')
        
        if method == 'sentences':
            chunks = self.chunk_by_sentences(text, metadata)
        else:
            chunks = self.chunk_by_paragraphs(text, metadata)
        
        return chunks


if __name__ == "__main__":
    # Test the chunker
    sample_text = """
    The contractor shall use quality materials where possible. All work must be completed
    to a reasonable standard. The project timeline should be faster than previous projects.
    Payment will be issued upon completion. Materials should not be sourced from non-approved
    vendors. Implementation of the plan will begin when feasible.
    """
    
    chunker = TextChunker(chunk_size=100, overlap=20)
    chunks = chunker.chunk_by_sentences(sample_text)
    
    print(f"Created {len(chunks)} chunks:")
    for chunk in chunks:
        print(f"\nChunk {chunk['chunk_id']}:")
        print(f"Text: {chunk['text'][:100]}...")