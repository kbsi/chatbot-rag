import sys
from utils import load_documents
from rag import setup_rag_pipeline
from embedding import setup_vector_store
import unittest
import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"  # Add this line

# Add parent directory to path to import project modules
sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')))


class TestRAGQueries(unittest.TestCase):
    """Test the RAG system with sample queries"""

    @classmethod
    def setUpClass(cls):
        """Set up the RAG system once for all tests"""
        data_path = os.path.join('data', 'train.jsonl')

        # Skip tests if data file doesn't exist
        if not os.path.exists(data_path):
            raise unittest.SkipTest(f"Data file not found at {data_path}")

        documents = load_documents(data_path)
        vector_store = setup_vector_store(
            documents, "test_chroma_db", force_rebuild=True)
        cls.rag_chain = setup_rag_pipeline(vector_store)

    def test_simple_query(self):
        """Test a simple query to verify basic functionality"""
        # Changed from __call__ to invoke
        result = self.rag_chain.invoke(
            {"query": "What is this document about?"})
        self.assertIsNotNone(result["result"])
        self.assertTrue(len(result["result"]) > 0)

    def test_specific_query(self):
        """Test a specific query that should have a clear answer in the data"""
        # Adjust this query to match your actual data
        # Changed from __call__ to invoke
        result = self.rag_chain.invoke(
            {"query": "Give me technical information about the system"})
        self.assertIsNotNone(result["result"])
        self.assertTrue(len(result["source_documents"]) > 0)

    def test_out_of_scope_query(self):
        """Test how the system handles questions outside the scope of the data"""
        # Changed from __call__ to invoke
        result = self.rag_chain.invoke(
            {"query": "What is the price of Bitcoin today?"})
        # The answer should indicate lack of knowledge or context
        self.assertIsNotNone(result["result"])


if __name__ == "__main__":
    unittest.main()
