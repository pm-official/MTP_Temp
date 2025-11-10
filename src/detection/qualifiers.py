"""
Qualifiers Module
Defines the five categories of vagueness with patterns and examples
"""

from typing import Dict, List, Set
import re


class VaguenessQualifiers:
    """Define and manage vagueness qualifiers"""
    
    def __init__(self):
        self.qualifiers = self._initialize_qualifiers()
    
    def _initialize_qualifiers(self) -> Dict:
        """Initialize the five vagueness qualifiers"""
        
        qualifiers = {
            "abstractness_subjective": {
                "name": "Abstractness & Subjective Language",
                "description": "Subjective adjectives/adverbs needing personal interpretation",
                "keywords": [
                    "quality", "user friendly", "reasonable", "appropriate",
                    "adequate", "suitable", "proper", "efficient", "effective",
                    "good", "bad", "excellent", "poor", "satisfactory",
                    "acceptable", "sufficient", "necessary", "important",
                    "significant", "minor", "major", "substantial", "considerable",
                    "appropriate", "proper", "correct", "right", "wrong"
                ],
                "patterns": [
                    r'\b(quality|user[\s-]friendly|reasonable|appropriate)\b',
                    r'\b(adequate|suitable|proper|efficient|effective)\b',
                    r'\b(good|bad|excellent|poor|satisfactory)\b',
                    r'\b(acceptable|sufficient|necessary|important)\b',
                    r'\b(significant|minor|major|substantial|considerable)\b'
                ],
                "examples": [
                    "quality food",
                    "user friendly interface",
                    "reasonable price",
                    "appropriate measures"
                ]
            },
            
            "ambiguous_modifiers": {
                "name": "Ambiguous Modifiers & Comparative Phrases",
                "description": "Fuzzy, scalable concepts without objective bounds",
                "keywords": [
                    "larger", "smaller", "faster", "slower", "better", "worse",
                    "more", "less", "higher", "lower", "greater", "lesser",
                    "improved", "enhanced", "optimized", "minimized", "maximized",
                    "increased", "decreased", "reduced", "expanded",
                    "approximately", "about", "around", "roughly", "nearly",
                    "almost", "close to", "up to", "as much as"
                ],
                "patterns": [
                    r'\b(larger|smaller|faster|slower|better|worse)\b',
                    r'\b(more|less|higher|lower|greater|lesser)\b',
                    r'\b(improved|enhanced|optimized)\b',
                    r'\b(approximately|about|around|roughly|nearly)\b',
                    r'\b(almost|close\s+to|up\s+to)\b'
                ],
                "examples": [
                    "larger than previous",
                    "faster performance",
                    "better quality",
                    "approximately 100 units"
                ]
            },
            
            "referent_ambiguity": {
                "name": "Referent Ambiguity & Complex Noun Phrases",
                "description": "Structural issues that obscure the actor or referent",
                "keywords": [
                    "it", "they", "them", "this", "that", "these", "those",
                    "such", "said", "aforementioned", "following", "preceding",
                    "implementation", "execution", "completion", "establishment",
                    "development", "creation", "formation", "construction"
                ],
                "patterns": [
                    r'\b(it|they|them|this|that|these|those)\s+\w+',
                    r'\b(such|said|aforementioned)\b',
                    r'\b(implementation|execution|completion|establishment)\s+of\b',
                    r'\b(development|creation|formation|construction)\s+of\b'
                ],
                "examples": [
                    "it should be done",
                    "they will complete",
                    "implementation of plan",
                    "execution of work"
                ]
            },
            
            "open_ended_terms": {
                "name": "Open-Ended / Non-Verifiable Terms & Loopholes",
                "description": "Conditional phrasing that creates escape clauses",
                "keywords": [
                    "if feasible", "where possible", "if necessary", "as required",
                    "when needed", "if applicable", "subject to", "depending on",
                    "may", "might", "could", "should", "would",
                    "not limited to", "including but not limited to",
                    "among others", "etc", "and so on", "and the like",
                    "as appropriate", "as deemed necessary", "at discretion"
                ],
                "patterns": [
                    r'\b(if|where)\s+(feasible|possible|necessary|required|applicable)\b',
                    r'\b(when|as)\s+(needed|required|appropriate|deemed)\b',
                    r'\b(may|might|could|should|would)\b',
                    r'\b(not\s+limited\s+to|including\s+but\s+not\s+limited\s+to)\b',
                    r'\b(etc|and\s+so\s+on|among\s+others|and\s+the\s+like)\b',
                    r'\b(subject\s+to|depending\s+on)\b'
                ],
                "examples": [
                    "if feasible",
                    "where possible",
                    "not limited to",
                    "may be required"
                ]
            },
            
            "negative_passive": {
                "name": "Negative & Passive Structures",
                "description": "Passive voice or negative commands reducing clarity",
                "keywords": [
                    "will be", "shall be", "is to be", "are to be",
                    "should be", "must be", "can be", "may be",
                    "should not", "must not", "cannot", "may not",
                    "will not", "shall not", "is not to", "are not to"
                ],
                "patterns": [
                    r'\b(will|shall|should|must|can|may)\s+be\s+\w+',
                    r'\b(is|are|was|were)\s+to\s+be\s+\w+',
                    r'\b(should|must|cannot|may|will|shall)\s+not\b',
                    r'\b(is|are)\s+not\s+to\b'
                ],
                "examples": [
                    "Payment will be issued",
                    "Work shall be completed",
                    "should not work with",
                    "must not exceed"
                ]
            }
        }
        
        return qualifiers
    
    def get_qualifier_info(self, qualifier_key: str) -> Dict:
        """Get information about a specific qualifier"""
        return self.qualifiers.get(qualifier_key, {})
    
    def get_all_qualifiers(self) -> Dict:
        """Get all qualifiers"""
        return self.qualifiers
    
    def check_text_for_qualifier(self, text: str, qualifier_key: str) -> List[Dict]:
        """
        Check if text contains patterns matching a specific qualifier
        
        Args:
            text: Text to check
            qualifier_key: Key of the qualifier to check
            
        Returns:
            List of matches with details
        """
        qualifier = self.qualifiers.get(qualifier_key)
        if not qualifier:
            return []
        
        matches = []
        text_lower = text.lower()
        
        # Check keywords
        for keyword in qualifier['keywords']:
            if keyword.lower() in text_lower:
                matches.append({
                    'type': 'keyword',
                    'match': keyword,
                    'qualifier': qualifier_key,
                    'qualifier_name': qualifier['name']
                })
        
        # Check patterns
        for pattern in qualifier['patterns']:
            regex_matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in regex_matches:
                matches.append({
                    'type': 'pattern',
                    'match': match.group(),
                    'position': match.span(),
                    'qualifier': qualifier_key,
                    'qualifier_name': qualifier['name']
                })
        
        return matches
    
    def check_text_all_qualifiers(self, text: str) -> Dict[str, List]:
        """
        Check text against all qualifiers
        
        Args:
            text: Text to check
            
        Returns:
            Dictionary with qualifier keys as keys and matches as values
        """
        all_matches = {}
        
        for qualifier_key in self.qualifiers.keys():
            matches = self.check_text_for_qualifier(text, qualifier_key)
            if matches:
                all_matches[qualifier_key] = matches
        
        return all_matches


# Predefined acronyms and their common meanings
COMMON_ACRONYMS = {
    "IS": "Indian Standard",
    "CPWD": "Central Public Works Department",
    "PWD": "Public Works Department",
    "RCC": "Reinforced Cement Concrete",
    "PCC": "Plain Cement Concrete",
    "DPC": "Damp Proof Course",
    "BOQ": "Bill of Quantities",
    "SOR": "Schedule of Rates",
    "M&E": "Mechanical and Electrical",
    "HVAC": "Heating, Ventilation, and Air Conditioning",
    "PSC": "Prestressed Concrete",
    "TMT": "Thermo-Mechanically Treated",
    "OPC": "Ordinary Portland Cement",
    "PPC": "Portland Pozzolana Cement"
}


if __name__ == "__main__":
    # Test the qualifiers
    qualifiers = VaguenessQualifiers()
    
    test_sentences = [
        "The contractor shall use quality materials where possible.",
        "Payment will be issued upon completion.",
        "Work should be faster than previous projects.",
        "Implementation of the plan will begin if feasible."
    ]
    
    for sentence in test_sentences:
        print(f"\nAnalyzing: {sentence}")
        matches = qualifiers.check_text_all_qualifiers(sentence)
        for qualifier_key, match_list in matches.items():
            print(f"  {qualifier_key}: {len(match_list)} matches")
            for match in match_list[:2]:  # Show first 2 matches
                print(f"    - {match['match']}")
