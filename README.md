# Philosophical RAG

## Description

Philosophical RAG is a Retrieval-Augmented Generation system designed to facilitate deep exploration and analysis of philosophical texts, starting with Plato's Republic. This project combines natural language processing, machine learning, and information retrieval techniques to provide intelligent, context-aware responses to user queries about philosophical concepts and ideas.

## Features

- Text preprocessing and chunking of philosophical texts
- Local embedding generation using HuggingFace models
- Efficient vector storage and retrieval with Chroma DB
- Django backend for API endpoints
- (Planned) React frontend for user interaction

## Project Structure

```
philosophical_rag/
├── backend/
│   ├── config/
│   ├── rag_app/
│   ├── rag_core/
│   └── manage.py
├── data/
│   ├── raw_texts/
│   │   └── plato/
│   └── processed_texts/
│       └── plato/
├── scripts/
├── .gitignore
├── README.md
└── requirements.txt
```

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/philosophical-rag.git
   cd philosophical-rag
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   Create a `.env` file in the `backend/config/` directory and add necessary variables (e.g., `SECRET_KEY` for Django).

## Usage

1. Prepare the text:
   Place the text file (e.g., `republic.txt`) in `data/raw_texts/plato/` along with its metadata file.

2. Process the text:
   ```
   python scripts/process_text.py
   ```

3. Run the Django development server:
   ```
   cd backend
   python manage.py runserver
   ```

4. (Coming soon) Start the React frontend.

## API Endpoints

- `/api/query/`: POST endpoint for submitting queries about the philosophical text.

## Development

- Backend: Django (Python)
- Frontend (Planned): React
- Database: SQLite (development), PostgreSQL (production)
- Vector Store: Chroma

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgements

- Plato's Republic text sourced from [Project Gutenberg](https://www.gutenberg.org/)
- Inspired by advancements in RAG systems and NLP technologies

## Contact

Your Name - j.c.alonzo.muller@gmail.com

Project Link: [https://github.com/yourusername/philosophical-rag](https://github.com/yourusername/philosophical-rag)
