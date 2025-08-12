import toml
from pathlib import Path
from docling_core.transforms.chunker import HierarchicalChunker
from docling.document_converter import DocumentConverter

def load_framework_metadata(framework_path):
    """Load metadata.toml for a framework directory."""
    metadata_path = framework_path / "metadata.toml"
    if metadata_path.exists():
        return toml.load(metadata_path)
    return None

def process_framework_documents(framework_path, metadata):
    """Process all documents for a single framework."""
    converter = DocumentConverter()
    chunker = HierarchicalChunker()
    
    framework_name = metadata['framework']['name']
    documents = metadata['files']['documents']
    
    framework_chunks = []
    
    for doc_file in documents:
        doc_path = framework_path / doc_file
        if doc_path.exists():
            print(f"Processing {framework_name}: {doc_file}")
            
            # Convert document
            doc = converter.convert(str(doc_path)).document
            
            # Chunk document
            chunks = chunker.chunk(doc)
            
            # Add metadata to each chunk
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
                framework_chunks.append(chunk_data)
        else:
            print(f"Warning: Document {doc_file} not found in {framework_path}")
    
    return framework_chunks

def process_all_frameworks(frameworks_dir="data/cyber-frameworks"):
    """Process all frameworks and organize chunks by framework."""
    frameworks_path = Path(frameworks_dir)
    all_chunks = {}
    
    for framework_dir in frameworks_path.iterdir():
        if framework_dir.is_dir() and framework_dir.name != "LICENSE":
            print(f"\n=== Processing Framework: {framework_dir.name} ===")
            
            metadata = load_framework_metadata(framework_dir)
            if metadata:
                chunks = process_framework_documents(framework_dir, metadata)
                framework_name = metadata['framework']['name']
                all_chunks[framework_name] = {
                    'metadata': metadata,
                    'chunks': chunks,
                    'total_chunks': len(chunks)
                }
                print(f"Generated {len(chunks)} chunks for {framework_name}")
            else:
                print(f"No metadata.toml found for {framework_dir.name}")
    
    return all_chunks

def print_framework_summary(all_chunks):
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

def save_chunks_by_framework(all_chunks, output_dir="output/chunks"):
    """Save chunks organized by framework to separate files."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    for framework_name, data in all_chunks.items():
        framework_file = output_path / f"{framework_name.lower().replace(' ', '_')}_chunks.json"
        
        # Save framework chunks as JSON
        import json
        with open(framework_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"Saved {len(data['chunks'])} chunks for {framework_name} to {framework_file}")

if __name__ == "__main__":
    # Process all frameworks
    all_chunks = process_all_frameworks()
    
    # Print summary
    print_framework_summary(all_chunks)
    
    # Optionally save to files
    save_chunks_by_framework(all_chunks)
    
    # Example: Access specific framework chunks
    print("\n=== Example: First chunk from NIST CSF ===")
    if 'NIST CSF' in all_chunks and all_chunks['NIST CSF']['chunks']:
        first_chunk = all_chunks['NIST CSF']['chunks'][0]
        print(f"Framework: {first_chunk['framework_name']}")
        print(f"Document: {first_chunk['document']}")
        print(f"Text preview: {first_chunk['text'][:200]}...")