"""
RAG Optimization module with improved chunking, hybrid search, and reranking.
Addresses Chroma's document size limitations and implements best practices for RAG systems.
"""

import re
import json
import hashlib
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from docling.document_converter import DocumentConverter
from docling_core.types.doc import DoclingDocument

try:
    from .utils import get_config, get_config_value
except ImportError:
    from src.utils import get_config, get_config_value


@dataclass
class OptimizedChunk:
    """Represents a chunk with enhanced metadata for better retrieval."""
    text: str
    chunk_id: str
    framework_name: str
    document: str
    char_count: int
    token_estimate: int
    position: int
    has_headers: bool
    section_title: Optional[str] = None
    subsection_title: Optional[str] = None
    keywords: List[str] = None
    chunk_hash: str = None
    
    def __post_init__(self):
        if self.keywords is None:
            self.keywords = []
        if self.chunk_hash is None:
            self.chunk_hash = hashlib.md5(self.text.encode()).hexdigest()


class SmartChunker:
    """Advanced chunking strategy that respects Chroma's size limits while preserving semantic coherence."""
    
    def __init__(self, max_chunk_chars: int = 4000, overlap_chars: int = 200):
        """
        Initialize chunker with size constraints.
        
        Args:
            max_chunk_chars: Maximum characters per chunk (well below 16KB limit)
            overlap_chars: Overlap between chunks for context preservation
        """
        self.max_chunk_chars = max_chunk_chars
        self.overlap_chars = overlap_chars
        self.config = get_config()
        
        # Patterns for detecting structure
        self.header_patterns = [
            r'^#+\s+(.+)$',  # Markdown headers
            r'^(\d+\.)+\s+(.+)$',  # Numbered sections
            r'^([A-Z][A-Z\s]+):\s*$',  # All caps headers
            r'^[A-Z][\w\s]+\n[-=]{3,}$',  # Underlined headers
        ]
        
        # Sentence boundary detection
        self.sentence_end_pattern = r'(?<=[.!?])\s+(?=[A-Z])'
        
        # Keywords extraction patterns
        self.keyword_patterns = [
            r'\b(?:control|requirement|standard|policy|procedure|security|compliance|audit|risk|assessment|framework|guideline|directive)\b',
            r'\b[A-Z]{2,}\b',  # Acronyms
            r'\b\d+\.\d+(?:\.\d+)*\b',  # Section numbers
        ]
    
    def extract_keywords(self, text: str) -> List[str]:
        """Extract relevant keywords from text for better searchability."""
        keywords = set()
        
        for pattern in self.keyword_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            keywords.update([match.lower() for match in matches if len(match) > 2])
        
        # Add important phrases
        important_phrases = re.findall(r'\b(?:shall|must|should|required|mandatory|prohibited|forbidden|compliance|security|risk|assessment|audit|control|monitoring|logging|access|authentication|authorization|encryption|backup|recovery|incident|response|vulnerability|threat|policy|procedure|standard|framework|guideline)\b', text, re.IGNORECASE)
        keywords.update([phrase.lower() for phrase in important_phrases])
        
        return list(keywords)[:20]  # Limit to top 20 keywords
    
    def detect_headers(self, text: str) -> List[Tuple[str, int]]:
        """Detect headers and their positions in the text."""
        headers = []
        lines = text.split('\n')
        
        for i, line in enumerate(lines):
            for pattern in self.header_patterns:
                match = re.match(pattern, line.strip(), re.MULTILINE)
                if match:
                    header_text = match.group(1) if match.groups() else line.strip()
                    headers.append((header_text, i))
                    break
        
        return headers
    
    def find_best_split_point(self, text: str, target_pos: int) -> int:
        """Find the best position to split text, preferring sentence boundaries."""
        # Look for sentence boundaries around the target position
        window_start = max(0, target_pos - 100)
        window_end = min(len(text), target_pos + 100)
        window = text[window_start:window_end]
        
        # Find sentence boundaries in the window
        sentence_ends = []
        for match in re.finditer(self.sentence_end_pattern, window):
            abs_pos = window_start + match.start()
            sentence_ends.append(abs_pos)
        
        if sentence_ends:
            # Find the sentence end closest to our target
            best_split = min(sentence_ends, key=lambda x: abs(x - target_pos))
            return best_split
        
        # Fall back to paragraph boundaries
        paragraph_ends = [match.start() for match in re.finditer(r'\n\s*\n', text[window_start:window_end])]
        if paragraph_ends:
            abs_pos = window_start + paragraph_ends[0]
            return abs_pos
        
        # Last resort: split at word boundary
        for i in range(target_pos, min(target_pos + 50, len(text))):
            if text[i].isspace():
                return i
        
        return target_pos
    
    def create_overlapping_chunks(self, text: str, framework_name: str, document: str) -> List[OptimizedChunk]:
        """Create overlapping chunks with smart splitting."""
        if len(text) <= self.max_chunk_chars:
            # Text fits in a single chunk
            chunk = OptimizedChunk(
                text=text,
                chunk_id=f"{framework_name}_{document}_0",
                framework_name=framework_name,
                document=document,
                char_count=len(text),
                token_estimate=len(text) // 4,  # Rough estimate
                position=0,
                has_headers=bool(self.detect_headers(text)),
                keywords=self.extract_keywords(text)
            )
            
            headers = self.detect_headers(text)
            if headers:
                chunk.section_title = headers[0][0]
                if len(headers) > 1:
                    chunk.subsection_title = headers[1][0]
            
            return [chunk]
        
        chunks = []
        current_pos = 0
        chunk_index = 0
        
        while current_pos < len(text):
            # Calculate chunk end position
            chunk_end = min(current_pos + self.max_chunk_chars, len(text))
            
            # Find the best split point if not at end of text
            if chunk_end < len(text):
                chunk_end = self.find_best_split_point(text, chunk_end)
            
            # Extract chunk text
            chunk_text = text[current_pos:chunk_end].strip()
            
            if not chunk_text:
                break
            
            # Create chunk with metadata
            chunk = OptimizedChunk(
                text=chunk_text,
                chunk_id=f"{framework_name}_{document}_{chunk_index}",
                framework_name=framework_name,
                document=document,
                char_count=len(chunk_text),
                token_estimate=len(chunk_text) // 4,
                position=chunk_index,
                has_headers=bool(self.detect_headers(chunk_text)),
                keywords=self.extract_keywords(chunk_text)
            )
            
            # Add section information
            headers = self.detect_headers(chunk_text)
            if headers:
                chunk.section_title = headers[0][0]
                if len(headers) > 1:
                    chunk.subsection_title = headers[1][0]
            
            chunks.append(chunk)
            
            # Move to next position with overlap
            if chunk_end >= len(text):
                break
                
            next_pos = chunk_end - self.overlap_chars
            current_pos = max(current_pos + 1, next_pos)  # Ensure progress
            chunk_index += 1
        
        return chunks
    
    def chunk_document(self, doc: DoclingDocument, framework_name: str, document_name: str) -> List[OptimizedChunk]:
        """Chunk a document using the smart chunking strategy."""
        text = doc.export_to_markdown()
        
        # Pre-processing: clean up excessive whitespace
        text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
        text = re.sub(r'[ \t]+', ' ', text)
        
        return self.create_overlapping_chunks(text, framework_name, document_name)


class OptimizedFrameworkProcessor:
    """Enhanced framework processor with improved chunking and validation."""
    
    def __init__(self, converter: Optional[DocumentConverter] = None, chunker: Optional[SmartChunker] = None):
        """Initialize with optimized components."""
        self.converter = converter or DocumentConverter()
        self.chunker = chunker or SmartChunker()
        self.config = get_config()
        
        # Statistics tracking
        self.processing_stats = {
            'total_documents': 0,
            'total_chunks': 0,
            'oversized_chunks': 0,
            'failed_documents': 0,
            'avg_chunk_size': 0,
            'size_distribution': {'small': 0, 'medium': 0, 'large': 0}
        }
    
    def validate_chunk_size(self, chunk: OptimizedChunk) -> bool:
        """Validate chunk size against Chroma limits."""
        # Chroma limit is 16384 bytes, but we're more conservative
        byte_size = len(chunk.text.encode('utf-8'))
        
        if byte_size > 12288:  # 12KB safety margin
            self.processing_stats['oversized_chunks'] += 1
            print(f"Warning: Chunk {chunk.chunk_id} is {byte_size} bytes (may exceed Chroma limits)")
            return False
        
        # Update size distribution stats
        if chunk.char_count < 1000:
            self.processing_stats['size_distribution']['small'] += 1
        elif chunk.char_count < 3000:
            self.processing_stats['size_distribution']['medium'] += 1
        else:
            self.processing_stats['size_distribution']['large'] += 1
        
        return True
    
    def process_document(self, doc_path: Path, framework_name: str) -> List[OptimizedChunk]:
        """Process a single document with enhanced chunking."""
        try:
            self.processing_stats['total_documents'] += 1
            
            # Convert document
            doc = self.converter.convert(str(doc_path)).document
            
            # Create optimized chunks
            chunks = self.chunker.chunk_document(doc, framework_name, doc_path.name)
            
            # Validate chunks
            valid_chunks = []
            for chunk in chunks:
                if self.validate_chunk_size(chunk):
                    valid_chunks.append(chunk)
                else:
                    print(f"Skipping oversized chunk from {doc_path.name}")
            
            self.processing_stats['total_chunks'] += len(valid_chunks)
            return valid_chunks
            
        except Exception as e:
            self.processing_stats['failed_documents'] += 1
            print(f"Error processing {doc_path}: {e}")
            return []
    
    def process_framework(self, framework_dir: Path, metadata: Dict[str, Any]) -> List[OptimizedChunk]:
        """Process all documents in a framework directory."""
        framework_name = metadata["framework"]["name"]
        documents = metadata["files"]["documents"]
        
        all_chunks = []
        
        for doc_file in documents:
            doc_path = framework_dir / doc_file
            if not doc_path.exists():
                print(f"Warning: Document {doc_file} not found in {framework_dir}")
                continue
            
            print(f"Processing {framework_name}: {doc_file}")
            chunks = self.process_document(doc_path, framework_name)
            all_chunks.extend(chunks)
        
        return all_chunks
    
    def convert_chunks_to_legacy_format(self, chunks: List[OptimizedChunk], metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Convert OptimizedChunk objects to legacy format for compatibility."""
        legacy_chunks = []
        
        for chunk in chunks:
            legacy_chunk = {
                "framework_name": chunk.framework_name,
                "framework_full_name": metadata["framework"]["full_name"],
                "framework_type": metadata["framework"]["type"],
                "document": chunk.document,
                "chunk_id": chunk.chunk_id,
                "text": chunk.text,
                "domain": metadata["metadata"]["domain"],
                "sector": metadata["metadata"]["sector"],
                # Enhanced metadata
                "char_count": chunk.char_count,
                "token_estimate": chunk.token_estimate,
                "position": chunk.position,
                "has_headers": chunk.has_headers,
                "section_title": chunk.section_title,
                "subsection_title": chunk.subsection_title,
                "keywords": chunk.keywords,
                "chunk_hash": chunk.chunk_hash
            }
            legacy_chunks.append(legacy_chunk)
        
        return legacy_chunks
    
    def get_processing_summary(self) -> Dict[str, Any]:
        """Get summary of processing statistics."""
        if self.processing_stats['total_chunks'] > 0:
            self.processing_stats['avg_chunk_size'] = sum([
                self.processing_stats['size_distribution']['small'] * 500,
                self.processing_stats['size_distribution']['medium'] * 2000,
                self.processing_stats['size_distribution']['large'] * 3500
            ]) / self.processing_stats['total_chunks']
        
        return self.processing_stats.copy()
    
    def process_all_frameworks(self, frameworks_dir="data/cyber-frameworks"):
        """Process all frameworks - compatibility wrapper."""
        return create_optimized_chunks(frameworks_dir)

    def save_chunks(self, all_chunks, output_dir="output/chunks"):
        """Save chunks - compatibility wrapper."""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        for framework_name, data in all_chunks.items():
            framework_file = output_path / f"{framework_name.lower().replace(' ', '_')}_chunks.json"
            with open(framework_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)


def create_optimized_chunks(frameworks_dir: str = "data/cyber-frameworks") -> Dict[str, Any]:
    """Create optimized chunks using the enhanced processor."""
    import toml
    
    processor = OptimizedFrameworkProcessor()
    frameworks_path = Path(frameworks_dir)
    all_chunks = {}
    
    for framework_dir in frameworks_path.iterdir():
        if not (framework_dir.is_dir() and framework_dir.name != "LICENSE"):
            continue
        
        print(f"\n=== Processing Framework: {framework_dir.name} ===")
        
        # Load metadata
        metadata_path = framework_dir / "metadata.toml"
        if not metadata_path.exists():
            print(f"No metadata.toml found for {framework_dir.name}")
            continue
        
        metadata = toml.load(metadata_path)
        
        # Process framework
        optimized_chunks = processor.process_framework(framework_dir, metadata)
        
        if optimized_chunks:
            # Convert to legacy format for compatibility
            legacy_chunks = processor.convert_chunks_to_legacy_format(optimized_chunks, metadata)
            
            framework_name = metadata["framework"]["name"]
            all_chunks[framework_name] = {
                "metadata": metadata,
                "chunks": legacy_chunks,
                "total_chunks": len(legacy_chunks),
                "optimized": True
            }
            
            print(f"Generated {len(legacy_chunks)} optimized chunks for {framework_name}")
    
    # Print processing summary
    stats = processor.get_processing_summary()
    print(f"\n=== Processing Summary ===")
    print(f"Documents processed: {stats['total_documents']}")
    print(f"Total chunks created: {stats['total_chunks']}")
    print(f"Oversized chunks (skipped): {stats['oversized_chunks']}")
    print(f"Failed documents: {stats['failed_documents']}")
    print(f"Average chunk size: {stats['avg_chunk_size']:.0f} characters")
    print(f"Size distribution: {stats['size_distribution']}")
    
    return all_chunks


if __name__ == "__main__":
    # Test the optimized chunking
    chunks = create_optimized_chunks()
    print(f"\nCreated optimized chunks for {len(chunks)} frameworks")
    
    # Save results
    output_path = Path("output/optimized_chunks")
    output_path.mkdir(parents=True, exist_ok=True)
    
    for framework_name, data in chunks.items():
        framework_file = output_path / f"{framework_name.lower().replace(' ', '_')}_optimized_chunks.json"
        with open(framework_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"Saved {framework_name} to {framework_file}")