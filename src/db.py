import chromadb
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from sentence_transformers import SentenceTransformer
import configparser

# Load configuration
config = configparser.ConfigParser()
config.read("config.cfg")


class VectorDatabase:
    """Vector database for storing and retrieving cybersecurity framework chunks."""

    def __init__(self, db_path: str = None):
        """Initialize the vector database with multi-collection support."""
        if db_path is None:
            db_path = config.get("Vector Database", "db_path", fallback="./vector_db")
        self.db_path = Path(db_path)
        self.db_path.mkdir(exist_ok=True)

        # Initialize ChromaDB
        self.client = chromadb.PersistentClient(path=str(self.db_path))

        # Initialize embedding model
        self.embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

        # Store collections by framework name
        self.collections = {}

    def get_or_create_collection(self, framework_name: str) -> chromadb.Collection:
        """Get or create a collection for a specific framework."""
        # Framework names are already standardized, use them directly as collection names
        collection_name = framework_name

        if collection_name in self.collections:
            return self.collections[collection_name]

        try:
            collection = self.client.get_collection(collection_name)
        except Exception:
            collection = self.client.create_collection(
                name=collection_name,
                metadata={"hnsw:space": "cosine", "framework": framework_name},
            )

        self.collections[collection_name] = collection
        return collection

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
                batch_size = 100
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
        self, query: str, n_results: int = 5, frameworks: Optional[List[str]] = None
    ) -> List[Dict]:
        """Search for relevant chunks across specified frameworks or all frameworks."""
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
                print(f"Warning: Could not search {framework_name} collection: {e}")
                continue

        # Sort by distance (lower is better) and limit to n_results
        all_results.sort(key=lambda x: x.get("distance", float("inf")))
        return all_results[:n_results]

    def search_framework(
        self, query: str, framework_name: str, n_results: int = 5
    ) -> List[Dict]:
        """Search within a specific framework collection."""
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
