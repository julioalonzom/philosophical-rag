import json
import logging
from pathlib import Path
from typing import List, Dict, Generator, Set, Tuple, Optional
import time
import hashlib
import os

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain.schema import Document
from dotenv import load_dotenv

# Constants
RAW_TEXTS_DIR = Path("data/raw_texts")
PROCESSED_TEXTS_DIR = Path("data/processed_texts")
CHROMA_DB_DIR = PROCESSED_TEXTS_DIR / "chroma_db"
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
BATCH_SIZE = 50
ENV_PATH = Path('backend/config/.env').resolve()

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_environment() -> None:
    """Load environment variables and ensure API key is set."""
    logger.info(f"Attempting to load .env file from: {ENV_PATH}")
    load_dotenv(ENV_PATH)
    
    if 'OPENAI_API_KEY' not in os.environ:
        raise ValueError("OPENAI_API_KEY is not set in the environment variables")

def get_input_files() -> List[Dict[str, str]]:
    """Get all input files and their corresponding metadata files."""
    input_files = []
    for author_dir in RAW_TEXTS_DIR.iterdir():
        if author_dir.is_dir():
            for text_file in author_dir.glob("*.txt"):
                metadata_file = text_file.with_suffix(".json")
                if metadata_file.exists():
                    input_files.append({
                        "text": str(text_file),
                        "metadata": str(metadata_file),
                        "author": author_dir.name,
                        "work": text_file.stem
                    })
    return input_files

def generate_document_id(doc: Document) -> str:
    """Create a unique ID based on the document content and metadata."""
    content = doc.page_content
    metadata = str(sorted((k, str(v)) for k, v in doc.metadata.items()))
    return hashlib.md5((content + metadata).encode()).hexdigest()

def get_existing_ids(vectorstore: Chroma) -> Set[str]:
    """Get existing document IDs from the vectorstore."""
    return set(vectorstore.get()['ids'])

def batch_generator(data: List, batch_size: int) -> Generator[List, None, None]:
    """Generate batches from a list."""
    for i in range(0, len(data), batch_size):
        yield data[i:i + batch_size]

def load_document(file_path: str, metadata_path: str) -> Tuple[str, Dict]:
    """Load the document text and its metadata."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
        
        with open(metadata_path, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        
        return text, metadata
    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
        raise
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON metadata: {e}")
        raise

def find_book_boundaries(text: str) -> List[Dict[str, int]]:
    """Find the line boundaries for each book in the text."""
    lines = text.split('\n')
    book_boundaries = []
    current_book = 0
    for i, line in enumerate(lines):
        if line.strip().lower().startswith('book'):
            if current_book > 0:
                book_boundaries[-1]['end_line'] = i - 1
            current_book += 1
            book_boundaries.append({'number': current_book, 'start_line': i + 1})
    
    if book_boundaries:
        book_boundaries[-1]['end_line'] = len(lines) - 1
    
    return book_boundaries

def split_document(text: str, metadata: Dict) -> List[Document]:
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=len,
    )
    
    book_boundaries = find_book_boundaries(text)
    chunks = text_splitter.split_text(text)
    
    documents = []
    current_line = 1
    for i, chunk in enumerate(chunks):
        chunk_metadata = {
            "author": metadata["author"],
            "translator": metadata["translator"],
            "work": metadata["work"],
            "chunk_id": i,
        }
        
        chunk_start_line = current_line
        chunk_end_line = current_line + len(chunk.split('\n')) - 1
        
        for book in book_boundaries:
            if book['start_line'] <= chunk_start_line <= book['end_line']:
                chunk_metadata['book_number'] = book['number']
                for book_info in metadata["books"]:
                    if book_info["number"] == book['number']:
                        chunk_metadata['book_title'] = book_info["title"]
                        break
                break
        
        chunk_metadata['start_line'] = chunk_start_line
        chunk_metadata['end_line'] = chunk_end_line
        
        documents.append(Document(page_content=chunk, metadata=chunk_metadata))
        
        current_line = chunk_end_line + 1
    
    return documents

def create_embeddings_and_store(chunks: List[Document], persist_directory: str) -> Chroma:
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    vectorstore = Chroma(
        embedding_function=embeddings,
        persist_directory=persist_directory
    )
    
    for batch in batch_generator(chunks, BATCH_SIZE):
        ids = [generate_document_id(doc) for doc in batch]
        texts = [doc.page_content for doc in batch]
        metadatas = [doc.metadata for doc in batch]
        
        vectorstore.add_texts(texts=texts, metadatas=metadatas, ids=ids)
        logger.info(f"Processed batch of {len(batch)} documents")
        time.sleep(0.5)  # Small delay between batches
    
    return vectorstore

def process_file(file_info: Dict[str, str]) -> None:
    logger.info(f"Processing {file_info['author']}'s {file_info['work']}...")
    text, metadata = load_document(file_info['text'], file_info['metadata'])
    chunks = split_document(text, metadata)
    
    # Print sample chunks
    for i in range(min(5, len(chunks))):
        logger.info(f"Sample chunk {i} for {file_info['author']}'s {file_info['work']}:")
        logger.info(f"Content: {chunks[i].page_content[:100]}...")
        logger.info(f"Metadata: {chunks[i].metadata}")
        logger.info("---")
    
    vectorstore = Chroma(
        persist_directory=str(CHROMA_DB_DIR),
        embedding_function=HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    )
    existing_ids = get_existing_ids(vectorstore)
    
    new_chunks = [chunk for chunk in chunks if generate_document_id(chunk) not in existing_ids]
    
    if new_chunks:
        vectorstore = create_embeddings_and_store(new_chunks, str(CHROMA_DB_DIR))
        logger.info(f"Added {len(new_chunks)} new documents to the vectorstore for {file_info['author']}'s {file_info['work']}.")
    else:
        logger.info(f"No new documents to add for {file_info['author']}'s {file_info['work']}. Vectorstore is up to date.")
    
    total_docs = vectorstore._collection.count()
    logger.info(f"Total documents in vectorstore: {total_docs}")

def main() -> None:
    """Main function to process all input files."""
    try:
        load_environment()
        input_files = get_input_files()
        for file_info in input_files:
            process_file(file_info)
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        import traceback
        logger.error(traceback.format_exc())

if __name__ == "__main__":
    main()