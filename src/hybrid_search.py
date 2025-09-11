"""
Hybrid Search module implementing BM25 + semantic search with fusion.
Provides keyword-based search alongside vector similarity for improved retrieval.
"""

import math
import json
import pickle
import re
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple, Set
from dataclasses import dataclass
from collections import defaultdict, Counter
import sqlite3

try:
    from .utils import get_config, get_config_value
except ImportError:
    from src.utils import get_config, get_config_value


@dataclass
class SearchResult:
    """Unified search result with scoring from multiple methods."""
    chunk_id: str
    text: str
    metadata: Dict[str, Any]
    framework: str
    semantic_score: Optional[float] = None
    bm25_score: Optional[float] = None
    hybrid_score: Optional[float] = None
    rerank_score: Optional[float] = None
    retrieval_method: str = "unknown"


class BM25Index:
    """Optimized BM25 implementation for keyword-based retrieval."""
    
    def __init__(self, k1: float = 1.2, b: float = 0.75, epsilon: float = 0.25):
        """
        Initialize BM25 with standard parameters.
        
        Args:
            k1: Controls term frequency saturation point (typically 1.2-2.0)
            b: Controls length normalization (0 = no normalization, 1 = full)
            epsilon: Minimum IDF score to prevent negative weights
        """
        self.k1 = k1
        self.b = b
        self.epsilon = epsilon
        
        # Index structures
        self.documents: Dict[str, str] = {}  # doc_id -> text
        self.doc_metadata: Dict[str, Dict] = {}  # doc_id -> metadata
        self.term_frequencies: Dict[str, Dict[str, int]] = {}  # term -> {doc_id: freq}
        self.document_lengths: Dict[str, int] = {}  # doc_id -> length
        self.vocabulary: Set[str] = set()
        self.doc_count = 0
        self.avg_doc_length = 0
        
        # Stopwords for filtering
        self.stopwords = {
            'a', 'an', 'and', 'are', 'as', 'at', 'be', 'been', 'by', 'for',
            'from', 'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that',
            'the', 'to', 'was', 'will', 'with', 'the', 'this', 'but', 'they',
            'have', 'had', 'what', 'said', 'each', 'which', 'their', 'time',
            'would', 'about', 'if', 'up', 'out', 'many', 'then', 'them', 'these',
            'so', 'some', 'her', 'only', 'no', 'when', 'my', 'can', 'over',
            'think', 'also', 'back', 'after', 'use', 'two', 'how', 'our', 'work',
            'first', 'well', 'way', 'even', 'new', 'want', 'because', 'any',
            'these', 'give', 'day', 'most', 'us'
        }
        
        # Technical term preservation (don't remove these as stopwords)
        self.preserve_terms = {
            'control', 'security', 'policy', 'access', 'data', 'system',
            'audit', 'risk', 'compliance', 'framework', 'standard', 'requirement',
            'procedure', 'guidelines', 'assessment', 'monitoring', 'incident',
            'response', 'recovery', 'backup', 'encryption', 'authentication',
            'authorization', 'vulnerability', 'threat', 'breach', 'privacy'
        }
    
    def tokenize(self, text: str) -> List[str]:
        """Tokenize text with domain-specific preprocessing."""
        # Convert to lowercase
        text = text.lower()
        
        # Preserve important technical terms and identifiers
        text = re.sub(r'\b(\d+\.\d+(?:\.\d+)*)\b', r' \1 ', text)  # Section numbers
        text = re.sub(r'\b([A-Z]{2,})\b', lambda m: f' {m.group(1).lower()} ', text)  # Acronyms
        
        # Extract alphanumeric tokens
        tokens = re.findall(r'\b[a-zA-Z0-9][a-zA-Z0-9._-]*[a-zA-Z0-9]\b|\b[a-zA-Z0-9]\b', text)
        
        # Filter tokens
        filtered_tokens = []
        for token in tokens:
            # Keep technical terms even if they're in stopwords
            if token in self.preserve_terms:
                filtered_tokens.append(token)
            # Skip regular stopwords
            elif token not in self.stopwords and len(token) > 1:
                filtered_tokens.append(token)
            # Keep single character tokens if they're digits or important
            elif len(token) == 1 and (token.isdigit() or token in 'abc'):
                filtered_tokens.append(token)
        
        return filtered_tokens
    
    def add_document(self, doc_id: str, text: str, metadata: Dict[str, Any] = None):
        """Add a document to the BM25 index."""
        tokens = self.tokenize(text)
        
        self.documents[doc_id] = text
        self.doc_metadata[doc_id] = metadata or {}
        self.document_lengths[doc_id] = len(tokens)
        
        # Update term frequencies
        term_counts = Counter(tokens)
        for term, count in term_counts.items():
            if term not in self.term_frequencies:
                self.term_frequencies[term] = {}
            self.term_frequencies[term][doc_id] = count
            self.vocabulary.add(term)
        
        self.doc_count += 1
        self._update_avg_length()
    
    def _update_avg_length(self):
        """Update average document length."""
        if self.doc_count > 0:
            self.avg_doc_length = sum(self.document_lengths.values()) / self.doc_count
    
    def get_idf(self, term: str) -> float:
        """Calculate IDF score for a term."""
        if term not in self.term_frequencies:
            return 0.0
        
        doc_freq = len(self.term_frequencies[term])
        idf = math.log((self.doc_count - doc_freq + 0.5) / (doc_freq + 0.5))
        return max(self.epsilon, idf)
    
    def score_document(self, doc_id: str, query_terms: List[str]) -> float:
        """Calculate BM25 score for a document given query terms."""
        if doc_id not in self.documents:
            return 0.0
        
        score = 0.0
        doc_length = self.document_lengths[doc_id]
        
        for term in query_terms:
            if term not in self.term_frequencies or doc_id not in self.term_frequencies[term]:
                continue
            
            # Term frequency in document
            tf = self.term_frequencies[term][doc_id]
            
            # IDF score
            idf = self.get_idf(term)
            
            # BM25 calculation
            numerator = tf * (self.k1 + 1)
            denominator = tf + self.k1 * (1 - self.b + self.b * (doc_length / self.avg_doc_length))
            
            score += idf * (numerator / denominator)
        
        return score
    
    def search(self, query: str, k: int = 10) -> List[Tuple[str, float]]:
        """Search the index and return top-k results with BM25 scores."""
        query_terms = self.tokenize(query)
        if not query_terms:
            return []
        
        # Score all documents
        scores = []
        for doc_id in self.documents:
            score = self.score_document(doc_id, query_terms)
            if score > 0:
                scores.append((doc_id, score))
        
        # Sort by score descending and return top-k
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:k]
    
    def save_index(self, filepath: Path):
        """Save the BM25 index to disk."""
        index_data = {
            'documents': self.documents,
            'doc_metadata': self.doc_metadata,
            'term_frequencies': self.term_frequencies,
            'document_lengths': self.document_lengths,
            'vocabulary': list(self.vocabulary),
            'doc_count': self.doc_count,
            'avg_doc_length': self.avg_doc_length,
            'parameters': {'k1': self.k1, 'b': self.b, 'epsilon': self.epsilon}
        }
        
        with open(filepath, 'wb') as f:
            pickle.dump(index_data, f)
    
    @classmethod
    def load_index(cls, filepath: Path) -> 'BM25Index':
        """Load a BM25 index from disk."""
        with open(filepath, 'rb') as f:
            index_data = pickle.load(f)
        
        # Create new instance with saved parameters
        params = index_data['parameters']
        instance = cls(k1=params['k1'], b=params['b'], epsilon=params['epsilon'])
        
        # Restore index data
        instance.documents = index_data['documents']
        instance.doc_metadata = index_data['doc_metadata']
        instance.term_frequencies = index_data['term_frequencies']
        instance.document_lengths = index_data['document_lengths']
        instance.vocabulary = set(index_data['vocabulary'])
        instance.doc_count = index_data['doc_count']
        instance.avg_doc_length = index_data['avg_doc_length']
        
        return instance


class HybridRetriever:
    """Combines semantic search (embeddings) with keyword search (BM25) using fusion."""
    
    def __init__(self, vector_db, bm25_index: Optional[BM25Index] = None):
        """
        Initialize hybrid retriever.
        
        Args:
            vector_db: Existing vector database for semantic search
            bm25_index: Optional BM25 index for keyword search
        """
        self.vector_db = vector_db
        self.bm25_index = bm25_index
        self.config = get_config()
        
        # Fusion parameters
        self.semantic_weight = get_config_value("HybridSearch", "semantic_weight", 0.6, float)
        self.bm25_weight = get_config_value("HybridSearch", "bm25_weight", 0.4, float)
        self.fusion_method = get_config_value("HybridSearch", "fusion_method", "rrf")  # rrf, weighted, or max
        self.rrf_k = get_config_value("HybridSearch", "rrf_k", 60, int)
    
    def build_bm25_index(self, chunks_data: Dict[str, Any]) -> BM25Index:
        """Build BM25 index from chunks data."""
        print("Building BM25 index...")
        
        bm25 = BM25Index(
            k1=get_config_value("HybridSearch", "bm25_k1", 1.2, float),
            b=get_config_value("HybridSearch", "bm25_b", 0.75, float),
            epsilon=get_config_value("HybridSearch", "bm25_epsilon", 0.25, float)
        )
        
        total_chunks = 0
        for framework_name, framework_data in chunks_data.items():
            for chunk in framework_data["chunks"]:
                # Add enhanced text for BM25 indexing
                enhanced_text = chunk["text"]
                
                # Add keywords if available
                if "keywords" in chunk and chunk["keywords"]:
                    keywords_text = " ".join(chunk["keywords"])
                    enhanced_text += f" KEYWORDS: {keywords_text}"
                
                # Add section titles if available
                if chunk.get("section_title"):
                    enhanced_text += f" SECTION: {chunk['section_title']}"
                if chunk.get("subsection_title"):
                    enhanced_text += f" SUBSECTION: {chunk['subsection_title']}"
                
                bm25.add_document(
                    doc_id=chunk["chunk_id"],
                    text=enhanced_text,
                    metadata={
                        "framework_name": chunk["framework_name"],
                        "document": chunk["document"],
                        "original_text": chunk["text"],
                        **{k: v for k, v in chunk.items() if k not in ["text", "chunk_id"]}
                    }
                )
                total_chunks += 1
        
        print(f"BM25 index built with {total_chunks} documents, vocabulary size: {len(bm25.vocabulary)}")
        self.bm25_index = bm25
        return bm25
    
    def enhance_query(self, query: str) -> Dict[str, Any]:
        """Enhance query with domain-specific processing."""
        enhanced = {
            "original": query,
            "processed": query.lower(),
            "keywords": [],
            "frameworks": [],
            "concepts": []
        }
        
        # Extract technical keywords
        technical_terms = re.findall(r'\b(?:control|requirement|standard|policy|procedure|security|compliance|audit|risk|assessment|framework|guideline|directive|access|authentication|authorization|encryption|backup|recovery|incident|response|vulnerability|threat|monitoring|logging)\b', query, re.IGNORECASE)
        enhanced["keywords"].extend([term.lower() for term in technical_terms])
        
        # Extract framework mentions
        framework_patterns = {
            "nist": r'\b(?:nist|national institute)\b',
            "soc": r'\bsoc\s*2?\b',
            "pci": r'\b(?:pci|payment card)\b',
            "hipaa": r'\bhipaa\b',
            "gdpr": r'\bgdpr\b',
            "iso": r'\biso\s*\d+\b',
            "cmmc": r'\bcmmc\b',
            "fedramp": r'\bfedramp\b'
        }
        
        for framework, pattern in framework_patterns.items():
            if re.search(pattern, query, re.IGNORECASE):
                enhanced["frameworks"].append(framework)
        
        # Extract section numbers and identifiers
        sections = re.findall(r'\b\d+\.\d+(?:\.\d+)*\b', query)
        enhanced["keywords"].extend(sections)
        
        return enhanced
    
    def reciprocal_rank_fusion(self, semantic_results: List[Tuple], bm25_results: List[Tuple], k: int = None) -> List[Tuple[str, float]]:
        """Combine results using Reciprocal Rank Fusion (RRF)."""
        if k is None:
            k = self.rrf_k
        
        # Create rank mappings
        semantic_ranks = {doc_id: 1/(rank + k) for rank, (doc_id, _) in enumerate(semantic_results)}
        bm25_ranks = {doc_id: 1/(rank + k) for rank, (doc_id, _) in enumerate(bm25_results)}
        
        # Get all unique document IDs
        all_doc_ids = set(semantic_ranks.keys()) | set(bm25_ranks.keys())
        
        # Calculate combined scores
        fused_scores = []
        for doc_id in all_doc_ids:
            rrf_score = semantic_ranks.get(doc_id, 0) + bm25_ranks.get(doc_id, 0)
            fused_scores.append((doc_id, rrf_score))
        
        # Sort by combined score
        fused_scores.sort(key=lambda x: x[1], reverse=True)
        return fused_scores
    
    def weighted_fusion(self, semantic_results: List[Tuple], bm25_results: List[Tuple]) -> List[Tuple[str, float]]:
        """Combine results using weighted score fusion."""
        # Normalize scores to [0, 1]
        if semantic_results:
            max_semantic = max(score for _, score in semantic_results) if semantic_results else 1.0
            semantic_scores = {doc_id: (1 - score/max_semantic) for doc_id, score in semantic_results}  # Invert distance
        else:
            semantic_scores = {}
        
        if bm25_results:
            max_bm25 = max(score for _, score in bm25_results) if bm25_results else 1.0
            bm25_scores = {doc_id: score/max_bm25 for doc_id, score in bm25_results}
        else:
            bm25_scores = {}
        
        # Get all unique document IDs
        all_doc_ids = set(semantic_scores.keys()) | set(bm25_scores.keys())
        
        # Calculate weighted scores
        weighted_scores = []
        for doc_id in all_doc_ids:
            semantic_score = semantic_scores.get(doc_id, 0)
            bm25_score = bm25_scores.get(doc_id, 0)
            
            combined_score = (self.semantic_weight * semantic_score + 
                            self.bm25_weight * bm25_score)
            weighted_scores.append((doc_id, combined_score))
        
        # Sort by combined score
        weighted_scores.sort(key=lambda x: x[1], reverse=True)
        return weighted_scores
    
    def hybrid_search(self, query: str, n_results: int = 10, frameworks: Optional[List[str]] = None) -> List[SearchResult]:
        """Perform hybrid search combining semantic and keyword-based retrieval."""
        enhanced_query = self.enhance_query(query)
        results = []
        
        # Perform semantic search
        semantic_results = []
        if self.vector_db:
            try:
                # Use base_search if available (for EnhancedVectorDatabase) to avoid recursion
                if hasattr(self.vector_db, 'base_search'):
                    vector_results = self.vector_db.base_search(query, n_results=n_results*2, frameworks=frameworks)
                else:
                    vector_results = self.vector_db.search(query, n_results=n_results*2, frameworks=frameworks)
                for result in vector_results:
                    semantic_results.append((result.get("framework", "") + "_" + result["metadata"].get("chunk_id", ""), result.get("distance", 0)))
            except Exception as e:
                print(f"Semantic search failed: {e}")
        
        # Perform BM25 search
        bm25_results = []
        if self.bm25_index:
            try:
                bm25_results = self.bm25_index.search(query, k=n_results*2)
            except Exception as e:
                print(f"BM25 search failed: {e}")
        
        # Combine results using configured fusion method
        if self.fusion_method == "rrf":
            fused_results = self.reciprocal_rank_fusion(semantic_results, bm25_results)
        elif self.fusion_method == "weighted":
            fused_results = self.weighted_fusion(semantic_results, bm25_results)
        else:  # max fusion
            all_results = semantic_results + bm25_results
            fused_results = sorted(all_results, key=lambda x: x[1], reverse=True)
        
        # Convert to SearchResult objects
        for i, (doc_id, score) in enumerate(fused_results[:n_results]):
            # Get document data
            doc_text = ""
            metadata = {}
            framework = ""
            
            # Try to get from BM25 index first
            if self.bm25_index and doc_id in self.bm25_index.documents:
                doc_text = self.bm25_index.doc_metadata[doc_id].get("original_text", self.bm25_index.documents[doc_id])
                metadata = self.bm25_index.doc_metadata[doc_id]
                framework = metadata.get("framework_name", "")
            
            # Fallback to vector database
            elif self.vector_db:
                # This is a simplified approach - in practice you'd want better ID mapping
                try:
                    # Use base_search if available (for EnhancedVectorDatabase) to avoid recursion
                    if hasattr(self.vector_db, 'base_search'):
                        vector_results = self.vector_db.base_search(query, n_results=100)
                    else:
                        vector_results = self.vector_db.search(query, n_results=100)
                    for vr in vector_results:
                        if vr["metadata"].get("chunk_id") in doc_id:
                            doc_text = vr["text"]
                            metadata = vr["metadata"]
                            framework = vr.get("framework", "")
                            break
                except:
                    continue
            
            if doc_text:
                search_result = SearchResult(
                    chunk_id=doc_id,
                    text=doc_text,
                    metadata=metadata,
                    framework=framework,
                    hybrid_score=score,
                    retrieval_method="hybrid"
                )
                results.append(search_result)
        
        return results
    
    def save_index(self, index_dir: Path):
        """Save the BM25 index."""
        index_dir.mkdir(parents=True, exist_ok=True)
        if self.bm25_index:
            self.bm25_index.save_index(index_dir / "bm25_index.pkl")
    
    def load_index(self, index_dir: Path):
        """Load the BM25 index."""
        bm25_path = index_dir / "bm25_index.pkl"
        if bm25_path.exists():
            self.bm25_index = BM25Index.load_index(bm25_path)
            print(f"Loaded BM25 index with {self.bm25_index.doc_count} documents")
        else:
            print(f"No BM25 index found at {bm25_path}")


if __name__ == "__main__":
    # Test BM25 functionality
    print("Testing BM25 index...")
    
    bm25 = BM25Index()
    
    # Add test documents
    test_docs = [
        ("doc1", "Access control policies must be implemented for all systems", {"framework": "NIST"}),
        ("doc2", "Security controls require regular audit and assessment procedures", {"framework": "SOC2"}),
        ("doc3", "Data encryption standards should follow industry best practices", {"framework": "PCI"}),
    ]
    
    for doc_id, text, metadata in test_docs:
        bm25.add_document(doc_id, text, metadata)
    
    # Test search
    results = bm25.search("access control security", k=5)
    print("\nBM25 search results for 'access control security':")
    for doc_id, score in results:
        print(f"  {doc_id}: {score:.3f}")
    
    print(f"Vocabulary size: {len(bm25.vocabulary)}")
    print("✓ BM25 index test completed")