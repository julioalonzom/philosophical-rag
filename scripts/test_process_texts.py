import pytest
from pathlib import Path
import json
from unittest.mock import patch, MagicMock

from scripts.process_texts import (
    get_input_files,
    generate_document_id,
    batch_generator,
    load_document,
    find_book_boundaries,
    split_document,
)
from langchain.schema import Document

# Mock data
MOCK_RAW_TEXTS_DIR = Path("mock_data/raw_texts")
MOCK_PROCESSED_TEXTS_DIR = Path("mock_data/processed_texts")

@pytest.fixture
def mock_directory_structure(tmp_path):
    author_dir = tmp_path / "plato"
    author_dir.mkdir()
    (author_dir / "republic.txt").touch()
    (author_dir / "republic_metadata.json").touch()
    return tmp_path

def test_get_input_files(mock_directory_structure):
    with patch("process_texts.RAW_TEXTS_DIR", mock_directory_structure):
        input_files = get_input_files()
        assert len(input_files) == 1
        assert input_files[0]["author"] == "plato"
        assert input_files[0]["work"] == "republic"

def test_generate_document_id():
    doc = Document(page_content="Test content", metadata={"key": "value"})
    doc_id = generate_document_id(doc)
    assert isinstance(doc_id, str)
    assert len(doc_id) == 32  # MD5 hash length

def test_batch_generator():
    data = list(range(10))
    batches = list(batch_generator(data, 3))
    assert len(batches) == 4
    assert batches == [[0, 1, 2], [3, 4, 5], [6, 7, 8], [9]]

@pytest.fixture
def mock_text_file(tmp_path):
    content = "This is a test file.\nIt has multiple lines.\nBook 1\nContent of book 1\nBook 2\nContent of book 2"
    file = tmp_path / "test.txt"
    file.write_text(content)
    return file

@pytest.fixture
def mock_metadata_file(tmp_path):
    metadata = {
        "author": "Test Author",
        "translator": "Test Translator",
        "work": "Test Work",
        "books": [
            {"number": 1, "title": "Book 1 Title"},
            {"number": 2, "title": "Book 2 Title"}
        ]
    }
    file = tmp_path / "test_metadata.json"
    file.write_text(json.dumps(metadata))
    return file

def test_load_document(mock_text_file, mock_metadata_file):
    text, metadata = load_document(str(mock_text_file), str(mock_metadata_file))
    assert "This is a test file." in text
    assert metadata["author"] == "Test Author"

def test_find_book_boundaries():
    text = "Book 1\nContent 1\nBook 2\nContent 2\nBook 3\nContent 3"
    boundaries = find_book_boundaries(text)
    assert len(boundaries) == 3
    assert boundaries[0]["number"] == 1
    assert boundaries[0]["start_line"] == 2
    assert boundaries[1]["number"] == 2
    assert boundaries[2]["number"] == 3
    assert boundaries[2]["end_line"] == 6

def test_split_document():
    text = "Book 1\nContent of book 1\nMore content\nBook 2\nContent of book 2"
    metadata = {
        "author": "Test Author",
        "translator": "Test Translator",
        "work": "Test Work",
        "books": [
            {"number": 1, "title": "Book 1 Title"},
            {"number": 2, "title": "Book 2 Title"}
        ]
    }
    documents = split_document(text, metadata)
    assert len(documents) > 0
    assert all(isinstance(doc, Document) for doc in documents)
    assert documents[0].metadata["author"] == "Test Author"
    assert "book_number" in documents[0].metadata
    assert "book_title" in documents[0].metadata

if __name__ == "__main__":
    pytest.main()