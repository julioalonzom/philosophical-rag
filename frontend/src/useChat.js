import { useState } from 'react';
import { submitQuery } from './api';

export function useChat() {
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (query) => {
    setIsLoading(true);
    setMessages(prevMessages => [...prevMessages, { type: 'user', content: query }]);

    try {
      const result = await submitQuery(query);
      setMessages(prevMessages => [
        ...prevMessages,
        {
          type: 'bot',
          content: result.response,
          citations: result.citations
        }
      ]);
    } catch (error) {
      console.error('Error submitting query:', error);
      setMessages(prevMessages => [
        ...prevMessages,
        {
          type: 'bot',
          content: 'Sorry, an error occurred while processing your query.'
        }
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return { messages, isLoading, handleSubmit };
}