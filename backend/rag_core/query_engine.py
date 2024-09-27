import os
import logging
from typing import List, Tuple, Dict
from pathlib import Path

from langchain_openai import OpenAIEmbeddings, OpenAI
from langchain_community.vectorstores import Chroma
from langchain.schema import Document
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
env_path = Path('backend/config/.env').resolve()
load_dotenv(env_path)

# Constants
CHROMA_PERSIST_DIRECTORY = "data/processed_texts/plato/republic/chroma_db"
MODEL_NAME = "gpt-4o-mini"

class PlatoRepublicRAG:
    def __init__(self):
        """Initialize the RAG system for Plato's Republic."""
        self.vectorstore = self._load_chroma_index()
        self.llm = OpenAI(model_name=MODEL_NAME, temperature=0)
        self.qa_chain = self._setup_qa_chain()

    def _load_chroma_index(self) -> Chroma:
        """Load the pre-built Chroma index."""
        try:
            embeddings = OpenAIEmbeddings()
            vectorstore = Chroma(persist_directory=CHROMA_PERSIST_DIRECTORY, embedding_function=embeddings)
            logger.info("Chroma index loaded successfully.")
            return vectorstore
        except Exception as e:
            logger.error(f"Error loading Chroma index: {e}")
            raise

    def _setup_qa_chain(self) -> RetrievalQA:
        """Set up the question-answering chain."""
        prompt_template = """Use the following pieces of context to answer the question at the end. If you don't know the answer, just say that you don't know, don't try to make up an answer.

        {context}

        Question: {question}
        Answer:"""
        PROMPT = PromptTemplate(
            template=prompt_template, input_variables=["context", "question"]
        )

        chain_type_kwargs = {"prompt": PROMPT}
        qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.vectorstore.as_retriever(),
            chain_type_kwargs=chain_type_kwargs,
            return_source_documents=True
        )
        return qa_chain

    def query(self, user_query: str) -> Tuple[str, List[Dict[str, str]]]:
        """
        Process a user query about Plato's Republic.

        Args:
            user_query (str): The user's question about Plato's Republic.

        Returns:
            Tuple[str, List[Dict[str, str]]]: A tuple containing the generated response
            and a list of source chunks with their citations.
        """
        try:
            # Retrieve relevant chunks and generate response
            result = self.qa_chain({"query": user_query})
            response = result['result']
            source_documents = result['source_documents']

            # Process source documents
            sources = []
            for doc in source_documents:
                source = {
                    "content": doc.page_content,
                    "book_number": doc.metadata.get("book_number", "Unknown"),
                    "chunk_id": doc.metadata.get("chunk_id", "Unknown")
                }
                sources.append(source)

            logger.info(f"Query processed successfully: {user_query}")
            return response, sources
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            raise

# Usage example
if __name__ == "__main__":
    rag = PlatoRepublicRAG()
    query = "What does Plato say about justice in the Republic?"
    response, sources = rag.query(query)
    print(f"Response: {response}")
    print("\nSources:")
    for source in sources:
        print(f"Book {source['book_number']}, Chunk {source['chunk_id']}:")
        print(source['content'])
        print()