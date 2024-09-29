import React, { useState } from 'react';
import QueryForm from './components/QueryForm';
import ResponseDisplay from './components/ResponseDisplay';
import CitationSection from './components/CitationSection';
import { submitQuery } from './api';

function App() {
  const [response, setResponse] = useState(null);
  const [citations, setCitations] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (query) => {
    setIsLoading(true);
    setError(null);
    try {
      console.log('Submitting query:', query);
      const result = await submitQuery(query);
      console.log('Received result:', result);
      setResponse(result.response);
      setCitations(result.citations);
    } catch (err) {
      console.error('Error:', err);
      setError('An error occurred while processing your query. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-4">Philosophical RAG: Plato's Republic</h1>
      <QueryForm onSubmit={handleSubmit} />
      {isLoading && <p className="text-gray-600">Processing your query...</p>}
      {error && <p className="text-red-500">{error}</p>}
      <ResponseDisplay response={response} />
      <CitationSection citations={citations} />
    </div>
  );
}

export default App;