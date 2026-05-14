import React from 'react';
import { Calendar, Trophy, GraduationCap, RefreshCw, ChevronRight } from 'lucide-react';

export default function SuggestionButtons({ suggestions, onSelect, isUIT }) {
    const themeText = isUIT ? 'text-blue-600' : 'text-emerald-600';
    const themeBgHover = isUIT ? 'hover:bg-blue-50 hover:border-blue-200' : 'hover:bg-emerald-50 hover:border-emerald-200';

    // Logic chọn Icon động dựa vào text
    const getIcon = (text) => {
        const lower = text.toLowerCase();
        if (lower.includes('dấu mốc') || lower.includes('lịch sử')) return <Calendar size={16} className={themeText} />;
        if (lower.includes('thành tựu')) return <Trophy size={16} className="text-yellow-500" />;
        if (lower.includes('đời sống') || lower.includes('sinh viên')) return <GraduationCap size={16} className="text-gray-700" />;
        if (lower.includes('chuyển sang')) return <RefreshCw size={16} className={themeText} />;
        return <ChevronRight size={16} className={themeText} />;
    };

    return (
        <div className="mx-4 mb-4 p-3 bg-white/60 backdrop-blur-sm border border-gray-200 rounded-2xl shadow-sm">
            <p className={`text-sm font-semibold mb-3 ${themeText}`}>Bạn muốn khám phá tiếp?</p>

            <div className="grid grid-cols-2 gap-2">
                {suggestions.map((sug, idx) => (
                    <button
                        key={idx}
                        onClick={() => onSelect(sug)}
                        className={`flex items-center gap-2 bg-white border border-gray-100 rounded-xl px-3 py-2 text-[13px] font-medium text-gray-700 text-left shadow-sm transition-all duration-200 ${themeBgHover}`}
                    >
                        <span className="shrink-0">{getIcon(sug)}</span>
                        <span className="flex-1 truncate">{sug}</span>
                    </button>
                ))}
            </div>
        </div>
    );
}