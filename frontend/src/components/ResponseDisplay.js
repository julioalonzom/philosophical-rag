import React from 'react';

const ResponseDisplay = ({ response }) => {
  if (!response) return null;

  return (
    <div className="mb-4">
      <h2 className="text-xl font-bold mb-2">Response:</h2>
      <p className="p-4 bg-gray-100 rounded">{response}</p>
    </div>
  );
};

export default ResponseDisplay;