import React, { createContext, useState } from 'react';

export const ChatModeContext = createContext();

export const ChatModeProvider = ({ children }) => {
  const [mode, setMode] = useState('uit');
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [focusYear, setFocusYear] = useState('2006');

  const switchMode = (newMode) => {
    if (newMode === mode) return;
    setMode(newMode);
    setMessages([]);
    setIsLoading(false);
    setFocusYear(newMode === 'uit' ? '2006' : '2008');
  };

  const addMessage = (msg) => {
    setMessages((prev) => [...prev, msg]);
  };

  return (
    <ChatModeContext.Provider value={{
      mode, switchMode,
      messages, addMessage,
      isLoading, setIsLoading,
      focusYear, setFocusYear,
    }}>
      {children}
    </ChatModeContext.Provider>
  );
};
