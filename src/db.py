import chromadb
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from sentence_transformers import SentenceTransformer

# Import torch for MPS cache management on macOS
try:
    import torch

    # Check if MPS is available and enable memory-efficient empty cache
    if torch.backends.mps.is_available():
        torch.mps.empty_cache()
except ImportError:
    torch = None

# Import RAG optimization modules when available
try:
    from .hybrid_search import HybridRetriever, SearchResult
    from .reranker import CrossEncoderReranker

    RAG_OPTIMIZATIONS_AVAILABLE = True
except ImportError:
    RAG_OPTIMIZATIONS_AVAILABLE = False

# Use centralized config loading
from .utils import get_config, get_config_value

config = get_config()


class VectorDatabase:
    """Vector database for storing and retrieving cybersecurity framework chunks with RAG optimizations."""

    def __init__(
        self,
        db_path: str = None,
        enable_hybrid_search: bool = None,
        enable_reranking: bool = None,
    ):
        """
        Initialize the vector database with multi-collection support and optional RAG optimizations.

        Args:
            db_path: Path to database storage
            enable_hybrid_search: Enable hybrid search (BM25 + semantic)
            enable_reranking: Enable cross-encoder reranking
        """
        if db_path is None:
            db_path = config.get("VectorDatabase", "db_path", fallback="./vector_db")
        self.db_path = Path(db_path)
        self.db_path.mkdir(exist_ok=True)

        # Initialize ChromaDB
        self.client = chromadb.PersistentClient(path=str(self.db_path))

        # Initialize embedding model
        embedding_model_name = config.get(
            "VectorDatabase", "embedding_model", fallback="all-mpnet-base-v2"
        )
        self.embedding_model = SentenceTransformer(embedding_model_name)

        # Validate embedding dimensions match config
        expected_dim = config.get(
            "VectorDatabase", "embedding_dimensions", fallback="768"
        )
        actual_dim = self.embedding_model.get_sentence_embedding_dimension()
        if str(actual_dim) != str(expected_dim):
            print(
                f"Warning: Embedding model dimension ({actual_dim}) doesn't match config ({expected_dim})"
            )
            print(f"Using model: {embedding_model_name}")

        print(
            f"Initialized embedding model: {embedding_model_name} ({actual_dim} dimensions)"
        )

        # Store collections by framework name
        self.collections = {}

        # Initialize RAG optimization features if available
        self.enable_hybrid_search = False
        self.enable_reranking = False
        self.hybrid_retriever = None
        self.reranker = None
        self.config_overrides = {}

        if RAG_OPTIMIZATIONS_AVAILABLE:
            # Feature flags from config or parameters
            if enable_hybrid_search is None:
                enable_hybrid_search = get_config_value(
                    "HybridSearch", "enable_hybrid_search", True, bool
                )
            if enable_reranking is None:
                enable_reranking = get_config_value(
                    "Reranking", "enable_reranking", True, bool
                )

            self.enable_hybrid_search = enable_hybrid_search
            self.enable_reranking = enable_reranking

            # Initialize hybrid retriever
            if self.enable_hybrid_search:
                try:
                    self.hybrid_retriever = HybridRetriever(vector_db=self)
                    print("✓ Hybrid search enabled")
                except Exception as e:
                    print(f"Warning: Failed to initialize hybrid search: {e}")
                    self.enable_hybrid_search = False

            # Initialize reranker
            if self.enable_reranking:
                try:
                    self.reranker = CrossEncoderReranker()
                    print("✓ Reranking enabled")
                except Exception as e:
                    print(f"Warning: Failed to initialize reranker: {e}")
                    self.enable_reranking = False

    def get_or_create_collection(self, framework_name: str) -> chromadb.Collection:
        """Get or create a collection for a specific framework."""
        # Framework names are already standardized, use them directly as collection names
        collection_name = framework_name

        if collection_name in self.collections:
            return self.collections[collection_name]

        try:
            collection = self.client.get_collection(collection_name)
        except Exception:
            # Create new collection with proper embedding function
            vector_space = config.get(
                "VectorDatabase", "vector_space", fallback="cosine"
            )
            embedding_model_name = config.get(
                "VectorDatabase", "embedding_model", fallback="all-mpnet-base-v2"
            )
            collection = self.client.create_collection(
                name=collection_name,
                metadata={"hnsw:space": vector_space, "framework": framework_name},
                embedding_function=chromadb.utils.embedding_functions.SentenceTransformerEmbeddingFunction(
                    model_name=embedding_model_name
                ),
            )

        self.collections[collection_name] = collection
        return collection

    def add_optimized_chunks(self, chunks_data: Dict[str, Any]) -> None:
        """Add optimized chunks to both vector and BM25 indexes."""
        if RAG_OPTIMIZATIONS_AVAILABLE:
            print("Adding optimized chunks to enhanced database...")

            # Add to vector database (parent class method)
            self.add_chunks(chunks_data)

            # Build BM25 index if hybrid search is enabled
            if self.enable_hybrid_search and self.hybrid_retriever:
                try:
                    self.hybrid_retriever.build_bm25_index(chunks_data)
                    print("✓ BM25 index built successfully")
                except Exception as e:
                    print(f"Warning: Failed to build BM25 index: {e}")
        else:
            # Fall back to regular chunk handling
            self.add_chunks(chunks_data)

    def add_chunks(self, chunks_data: Dict[str, Any]) -> None:
        """Add framework chunks to separate collections by framework."""
        total_chunks = 0

        for framework_name, framework_data in chunks_data.items():
            collection = self.get_or_create_collection(framework_name)

            documents = []
            metadatas = []
            ids = []

            for chunk in framework_data["chunks"]:
                documents.append(chunk["text"])
                metadatas.append(
                    {
                        "framework_name": chunk["framework_name"],
                        "framework_full_name": chunk["framework_full_name"],
                        "framework_type": chunk["framework_type"],
                        "document": chunk["document"],
                        "domain": chunk["domain"],
                        "sector": chunk["sector"],
                    }
                )
                ids.append(chunk["chunk_id"])

            if documents:
                # Generate embeddings
                embeddings = self.embedding_model.encode(documents).tolist()

                # Add to collection in batches
                batch_size = int(
                    config.get("VectorDatabase", "batch_size", fallback=100)
                )
                for i in range(0, len(documents), batch_size):
                    batch_docs = documents[i : i + batch_size]
                    batch_meta = metadatas[i : i + batch_size]
                    batch_ids = ids[i : i + batch_size]
                    batch_emb = embeddings[i : i + batch_size]

                    collection.add(
                        documents=batch_docs,
                        metadatas=batch_meta,
                        ids=batch_ids,
                        embeddings=batch_emb,
                    )

                total_chunks += len(documents)
                print(f"Added {len(documents)} chunks to {framework_name} collection")

        print(f"Total chunks added: {total_chunks}")

    def search(
        self, query: str, n_results: int = None, frameworks: Optional[List[str]] = None
    ) -> List[Dict]:
        """Search for relevant chunks across specified frameworks or all frameworks."""
        if n_results is None:
            n_results = self.config_overrides.get(
                "default_search_results",
                get_config_value("VectorDatabase", "default_search_results", 5, int),
            )
        all_results = []

        # If no frameworks specified, search all available collections
        if not frameworks:
            available_frameworks = []
            for collection in self.client.list_collections():
                available_frameworks.append(collection.name)
            frameworks = available_frameworks

        for framework_name in frameworks:
            try:
                collection = self.get_or_create_collection(framework_name)
                if collection.count() == 0:
                    continue

                results = collection.query(query_texts=[query], n_results=n_results)

                if results["documents"][0]:
                    for i, doc in enumerate(results["documents"][0]):
                        all_results.append(
                            {
                                "text": doc,
                                "metadata": results["metadatas"][0][i],
                                "distance": (
                                    results["distances"][0][i]
                                    if "distances" in results
                                    else None
                                ),
                                "framework": framework_name,
                            }
                        )
            except Exception as e:
                error_msg = str(e)
                if "embedding with dimension" in error_msg:
                    print(f"Warning: Could not search {framework_name} collection: {e}")
                    print(
                        "This indicates a dimension mismatch. The collection was likely created with a different embedding model."
                    )
                    print(
                        f"Current model: {self.embedding_model.get_sentence_embedding_dimension()} dimensions"
                    )
                    print(
                        "Consider recreating the vector database or using the correct embedding model."
                    )
                else:
                    print(f"Warning: Could not search {framework_name} collection: {e}")
                continue

        # Sort by distance (lower is better) and limit to n_results
        all_results.sort(key=lambda x: x.get("distance", float("inf")))
        return all_results[:n_results]

    def enhanced_search(
        self,
        query: str,
        n_results: int = None,
        frameworks: Optional[List[str]] = None,
        use_hybrid: bool = None,
        use_reranking: bool = None,
    ) -> List[Dict]:
        """
        Enhanced search with hybrid retrieval and reranking when available.
        Falls back to regular search if RAG optimizations are not available.

        Args:
            query: Search query
            n_results: Number of results to return
            frameworks: Specific frameworks to search
            use_hybrid: Override hybrid search setting
            use_reranking: Override reranking setting

        Returns:
            List of enhanced search results
        """
        if n_results is None:
            n_results = self.config_overrides.get(
                "default_search_results",
                get_config_value("VectorDatabase", "default_search_results", 7, int),
            )

        # If RAG optimizations are not available, fall back to regular search
        if not RAG_OPTIMIZATIONS_AVAILABLE:
            return self.search(query, n_results=n_results, frameworks=frameworks)

        # Determine which features to use
        use_hybrid = use_hybrid if use_hybrid is not None else self.enable_hybrid_search
        use_reranking = (
            use_reranking if use_reranking is not None else self.enable_reranking
        )

        search_results = []

        if use_hybrid and self.hybrid_retriever:
            # Use hybrid search
            try:
                hybrid_results = self.hybrid_retriever.hybrid_search(
                    query,
                    n_results=n_results * 2,
                    frameworks=frameworks,  # Get more results for reranking
                )

                # Convert to standard format
                for result in hybrid_results:
                    search_results.append(
                        {
                            "text": result.text,
                            "metadata": result.metadata,
                            "framework": result.framework,
                            "distance": (
                                1.0 - result.hybrid_score
                                if result.hybrid_score
                                else 0.5
                            ),
                            "hybrid_score": result.hybrid_score,
                            "retrieval_method": "hybrid",
                        }
                    )

                print(f"Hybrid search returned {len(search_results)} results")

            except Exception as e:
                print(f"Hybrid search failed, falling back to semantic: {e}")
                use_hybrid = False

        if not use_hybrid:
            # Fall back to semantic search only
            search_results = self.search(
                query, n_results=n_results * 2, frameworks=frameworks
            )

            # Add retrieval method info
            for result in search_results:
                result["retrieval_method"] = "semantic"

        # Apply reranking if enabled
        if use_reranking and self.reranker and search_results:
            try:
                # Convert to SearchResult objects
                search_result_objects = []
                for result in search_results:
                    sr = SearchResult(
                        chunk_id=result["metadata"].get("chunk_id", ""),
                        text=result["text"],
                        metadata=result["metadata"],
                        framework=result.get("framework", ""),
                        semantic_score=1.0 - result.get("distance", 0.5),
                        hybrid_score=result.get("hybrid_score"),
                        retrieval_method=result.get("retrieval_method", "unknown"),
                    )
                    search_result_objects.append(sr)

                # Rerank results
                ranked_results = self.reranker.rerank_results(
                    query, search_result_objects, top_k=n_results
                )

                # Convert back to standard format
                final_results = []
                for ranked_result in ranked_results:
                    result_dict = {
                        "text": ranked_result.search_result.text,
                        "metadata": ranked_result.search_result.metadata,
                        "framework": ranked_result.search_result.framework,
                        "distance": 1.0 - ranked_result.rerank_score,
                        "rerank_score": ranked_result.rerank_score,
                        "confidence": ranked_result.confidence,
                        "rank_change": ranked_result.rank_change,
                        "retrieval_method": ranked_result.search_result.retrieval_method
                        + "+rerank",
                    }
                    final_results.append(result_dict)

                print(f"Reranking refined results to {len(final_results)} items")
                return final_results

            except Exception as e:
                print(f"Reranking failed, returning unranked results: {e}")

        # Return top n_results without reranking
        return search_results[:n_results]

    def search_framework(
        self, query: str, framework_name: str, n_results: int = None
    ) -> List[Dict]:
        """Search within a specific framework collection."""
        if n_results is None:
            n_results = self.config_overrides.get(
                "default_search_results",
                get_config_value("VectorDatabase", "default_search_results", 5, int),
            )
        try:
            collection = self.get_or_create_collection(framework_name)
            if collection.count() == 0:
                return []

            results = collection.query(query_texts=[query], n_results=n_results)

            formatted_results = []
            if results["documents"][0]:
                for i, doc in enumerate(results["documents"][0]):
                    formatted_results.append(
                        {
                            "text": doc,
                            "metadata": results["metadatas"][0][i],
                            "distance": (
                                results["distances"][0][i]
                                if "distances" in results
                                else None
                            ),
                            "framework": framework_name,
                        }
                    )

            return formatted_results
        except Exception as e:
            print(f"Warning: Could not search {framework_name} collection: {e}")
            return []

    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about all collections."""
        total_chunks = 0
        frameworks = {}
        collection_details = {}

        # Get stats from all existing collections
        for collection_name in self.client.list_collections():
            try:
                collection = self.client.get_collection(collection_name.name)
                count = collection.count()
                total_chunks += count

                # Get framework name from metadata or collection name
                framework_name = collection_name.name
                if hasattr(collection_name, "metadata") and collection_name.metadata:
                    framework_name = collection_name.metadata.get(
                        "framework", collection_name.name
                    )

                frameworks[framework_name] = count
                collection_details[collection_name.name] = {
                    "framework": framework_name,
                    "chunks": count,
                }
            except Exception as e:
                print(
                    f"Warning: Could not get stats for collection {collection_name.name}: {e}"
                )

        return {
            "total_chunks": total_chunks,
            "frameworks": frameworks,
            "collections": collection_details,
            "num_collections": len(collection_details),
        }

    def save_indexes(self, index_dir: str = None) -> None:
        """Save BM25 indexes to disk if hybrid search is enabled."""
        if (
            RAG_OPTIMIZATIONS_AVAILABLE
            and self.enable_hybrid_search
            and self.hybrid_retriever
        ):
            try:
                if index_dir is None:
                    index_dir = str(self.db_path / "indexes")
                self.hybrid_retriever.save_indexes(index_dir)
                print(f"✓ Indexes saved to {index_dir}")
            except Exception as e:
                print(f"Warning: Failed to save indexes: {e}")

    def load_indexes(self, index_dir: str = None) -> None:
        """Load BM25 indexes from disk if hybrid search is enabled."""
        if (
            RAG_OPTIMIZATIONS_AVAILABLE
            and self.enable_hybrid_search
            and self.hybrid_retriever
        ):
            try:
                if index_dir is None:
                    index_dir = str(self.db_path / "indexes")
                self.hybrid_retriever.load_indexes(index_dir)
                print(f"✓ Indexes loaded from {index_dir}")
            except Exception as e:
                print(f"Warning: Failed to load indexes: {e}")

    @classmethod
    def initialize_from_chunks(
        cls, chunks_file_dir: str = "output/chunks", db_path: str = None
    ) -> "VectorDatabase":
        """Initialize database from existing chunk files with separate collections."""
        db = cls(db_path=db_path)

        chunks_path = Path(chunks_file_dir)
        all_chunks = {}

        # Load all chunk files
        for chunk_file in chunks_path.glob("*_chunks.json"):
            with open(chunk_file, "r", encoding="utf-8") as f:
                framework_data = json.load(f)
                framework_name = framework_data["metadata"]["framework"]["name"]
                all_chunks[framework_name] = framework_data

        # Add chunks to database (now creates separate collections)
        if all_chunks:
            db.add_chunks(all_chunks)
            print(
                f"Initialized database with {len(all_chunks)} frameworks in separate collections"
            )

        return db
