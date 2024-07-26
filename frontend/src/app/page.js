// pages/index.js
'use client';
import { useState, useRef, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import { sendChatQuery } from './Api/rout';

// Define variables for styles
const styles = {
  fontSize: {
    small: 'text-sm',
    medium: 'text-base',
    large: 'text-lg',
    xlarge: 'text-2xl',
  },
  bgColor: {
    primary: 'bg-blue-700',
    secondary: 'bg-gray-50',
    tertiary: 'bg-gray-100',
  },
  borderColor: {
    primary: 'border-blue-500',
  },
  textColor: {
    primary: 'text-white',
    secondary: 'text-gray-800',
    accent: 'text-blue-600',
  },
};

export default function Home() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const chatContainerRef = useRef(null);

  useEffect(() => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
    }
  }, [messages]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (input.trim()) {
      setMessages(prev => [...prev, { text: input, sender: 'user' }]);
      setInput('');
      setIsLoading(true);
      try {
        const result = await sendChatQuery(input.trim());
        setMessages(prev => [...prev, { text: result.response, sender: 'bot' }]);
      } catch (error) {
        console.error('Error:', error);
        setMessages(prev => [...prev, { text: "Sorry, I couldn't process your request. Please try again.", sender: 'bot' }]);
      } finally {
        setIsLoading(false);
      }
    }
  };

  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-100">
      <div className={`w-full max-w-4xl h-[calc(100vh-2rem)] bg-white rounded-lg shadow-lg flex flex-col overflow-hidden`}>
        <div className={`${styles.bgColor.primary} ${styles.textColor.primary} p-4`}>
          <h1 className={`${styles.fontSize.xlarge} font-bold text-center`}>AI Travel Assistant</h1>
        </div>
        <div
          ref={chatContainerRef}
          className={`flex-grow overflow-y-auto p-6 space-y-4 ${styles.bgColor.secondary} `}
        >
          {messages.map((message, index) => (
            <div key={index} className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div className={`flex items-end space-x-2 ${message.sender === 'user' ? 'flex-row-reverse' : 'flex-row'}`}>
                <div className="w-8 h-8 rounded-full overflow-hidden flex-shrink-0">
                  <img 
                    src={message.sender === 'user' ? '/Images/user-avatar.png' : '/Images/bot-avatar.png'} 
                    alt={`${message.sender} avatar`}
                    className="w-full h-full object-cover"
                  />
                </div>
                <div className={`rounded-lg p-2 max-w-[80%] border ${
                  message.sender === 'user' ? 'bg-blue-500 text-white' : 'bg-white text-gray-800'
                } shadow-md ${styles.fontSize.small}`}>
                  <ReactMarkdown>{message.text}</ReactMarkdown>
                </div>
              </div>
            </div>
          ))}
          {isLoading && (
            <div className="flex justify-start">
              <div className={`bg-white text-gray-800 rounded-lg p-4 shadow-md animate-pulse ${styles.fontSize.medium}`}>
                <div className="flex space-x-2">
                  <div className="w-3 h-3 bg-gray-400 rounded-full animate-bounce"></div>
                  <div className="w-3 h-3 bg-gray-400 rounded-full animate-bounce delay-75"></div>
                  <div className="w-3 h-3 bg-gray-400 rounded-full animate-bounce delay-150"></div>
                </div>
              </div>
            </div>
          )}
        </div>
        <div className={`${styles.bgColor.tertiary} p-4 border-t ${styles.borderColor.primary}`}>
          <form onSubmit={handleSubmit} className="flex space-x-2">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask about tourist spots or anything else..."
              className={`flex-grow p-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all duration-200 ${styles.fontSize.medium}`}
              disabled={isLoading}
            />
            <button
              type="submit"
              className={`px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all duration-200 disabled:bg-blue-300 disabled:cursor-not-allowed ${styles.fontSize.medium}`}
              disabled={isLoading}
            >
              Send
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
