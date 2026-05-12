import React from 'react';
import { Bot, ExternalLink } from 'lucide-react';
import FeedbackButtons from './FeedbackButtons'; // Import component vừa tạo

export default function Message({ msg, themeColor }) {
    const isUser = msg.sender === 'user';

    // ----- UI CHO TIN NHẮN CỦA USER -----
    if (isUser) {
        return (
            <div className="flex justify-end mb-4">
                <div className="max-w-[80%] bg-blue-100 text-gray-800 rounded-2xl rounded-tr-sm px-4 py-2 shadow-sm">
                    <p className="text-sm">{msg.text}</p>
                    <span className="text-[10px] text-gray-500 block text-right mt-1">{msg.time}</span>
                </div>
            </div>
        );
    }

    // ----- UI CHO TIN NHẮN CỦA BOT -----
    // Lấy màu nền nhạt cho avatar bot dựa theo theme hiện tại
    const bgSoftColor = themeColor.includes('blue') ? 'bg-blue-100' : 'bg-emerald-100';

    return (
        <div className="flex justify-start mb-6">
            {/* Bot Avatar */}
            <div className={`w-8 h-8 rounded-full flex items-center justify-center mr-2 shrink-0 mt-1 ${bgSoftColor}`}>
                <Bot size={18} className={themeColor} />
            </div>

            {/* Bot Content */}
            <div className="max-w-[85%]">
                <div className="bg-white rounded-2xl rounded-tl-sm px-4 py-3 shadow-sm border border-gray-100">
                    <p className="text-sm text-gray-700 whitespace-pre-wrap leading-relaxed">{msg.text}</p>

                    {/* Render Nguồn trích dẫn (Nếu có) */}
                    {msg.sources && msg.sources.length > 0 && (
                        <div className="mt-3 pt-2 border-t border-gray-100">
                            <p className="text-xs font-semibold text-gray-400 mb-1 flex items-center">
                                <ExternalLink size={12} className="mr-1" /> Nguồn tham khảo:
                            </p>
                            <ul className="space-y-1">
                                {msg.sources.map((src, i) => (
                                    <li key={i}>
                                        <a href={src.url} target="_blank" rel="noopener noreferrer"
                                            className={`text-xs hover:underline flex items-center gap-1 ${themeColor}`}>
                                            - {src.url.replace(/^https?:\/\//, '')}
                                        </a>
                                    </li>
                                ))}
                            </ul>
                        </div>
                    )}
                    <span className="text-[10px] text-gray-400 block mt-2">{msg.time}</span>
                </div>

                {/* NHÚNG COMPONENT FEEDBACK VÀO ĐÂY */}
                {msg.id && (
                    <FeedbackButtons
                        messageId={msg.id}
                        themeColor={themeColor}
                        question={msg.question || ""}
                        answer={msg.text || ""}
                    />
                )}
            </div>
        </div>
    );
}