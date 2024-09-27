import json
import logging
from pathlib import Path
from typing import List, Dict, Generator
import time

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.schema import Document
from dotenv import load_dotenv
import os

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Constants
INPUT_FILE = "data/raw_texts/plato/republic.txt"
METADATA_FILE = "data/raw_texts/plato/republic_metadata.json"
CHROMA_PERSIST_DIRECTORY = "data/processed_texts/plato/republic/chroma_db"
CHUNK_SIZE = 500
CHUNK_OVERLAP = 100

# Get the absolute path to the .env file
env_path = Path('backend/config/.env').resolve()
logging.info(f"Attempting to load .env file from: {env_path}")

# Load environment variables
load_dotenv(env_path)

# Ensure the API key is set
if 'OPENAI_API_KEY' not in os.environ:
    raise ValueError("OPENAI_API_KEY is not set in the environment variables")

BATCH_SIZE = 50

def batch_generator(data: List, batch_size: int) -> Generator:
    for i in range(0, len(data), batch_size):
        yield data[i:i + batch_size]

def load_document(file_path: str, metadata_path: str) -> tuple[str, Dict]:
    """Load the document text and its metadata."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
        
        with open(metadata_path, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        
        return text, metadata
    except FileNotFoundError as e:
        logging.error(f"File not found: {e}")
        raise
    except json.JSONDecodeError as e:
        logging.error(f"Error decoding JSON metadata: {e}")
        raise

def find_book_boundaries(text: str) -> List[Dict]:
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
    """Split the document into chunks and assign correct book numbers."""
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
        chunk_metadata = metadata.copy()
        chunk_metadata['chunk_id'] = i
        
        chunk_start_line = current_line
        chunk_end_line = current_line + len(chunk.split('\n')) - 1
        
        # Determine which book this chunk belongs to
        for book in book_boundaries:
            if book['start_line'] <= chunk_start_line <= book['end_line']:
                chunk_metadata['book_number'] = book['number']
                break
        
        chunk_metadata['start_line'] = chunk_start_line
        chunk_metadata['end_line'] = chunk_end_line
        
        documents.append(Document(page_content=chunk, metadata=chunk_metadata))
        
        current_line = chunk_end_line + 1
    
    return documents

def create_embeddings_and_store(chunks: List[Document]) -> Chroma:
    """Create embeddings and store them in Chroma using a local model and batching."""
    # Use a local embedding model
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    vectorstore = Chroma(
        embedding_function=embeddings,
        persist_directory=CHROMA_PERSIST_DIRECTORY
    )
    
    for batch in batch_generator(chunks, BATCH_SIZE):
        filtered_batch = []
        for doc in batch:
            filtered_metadata = {}
            for key, value in doc.metadata.items():
                if isinstance(value, (str, int, float, bool)):
                    filtered_metadata[key] = value
            filtered_batch.append(Document(page_content=doc.page_content, metadata=filtered_metadata))
        
        vectorstore.add_documents(filtered_batch)
        logging.info(f"Processed batch of {len(batch)} documents")
        time.sleep(0.5)  # Small delay between batches to prevent potential issues
    
    vectorstore.persist()
    return vectorstore

def main():
    try:
        # Load document and metadata
        logging.info("Loading document and metadata...")
        text, metadata = load_document(INPUT_FILE, METADATA_FILE)
        
        # Split document into chunks
        logging.info("Splitting document into chunks...")
        chunks = split_document(text, metadata)
        
        # Create embeddings and store in Chroma
        logging.info("Creating embeddings and storing in Chroma...")
        vectorstore = create_embeddings_and_store(chunks)
        
        logging.info("Processing complete. Chroma index saved.")
    
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        import traceback
        logging.error(traceback.format_exc())

if __name__ == "__main__":
    main()