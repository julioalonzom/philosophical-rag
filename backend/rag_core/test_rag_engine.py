import os
import logging
from typing import List, Dict, Tuple, Any
from pathlib import Path

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.chains import RetrievalQA
from langchain.schema import Document

from dotenv import load_dotenv

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv("backend/config/.env")

class RAGEngine:
    def __init__(self, chroma_persist_directory=None):
        if chroma_persist_directory is None:
            self.chroma_persist_directory = os.getenv('RAG_CHROMA_PERSIST_DIRECTORY', 'data/processed_texts/chroma_db')
        else:
            self.chroma_persist_directory = chroma_persist_directory

        self.embeddings = None
        self.vectorstore = None
        self.qa_chain = None
        
        self._load_chroma_index()
        self._setup_qa_chain()

    def _load_chroma_index(self):
        try:
            logger.info(f"Loading Chroma index from {self.chroma_persist_directory}")
            self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
            self.vectorstore = Chroma(
                persist_directory=self.chroma_persist_directory,
                embedding_function=self.embeddings
            )
            doc_count = self.vectorstore._collection.count()
            logger.info(f"Chroma index loaded successfully. Number of documents: {doc_count}")
            if doc_count == 0:
                raise ValueError("Chroma index is empty. Please check the indexing process.")
        except Exception as e:
            logger.error(f"Error loading Chroma index: {e}")
            raise

    def _setup_qa_chain(self):
        try:
            logger.info("Setting up QA chain")
            retriever = self.vectorstore.as_retriever(search_kwargs={"k": 5})  # Increased k for more context
            llm = ChatOpenAI(model_name="gpt-4o-mini",
                             temperature=0,
                             api_key=os.getenv("OPENAI_API_KEY"))
            
            template = """You are an AI assistant specializing in philosophy, particularly the works of Plato and Aristotle. Use the following pieces of context to answer the question at the end. If you don't know the answer, just say that you don't know, don't try to make up an answer. Always try to provide specific references to the text when possible, including the author, work, and book number if available.

Context:
{context}

Question: {question}
Answer: """
            
            prompt = ChatPromptTemplate.from_template(template)
            
            self.qa_chain = RetrievalQA.from_chain_type(
                llm=llm,
                chain_type="stuff",
                retriever=retriever,
                return_source_documents=True,
                chain_type_kwargs={"prompt": prompt}
            )
            logger.info("QA chain set up successfully")
        except Exception as e:
            logger.error(f"Error setting up QA chain: {e}")
            raise

    def process_query(self, question: str) -> Tuple[str, List[Dict[str, Any]]]:
        try:
            logger.info(f"Processing query: {question}")
            
            result = self.qa_chain({"query": question})
            
            answer = result['result']
            source_documents = result.get('source_documents', [])
            
            logger.info(f"Number of source documents: {len(source_documents)}")
            
            if len(source_documents) == 0:
                logger.warning("No source documents returned. This may indicate an issue with the retriever.")
            
            context = self._format_context(source_documents)
            
            logger.info("Query processed successfully")
            return answer, context
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            raise

    def _format_context(self, source_documents: List[Document]) -> List[Dict[str, Any]]:
        context = []
        for doc in source_documents:
            context_item = {
                "content": doc.page_content,
                "metadata": doc.metadata
            }
            context.append(context_item)
        return context

    def _format_citations(self, source_documents: List[Document]) -> List[Dict[str, str]]:
        citations = []
        for doc in source_documents:
            citation = {
                "content": doc.page_content,
                "book_number": doc.metadata.get("book_number", "Unknown"),
                "book_title": doc.metadata.get("book_title", "Unknown"),
                "start_line": doc.metadata.get("start_line", "Unknown"),
                "end_line": doc.metadata.get("end_line", "Unknown")
            }
            citations.append(citation)
        return citations

if __name__ == "__main__":
    rag_engine = RAGEngine()
    questions = [
        "What are the forms in Plato's philosophy?",
        "How does Plato define justice in the Republic?",
        "What is the role of the philosopher-king in Plato's ideal state?"
    ]
    for question in questions:
        answer, context = rag_engine.process_query(question)
        print(f"\nQuestion: {question}")
        print(f"Answer: {answer}")
        print("\nContext:")
        for item in context:
            print(f"- Author: {item['metadata']['author']}")
            print(f"  Work: {item['metadata']['work']}")
            print(f"  Book: {item['metadata'].get('book_number', 'N/A')} - {item['metadata'].get('book_title', 'N/A')}")
            print(f"  Lines: {item['metadata']['start_line']}-{item['metadata']['end_line']}")
            print(f"  Content: {item['content'][:100]}...")
            print()
        print("=" * 50)