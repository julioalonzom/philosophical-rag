import React, { lazy, Suspense, useState } from 'react';
import { useChat } from './useChat';
import ErrorBoundary from './components/ErrorBoundary';
import './App.css';

const QueryForm = lazy(() => import('./components/QueryForm'));
const ChatMessage = lazy(() => import('./components/ChatMessage'));

function App() {
  const { messages, isLoading, handleSubmit } = useChat();
  const [user, setUser] = useState(null);

  const handleLogin = () => {
    // Implement login logic here
    setUser({ name: 'John Doe', tier: 'free' }); // Example user object
  };

  const handleLogout = () => {
    setUser(null);
  };

  return (
    <ErrorBoundary>
      <div className="min-h-screen bg-gray-100">
        <nav className="bg-blue-500 p-4">
          <div className="max-w-4xl mx-auto flex justify-between items-center">
            <h1 className="text-white text-2xl font-bold">Philosophical RAG</h1>
            {user ? (
              <div className="text-white">
                Welcome, {user.name} ({user.tier} tier) |{' '}
                <button onClick={handleLogout} className="underline">Logout</button>
              </div>
            ) : (
              <button onClick={handleLogin} className="bg-white text-blue-500 px-4 py-2 rounded">Login</button>
            )}
          </div>
        </nav>
        <div className="chat-container max-w-4xl mx-auto p-4">
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
      </div>
    </ErrorBoundary>
  );
}

export default App;