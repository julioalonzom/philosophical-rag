import React, { useState } from 'react';

function QueryForm({ onSubmit }) {
    const [query, setQuery] = useState('');

    const handleSubmit = (e) => {
        e.preventDefault();
        if (query.trim()) {
            onSubmit(query);
            setQuery('');
        }
    };

    return (
        <form onSubmit={handleSubmit} className="query-form">
            <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Ask a philosophical question..."
                className="query-input"
            />
            <button type="submit" className="query-submit">Ask</button>
        </form>
    );
}

export default QueryForm;