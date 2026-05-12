import React, { useState } from 'react';
import { ThumbsUp, ThumbsDown, Send } from 'lucide-react';
import { sendFeedback } from '../api';

export default function FeedbackButtons({ messageId, themeColor, question, answer }) {
    const [feedback, setFeedback] = useState(null);
    const [showInput, setShowInput] = useState(false);
    const [note, setNote] = useState('');
    const [submitted, setSubmitted] = useState(false);

    // Xử lý khi bấm LIKE
    const handleLike = async () => {
        if (submitted) return;
        setFeedback('like');
        setSubmitted(true);
        if (messageId) {
            await sendFeedback(messageId, 'like', '', question, answer);
        }
    };

    // Xử lý khi bấm DISLIKE (Mở ô nhập liệu)
    const handleDislikeClick = () => {
        if (submitted) return;
        setFeedback('dislike');
        setShowInput(true); // Hiện ô input
    };

    // Xử lý khi bấm Gửi lý do Dislike
    const submitDislikeNote = async () => {
        setShowInput(false);
        setSubmitted(true);
        if (messageId) {
            await sendFeedback(messageId, 'dislike', note, question, answer);
        }
    };

    // Nếu đã gửi xong, hiện lời cảm ơn cho tinh tế
    if (submitted && !showInput) {
        return <div className="text-xs text-gray-400 mt-2 ml-2 italic">✨ Cảm ơn bạn đã góp ý!</div>;
    }

    return (
        <div className="mt-2 ml-2">
            {/* Hai nút Like / Dislike */}
            <div className="flex items-center gap-4 text-gray-400">
                <button
                    onClick={handleLike}
                    className={`hover:${themeColor} transition-colors ${feedback === 'like' ? themeColor : ''}`}
                    title="Câu trả lời hữu ích"
                >
                    <ThumbsUp size={16} />
                </button>

                <button
                    onClick={handleDislikeClick}
                    className={`hover:text-red-500 transition-colors ${feedback === 'dislike' ? 'text-red-500' : ''}`}
                    title="Chưa chính xác"
                >
                    <ThumbsDown size={16} />
                </button>
            </div>

            {/* Ô nhập lý do (Chỉ hiện khi bấm Dislike) */}
            {showInput && (
                <div className="mt-3 flex items-center gap-2 bg-red-50/50 p-1.5 rounded-xl border border-red-100 w-full max-w-sm animate-in fade-in zoom-in duration-200">
                    <input
                        type="text"
                        placeholder="Cho bot biết lý do chưa đúng nhé..."
                        value={note}
                        onChange={(e) => setNote(e.target.value)}
                        onKeyDown={(e) => e.key === 'Enter' && submitDislikeNote()}
                        className="flex-1 bg-transparent outline-none text-[13px] px-2 text-gray-700 placeholder-red-300"
                        autoFocus
                    />
                    <button
                        onClick={submitDislikeNote}
                        className="p-1.5 rounded-lg text-white bg-red-400 hover:bg-red-500 transition-colors shadow-sm"
                    >
                        <Send size={14} className="-ml-0.5" />
                    </button>
                </div>
            )}
        </div>
    );
}