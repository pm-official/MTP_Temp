"""
Utility functions for the Vagueness Detection System
"""

import json
import os
from typing import Dict, List, Any
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def save_json(data: Any, filepath: str, indent: int = 2) -> bool:
    """
    Save data as JSON file
    
    Args:
        data: Data to save
        filepath: Path to save file
        indent: JSON indentation
        
    Returns:
        True if successful, False otherwise
    """
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=indent, ensure_ascii=False)
        logger.info(f"Saved JSON to {filepath}")
        return True
    except Exception as e:
        logger.error(f"Error saving JSON: {str(e)}")
        return False


def load_json(filepath: str) -> Any:
    """
    Load data from JSON file
    
    Args:
        filepath: Path to JSON file
        
    Returns:
        Loaded data or None if error
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        logger.info(f"Loaded JSON from {filepath}")
        return data
    except Exception as e:
        logger.error(f"Error loading JSON: {str(e)}")
        return None


def get_timestamp() -> str:
    """
    Get current timestamp as string
    
    Returns:
        Timestamp string in format YYYYMMDD_HHMMSS
    """
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def format_filename(base_name: str, extension: str = "", add_timestamp: bool = True) -> str:
    """
    Format a filename with optional timestamp
    
    Args:
        base_name: Base name of the file
        extension: File extension (with or without dot)
        add_timestamp: Whether to add timestamp
        
    Returns:
        Formatted filename
    """
    if extension and not extension.startswith('.'):
        extension = f'.{extension}'
    
    if add_timestamp:
        timestamp = get_timestamp()
        return f"{base_name}_{timestamp}{extension}"
    else:
        return f"{base_name}{extension}"


def ensure_directory(directory: str) -> bool:
    """
    Ensure a directory exists, create if it doesn't
    
    Args:
        directory: Path to directory
        
    Returns:
        True if directory exists or was created
    """
    try:
        os.makedirs(directory, exist_ok=True)
        return True
    except Exception as e:
        logger.error(f"Error creating directory: {str(e)}")
        return False


def clean_text(text: str) -> str:
    """
    Clean text by removing extra whitespace and special characters
    
    Args:
        text: Input text
        
    Returns:
        Cleaned text
    """
    import re
    
    # Remove multiple spaces
    text = re.sub(r'\s+', ' ', text)
    
    # Remove leading/trailing whitespace
    text = text.strip()
    
    return text


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate text to maximum length
    
    Args:
        text: Input text
        max_length: Maximum length
        suffix: Suffix to add if truncated
        
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def count_words(text: str) -> int:
    """
    Count words in text
    
    Args:
        text: Input text
        
    Returns:
        Word count
    """
    return len(text.split())


def highlight_phrase(text: str, phrase: str, 
                    start_tag: str = "**", end_tag: str = "**") -> str:
    """
    Highlight a phrase in text
    
    Args:
        text: Input text
        phrase: Phrase to highlight
        start_tag: Tag to add before phrase
        end_tag: Tag to add after phrase
        
    Returns:
        Text with highlighted phrase
    """
    return text.replace(phrase, f"{start_tag}{phrase}{end_tag}")


def calculate_similarity(text1: str, text2: str) -> float:
    """
    Calculate simple similarity between two texts
    
    Args:
        text1: First text
        text2: Second text
        
    Returns:
        Similarity score (0-1)
    """
    # Simple word overlap similarity
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())
    
    if not words1 or not words2:
        return 0.0
    
    intersection = words1.intersection(words2)
    union = words1.union(words2)
    
    return len(intersection) / len(union)


def extract_sentences(text: str) -> List[str]:
    """
    Extract sentences from text
    
    Args:
        text: Input text
        
    Returns:
        List of sentences
    """
    import re
    sentences = re.split(r'(?<=[.!?])\s+', text)
    return [s.strip() for s in sentences if s.strip()]


def format_result_summary(results: List[Dict]) -> Dict:
    """
    Create a summary of detection results
    
    Args:
        results: List of detection results
        
    Returns:
        Summary dictionary
    """
    total = len(results)
    vague = sum(1 for r in results if r.get('is_vague', False))
    
    # Calculate average vagueness score
    vague_results = [r for r in results if r.get('is_vague', False)]
    avg_score = (sum(r.get('vagueness_score', 0) for r in vague_results) / len(vague_results)) if vague_results else 0
    
    # Count by severity
    severity_counts = {
        'high': sum(1 for r in vague_results if r.get('gemini_analysis', {}).get('severity') == 'high'),
        'medium': sum(1 for r in vague_results if r.get('gemini_analysis', {}).get('severity') == 'medium'),
        'low': sum(1 for r in vague_results if r.get('gemini_analysis', {}).get('severity') == 'low')
    }
    
    return {
        'total_chunks': total,
        'vague_chunks': vague,
        'clear_chunks': total - vague,
        'vagueness_rate': (vague / total * 100) if total > 0 else 0,
        'average_vagueness_score': avg_score,
        'severity_distribution': severity_counts
    }


def merge_detection_results(results1: List[Dict], results2: List[Dict]) -> List[Dict]:
    """
    Merge two sets of detection results
    
    Args:
        results1: First set of results
        results2: Second set of results
        
    Returns:
        Merged results
    """
    # Create a dictionary keyed by chunk_id
    merged = {}
    
    for result in results1:
        chunk_id = result.get('chunk_id')
        if chunk_id is not None:
            merged[chunk_id] = result
    
    for result in results2:
        chunk_id = result.get('chunk_id')
        if chunk_id is not None:
            if chunk_id in merged:
                # Merge the results
                merged[chunk_id].update(result)
            else:
                merged[chunk_id] = result
    
    return list(merged.values())


def export_to_markdown(results: List[Dict], filepath: str) -> bool:
    """
    Export results to markdown format
    
    Args:
        results: Detection results
        filepath: Path to save markdown file
        
    Returns:
        True if successful
    """
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("# Vagueness Detection Results\n\n")
            
            # Summary
            summary = format_result_summary(results)
            f.write("## Summary\n\n")
            f.write(f"- Total Chunks: {summary['total_chunks']}\n")
            f.write(f"- Vague Chunks: {summary['vague_chunks']}\n")
            f.write(f"- Vagueness Rate: {summary['vagueness_rate']:.1f}%\n")
            f.write(f"- Average Score: {summary['average_vagueness_score']:.2f}\n\n")
            
            # Results
            f.write("## Detected Vague Phrases\n\n")
            
            vague_results = [r for r in results if r.get('is_vague')]
            
            for i, result in enumerate(vague_results, 1):
                f.write(f"### {i}. Chunk {result.get('chunk_id')}\n\n")
                f.write(f"**Text:** {result.get('text')}\n\n")
                f.write(f"**Score:** {result.get('vagueness_score', 0):.2f}\n\n")
                
                analysis = result.get('gemini_analysis', {})
                f.write(f"**Vague Phrases:** {', '.join(analysis.get('vague_phrases', []))}\n\n")
                f.write(f"**Explanation:** {analysis.get('explanation', '')}\n\n")
                f.write("---\n\n")
        
        logger.info(f"Exported results to markdown: {filepath}")
        return True
        
    except Exception as e:
        logger.error(f"Error exporting to markdown: {str(e)}")
        return False


if __name__ == "__main__":
    # Test utilities
    print("Testing utility functions...")
    
    # Test timestamp
    print(f"Timestamp: {get_timestamp()}")
    
    # Test filename formatting
    print(f"Filename: {format_filename('report', 'pdf')}")
    
    # Test text utilities
    text = "The contractor shall use quality materials where possible."
    print(f"Word count: {count_words(text)}")
    print(f"Truncated: {truncate_text(text, 30)}")
