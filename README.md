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

# Philosophical RAG

# Philosophical RAG: Plato's Republic

## Backend Setup

... (keep existing backend setup instructions)

## Frontend Setup

1. Navigate to the frontend directory:
   ```
   cd frontend
   ```

2. Install dependencies:
   ```
   npm install
   ```

3. Create a `.env` file in the frontend directory and add:
   ```
   REACT_APP_API_BASE_URL=http://localhost:8000/api
   ```

4. Start the development server:
   ```
   npm start
   ```

5. The React app will be available at `http://localhost:3000`

## Running the Application

1. Start the Django backend server (from the `backend` directory):
   ```
   python manage.py runserver
   ```

2. In a separate terminal, start the React frontend server (from the `frontend` directory):
   ```
   npm start
   ```

3. Open your browser and navigate to `http://localhost:3000` to use the application.

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
