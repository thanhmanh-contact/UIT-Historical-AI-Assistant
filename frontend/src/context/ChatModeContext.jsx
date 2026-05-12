import React, { createContext, useState } from 'react';

export const ChatModeContext = createContext();

export const ChatModeProvider = ({ children }) => {
  // mode có thể là: 'welcome', 'uit', 'cnpm'
  const [mode, setMode] = useState('welcome'); 
  const [messages, setMessages] = useState([]);
  const[isLoading, setIsLoading] = useState(false);

  const switchMode = (newMode) => {
    setMode(newMode);
    // Reset tin nhắn khi đổi nhánh (Tuỳ logic của em, có thể giữ lại)
    if (newMode === 'welcome') setMessages([]); 
  };

  const addMessage = (msg) => {
    setMessages((prev) => [...prev, msg]);
  };

  return (
    <ChatModeContext.Provider value={{ mode, switchMode, messages, addMessage, isLoading, setIsLoading }}>
      {children}
    </ChatModeContext.Provider>
  );
};