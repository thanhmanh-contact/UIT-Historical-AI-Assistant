import React, { useState } from 'react';
import { sendFeedback } from '../api';

export default function FeedbackButtons({ messageId, accentColor, question, answer }) {
  const [feedback, setFeedback]   = useState(null);
  const [showInput, setShowInput] = useState(false);
  const [note, setNote]           = useState('');
  const [submitted, setSubmitted] = useState(false);

  const handleLike = async () => {
    if (submitted) return;
    setFeedback('like');
    setSubmitted(true);
    if (messageId) await sendFeedback(messageId, 'like', '', question, answer);
  };

  const handleDislikeClick = () => {
    if (submitted) return;
    setFeedback('dislike');
    setShowInput(true);
  };

  const submitDislikeNote = async () => {
    setShowInput(false);
    setSubmitted(true);
    if (messageId) await sendFeedback(messageId, 'dislike', note, question, answer);
  };

  if (submitted && !showInput) {
    return (
      <div style={{ fontSize: 12, color: '#9ca3af', marginTop: 8, marginLeft: 2, fontStyle: 'italic' }}>
        Cảm ơn bạn đã góp ý!
      </div>
    );
  }

  return (
    <div style={{ marginTop: 8, marginLeft: 2 }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
        <TextButton
          onClick={handleLike}
          active={feedback === 'like'}
          activeColor={accentColor}
          title="Câu trả lời hữu ích"
          label="Hữu ích"
        />
        <TextButton
          onClick={handleDislikeClick}
          active={feedback === 'dislike'}
          activeColor="#ef4444"
          hoverColor="#ef4444"
          title="Chưa chính xác"
          label="Chưa đúng"
        />
      </div>

      {showInput && (
        <div style={{
          marginTop: 10, display: 'flex', alignItems: 'center', gap: 8,
          background: 'rgba(254,226,226,0.5)', padding: '6px 10px',
          borderRadius: 12, border: '1px solid #fecaca',
          maxWidth: 360, animation: 'fadeUp .2s both',
        }}>
          <input
            type="text"
            placeholder="Cho bot biết lý do chưa đúng nhé..."
            value={note}
            onChange={(e) => setNote(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && submitDislikeNote()}
            autoFocus
            style={{
              flex: 1, background: 'transparent', border: 'none', outline: 'none',
              fontSize: 13, color: '#374151', fontFamily: 'inherit',
            }}
          />
          <button
            onClick={submitDislikeNote}
            style={{
              padding: '5px 10px', borderRadius: 8, border: 'none',
              background: '#f87171', color: '#fff', cursor: 'pointer',
              fontSize: 12, fontWeight: 600, fontFamily: 'inherit',
              transition: 'background .15s',
            }}
          >
            Gửi
          </button>
        </div>
      )}
    </div>
  );
}

function TextButton({ label, onClick, active, activeColor, hoverColor, title }) {
  const [hovered, setHovered] = useState(false);
  const color = active ? activeColor : hovered ? (hoverColor || activeColor) : '#9ca3af';
  return (
    <button
      onClick={onClick}
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
      title={title}
      style={{
        background: 'transparent', border: `1px solid ${color}60`,
        cursor: 'pointer', color, padding: '3px 10px',
        borderRadius: 6, fontSize: 12, fontFamily: 'inherit',
        transition: 'all .15s',
      }}
    >
      {label}
    </button>
  );
}
