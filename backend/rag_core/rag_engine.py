import os
import logging
from typing import List, Tuple, Dict, Any
from pathlib import Path

from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import Document
from langchain.chains import RetrievalQA
from dotenv import load_dotenv
from django.conf import settings
from rag_app.models import User
from rag_app.config import ACCOUNT_TIERS

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Suppress HuggingFace tokenizer warnings
os.environ["TOKENIZERS_PARALLELISM"] = "false"

env_path = Path('backend/config/.env').resolve()
load_dotenv(env_path)



class RAGEngine:
    def __init__(self, chroma_persist_directory=None):
        if chroma_persist_directory is None:
            project_root = Path(__file__).resolve().parent.parent.parent
            self.chroma_persist_directory = str(project_root / 'data' / 'processed_texts' / 'chroma_db')
        else:
            self.chroma_persist_directory = chroma_persist_directory

        self.chroma_persist_directory = str(Path(self.chroma_persist_directory).resolve())
        print(f"Chroma persist directory: {self.chroma_persist_directory}")

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
            retriever = self.vectorstore.as_retriever(search_kwargs={"k": 5})
            llm = ChatOpenAI(model_name="gpt-4o-mini",
                             temperature=0,
                             api_key=os.getenv("OPENAI_API_KEY"))
            
            template = """system_message: You are an AI assistant specializing in ancient and medieval philosophy, with expertise in Plato, Aristotle, and Aquinas. Answer the question using the provided context. Follow these guidelines:

1. Use at least one context piece, prioritizing primary sources.
2. Cite specific references (author, work, section) when possible.
3. If unsure, state that clearly instead of speculating.
4. Be concise but accurate, using philosophical terms correctly.
5. Compare philosophers' views briefly if relevant.

human_message: Context:
{context}

Question: {question}

Answer:"""
            
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
            
            citations = self._format_citations(source_documents)
            
            logger.info("Query processed successfully")
            return answer, citations
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            raise

    def _format_citations(self, source_documents: List[Document]) -> List[Dict[str, Any]]:
        citations = []
        for doc in source_documents:
            citation = {
                "content": doc.page_content,
                "author": doc.metadata.get("author", "Unknown"),
                "work": doc.metadata.get("work", "Unknown"),
                "section": doc.metadata.get("section", "Unknown"),
                "start_line": doc.metadata.get("start_line", "Unknown"),
                "end_line": doc.metadata.get("end_line", "Unknown")
            }
            citations.append(citation)
        return citations

# Function to set up Django environment
def setup_django():
    import django
    import sys
    from pathlib import Path

    project_root = Path(__file__).resolve().parent.parent.parent
    sys.path.append(str(project_root))

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.config.settings')
    django.setup()

# Test the RAGEngine class
if __name__ == "__main__":
    setup_django()
    rag_engine = RAGEngine()
    questions = [
        "What is the allegory of the cave?",
        "How does Plato define justice in the Republic?",
        "What is the role of the philosopher-king in Plato's ideal state?"
    ]
    for question in questions:
        answer, citations = rag_engine.process_query(question)
        print(f"\nQuestion: {question}")
        print(f"Answer: {answer}")
        print("Citations:")
        for citation in citations:
            print(f"- {citation['author']}, {citation['work']}")
            print(f"  Section: {citation['section']}")
            print(f"  Lines {citation['start_line']}-{citation['end_line']}")
            print(f"  Content: {citation['content'][:100]}...")
        print("\n" + "="*50 + "\n")