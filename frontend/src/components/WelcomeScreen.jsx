import React, { useContext, useState } from 'react';
import { ChatModeContext } from '../context/ChatModeContext';
import { sendChatMessage } from '../api';
import { Send, Building2, Code2, Bot, ChevronRight } from 'lucide-react';

export default function WelcomeScreen() {
  const { switchMode, addMessage, setIsLoading } = useContext(ChatModeContext);
  const [input, setInput] = useState('');

  const handleFreeTextChat = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    const textToSend = input;
    setInput('');

    addMessage({ text: textToSend, sender: 'user', time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) });
    switchMode('uit');
    setIsLoading(true);

    const data = await sendChatMessage(textToSend, 'auto');
    setIsLoading(false);

    if (data) {
      switchMode(data.detected_scope);
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
    // Bỏ 'relative' đi, cấu trúc thành 3 phần rạch ròi bằng Flexbox
    <div className="flex flex-col h-full bg-gradient-to-b from-sky-50 via-white to-blue-50/30">

      {/* 1. Phần Header (Cố định trên cùng) */}
      <div className="flex items-center px-6 py-4 text-blue-900 border-b border-blue-100/50 bg-white/50 backdrop-blur-sm shadow-sm shrink-0">
        <Bot size={22} className="text-blue-600 mr-2" />
        <span className="font-semibold text-base">Khám phá 20 năm UIT & CNPM</span>
      </div>

      {/* 2. Phần Nội dung (Tự động co giãn và cho phép cuộn) */}
      <div className="flex-1 overflow-y-auto px-5 py-10 flex justify-center">
        <div className="w-full max-w-2xl">

          <div className="text-center mb-10">
            <h1 className="text-3xl md:text-4xl leading-tight font-extrabold text-[#0B3B60] mb-4">
              Khám phá 20 năm UIT & Khoa CNPM
            </h1>
            <p className="text-base text-gray-600 px-2 leading-relaxed max-w-lg mx-auto">
              Cùng chatbot khám phá hành trình hình thành và phát triển của UIT và Khoa CNPM qua các dấu mốc.
            </p>

            {/* Ảnh Mascot */}
            {/* <div className="mt-8 mb-4 flex justify-center">
              <img src="/bot-mascot.png" alt="Bot Mascot" className="h-48 object-contain drop-shadow-xl" />
            </div> */}
          </div>

          <p className="text-center text-[#0B3B60] font-bold mb-5 text-[16px]">Bạn muốn khám phá hành trình nào?</p>

          <div className="space-y-4">
            <button
              onClick={() => switchMode('uit')}
              className="w-full flex items-center bg-white border border-blue-100 p-5 rounded-3xl shadow-sm hover:shadow-md transition-all text-left group"
            >
              <div className="bg-[#1D63A5] p-4 rounded-full mr-5 text-white group-hover:scale-105 transition-transform shadow-inner">
                <Building2 size={28} strokeWidth={1.5} />
              </div>
              <div className="flex-1 pr-2">
                <h3 className="font-bold text-[#0B3B60] text-lg mb-1">Hành trình UIT</h3>
                <p className="text-sm text-gray-500 leading-snug">Khám phá lịch sử hình thành, phát triển và thành tựu của UIT.</p>
              </div>
              <ChevronRight size={24} className="text-blue-300" />
            </button>

            <button
              onClick={() => switchMode('cnpm')}
              className="w-full flex items-center bg-white border border-emerald-100 p-5 rounded-3xl shadow-sm hover:shadow-md transition-all text-left group"
            >
              <div className="bg-[#0D8967] p-4 rounded-full mr-5 text-white group-hover:scale-105 transition-transform shadow-inner">
                <Code2 size={28} strokeWidth={1.5} />
              </div>
              <div className="flex-1 pr-2">
                <h3 className="font-bold text-[#0D8967] text-lg mb-1">Hành trình Khoa CNPM</h3>
                <p className="text-sm text-gray-500 leading-snug">Khám phá lịch sử và những dấu ấn của Khoa Công nghệ Phần mềm.</p>
              </div>
              <ChevronRight size={24} className="text-emerald-300" />
            </button>
          </div>
        </div>
      </div>

      {/* 3. Phần Input Chat (Cố định ở dưới cùng, đẩy nội dung lên) */}
      <div className="w-full p-4 bg-white flex justify-center shrink-0 border-t border-gray-100">
        <div className="w-full max-w-2xl">

          {/* KHUNG NỀN MÀU XÁM/TÍM NHẠT BAO QUANH */}
          <div className="bg-[#F4F5F8] p-3.5 rounded-2xl">

            <p className="text-[13px] text-gray-500 mb-2.5 flex items-center gap-1.5 font-medium px-1">
              💡 Hoặc bạn có thể đặt câu hỏi tự do cho chatbot
            </p>

            {/* Dùng flex gap-3 để tách rời Input và Nút Gửi ra */}
            <form onSubmit={handleFreeTextChat} className="flex gap-3">

              <input
                type="text"
                placeholder="Nhập câu hỏi của bạn..."
                className="flex-1 bg-white border border-gray-200/60 rounded-xl py-3 px-4 outline-none focus:border-blue-400 focus:ring-2 focus:ring-blue-100 transition-all text-[15px] shadow-sm text-gray-700"
                value={input}
                onChange={(e) => setInput(e.target.value)}
              />

              {/* Nút gửi hình vuông bo góc, đứng tách biệt */}
              <button
                type="submit"
                disabled={!input.trim()}
                className="bg-[#2B78E4] disabled:bg-gray-300 text-white w-12 h-[46px] shrink-0 flex items-center justify-center rounded-xl hover:bg-blue-600 transition-colors shadow-sm"
              >
                <Send size={18} className="-ml-0.5" />
              </button>

            </form>

          </div>

        </div>
      </div>

    </div>
  );
}