"""
Vagueness Detector Module
Uses Gemini API to detect and classify vague language in text
"""

import google.generativeai as genai
from typing import Dict, List, Optional
import json
import re
import logging
import time
from .qualifiers import VaguenessQualifiers, COMMON_ACRONYMS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VaguenessDetector:
    """Detect vague language using Gemini AI"""
    
    def __init__(self, api_key: str, model_name: str = "gemini-2.0-flash-lite", max_retries: int = 3, timeout: int = 120):
        """
        Initialize vagueness detector
        
        Args:
            api_key: Gemini API key
            model_name: Gemini model to use (gemini-2.0-flash-lite is fastest)
            max_retries: Maximum number of retry attempts
            timeout: Timeout in seconds for API calls
        """
        genai.configure(api_key=api_key)
        
        # Try to list available models to verify API key works
        try:
            available_models = []
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    available_models.append(m.name)
            
            if available_models:
                logger.info(f"Available models: {', '.join(available_models)}")
            else:
                logger.warning("No models with generateContent support found!")
        except Exception as e:
            logger.warning(f"Could not list models: {e}")
        
        # Configure generation with timeout
        generation_config = genai.GenerationConfig(
            temperature=0.3,
            top_p=0.95,
            top_k=40,
            max_output_tokens=2048,
        )
        
        # Try to initialize model
        try:
            self.model = genai.GenerativeModel(
                model_name,
                generation_config=generation_config
            )
            logger.info(f"✅ Successfully initialized VaguenessDetector with model: {model_name}")
        except Exception as e:
            logger.error(f"❌ Failed to initialize model {model_name}: {e}")
            # Try fallback models from Gemini 2.x family (in order of speed/availability)
            fallback_models = [
                "gemini-2.0-flash-lite",     # Fastest - 30 req/min
                "gemini-2.5-flash-lite",     # Very fast - 15 req/min
                "gemini-2.0-flash",          # Fast - 15 req/min
                "gemini-2.5-flash",          # Fast - 10 req/min
                "gemini-2.5-pro",            # Best quality - 5 req/min
                "models/gemini-2.0-flash-lite",
                "models/gemini-2.5-flash",
            ]
            for fallback in fallback_models:
                try:
                    logger.info(f"Trying fallback model: {fallback}")
                    self.model = genai.GenerativeModel(
                        fallback,
                        generation_config=generation_config
                    )
                    logger.info(f"✅ Using fallback model: {fallback}")
                    break
                except Exception as e2:
                    logger.warning(f"Fallback {fallback} also failed: {e2}")
                    continue
            else:
                # No models worked
                raise ValueError(
                    f"Could not initialize any Gemini model. "
                    f"Please check:\n"
                    f"1. API key is valid\n"
                    f"2. Gemini API is enabled in your Google Cloud project\n"
                    f"3. You have access to Gemini models\n"
                    f"Visit: https://makersuite.google.com/app/apikey"
                )
        
        self.qualifiers = VaguenessQualifiers()
        self.max_retries = max_retries
        self.timeout = timeout
    
    def detect_vagueness_in_text(self, text: str, chunk_id: int = 0) -> Dict:
        """
        Detect vagueness in a text chunk
        
        Args:
            text: Text to analyze
            chunk_id: ID of the chunk
            
        Returns:
            Dictionary containing detection results
        """
        # First, check with rule-based qualifiers
        rule_based_matches = self.qualifiers.check_text_all_qualifiers(text)
        
        # Then, use Gemini for deeper analysis
        gemini_analysis = self._analyze_with_gemini(text)
        
        # Detect acronyms
        acronyms = self._detect_acronyms(text)
        
        # Combine results
        result = {
            'chunk_id': chunk_id,
            'text': text,
            'is_vague': bool(rule_based_matches) or gemini_analysis.get('is_vague', False),
            'rule_based_matches': rule_based_matches,
            'gemini_analysis': gemini_analysis,
            'acronyms': acronyms,
            'vagueness_score': self._calculate_vagueness_score(rule_based_matches, gemini_analysis)
        }
        
        return result
    
    def _analyze_with_gemini(self, text: str) -> Dict:
        """
        Use Gemini to analyze text for vagueness
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary with Gemini's analysis
        """
        prompt = f"""
You are an expert in analyzing technical and contractual documents for vague, ambiguous, or poorly defined language.

Analyze the following text and identify any vague or ambiguous language:

TEXT: "{text}"

Classify any vagueness into these categories:
1. Abstractness & Subjective Language - subjective terms needing interpretation
2. Ambiguous Modifiers & Comparative Phrases - fuzzy concepts without bounds
3. Referent Ambiguity & Complex Noun Phrases - unclear actors or referents
4. Open-Ended / Non-Verifiable Terms - conditional phrasing creating loopholes
5. Negative & Passive Structures - passive voice reducing clarity

Provide your response in JSON format with the following structure:
{{
    "is_vague": true/false,
    "vague_phrases": ["phrase1", "phrase2"],
    "categories": ["category1", "category2"],
    "explanation": "Brief explanation of why this is vague",
    "severity": "low/medium/high"
}}

Response:
"""
        
        # Retry logic for network issues
        for attempt in range(self.max_retries):
            try:
                # Generate content (timeout handled by generation_config)
                response = self.model.generate_content(prompt)
                
                # Extract JSON from response
                response_text = response.text.strip()
                
                # Try to parse JSON
                # Remove markdown code blocks if present
                if "```json" in response_text:
                    response_text = response_text.split("```json")[1].split("```")[0].strip()
                elif "```" in response_text:
                    response_text = response_text.split("```")[1].split("```")[0].strip()
                
                result = json.loads(response_text)
                return result
                
            except Exception as e:
                error_msg = str(e)
                
                # Check if it's a network/timeout error
                if any(x in error_msg.lower() for x in ['timeout', 'connect', '503', 'network']):
                    if attempt < self.max_retries - 1:
                        wait_time = (attempt + 1) * 2  # Exponential backoff: 2s, 4s, 6s
                        logger.warning(f"Network error (attempt {attempt + 1}/{self.max_retries}): {error_msg}")
                        logger.info(f"Retrying in {wait_time} seconds...")
                        time.sleep(wait_time)
                        continue
                    else:
                        logger.error(f"Max retries reached. Error: {error_msg}")
                else:
                    logger.error(f"Error in Gemini analysis: {error_msg}")
                
                # Return safe fallback
                return {
                    'is_vague': False,
                    'vague_phrases': [],
                    'categories': [],
                    'explanation': f"Error in analysis: {error_msg}",
                    'severity': 'unknown'
                }
    
    def _detect_acronyms(self, text: str) -> List[Dict]:
        """
        Detect acronyms in text
        
        Args:
            text: Text to analyze
            
        Returns:
            List of detected acronyms with information
        """
        # Pattern for acronyms (2+ capital letters, possibly with numbers)
        acronym_pattern = r'\b[A-Z]{2,}(?:\d+)?(?::[A-Z]?\d+)?\b'
        
        matches = re.finditer(acronym_pattern, text)
        acronyms = []
        
        for match in matches:
            acronym = match.group()
            info = {
                'acronym': acronym,
                'position': match.span(),
                'known': acronym in COMMON_ACRONYMS,
                'meaning': COMMON_ACRONYMS.get(acronym, 'Unknown')
            }
            acronyms.append(info)
        
        return acronyms
    
    def _calculate_vagueness_score(self, 
                                   rule_based_matches: Dict, 
                                   gemini_analysis: Dict) -> float:
        """
        Calculate overall vagueness score
        
        Args:
            rule_based_matches: Rule-based detection results
            gemini_analysis: Gemini analysis results
            
        Returns:
            Vagueness score (0-1)
        """
        score = 0.0
        
        # Rule-based contribution (max 0.5)
        if rule_based_matches:
            total_matches = sum(len(matches) for matches in rule_based_matches.values())
            score += min(total_matches * 0.1, 0.5)
        
        # Gemini analysis contribution (max 0.5)
        if gemini_analysis.get('is_vague'):
            severity = gemini_analysis.get('severity', 'medium')
            severity_scores = {'low': 0.2, 'medium': 0.35, 'high': 0.5}
            score += severity_scores.get(severity, 0.35)
        
        return min(score, 1.0)
    
    def detect_batch(self, chunks: List[Dict]) -> List[Dict]:
        """
        Detect vagueness in multiple chunks
        
        Args:
            chunks: List of text chunks
            
        Returns:
            List of detection results
        """
        results = []
        
        logger.info(f"Detecting vagueness in {len(chunks)} chunks")
        
        for i, chunk in enumerate(chunks):
            text = chunk.get('text', '')
            chunk_id = chunk.get('chunk_id', i)
            
            result = self.detect_vagueness_in_text(text, chunk_id)
            result['metadata'] = chunk.get('metadata', {})
            
            results.append(result)
            
            if (i + 1) % 10 == 0:
                logger.info(f"Processed {i + 1}/{len(chunks)} chunks")
        
        logger.info(f"Completed vagueness detection for {len(chunks)} chunks")
        return results
    
    def filter_vague_chunks(self, results: List[Dict], threshold: float = 0.3) -> List[Dict]:
        """
        Filter results to only include vague chunks
        
        Args:
            results: Detection results
            threshold: Minimum vagueness score to include
            
        Returns:
            Filtered list of vague chunks
        """
        vague_chunks = [
            r for r in results 
            if r.get('is_vague') and r.get('vagueness_score', 0) >= threshold
        ]
        
        logger.info(f"Found {len(vague_chunks)} vague chunks above threshold {threshold}")
        return vague_chunks


if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    api_key = os.getenv('GEMINI_API_KEY')
    
    if api_key:
        detector = VaguenessDetector(api_key)
        
        test_text = "The contractor shall use quality materials where possible and complete work faster than previous projects."
        
        result = detector.detect_vagueness_in_text(test_text)
        
        print(f"\nVagueness Analysis:")
        print(f"Is Vague: {result['is_vague']}")
        print(f"Score: {result['vagueness_score']:.2f}")
        print(f"\nGemini Analysis:")
        print(json.dumps(result['gemini_analysis'], indent=2))
    else:
        print("Please set GEMINI_API_KEY in .env file")
