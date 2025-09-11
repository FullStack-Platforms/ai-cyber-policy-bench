"""
Reranking module using cross-encoder models for improved relevance scoring.
Provides second-stage ranking to optimize retrieval results quality.
"""

import torch
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from sentence_transformers import CrossEncoder
import numpy as np
from pathlib import Path
import json

try:
    from .hybrid_search import SearchResult
    from .utils import get_config, get_config_value
except ImportError:
    from src.hybrid_search import SearchResult
    from src.utils import get_config, get_config_value


@dataclass
class RankedResult:
    """Search result with reranking score."""
    search_result: SearchResult
    rerank_score: float
    confidence: float
    rank_change: int  # How much the rank changed from original position


class CrossEncoderReranker:
    """Cross-encoder based reranking for improving retrieval quality."""
    
    def __init__(self, model_name: str = None, device: str = None):
        """
        Initialize cross-encoder reranker.
        
        Args:
            model_name: HuggingFace model for cross-encoding (default: ms-marco-MiniLM-L-6-v2)
            device: Device to run model on (cuda/cpu, auto-detected if None)
        """
        self.config = get_config()
        
        # Model configuration
        if model_name is None:
            model_name = get_config_value("Reranking", "model_name", "cross-encoder/ms-marco-MiniLM-L-6-v2")
        
        self.model_name = model_name
        
        # Device selection
        if device is None:
            if torch.cuda.is_available():
                device = "cuda"
            elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
                device = "mps"
            else:
                device = "cpu"
        
        self.device = device
        print(f"Initializing reranker with model: {model_name} on device: {device}")
        
        # Load model
        try:
            self.model = CrossEncoder(model_name, device=device)
            print("✓ Cross-encoder model loaded successfully")
        except Exception as e:
            print(f"Warning: Failed to load cross-encoder model {model_name}: {e}")
            self.model = None
        
        # Reranking parameters
        self.batch_size = get_config_value("Reranking", "batch_size", 32, int)
        self.rerank_threshold = get_config_value("Reranking", "threshold", 0.3, float)
        self.max_length = get_config_value("Reranking", "max_length", 512, int)
        self.top_k_rerank = get_config_value("Reranking", "top_k", 50, int)
    
    def truncate_text(self, text: str, max_length: int = None) -> str:
        """Truncate text to fit model's input length constraints."""
        if max_length is None:
            max_length = self.max_length
        
        # Simple character-based truncation (could be improved with tokenizer)
        if len(text) <= max_length:
            return text
        
        # Try to cut at sentence boundary
        truncated = text[:max_length]
        last_sentence = truncated.rfind('.')
        if last_sentence > max_length * 0.7:  # If we can find a sentence end in the last 30%
            return truncated[:last_sentence + 1]
        
        # Otherwise just cut and add ellipsis
        return truncated[:max_length-3] + "..."
    
    def create_query_passage_pairs(self, query: str, search_results: List[SearchResult]) -> List[Tuple[str, str]]:
        """Create query-passage pairs for cross-encoder input."""
        pairs = []
        
        for result in search_results:
            # Enhance passage with metadata for better context
            passage = result.text
            
            # Add framework context
            if result.framework:
                passage = f"[{result.framework}] {passage}"
            
            # Add section context if available
            metadata = result.metadata
            if isinstance(metadata, dict):
                section_info = []
                if metadata.get("section_title"):
                    section_info.append(f"Section: {metadata['section_title']}")
                if metadata.get("subsection_title"):
                    section_info.append(f"Subsection: {metadata['subsection_title']}")
                
                if section_info:
                    context = " | ".join(section_info)
                    passage = f"{context}\n{passage}"
            
            # Truncate to model limits
            passage = self.truncate_text(passage)
            query_truncated = self.truncate_text(query, 200)  # Shorter limit for query
            
            pairs.append((query_truncated, passage))
        
        return pairs
    
    def predict_scores(self, query_passage_pairs: List[Tuple[str, str]]) -> np.ndarray:
        """Predict relevance scores for query-passage pairs."""
        if not self.model:
            # Fallback: return neutral scores
            return np.array([0.5] * len(query_passage_pairs))
        
        try:
            # Batch prediction for efficiency
            scores = self.model.predict(query_passage_pairs, batch_size=self.batch_size)
            
            # Convert to numpy array and handle different score ranges
            scores = np.array(scores)
            
            # Normalize scores to [0, 1] range if needed
            if scores.min() < 0 or scores.max() > 1:
                scores = (scores - scores.min()) / (scores.max() - scores.min() + 1e-8)
            
            return scores
            
        except Exception as e:
            print(f"Error during cross-encoder prediction: {e}")
            # Fallback to neutral scores
            return np.array([0.5] * len(query_passage_pairs))
    
    def calculate_confidence(self, scores: np.ndarray) -> np.ndarray:
        """Calculate confidence scores based on prediction certainty."""
        # Distance from neutral (0.5) indicates confidence
        confidences = np.abs(scores - 0.5) * 2  # Scale to [0, 1]
        return confidences
    
    def rerank_results(self, query: str, search_results: List[SearchResult], top_k: int = None) -> List[RankedResult]:
        """
        Rerank search results using cross-encoder model.
        
        Args:
            query: Original search query
            search_results: Initial search results to rerank
            top_k: Number of top results to return (default: all)
        
        Returns:
            List of reranked results with scores
        """
        if not search_results:
            return []
        
        # Limit reranking to top results for efficiency
        results_to_rerank = search_results[:self.top_k_rerank]
        
        print(f"Reranking {len(results_to_rerank)} results...")
        
        # Create query-passage pairs
        query_passage_pairs = self.create_query_passage_pairs(query, results_to_rerank)
        
        # Get relevance scores
        rerank_scores = self.predict_scores(query_passage_pairs)
        confidences = self.calculate_confidence(rerank_scores)
        
        # Create ranked results
        ranked_results = []
        for i, (result, score, confidence) in enumerate(zip(results_to_rerank, rerank_scores, confidences)):
            # Update the search result with rerank score
            result.rerank_score = float(score)
            
            ranked_result = RankedResult(
                search_result=result,
                rerank_score=float(score),
                confidence=float(confidence),
                rank_change=0  # Will be calculated after sorting
            )
            ranked_results.append(ranked_result)
        
        # Sort by rerank score
        original_ranks = {id(result): i for i, result in enumerate(ranked_results)}
        ranked_results.sort(key=lambda x: x.rerank_score, reverse=True)
        
        # Calculate rank changes
        for new_rank, ranked_result in enumerate(ranked_results):
            original_rank = original_ranks[id(ranked_result)]
            ranked_result.rank_change = original_rank - new_rank
        
        # Apply threshold filtering
        filtered_results = [
            r for r in ranked_results 
            if r.rerank_score >= self.rerank_threshold
        ]
        
        # If filtering removes too many results, keep top results anyway
        if len(filtered_results) < len(ranked_results) * 0.3:
            filtered_results = ranked_results[:max(5, len(ranked_results) // 2)]
        
        # Return top-k if specified
        if top_k:
            filtered_results = filtered_results[:top_k]
        
        print(f"Reranking complete. Filtered to {len(filtered_results)} results (threshold: {self.rerank_threshold})")
        
        return filtered_results
    
    def get_reranking_statistics(self, ranked_results: List[RankedResult]) -> Dict[str, Any]:
        """Generate statistics about the reranking process."""
        if not ranked_results:
            return {}
        
        scores = [r.rerank_score for r in ranked_results]
        confidences = [r.confidence for r in ranked_results]
        rank_changes = [r.rank_change for r in ranked_results]
        
        stats = {
            "total_results": len(ranked_results),
            "score_stats": {
                "mean": float(np.mean(scores)),
                "std": float(np.std(scores)),
                "min": float(np.min(scores)),
                "max": float(np.max(scores)),
                "median": float(np.median(scores))
            },
            "confidence_stats": {
                "mean": float(np.mean(confidences)),
                "high_confidence_count": len([c for c in confidences if c > 0.7]),
                "low_confidence_count": len([c for c in confidences if c < 0.3])
            },
            "rank_change_stats": {
                "mean_change": float(np.mean(np.abs(rank_changes))),
                "promoted_count": len([c for c in rank_changes if c > 0]),
                "demoted_count": len([c for c in rank_changes if c < 0]),
                "unchanged_count": len([c for c in rank_changes if c == 0])
            }
        }
        
        return stats


class EnsembleReranker:
    """Ensemble reranker combining multiple ranking signals."""
    
    def __init__(self, rerankers: List[CrossEncoderReranker] = None):
        """Initialize ensemble reranker with multiple models."""
        self.rerankers = rerankers or []
        self.config = get_config()
        
        # Ensemble weights
        self.weights = get_config_value("Reranking", "ensemble_weights", [1.0], list)
        if len(self.weights) < len(self.rerankers):
            self.weights.extend([1.0] * (len(self.rerankers) - len(self.weights)))
    
    def add_reranker(self, reranker: CrossEncoderReranker, weight: float = 1.0):
        """Add a reranker to the ensemble."""
        self.rerankers.append(reranker)
        self.weights.append(weight)
    
    def ensemble_rerank(self, query: str, search_results: List[SearchResult], top_k: int = None) -> List[RankedResult]:
        """Rerank using ensemble of rerankers."""
        if not self.rerankers:
            print("Warning: No rerankers in ensemble")
            return []
        
        print(f"Ensemble reranking with {len(self.rerankers)} models...")
        
        # Get predictions from all rerankers
        all_scores = []
        for i, reranker in enumerate(self.rerankers):
            ranked_results = reranker.rerank_results(query, search_results, top_k=None)
            scores = [r.rerank_score for r in ranked_results]
            all_scores.append(scores)
        
        # Combine scores using weighted average
        if all_scores:
            ensemble_scores = np.zeros(len(search_results))
            total_weight = sum(self.weights[:len(all_scores)])
            
            for scores, weight in zip(all_scores, self.weights):
                if len(scores) == len(search_results):
                    ensemble_scores += np.array(scores) * weight / total_weight
        
        # Create ensemble results
        ranked_results = []
        for i, (result, score) in enumerate(zip(search_results, ensemble_scores)):
            result.rerank_score = float(score)
            ranked_result = RankedResult(
                search_result=result,
                rerank_score=float(score),
                confidence=min(1.0, float(score)),  # Simple confidence estimate
                rank_change=0
            )
            ranked_results.append(ranked_result)
        
        # Sort and calculate rank changes
        original_ranks = {id(result): i for i, result in enumerate(ranked_results)}
        ranked_results.sort(key=lambda x: x.rerank_score, reverse=True)
        
        for new_rank, ranked_result in enumerate(ranked_results):
            original_rank = original_ranks[id(ranked_result)]
            ranked_result.rank_change = original_rank - new_rank
        
        return ranked_results[:top_k] if top_k else ranked_results


def create_default_reranker() -> CrossEncoderReranker:
    """Create a default reranker with standard settings."""
    return CrossEncoderReranker()


if __name__ == "__main__":
    # Test reranker functionality
    print("Testing cross-encoder reranker...")
    
    try:
        reranker = CrossEncoderReranker()
        
        # Create dummy search results for testing
        dummy_results = [
            SearchResult(
                chunk_id="test1", 
                text="Access control policies must be implemented for all systems to ensure security compliance.",
                metadata={"framework_name": "NIST", "section_title": "Access Control"},
                framework="NIST",
                semantic_score=0.8
            ),
            SearchResult(
                chunk_id="test2",
                text="Regular security audits are required to maintain SOC 2 compliance standards.",
                metadata={"framework_name": "SOC2"},
                framework="SOC2", 
                semantic_score=0.6
            ),
            SearchResult(
                chunk_id="test3",
                text="Data encryption should follow industry best practices and standards.",
                metadata={"framework_name": "PCI"},
                framework="PCI",
                semantic_score=0.7
            )
        ]
        
        # Test reranking
        query = "What access control policies are required for security compliance?"
        ranked_results = reranker.rerank_results(query, dummy_results)
        
        print(f"\nReranking results for query: '{query}'")
        print(f"Results: {len(ranked_results)}")
        
        for i, result in enumerate(ranked_results):
            print(f"{i+1}. Score: {result.rerank_score:.3f}, Confidence: {result.confidence:.3f}, Change: {result.rank_change:+d}")
            print(f"   Framework: {result.search_result.framework}")
            print(f"   Text: {result.search_result.text[:100]}...")
        
        # Test statistics
        stats = reranker.get_reranking_statistics(ranked_results)
        print(f"\nReranking statistics:")
        print(f"Mean score: {stats['score_stats']['mean']:.3f}")
        print(f"High confidence results: {stats['confidence_stats']['high_confidence_count']}")
        print(f"Results promoted: {stats['rank_change_stats']['promoted_count']}")
        
        print("✓ Reranker test completed successfully")
        
    except Exception as e:
        print(f"Reranker test failed: {e}")
        # This is expected if the model isn't available