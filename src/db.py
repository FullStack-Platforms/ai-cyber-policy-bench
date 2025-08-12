import chromadb
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from sentence_transformers import SentenceTransformer
import configparser

# Load configuration
config = configparser.ConfigParser()
config.read('config.cfg')

class VectorDatabase:
    """Vector database for storing and retrieving cybersecurity framework chunks."""
    
    def __init__(self, db_path: str = None, collection_name: str = "cyber_frameworks"):
        """Initialize the vector database."""
        if db_path is None:
            db_path = config.get('Vector Database', 'db_path', fallback='./vector_db')
        self.db_path = Path(db_path)
        self.db_path.mkdir(exist_ok=True)
        
        # Initialize ChromaDB
        self.client = chromadb.PersistentClient(path=str(self.db_path))
        self.collection_name = collection_name
        
        # Initialize embedding model
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Get or create collection
        try:
            self.collection = self.client.get_collection(collection_name)
        except:
            self.collection = self.client.create_collection(
                name=collection_name,
                metadata={"hnsw:space": "cosine"}
            )
    
    def add_chunks(self, chunks_data: Dict[str, Any]) -> None:
        """Add framework chunks to the vector database."""
        documents = []
        metadatas = []
        ids = []
        
        for framework_data in chunks_data.values():
            for chunk in framework_data['chunks']:
                documents.append(chunk['text'])
                metadatas.append({
                    'framework_name': chunk['framework_name'],
                    'framework_full_name': chunk['framework_full_name'],
                    'framework_type': chunk['framework_type'],
                    'document': chunk['document'],
                    'domain': chunk['domain'],
                    'sector': chunk['sector']
                })
                ids.append(chunk['chunk_id'])
        
        # Generate embeddings
        embeddings = self.embedding_model.encode(documents).tolist()
        
        # Add to collection in batches
        batch_size = 100
        for i in range(0, len(documents), batch_size):
            batch_docs = documents[i:i+batch_size]
            batch_meta = metadatas[i:i+batch_size]
            batch_ids = ids[i:i+batch_size]
            batch_emb = embeddings[i:i+batch_size]
            
            self.collection.add(
                documents=batch_docs,
                metadatas=batch_meta,
                ids=batch_ids,
                embeddings=batch_emb
            )
        
        print(f"Added {len(documents)} chunks to vector database")
    
    def search(self, query: str, n_results: int = 5, framework_filter: Optional[str] = None) -> List[Dict]:
        """Search for relevant chunks based on query."""
        where_clause = {}
        if framework_filter:
            where_clause = {"framework_name": framework_filter}
        
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results,
            where=where_clause if where_clause else None
        )
        
        formatted_results = []
        if results['documents'][0]:
            for i, doc in enumerate(results['documents'][0]):
                formatted_results.append({
                    'text': doc,
                    'metadata': results['metadatas'][0][i],
                    'distance': results['distances'][0][i] if 'distances' in results else None
                })
        
        return formatted_results
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the collection."""
        count = self.collection.count()
        
        # Get sample of metadata to analyze frameworks
        if count > 0:
            sample = self.collection.get(limit=min(count, 1000))
            frameworks = {}
            for meta in sample['metadatas']:
                fw_name = meta['framework_name']
                frameworks[fw_name] = frameworks.get(fw_name, 0) + 1
        else:
            frameworks = {}
        
        return {
            'total_chunks': count,
            'frameworks': frameworks,
            'collection_name': self.collection_name
        }
    
    @classmethod
    def initialize_from_chunks(cls, chunks_file_dir: str = "output/chunks", 
                             db_path: str = None) -> 'VectorDatabase':
        """Initialize database from existing chunk files."""
        db = cls(db_path=db_path)
        
        chunks_path = Path(chunks_file_dir)
        all_chunks = {}
        
        # Load all chunk files
        for chunk_file in chunks_path.glob("*_chunks.json"):
            with open(chunk_file, 'r', encoding='utf-8') as f:
                framework_data = json.load(f)
                framework_name = framework_data['metadata']['framework']['name']
                all_chunks[framework_name] = framework_data
        
        # Add chunks to database
        if all_chunks:
            db.add_chunks(all_chunks)
            print(f"Initialized database with {len(all_chunks)} frameworks")
        
        return db