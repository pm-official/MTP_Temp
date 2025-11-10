"""
Expert Validation Module
Compare model output with expert ratings for evaluation
"""

import pandas as pd
from typing import List, Dict
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ExpertValidator:
    """Validate model output against expert ratings"""
    
    def __init__(self):
        self.expert_ratings = []
        self.model_outputs = []
    
    def load_expert_ratings(self, csv_path: str) -> pd.DataFrame:
        """
        Load expert ratings from CSV
        
        Args:
            csv_path: Path to CSV file with expert ratings
            
        Expected CSV format:
            chunk_id, text, is_vague, clarity_score (1-5), comments
            
        Returns:
            DataFrame with expert ratings
        """
        try:
            df = pd.read_csv(csv_path)
            self.expert_ratings = df.to_dict('records')
            logger.info(f"Loaded {len(self.expert_ratings)} expert ratings")
            return df
        except Exception as e:
            logger.error(f"Error loading expert ratings: {str(e)}")
            return pd.DataFrame()
    
    def load_model_outputs(self, json_path: str) -> List[Dict]:
        """
        Load model outputs from JSON
        
        Args:
            json_path: Path to JSON file with model outputs
            
        Returns:
            List of model outputs
        """
        try:
            with open(json_path, 'r') as f:
                self.model_outputs = json.load(f)
            logger.info(f"Loaded {len(self.model_outputs)} model outputs")
            return self.model_outputs
        except Exception as e:
            logger.error(f"Error loading model outputs: {str(e)}")
            return []
    
    def calculate_metrics(self) -> Dict:
        """
        Calculate precision, recall, F1 for vagueness detection
        
        Returns:
            Dictionary with metrics
        """
        if not self.expert_ratings or not self.model_outputs:
            logger.error("Expert ratings or model outputs not loaded")
            return {}
        
        # Create lookup for model outputs
        model_dict = {m['chunk_id']: m for m in self.model_outputs}
        
        true_positives = 0
        false_positives = 0
        true_negatives = 0
        false_negatives = 0
        
        for expert in self.expert_ratings:
            chunk_id = expert.get('chunk_id')
            expert_vague = expert.get('is_vague', False)
            
            model_result = model_dict.get(chunk_id)
            if not model_result:
                continue
            
            model_vague = model_result.get('is_vague', False)
            
            if expert_vague and model_vague:
                true_positives += 1
            elif not expert_vague and model_vague:
                false_positives += 1
            elif not expert_vague and not model_vague:
                true_negatives += 1
            elif expert_vague and not model_vague:
                false_negatives += 1
        
        # Calculate metrics
        precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0
        recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        accuracy = (true_positives + true_negatives) / len(self.expert_ratings) if len(self.expert_ratings) > 0 else 0
        
        metrics = {
            'precision': precision,
            'recall': recall,
            'f1_score': f1,
            'accuracy': accuracy,
            'true_positives': true_positives,
            'false_positives': false_positives,
            'true_negatives': true_negatives,
            'false_negatives': false_negatives,
            'total_samples': len(self.expert_ratings)
        }
        
        logger.info(f"Metrics calculated: Precision={precision:.3f}, Recall={recall:.3f}, F1={f1:.3f}")
        return metrics
    
    def compare_suggestions(self) -> List[Dict]:
        """
        Compare model suggestions with expert feedback
        
        Returns:
            List of comparison results
        """
        comparisons = []
        
        model_dict = {m['chunk_id']: m for m in self.model_outputs}
        
        for expert in self.expert_ratings:
            chunk_id = expert.get('chunk_id')
            model_result = model_dict.get(chunk_id)
            
            if not model_result:
                continue
            
            comparison = {
                'chunk_id': chunk_id,
                'text': expert.get('text', ''),
                'expert_rating': expert.get('clarity_score', 0),
                'expert_comments': expert.get('comments', ''),
                'model_vagueness_score': model_result.get('vagueness_score', 0),
                'model_suggestions': model_result.get('suggestions', []),
                'agreement': expert.get('is_vague') == model_result.get('is_vague')
            }
            
            comparisons.append(comparison)
        
        return comparisons
    
    def generate_report(self, output_path: str = None) -> Dict:
        """
        Generate comprehensive evaluation report
        
        Args:
            output_path: Optional path to save report as JSON
            
        Returns:
            Dictionary with complete report
        """
        metrics = self.calculate_metrics()
        comparisons = self.compare_suggestions()
        
        report = {
            'metrics': metrics,
            'comparisons': comparisons,
            'summary': {
                'total_chunks_evaluated': len(self.expert_ratings),
                'vague_chunks_identified_by_model': sum(1 for m in self.model_outputs if m.get('is_vague')),
                'vague_chunks_identified_by_experts': sum(1 for e in self.expert_ratings if e.get('is_vague')),
                'agreement_rate': sum(1 for c in comparisons if c['agreement']) / len(comparisons) if comparisons else 0
            }
        }
        
        if output_path:
            with open(output_path, 'w') as f:
                json.dump(report, f, indent=2)
            logger.info(f"Report saved to {output_path}")
        
        return report
    
    def create_expert_rating_template(self, 
                                     chunks: List[Dict],
                                     output_path: str = "expert_ratings_template.csv"):
        """
        Create a CSV template for expert ratings
        
        Args:
            chunks: List of text chunks to be rated
            output_path: Path to save the template
        """
        data = []
        for chunk in chunks:
            data.append({
                'chunk_id': chunk.get('chunk_id', 0),
                'text': chunk.get('text', ''),
                'is_vague': '',  # To be filled by expert
                'clarity_score': '',  # 1-5 scale, to be filled by expert
                'comments': ''  # Expert comments
            })
        
        df = pd.DataFrame(data)
        df.to_csv(output_path, index=False)
        logger.info(f"Expert rating template saved to {output_path}")


if __name__ == "__main__":
    # Test the validator
    validator = ExpertValidator()
    
    # Create a sample template
    sample_chunks = [
        {'chunk_id': 0, 'text': 'The contractor shall use quality materials.'},
        {'chunk_id': 1, 'text': 'All concrete work must comply with IS 456:2000.'},
    ]
    
    validator.create_expert_rating_template(sample_chunks, "test_template.csv")
    print("Created expert rating template")
