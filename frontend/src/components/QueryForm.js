import React, { useState } from 'react';
import axios from 'axios';

function QueryForm() {
    const [query, setQuery] = useState('');
    const [response, setResponse] = useState(null);

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            const result = await axios.post('/api/query/', { query });
            setResponse(result.data);
        } catch (error) {
            console.error('Error querying the RAG engine:', error);
        }
    };

    return (
        <div>
            <form onSubmit={handleSubmit}>
                <input
                    type="text"
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    placeholder="Enter your philosophical question"
                />
                <button type="submit">Ask</button>
            </form>
            {response && (
                <div>
                    <h3>Answer:</h3>
                    <p>{response.response}</p>
                    <h3>Citations:</h3>
                    <ul>
                        {response.citations.map((citation, index) => (
                            <li key={index}>
                                Book {citation.book_number}, {citation.book_title}: 
                                Lines {citation.start_line}-{citation.end_line}
                                <p>{citation.content.substring(0, 100)}...</p>
                            </li>
                        ))}
                    </ul>
                </div>
            )}
        </div>
    );
}

export default QueryForm;