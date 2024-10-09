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
        <form onSubmit={handleSubmit} className="query-form mt-4">
            <div className="flex">
                <input
                    type="text"
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    placeholder="Ask a philosophical question..."
                    className="query-input flex-grow p-2 border border-gray-300 rounded-l-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                <button type="submit" className="query-submit bg-blue-500 text-white px-4 py-2 rounded-r-md hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500">Ask</button>
            </div>
        </form>
    );
}

export default QueryForm;