import React from 'react';
import Home from './pages/Home';
import { ChatModeProvider } from './context/ChatModeContext';

function App() {
  return (
    <ChatModeProvider>
      <Home />
    </ChatModeProvider>
  );
}

export default App;