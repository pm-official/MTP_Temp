"""
Embeddings Module
Creates embeddings and stores them in ChromaDB for semantic search
"""

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from typing import List, Dict
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EmbeddingManager:
    """Manage embeddings and vector database operations"""
    
    def __init__(self, 
                 embedding_model: str = 'all-MiniLM-L6-v2',
                 persist_directory: str = './data/embeddings'):
        """
        Initialize embedding manager
        
        Args:
            embedding_model: Name of sentence-transformers model
            persist_directory: Directory to persist ChromaDB
        """
        self.embedding_model = SentenceTransformer(embedding_model)
        self.persist_directory = persist_directory
        
        # Create directory if it doesn't exist
        os.makedirs(persist_directory, exist_ok=True)
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(path=persist_directory)
        
        logger.info(f"Initialized EmbeddingManager with model: {embedding_model}")
    
    def create_collection(self, collection_name: str, reset: bool = False):
        """
        Create or get a collection
        
        Args:
            collection_name: Name of the collection
            reset: If True, delete existing collection and create new one
            
        Returns:
            ChromaDB collection
        """
        if reset:
            try:
                self.client.delete_collection(collection_name)
                logger.info(f"Deleted existing collection: {collection_name}")
            except:
                pass
        
        collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )
        
        logger.info(f"Collection '{collection_name}' ready")
        return collection
    
    def add_documents_to_collection(self, 
                                   collection_name: str,
                                   chunks: List[Dict],
                                   batch_size: int = 100):
        """
        Add documents to collection with embeddings
        
        Args:
            collection_name: Name of the collection
            chunks: List of chunk dictionaries
            batch_size: Number of chunks to process at once
        """
        collection = self.client.get_collection(collection_name)
        
        total_chunks = len(chunks)
        logger.info(f"Adding {total_chunks} chunks to collection '{collection_name}'")
        
        for i in range(0, total_chunks, batch_size):
            batch = chunks[i:i + batch_size]
            
            # Prepare data
            texts = [chunk['text'] for chunk in batch]
            ids = [f"chunk_{chunk.get('chunk_id', i+j)}" for j, chunk in enumerate(batch)]
            
            # Create embeddings
            embeddings = self.embedding_model.encode(texts, convert_to_numpy=True).tolist()
            
            # Prepare metadata
            metadatas = []
            for chunk in batch:
                metadata = chunk.get('metadata', {})
                metadata['chunk_id'] = chunk.get('chunk_id', 0)
                metadata['text_preview'] = chunk['text'][:200]
                metadatas.append(metadata)
            
            # Add to collection
            collection.add(
                embeddings=embeddings,
                documents=texts,
                metadatas=metadatas,
                ids=ids
            )
            
            logger.info(f"Added batch {i//batch_size + 1}/{(total_chunks-1)//batch_size + 1}")
        
        logger.info(f"Successfully added {total_chunks} chunks to collection")
    
    def search_similar(self, 
                      collection_name: str,
                      query: str,
                      n_results: int = 5) -> Dict:
        """
        Search for similar documents
        
        Args:
            collection_name: Name of the collection to search
            query: Query text
            n_results: Number of results to return
            
        Returns:
            Dictionary containing search results
        """
        collection = self.client.get_collection(collection_name)
        
        # Create query embedding
        query_embedding = self.embedding_model.encode([query], convert_to_numpy=True).tolist()
        
        # Search
        results = collection.query(
            query_embeddings=query_embedding,
            n_results=n_results
        )
        
        return results
    
    def get_collection_stats(self, collection_name: str) -> Dict:
        """
        Get statistics about a collection
        
        Args:
            collection_name: Name of the collection
            
        Returns:
            Dictionary with collection statistics
        """
        try:
            collection = self.client.get_collection(collection_name)
            count = collection.count()
            return {
                'name': collection_name,
                'count': count,
                'exists': True
            }
        except:
            return {
                'name': collection_name,
                'count': 0,
                'exists': False
            }
    
    def list_collections(self) -> List[str]:
        """
        List all collections
        
        Returns:
            List of collection names
        """
        collections = self.client.list_collections()
        return [c.name for c in collections]


class ReferenceDocumentStore:
    """Specialized store for reference documents (IS Codes, CPWD manuals)"""
    
    def __init__(self, embedding_manager: EmbeddingManager):
        self.embedding_manager = embedding_manager
        self.collection_name = "reference_documents"
    
    def initialize(self, reset: bool = False):
        """Initialize reference document collection"""
        self.embedding_manager.create_collection(self.collection_name, reset=reset)
    
    def add_reference_docs(self, chunks: List[Dict]):
        """Add reference documents to the store"""
        self.embedding_manager.add_documents_to_collection(
            self.collection_name, 
            chunks
        )
    
    def search_reference(self, query: str, n_results: int = 5):
        """Search in reference documents"""
        return self.embedding_manager.search_similar(
            self.collection_name,
            query,
            n_results
        )


if __name__ == "__main__":
    # Test the embedding manager
    manager = EmbeddingManager()
    
    # Test chunks
    test_chunks = [
        {
            'chunk_id': 0,
            'text': 'The contractor shall use quality materials where possible.',
            'metadata': {'filename': 'test.pdf', 'page': 1}
        },
        {
            'chunk_id': 1,
            'text': 'All concrete work must comply with IS 456:2000 standards.',
            'metadata': {'filename': 'test.pdf', 'page': 1}
        }
    ]
    
    # Create collection and add documents
    manager.create_collection('test_collection', reset=True)
    manager.add_documents_to_collection('test_collection', test_chunks)
    
    # Test search
    results = manager.search_similar('test_collection', 'quality materials')
    print(f"Found {len(results['documents'][0])} results")
