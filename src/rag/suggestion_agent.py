"""
Suggestion Agent Module
Uses Gemini API with RAG-retrieved context to generate improvement suggestions
"""

import google.generativeai as genai
from typing import Dict, List, Optional
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SuggestionAgent:
    """Generate suggestions using Gemini with RAG context"""
    
    def __init__(self, api_key: str, retriever, model_name: str = "gemini-2.0-flash-lite"):
        """
        Initialize suggestion agent
        
        Args:
            api_key: Gemini API key
            retriever: RAGRetriever instance
            model_name: Gemini model to use
        """
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)
        self.retriever = retriever
        
        logger.info(f"Initialized SuggestionAgent with model: {model_name}")
    
    def identify_source_documents(self, vague_phrase: str, context: str = "") -> Dict:
        """
        Ask Gemini to identify which reference documents might contain relevant information
        
        Args:
            vague_phrase: The vague phrase to clarify
            context: Original context around the phrase
            
        Returns:
            Dictionary with document suggestions from Gemini
        """
        prompt = f"""
You are an expert in Indian construction standards, IS Codes, CPWD manuals, and technical specifications.

Given this vague phrase from a tender document: "{vague_phrase}"
Context: "{context}"

Identify which specific reference documents or standards would help clarify this vague language.

Consider:
- IS Codes (Indian Standards) for materials, testing, specifications
- CPWD manuals and specifications
- Other relevant technical standards

Provide your response in JSON format:
{{
    "suggested_documents": ["Document1", "Document2"],
    "search_terms": ["term1", "term2", "term3"],
    "reasoning": "Why these documents would help clarify this vague phrase"
}}

Focus on specific IS codes (like IS 456 for concrete, IS 383 for aggregates) when applicable.

Response:
"""
        
        try:
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            
            # Parse JSON from response
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            result = json.loads(response_text)
            return result
            
        except Exception as e:
            logger.error(f"Error identifying source documents: {str(e)}")
            return {
                'suggested_documents': [],
                'search_terms': [vague_phrase],
                'reasoning': f"Error: {str(e)}"
            }
    
    def retrieve_relevant_chunks(self, 
                                document_suggestions: Dict,
                                vague_phrase: str) -> List[Dict]:
        """
        Retrieve relevant chunks based on Gemini's document suggestions
        
        Args:
            document_suggestions: Output from identify_source_documents
            vague_phrase: The vague phrase
            
        Returns:
            List of relevant document chunks
        """
        all_chunks = []
        
        # Get search terms from Gemini
        search_terms = document_suggestions.get('search_terms', [vague_phrase])
        
        # Search for each term
        for term in search_terms:
            chunks = self.retriever.retrieve_for_phrase(term, n_results=3)
            all_chunks.extend(chunks)
        
        # Remove duplicates based on id
        unique_chunks = {}
        for chunk in all_chunks:
            chunk_id = chunk.get('id')
            if chunk_id and chunk_id not in unique_chunks:
                unique_chunks[chunk_id] = chunk
        
        return list(unique_chunks.values())
    
    def generate_suggestion(self, 
                          vague_text: str,
                          vague_phrase: str,
                          vagueness_category: str,
                          reference_context: List[Dict]) -> Dict:
        """
        Generate improvement suggestion using retrieved reference context
        
        Args:
            vague_text: The full vague sentence/chunk
            vague_phrase: Specific vague phrase identified
            vagueness_category: Category of vagueness
            reference_context: Retrieved reference documents
            
        Returns:
            Dictionary with suggestion
        """
        # Format reference context
        context_str = "\n\n".join([
            f"Reference {i+1} (from {ref.get('metadata', {}).get('filename', 'Unknown')}):\n{ref.get('text', '')}"
            for i, ref in enumerate(reference_context[:3])
        ])
        
        prompt = f"""
You are an expert in improving technical and contractual language for construction tenders.

ORIGINAL TEXT: "{vague_text}"
VAGUE PHRASE: "{vague_phrase}"
VAGUENESS TYPE: {vagueness_category}

REFERENCE CONTEXT FROM STANDARDS:
{context_str if context_str else "No specific reference found."}

Based on the reference standards, provide a specific, clear, and measurable improvement for this vague language.

Your suggestion should:
1. Remove ambiguity and subjectivity
2. Reference specific standards or codes when available
3. Use precise, measurable terms
4. Maintain the original intent

Provide your response in JSON format:
{{
    "improved_text": "The rewritten sentence with clarity",
    "specific_changes": ["Change 1", "Change 2"],
    "standards_referenced": ["IS Code 1", "CPWD Specification 2"],
    "explanation": "Brief explanation of improvements"
}}

Response:
"""
        
        try:
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            
            # Parse JSON from response
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            result = json.loads(response_text)
            
            # Add metadata
            result['original_text'] = vague_text
            result['vague_phrase'] = vague_phrase
            result['reference_chunks_used'] = len(reference_context)
            
            return result
            
        except Exception as e:
            logger.error(f"Error generating suggestion: {str(e)}")
            return {
                'improved_text': vague_text,
                'specific_changes': [],
                'standards_referenced': [],
                'explanation': f"Error generating suggestion: {str(e)}",
                'original_text': vague_text,
                'vague_phrase': vague_phrase,
                'reference_chunks_used': 0
            }
    
    def process_vague_chunk(self, detection_result: Dict) -> Dict:
        """
        Complete pipeline: identify sources -> retrieve context -> generate suggestion
        
        Args:
            detection_result: Result from vagueness detection
            
        Returns:
            Dictionary with complete suggestion pipeline results
        """
        text = detection_result.get('text', '')
        vague_phrases = detection_result.get('gemini_analysis', {}).get('vague_phrases', [])
        categories = detection_result.get('gemini_analysis', {}).get('categories', [])
        
        suggestions = []
        
        for i, phrase in enumerate(vague_phrases):
            category = categories[i] if i < len(categories) else "Unknown"
            
            # Step 1: Ask Gemini which documents to search
            logger.info(f"Step 1: Identifying source documents for phrase: {phrase}")
            doc_suggestions = self.identify_source_documents(phrase, text)
            
            # Step 2: Retrieve relevant chunks based on Gemini's suggestions
            logger.info(f"Step 2: Retrieving chunks based on search terms: {doc_suggestions.get('search_terms', [])}")
            retrieved_chunks = self.retrieve_relevant_chunks(doc_suggestions, phrase)
            
            # Step 3: Generate suggestion with retrieved context
            logger.info(f"Step 3: Generating suggestion with {len(retrieved_chunks)} retrieved chunks")
            suggestion = self.generate_suggestion(
                text,
                phrase,
                category,
                retrieved_chunks
            )
            
            # Combine all information
            complete_suggestion = {
                'vague_phrase': phrase,
                'category': category,
                'document_suggestions': doc_suggestions,
                'retrieved_chunks_count': len(retrieved_chunks),
                'retrieved_chunks': retrieved_chunks,
                'suggestion': suggestion
            }
            
            suggestions.append(complete_suggestion)
        
        # Add suggestions to detection result
        detection_result['suggestions'] = suggestions
        
        return detection_result
    
    def process_batch(self, detection_results: List[Dict]) -> List[Dict]:
        """
        Process multiple detection results to generate suggestions
        
        Args:
            detection_results: List of vagueness detection results
            
        Returns:
            List of results with suggestions
        """
        processed_results = []
        
        logger.info(f"Processing {len(detection_results)} chunks for suggestions")
        
        for i, result in enumerate(detection_results):
            if result.get('is_vague'):
                processed = self.process_vague_chunk(result)
                processed_results.append(processed)
            else:
                processed_results.append(result)
            
            if (i + 1) % 5 == 0:
                logger.info(f"Processed {i + 1}/{len(detection_results)} chunks")
        
        logger.info(f"Completed suggestion generation for {len(detection_results)} chunks")
        return processed_results


if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    from ..embeddings.create_embeddings import EmbeddingManager
    from ..rag.retriever import RAGRetriever
    
    load_dotenv()
    api_key = os.getenv('GEMINI_API_KEY')
    
    if api_key:
        # Initialize components
        manager = EmbeddingManager()
        retriever = RAGRetriever(manager)
        agent = SuggestionAgent(api_key, retriever)
        
        # Test document identification
        doc_suggestions = agent.identify_source_documents(
            "quality materials",
            "The contractor shall use quality materials for construction"
        )
        
        print("Document Suggestions:")
        print(json.dumps(doc_suggestions, indent=2))
    else:
        print("Please set GEMINI_API_KEY in .env file")
