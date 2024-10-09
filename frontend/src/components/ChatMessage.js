import React, { useState } from 'react';

const ChatMessage = React.memo(({ message }) => {
  const [showCitations, setShowCitations] = useState(false);

  return (
    <div className={`chat-message ${message.type} mb-4 p-4 rounded-lg ${message.type === 'user' ? 'bg-blue-100' : 'bg-green-100'}`}>
      <div className="message-content text-lg mb-2">{message.content}</div>
      {message.citations && message.citations.length > 0 && (
        <div className="citations mt-2">
          <button
            onClick={() => setShowCitations(!showCitations)}
            className="text-blue-600 hover:text-blue-800 font-semibold focus:outline-none"
          >
            {showCitations ? 'Hide Citations' : 'Show Citations'}
          </button>
          {showCitations && (
            <div className="mt-2 space-y-2">
              {message.citations.map((citation, index) => (
                <div key={index} className="citation bg-white p-3 rounded-md shadow-sm">
                  <p className="font-semibold text-sm text-gray-600">
                    {citation.author}, {citation.work}
                  </p>
                  <p className="text-sm text-gray-500">
                    Section: {citation.section}, Lines {citation.start_line}-{citation.end_line}
                  </p>
                  <p className="mt-1 text-sm">{citation.content}</p>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
});

export default ChatMessage;