import React, { lazy, Suspense } from 'react';
import { useChat } from './useChat';
import ErrorBoundary from './components/ErrorBoundary';
import './App.css';

const QueryForm = lazy(() => import('./components/QueryForm'));
const ChatMessage = lazy(() => import('./components/ChatMessage'));

function App() {
  const { messages, isLoading, handleSubmit } = useChat();

  return (
    <ErrorBoundary>
      <div className="chat-container max-w-4xl mx-auto p-4">
        <h1 className="chat-title text-3xl font-bold mb-6 text-center">Philosophical RAG: Plato's Republic</h1>
        <Suspense fallback={<div>Loading...</div>}>
          <div className="chat-messages space-y-4 mb-4">
            {messages.map((message, index) => (
              <ChatMessage key={index} message={message} />
            ))}
            {isLoading && <div className="loading-indicator text-center text-gray-500">Processing your query...</div>}
          </div>
          <QueryForm onSubmit={handleSubmit} />
        </Suspense>
      </div>
    </ErrorBoundary>
  );
}

export default App;