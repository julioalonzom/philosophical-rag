from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rag_core.rag_engine import RAGEngine
from django.conf import settings
from pathlib import Path
import os

class RAGAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        # Ensure the RAG_CHROMA_PERSIST_DIRECTORY setting is available
        if not hasattr(settings, 'RAG_CHROMA_PERSIST_DIRECTORY'):
            settings.RAG_CHROMA_PERSIST_DIRECTORY = os.getenv('RAG_CHROMA_PERSIST_DIRECTORY', Path('data/processed_texts/plato/republic/chroma_db').resolve())
        self.rag_engine = RAGEngine()

    def test_query_endpoint(self):
        url = reverse('query')
        data = {'query': 'What is justice according to Plato?'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('response', response.data)
        self.assertIn('citations', response.data)

    def test_rag_engine(self):
        query = "What is the allegory of the cave?"
        response, citations = self.rag_engine.process_query(query)
        self.assertIsNotNone(response)
        self.assertIsInstance(citations, list)
        self.assertTrue(len(citations) > 0)

    def test_invalid_query(self):
        url = reverse('query')
        data = {'query': ''}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 400)

    def test_chroma_index_loading(self):
        self.assertIsNotNone(self.rag_engine.vectorstore)
        self.assertTrue(self.rag_engine.vectorstore._collection.count() > 0)

    def test_qa_chain_setup(self):
        self.assertIsNotNone(self.rag_engine.qa_chain)