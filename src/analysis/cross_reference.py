"""
Cross-Reference Analysis Module
Searches for relevant information about vague phrases across all uploaded documents
"""

import google.generativeai as genai
from typing import Dict, List, Optional, Tuple
import json
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CrossReferenceAnalyzer:
    """Analyze cross-references for vague phrases across documents"""
    
    def __init__(self, api_key: str, embedding_manager, model_name: str = "gemini-2.0-flash-lite"):
        """
        Initialize cross-reference analyzer
        
        Args:
            api_key: Gemini API key
            embedding_manager: EmbeddingManager instance
            model_name: Gemini model to use
        """
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)
        self.embedding_manager = embedding_manager
        
        logger.info(f"Initialized CrossReferenceAnalyzer with model: {model_name}")
    
    def search_related_chunks(self, 
                             vague_phrase: str,
                             original_context: str,
                             collection_name: str = "tender_documents",
                             n_results: int = 10,
                             exclude_chunk_id: str = None) -> List[Dict]:
        """
        Search for chunks that might contain relevant information about the vague phrase
        
        Args:
            vague_phrase: The vague phrase to search for
            original_context: Original context around the phrase
            collection_name: Collection to search in
            n_results: Number of results to retrieve
            exclude_chunk_id: Chunk ID to exclude (the original chunk)
            
        Returns:
            List of potentially relevant chunks
        """
        try:
            # Create search query
            search_query = f"{vague_phrase} definition specification details requirements"
            
            # Search in vector database
            results = self.embedding_manager.search_similar(
                collection_name,
                search_query,
                n_results=n_results
            )
            
            # Format results
            formatted_results = []
            
            if results and 'documents' in results and results['documents']:
                for i, doc in enumerate(results['documents'][0]):
                    chunk_id = results['ids'][0][i] if 'ids' in results else None
                    
                    # Skip the original chunk
                    if chunk_id == exclude_chunk_id:
                        continue
                    
                    formatted_results.append({
                        'text': doc,
                        'metadata': results['metadatas'][0][i] if 'metadatas' in results else {},
                        'distance': results['distances'][0][i] if 'distances' in results else None,
                        'id': chunk_id,
                        'similarity_score': 1 - results['distances'][0][i] if 'distances' in results else 0
                    })
            
            logger.info(f"Found {len(formatted_results)} related chunks for phrase: {vague_phrase}")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error searching related chunks: {str(e)}")
            return []
    
    def analyze_chunk_relevance(self,
                                vague_phrase: str,
                                vague_context: str,
                                related_chunk: Dict) -> Dict:
        """
        Use Gemini to analyze if a related chunk provides clarifying information
        
        Args:
            vague_phrase: The vague phrase
            vague_context: Original context with vague phrase
            related_chunk: Potentially related chunk
            
        Returns:
            Dictionary with relevance analysis
        """
        prompt = f"""
You are an expert at analyzing technical documents to identify clarifying information.

VAGUE PHRASE: "{vague_phrase}"
ORIGINAL CONTEXT: "{vague_context}"

POTENTIALLY RELATED CHUNK:
"{related_chunk['text']}"

CHUNK SOURCE: {related_chunk.get('metadata', {}).get('filename', 'Unknown document')}

Analyze if this related chunk provides any clarifying information about the vague phrase.

Consider:
1. Does it define or specify what "{vague_phrase}" means?
2. Does it provide measurable criteria, standards, or specifications?
3. Does it give examples or details that reduce ambiguity?
4. Is the information directly relevant and helpful?

Provide your response in JSON format:
{{
    "is_relevant": true/false,
    "relevance_score": 0.0-1.0,
    "clarification_type": "definition|specification|example|standard|none",
    "key_information": "What specific information does this provide?",
    "reasoning": "Why is this relevant or not relevant?",
    "extracted_details": ["detail1", "detail2"]
}}

Response:
"""
        
        try:
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            
            # Parse JSON
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            result = json.loads(response_text)
            
            # Add metadata
            result['chunk_id'] = related_chunk.get('id')
            result['source_document'] = related_chunk.get('metadata', {}).get('filename', 'Unknown')
            result['similarity_score'] = related_chunk.get('similarity_score', 0)
            result['chunk_text'] = related_chunk['text']
            
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing chunk relevance: {str(e)}")
            return {
                'is_relevant': False,
                'relevance_score': 0.0,
                'clarification_type': 'none',
                'key_information': '',
                'reasoning': f'Error in analysis: {str(e)}',
                'extracted_details': [],
                'chunk_id': related_chunk.get('id'),
                'source_document': related_chunk.get('metadata', {}).get('filename', 'Unknown'),
                'similarity_score': related_chunk.get('similarity_score', 0),
                'chunk_text': related_chunk['text']
            }
    
    def calculate_cross_reference_score(self,
                                       vague_phrase: str,
                                       relevance_analyses: List[Dict]) -> Tuple[float, Dict]:
        """
        Calculate overall cross-reference score and generate reasoning
        
        Args:
            vague_phrase: The vague phrase
            relevance_analyses: List of relevance analyses for related chunks
            
        Returns:
            Tuple of (score, reasoning_dict)
        """
        if not relevance_analyses:
            return 0.0, {
                'score': 0.0,
                'interpretation': 'no_information',
                'reasoning': 'No related information found in uploaded documents.',
                'evidence_count': 0,
                'clarification_types': []
            }
        
        # Filter relevant chunks
        relevant_chunks = [a for a in relevance_analyses if a.get('is_relevant', False)]
        
        if not relevant_chunks:
            return 0.1, {
                'score': 0.1,
                'interpretation': 'weak_connection',
                'reasoning': f'Found {len(relevance_analyses)} related chunks, but none provide clear clarification for "{vague_phrase}".',
                'evidence_count': 0,
                'clarification_types': []
            }
        
        # Calculate weighted score
        # Factors: number of relevant chunks, their relevance scores, clarification types
        
        num_relevant = len(relevant_chunks)
        avg_relevance = sum(c.get('relevance_score', 0) for c in relevant_chunks) / num_relevant
        
        # Bonus for multiple sources of clarification
        source_diversity = len(set(c.get('source_document', '') for c in relevant_chunks))
        diversity_bonus = min(source_diversity * 0.1, 0.3)
        
        # Bonus for strong clarification types
        clarification_types = [c.get('clarification_type', 'none') for c in relevant_chunks]
        type_weights = {
            'definition': 0.4,
            'specification': 0.3,
            'standard': 0.3,
            'example': 0.2,
            'none': 0.0
        }
        type_bonus = sum(type_weights.get(ct, 0) for ct in clarification_types) / len(clarification_types)
        
        # Calculate final score (0-1)
        base_score = avg_relevance * 0.5
        bonus_score = (diversity_bonus + type_bonus) * 0.5
        final_score = min(base_score + bonus_score, 1.0)
        
        # Generate interpretation
        if final_score >= 0.8:
            interpretation = 'strong_clarification'
            interpretation_text = f'Strong clarification found: {num_relevant} relevant chunk(s) provide clear information about "{vague_phrase}".'
        elif final_score >= 0.6:
            interpretation = 'moderate_clarification'
            interpretation_text = f'Moderate clarification found: {num_relevant} chunk(s) provide some information about "{vague_phrase}".'
        elif final_score >= 0.4:
            interpretation = 'partial_clarification'
            interpretation_text = f'Partial clarification found: {num_relevant} chunk(s) provide limited information about "{vague_phrase}".'
        else:
            interpretation = 'weak_clarification'
            interpretation_text = f'Weak clarification: {num_relevant} chunk(s) found but information is limited.'
        
        # Build detailed reasoning
        reasoning_parts = [interpretation_text]
        
        # Add information about sources
        if source_diversity > 1:
            reasoning_parts.append(f'Information found across {source_diversity} different document(s).')
        
        # Add information about clarification types
        unique_types = set(ct for ct in clarification_types if ct != 'none')
        if unique_types:
            types_text = ', '.join(unique_types)
            reasoning_parts.append(f'Types of clarification: {types_text}.')
        
        reasoning_dict = {
            'score': final_score,
            'interpretation': interpretation,
            'reasoning': ' '.join(reasoning_parts),
            'evidence_count': num_relevant,
            'clarification_types': list(unique_types) if unique_types else [],
            'source_diversity': source_diversity,
            'calculation_breakdown': {
                'base_score': base_score,
                'diversity_bonus': diversity_bonus,
                'type_bonus': type_bonus,
                'final_score': final_score
            }
        }
        
        return final_score, reasoning_dict
    
    def analyze_vague_chunk_cross_references(self,
                                            vague_chunk: Dict,
                                            collection_name: str = "tender_documents") -> Dict:
        """
        Complete cross-reference analysis for a vague chunk
        
        Args:
            vague_chunk: Vague chunk from detection results
            collection_name: Collection to search in
            
        Returns:
            Dictionary with complete cross-reference analysis
        """
        chunk_text = vague_chunk.get('text', '')
        chunk_id = vague_chunk.get('chunk_id')
        vague_phrases = vague_chunk.get('gemini_analysis', {}).get('vague_phrases', [])
        
        if not vague_phrases:
            return {
                'chunk_id': chunk_id,
                'has_cross_references': False,
                'cross_reference_score': 0.0,
                'phrase_analyses': []
            }
        
        all_phrase_analyses = []
        
        for phrase in vague_phrases:
            logger.info(f"Analyzing cross-references for phrase: {phrase}")
            
            # Step 1: Search for related chunks
            related_chunks = self.search_related_chunks(
                phrase,
                chunk_text,
                collection_name,
                n_results=10,
                exclude_chunk_id=chunk_id
            )
            
            # Step 2: Analyze each related chunk
            relevance_analyses = []
            for related_chunk in related_chunks[:5]:  # Analyze top 5
                analysis = self.analyze_chunk_relevance(
                    phrase,
                    chunk_text,
                    related_chunk
                )
                relevance_analyses.append(analysis)
            
            # Step 3: Calculate cross-reference score for this phrase
            xref_score, reasoning = self.calculate_cross_reference_score(
                phrase,
                relevance_analyses
            )
            
            phrase_analysis = {
                'vague_phrase': phrase,
                'related_chunks_found': len(related_chunks),
                'relevant_chunks_found': len([a for a in relevance_analyses if a.get('is_relevant', False)]),
                'cross_reference_score': xref_score,
                'reasoning': reasoning,
                'top_relevant_chunks': [a for a in relevance_analyses if a.get('is_relevant', False)][:3]
            }
            
            all_phrase_analyses.append(phrase_analysis)
        
        # Calculate overall cross-reference score for the chunk
        if all_phrase_analyses:
            overall_score = sum(pa['cross_reference_score'] for pa in all_phrase_analyses) / len(all_phrase_analyses)
        else:
            overall_score = 0.0
        
        return {
            'chunk_id': chunk_id,
            'has_cross_references': overall_score > 0.3,
            'cross_reference_score': overall_score,
            'phrase_analyses': all_phrase_analyses,
            'summary': self._generate_summary(all_phrase_analyses, overall_score)
        }
    
    def _generate_summary(self, phrase_analyses: List[Dict], overall_score: float) -> str:
        """Generate a summary of cross-reference analysis"""
        if not phrase_analyses:
            return "No vague phrases to analyze."
        
        total_relevant = sum(pa['relevant_chunks_found'] for pa in phrase_analyses)
        
        if overall_score >= 0.8:
            return f"Excellent: Found clarifying information for most vague terms ({total_relevant} relevant chunks). Consider cross-referencing these sections."
        elif overall_score >= 0.6:
            return f"Good: Found clarifying information for some vague terms ({total_relevant} relevant chunks). Review related sections."
        elif overall_score >= 0.4:
            return f"Moderate: Limited clarifying information found ({total_relevant} relevant chunks). May need external references."
        elif overall_score >= 0.2:
            return f"Poor: Minimal clarifying information found ({total_relevant} relevant chunks). External standards recommended."
        else:
            return "No clarifying information found in uploaded documents. External references required."
    
    def batch_analyze_cross_references(self,
                                      vague_chunks: List[Dict],
                                      collection_name: str = "tender_documents") -> List[Dict]:
        """
        Analyze cross-references for multiple vague chunks
        
        Args:
            vague_chunks: List of vague chunks
            collection_name: Collection to search in
            
        Returns:
            List of chunks with cross-reference analysis
        """
        analyzed_chunks = []
        
        logger.info(f"Analyzing cross-references for {len(vague_chunks)} vague chunks")
        
        for i, chunk in enumerate(vague_chunks):
            logger.info(f"Processing chunk {i+1}/{len(vague_chunks)}")
            
            analysis = self.analyze_vague_chunk_cross_references(chunk, collection_name)
            
            # Add analysis to chunk
            chunk['cross_reference_analysis'] = analysis
            analyzed_chunks.append(chunk)
        
        logger.info(f"Completed cross-reference analysis for {len(vague_chunks)} chunks")
        return analyzed_chunks


if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    api_key = os.getenv('GEMINI_API_KEY')
    
    if api_key:
        from embeddings.create_embeddings import EmbeddingManager
        
        manager = EmbeddingManager()
        analyzer = CrossReferenceAnalyzer(api_key, manager)
        
        # Test
        test_chunk = {
            'chunk_id': 'test_chunk_1',
            'text': 'The contractor shall use quality materials for construction.',
            'gemini_analysis': {
                'vague_phrases': ['quality materials']
            }
        }
        
        result = analyzer.analyze_vague_chunk_cross_references(test_chunk)
        print(json.dumps(result, indent=2))
    else:
        print("Please set GEMINI_API_KEY in .env file")