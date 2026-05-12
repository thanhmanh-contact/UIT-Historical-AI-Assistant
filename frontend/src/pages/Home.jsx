import React, { useContext } from 'react';
import { ChatModeContext } from '../context/ChatModeContext';
import WelcomeScreen from '../components/WelcomeScreen';
import ChatBox from '../components/ChatBox';

export default function Home() {
  const { mode } = useContext(ChatModeContext);

  return (
    // w-full và h-[100dvh] giúp tràn viền 100% màn hình thiết bị
    <div className="w-full h-[100dvh] bg-white overflow-hidden flex flex-col">
      {mode === 'welcome' ? <WelcomeScreen /> : <ChatBox />}
    </div>
  );
}