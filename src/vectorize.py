from docling_core.transforms.chunker import HierarchicalChunker

from docling.document_converter import DocumentConverter

converter = DocumentConverter()
chunker = HierarchicalChunker()

# Convert the input file to Docling Document
source = "data/cyber-frameworks/cjis/CJIS-Security-Policy_v5-8_20190601.md"
doc = converter.convert(source).document

# Perform hierarchical chunking
texts = [chunk.text for chunk in chunker.chunk(doc)]

# Print the chunked texts
for i, text in enumerate(texts):
    print(f"Chunk {i+1}:\n{text}\n")