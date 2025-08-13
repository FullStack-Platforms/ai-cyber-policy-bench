import toml
import json
from pathlib import Path
from docling_core.transforms.chunker import HierarchicalChunker
from docling.document_converter import DocumentConverter

# Example usage:
# ```python
# from src.vectorize import FrameworkProcessor
# 
# # Process all frameworks
# processor = FrameworkProcessor()
# all_chunks = processor.process_all_frameworks()
# processor.print_summary(all_chunks)
# processor.save_chunks(all_chunks)
# ```

class FrameworkProcessor:
    """Process cybersecurity frameworks into chunks for analysis."""
    
    def __init__(self, converter=None, chunker=None):
        """Initialize with document converter and chunker."""
        self.converter = converter or DocumentConverter()
        self.chunker = chunker or HierarchicalChunker()
    
    def load_metadata(self, framework_path):
        """Load metadata.toml for a framework directory."""
        metadata_path = framework_path / "metadata.toml"
        return toml.load(metadata_path) if metadata_path.exists() else None
    
    def process_documents(self, framework_path, metadata):
        """Process all documents for a single framework."""
        framework_name = metadata['framework']['name']
        documents = metadata['files']['documents']
        
        framework_chunks = []
        
        for doc_file in documents:
            doc_path = framework_path / doc_file
            if not doc_path.exists():
                print(f"Warning: Document {doc_file} not found in {framework_path}")
                continue
                
            print(f"Processing {framework_name}: {doc_file}")
            
            # Convert and chunk document
            doc = self.converter.convert(str(doc_path)).document
            chunks = self.chunker.chunk(doc)
            
            # Add metadata to each chunk
            framework_chunks.extend(self._create_chunk_data(chunks, metadata, doc_file))
        
        return framework_chunks
    
    def _create_chunk_data(self, chunks, metadata, doc_file):
        """Create chunk data with metadata."""
        framework_name = metadata['framework']['name']
        result = []
        
        for i, chunk in enumerate(chunks):
            chunk_data = {
                'framework_name': framework_name,
                'framework_full_name': metadata['framework']['full_name'],
                'framework_type': metadata['framework']['type'],
                'document': doc_file,
                'chunk_id': f"{framework_name}_{doc_file}_{i+1}",
                'text': chunk.text,
                'domain': metadata['metadata']['domain'],
                'sector': metadata['metadata']['sector']
            }
            result.append(chunk_data)
            
        return result
    
    def process_all_frameworks(self, frameworks_dir="data/cyber-frameworks"):
        """Process all frameworks and organize chunks by framework."""
        frameworks_path = Path(frameworks_dir)
        all_chunks = {}
        
        for framework_dir in frameworks_path.iterdir():
            if not (framework_dir.is_dir() and framework_dir.name != "LICENSE"):
                continue
                
            print(f"\n=== Processing Framework: {framework_dir.name} ===")
            
            metadata = self.load_metadata(framework_dir)
            if not metadata:
                print(f"No metadata.toml found for {framework_dir.name}")
                continue
                
            chunks = self.process_documents(framework_dir, metadata)
            framework_name = metadata['framework']['name']
            all_chunks[framework_name] = {
                'metadata': metadata,
                'chunks': chunks,
                'total_chunks': len(chunks)
            }
            print(f"Generated {len(chunks)} chunks for {framework_name}")
        
        return all_chunks
    
    def print_summary(self, all_chunks):
        """Print summary of all processed frameworks."""
        print("\n" + "="*50)
        print("FRAMEWORK PROCESSING SUMMARY")
        print("="*50)
        
        total_chunks = 0
        for framework_name, data in all_chunks.items():
            chunk_count = data['total_chunks']
            total_chunks += chunk_count
            framework_type = data['metadata']['framework']['type']
            print(f"{framework_name}: {chunk_count} chunks ({framework_type})")
        
        print(f"\nTotal frameworks: {len(all_chunks)}")
        print(f"Total chunks: {total_chunks}")
    
    def save_chunks(self, all_chunks, output_dir="output/chunks"):
        """Save chunks organized by framework to separate files."""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        for framework_name, data in all_chunks.items():
            framework_file = output_path / f"{framework_name.lower().replace(' ', '_')}_chunks.json"
            
            with open(framework_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            print(f"Saved {len(data['chunks'])} chunks for {framework_name} to {framework_file}")
    
    def initialize_vector_db(self, all_chunks, db_path=None):
        """Initialize vector database with processed chunks using separate collections."""
        try:
            from .db import VectorDatabase
        except ImportError:
            from src.db import VectorDatabase
        
        print("\n=== Initializing Vector Database ===")
        db = VectorDatabase(db_path=db_path)
        db.add_chunks(all_chunks)
        
        # Print statistics
        stats = db.get_collection_stats()
        print(f"Vector database initialized with {stats['num_collections']} collections")
        print(f"Total chunks: {stats['total_chunks']}")
        for framework, count in stats['frameworks'].items():
            print(f"  {framework}: {count} chunks")
        
        return db

if __name__ == "__main__":
    # Process all frameworks
    processor = FrameworkProcessor()
    all_chunks = processor.process_all_frameworks()
    
    # Print summary
    processor.print_summary(all_chunks)
    
    # Save to files
    processor.save_chunks(all_chunks)
    
    # Example: Access specific framework chunks
    print("\n=== Example: First chunk from NIST CSF ===")
    if 'NIST CSF' in all_chunks and all_chunks['NIST CSF']['chunks']:
        first_chunk = all_chunks['NIST CSF']['chunks'][0]
        print(f"Framework: {first_chunk['framework_name']}")
        print(f"Document: {first_chunk['document']}")
        print(f"Text preview: {first_chunk['text'][:200]}...")