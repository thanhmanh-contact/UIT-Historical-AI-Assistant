import React, { useContext, useState, useRef, useEffect } from 'react';
import { ChatModeContext } from '../context/ChatModeContext';
import { sendChatMessage } from '../api';
import Message from './Message';
import SuggestionButtons from './SuggestionButtons';
import { ArrowLeft, Send, Bot } from 'lucide-react';

export default function ChatBox() {
  const { mode, switchMode, messages, addMessage, isLoading, setIsLoading } = useContext(ChatModeContext);
  const [input, setInput] = useState('');
  const messagesEndRef = useRef(null);

  // Auto scroll xuống cuối
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Cấu hình màu sắc theo Mode
  const isUIT = mode === 'uit';
  const themeColor = isUIT ? 'bg-blue-600' : 'bg-emerald-600';
  const title = isUIT ? 'Hành trình UIT' : 'Hành trình Khoa CNPM';

  const handleSend = async (textToSend) => {
    if (!textToSend.trim()) return;

    setInput('');
    addMessage({ text: textToSend, sender: 'user', time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) });

    setIsLoading(true);
    const data = await sendChatMessage(textToSend, mode); // Gửi kèm mode hiện tại
    setIsLoading(false);

    if (data) {
      addMessage({
        id: data.message_id,
        text: data.answer,
        sender: 'bot',
        question: textToSend,
        suggestions: data.suggestions,
        sources: data.sources,
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      });
    }
  };

  return (
    <div className="flex flex-col h-full bg-gray-50">
      {/* Header */}
      <div className={`${themeColor} text-white px-4 py-3 flex items-center shadow-md`}>
        <button onClick={() => switchMode('welcome')} className="mr-3 hover:bg-white/20 p-1 rounded-full">
          <ArrowLeft size={20} />
        </button>
        <div className="bg-white p-1 rounded-full mr-2">
          <Bot size={20} className={isUIT ? "text-blue-600" : "text-emerald-600"} />
        </div>
        <h2 className="font-semibold">{title}</h2>
      </div>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {/* Câu chào mừng */}
        {messages.length === 0 && (
          <div className="text-center text-gray-500 text-sm mt-4">
            Chào mừng bạn đến với {title}. Hãy đặt câu hỏi hoặc chọn gợi ý bên dưới nhé!
          </div>
        )}

        {messages.map((msg, idx) => (
          <Message key={idx} msg={msg} themeColor={isUIT ? 'text-blue-600' : 'text-emerald-600'} />
        ))}

        {isLoading && (
          <div className="flex text-gray-500 items-center"><Bot size={16} className="mr-2 animate-bounce" /> Đang suy nghĩ...</div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Suggestions Box (Nếu có) */}
      {messages.length > 0 && messages[messages.length - 1].suggestions && (
        <SuggestionButtons
          suggestions={messages[messages.length - 1].suggestions}
          onSelect={(text) => handleSend(text)}
          isUIT={isUIT}
        />
      )}

      {/* Input */}
      <div className="p-4 bg-white border-t">
        <form onSubmit={(e) => { e.preventDefault(); handleSend(input); }} className="flex relative">
          <input
            type="text"
            maxLength={500}
            placeholder="Nhập câu hỏi của bạn..."
            className="flex-1 border border-gray-300 rounded-full py-3 px-4 pr-12 outline-none focus:border-blue-500"
            value={input}
            onChange={(e) => setInput(e.target.value)}
          />
          <button type="submit" className={`absolute right-1 top-1 bottom-1 ${themeColor} text-white p-2 rounded-full hover:opacity-80`}>
            <Send size={18} />
          </button>
        </form>
      </div>
    </div>
  );
}