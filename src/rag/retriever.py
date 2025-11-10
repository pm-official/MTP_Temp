"""
RAG Retriever Module
Retrieves relevant context from reference documents using semantic search
"""

from typing import List, Dict, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RAGRetriever:
    """Retrieve relevant context from vector database"""
    
    def __init__(self, embedding_manager):
        """
        Initialize RAG retriever
        
        Args:
            embedding_manager: Instance of EmbeddingManager
        """
        self.embedding_manager = embedding_manager
        self.reference_collection = "reference_documents"
        
        logger.info("Initialized RAGRetriever")
    
    def retrieve_for_phrase(self, 
                           vague_phrase: str,
                           context: str = "",
                           n_results: int = 5) -> List[Dict]:
        """
        Retrieve relevant reference documents for a vague phrase
        
        Args:
            vague_phrase: The vague phrase to search for
            context: Additional context around the phrase
            n_results: Number of results to return
            
        Returns:
            List of relevant document chunks
        """
        # Combine phrase with context for better retrieval
        query = f"{vague_phrase} {context}".strip()
        
        try:
            results = self.embedding_manager.search_similar(
                self.reference_collection,
                query,
                n_results
            )
            
            # Format results
            formatted_results = []
            
            if results and 'documents' in results and results['documents']:
                for i, doc in enumerate(results['documents'][0]):
                    formatted_results.append({
                        'text': doc,
                        'metadata': results['metadatas'][0][i] if 'metadatas' in results else {},
                        'distance': results['distances'][0][i] if 'distances' in results else None,
                        'id': results['ids'][0][i] if 'ids' in results else None
                    })
            
            logger.info(f"Retrieved {len(formatted_results)} results for phrase: {vague_phrase}")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error retrieving documents: {str(e)}")
            return []
    
    def retrieve_for_acronym(self, 
                            acronym: str,
                            n_results: int = 3) -> List[Dict]:
        """
        Retrieve definition for an acronym
        
        Args:
            acronym: The acronym to search for
            n_results: Number of results to return
            
        Returns:
            List of relevant document chunks
        """
        # Search for the acronym
        query = f"{acronym} definition meaning specification"
        
        return self.retrieve_for_phrase(query, n_results=n_results)
    
    def retrieve_multiple_phrases(self, 
                                  phrases: List[str],
                                  n_results_per_phrase: int = 3) -> Dict[str, List[Dict]]:
        """
        Retrieve context for multiple phrases
        
        Args:
            phrases: List of vague phrases
            n_results_per_phrase: Number of results per phrase
            
        Returns:
            Dictionary mapping phrases to their retrieved contexts
        """
        results = {}
        
        for phrase in phrases:
            results[phrase] = self.retrieve_for_phrase(
                phrase, 
                n_results=n_results_per_phrase
            )
        
        return results
    
    def get_best_reference_document(self, results: List[Dict]) -> Optional[Dict]:
        """
        Get the most relevant reference document from results
        
        Args:
            results: List of retrieval results
            
        Returns:
            Best matching document or None
        """
        if not results:
            return None
        
        # Sort by distance (lower is better)
        sorted_results = sorted(
            results, 
            key=lambda x: x.get('distance', float('inf'))
        )
        
        return sorted_results[0]
    
    def check_reference_availability(self) -> Dict:
        """
        Check if reference documents are available
        
        Returns:
            Dictionary with availability status
        """
        stats = self.embedding_manager.get_collection_stats(self.reference_collection)
        
        return {
            'available': stats['exists'] and stats['count'] > 0,
            'count': stats['count'],
            'collection_name': self.reference_collection
        }


class ContextEnhancer:
    """Enhance vague text with context from reference documents"""
    
    def __init__(self, retriever: RAGRetriever):
        """
        Initialize context enhancer
        
        Args:
            retriever: Instance of RAGRetriever
        """
        self.retriever = retriever
    
    def enhance_vague_phrase(self, 
                            vague_phrase: str,
                            original_context: str = "") -> Dict:
        """
        Enhance a vague phrase with reference context
        
        Args:
            vague_phrase: The vague phrase
            original_context: Original context around the phrase
            
        Returns:
            Dictionary with enhanced information
        """
        # Retrieve relevant references
        references = self.retriever.retrieve_for_phrase(
            vague_phrase, 
            original_context,
            n_results=3
        )
        
        # Get best reference
        best_ref = self.retriever.get_best_reference_document(references)
        
        enhancement = {
            'vague_phrase': vague_phrase,
            'original_context': original_context,
            'references_found': len(references),
            'best_reference': best_ref,
            'all_references': references
        }
        
        return enhancement
    
    def enhance_detection_results(self, 
                                 detection_results: List[Dict]) -> List[Dict]:
        """
        Enhance detection results with reference context
        
        Args:
            detection_results: List of vagueness detection results
            
        Returns:
            Enhanced results with reference context
        """
        enhanced_results = []
        
        for result in detection_results:
            if not result.get('is_vague'):
                enhanced_results.append(result)
                continue
            
            # Get vague phrases from Gemini analysis
            vague_phrases = result.get('gemini_analysis', {}).get('vague_phrases', [])
            
            # Enhance each phrase
            enhancements = []
            for phrase in vague_phrases:
                enhancement = self.enhance_vague_phrase(
                    phrase, 
                    result.get('text', '')
                )
                enhancements.append(enhancement)
            
            # Add enhancements to result
            result['reference_enhancements'] = enhancements
            enhanced_results.append(result)
        
        return enhanced_results


if __name__ == "__main__":
    from ..embeddings.create_embeddings import EmbeddingManager
    
    # Test the retriever
    manager = EmbeddingManager()
    retriever = RAGRetriever(manager)
    
    # Check if reference documents are available
    status = retriever.check_reference_availability()
    print(f"Reference documents available: {status['available']}")
    print(f"Document count: {status['count']}")
    
    if status['available']:
        # Test retrieval
        results = retriever.retrieve_for_phrase("quality materials")
        print(f"\nFound {len(results)} results for 'quality materials'")
        
        if results:
            best = retriever.get_best_reference_document(results)
            print(f"\nBest match: {best['text'][:200]}...")
