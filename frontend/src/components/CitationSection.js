import React from 'react';

const CitationSection = ({ citations }) => {
  if (!citations || citations.length === 0) return null;

  return (
    <div>
      <h2 className="text-xl font-bold mb-2">Citations:</h2>
      {citations.map((citation, index) => (
        <div key={index} className="mb-4 p-4 bg-gray-100 rounded">
          <p className="font-semibold">Book {citation.book}, Line {citation.line}</p>
          <p className="mt-2">{citation.text}</p>
        </div>
      ))}
    </div>
  );
};

export default CitationSection;