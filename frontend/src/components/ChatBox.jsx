import React, { useContext, useState, useRef, useEffect } from 'react';
import { ChatModeContext } from '../context/ChatModeContext';
import { sendChatMessage } from '../api';
import Message from './Message';

export default function ChatBox({ pal, brand, suggested }) {
  const { mode, messages, addMessage, isLoading, setIsLoading } = useContext(ChatModeContext);
  const [input, setInput] = useState('');
  const scrollRef = useRef(null);

  useEffect(() => {
    if (scrollRef.current) scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
  }, [messages, isLoading]);

  const handleSend = async (q) => {
    if (!q.trim() || isLoading) return;
    setInput('');
    addMessage({ role: 'user', text: q });
    setIsLoading(true);
    const isFirst = messages.filter(m => m.role === 'bot').length === 0;
    const data = await sendChatMessage(q, mode, isFirst);
    setIsLoading(false);
    if (data) {
      addMessage({
        id: data.message_id,
        role: 'bot',
        text: data.answer,
        question: q,
        suggestions: data.suggestions,
        sources: data.sources,
      });
    }
  };

  const hasMessages = messages.length > 0;

  return (
    <section style={{
      background: pal.isDark ? pal.panel : '#ffffff',
      borderRadius: 20,
      border: `1px solid ${pal.accent}${pal.isDark ? '30' : '22'}`,
      minHeight: 580, display: 'flex', flexDirection: 'column', overflow: 'hidden',
      boxShadow: pal.isDark
        ? `0 30px 80px -40px ${pal.accent}80`
        : '0 30px 80px -40px rgba(29,78,216,0.35)',
    }}>
      {/* Panel header */}
      <div style={{
        padding: '14px 22px', display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        borderBottom: `1px solid ${pal.accent}${pal.isDark ? '20' : '15'}`,
        background: pal.isDark ? 'transparent' : pal.soft + '60',
        flexShrink: 0,
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <div style={{ width: 8, height: 8, borderRadius: '50%', background: pal.warm, boxShadow: `0 0 12px ${pal.warm}` }}/>
          <div style={{ fontSize: 13, fontWeight: 600, color: pal.ink }}>{brand.botName}</div>
          <div style={{ fontSize: 11, color: pal.mute, padding: '2px 8px', borderRadius: 99, background: `${pal.accent}15`, border: `1px solid ${pal.accent}30` }}>
            {brand.botBadge}
          </div>
        </div>
        <div style={{ fontSize: 11, color: pal.mute, fontFamily: "'JetBrains Mono', monospace" }}>
          {brand.version}
        </div>
      </div>

      {/* Messages / empty state */}
      <div ref={scrollRef} style={{
        flex: 1, overflowY: 'auto', padding: '28px 28px 8px',
        scrollbarWidth: 'thin', scrollbarColor: `${pal.accent}40 transparent`,
      }}>
        {!hasMessages && (
          <EmptyState pal={pal} mode={mode} suggested={suggested} onAsk={handleSend} />
        )}

        {messages.map((msg, i) => (
          <Message key={i} msg={msg} pal={pal} brand={brand} onChip={handleSend} />
        ))}

        {isLoading && <TypingIndicator pal={pal} />}
      </div>

      {/* Input */}
      <div style={{ padding: '14px 18px 18px', borderTop: `1px solid ${pal.accent}${pal.isDark ? '20' : '15'}`, flexShrink: 0 }}>
        <div style={{
          display: 'flex', alignItems: 'center', gap: 10,
          padding: '6px 6px 6px 16px', borderRadius: 14,
          background: pal.soft, border: `1px solid ${pal.accent}35`,
        }}>
          <input
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && handleSend(input)}
            placeholder={brand.placeholder}
            style={{
              flex: 1, background: 'transparent', border: 'none', outline: 'none',
              color: pal.ink, fontSize: 14, padding: '10px 0', fontFamily: 'inherit',
            }}
          />
          <button onClick={() => handleSend(input)} style={{
            padding: '10px 18px', borderRadius: 10, border: 'none',
            background: `linear-gradient(135deg, ${pal.accent}, ${pal.accent2})`,
            color: '#fff', fontWeight: 600, fontSize: 13, cursor: 'pointer',
            boxShadow: `0 8px 24px -8px ${pal.accent}`,
            display: 'flex', alignItems: 'center', gap: 6, fontFamily: 'inherit',
            transition: 'opacity .15s',
          }}>
            Kể tiếp <span style={{ fontSize: 14 }}>→</span>
          </button>
        </div>
        <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 8, fontSize: 11, color: pal.mute }}>
          <div>↵ Enter để gửi</div>
          <div>{mode === 'uit' ? 'UIT · 2006—2026' : 'Khoa CNPM · 2008—2026'}</div>
        </div>
      </div>
    </section>
  );
}

function EmptyState({ pal, mode, suggested, onAsk }) {
  return (
    <div style={{ textAlign: 'center', padding: '32px 12px 16px' }}>
      <div style={{
        display: 'inline-block', padding: '6px 14px', borderRadius: 99,
        background: `${pal.warm}15`, border: `1px solid ${pal.warm}40`, color: pal.warm,
        fontSize: 11, letterSpacing: '0.2em', fontWeight: 700, marginBottom: 20,
      }}>BẮT ĐẦU HÀNH TRÌNH</div>

      <div style={{ fontFamily: "'Fraunces', serif", fontSize: 22, lineHeight: 1.4, color: pal.ink, maxWidth: 500, margin: '0 auto 8px', letterSpacing: '-0.01em' }}>
        "Mỗi câu hỏi của bạn sẽ{' '}
        <em style={{ color: pal.warm, fontStyle: 'italic' }}>mở ra một chương</em>
        {' '}trong cuốn sách {mode === 'uit' ? '20' : '18'} năm."
      </div>
      <div style={{ fontSize: 13, color: pal.mute, marginBottom: 24 }}>
        Chọn một chủ đề bên dưới, hoặc tự gõ câu hỏi của bạn.
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 10, maxWidth: 560, margin: '0 auto', textAlign: 'left' }}>
        {suggested.map((s, i) => (
          <PromptCard key={i} s={s} pal={pal} onClick={() => onAsk(s.q)} />
        ))}
      </div>
    </div>
  );
}

function PromptCard({ s, pal, onClick }) {
  const [hovered, setHovered] = React.useState(false);
  return (
    <button onClick={onClick}
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
      style={{
        display: 'flex', alignItems: 'center', gap: 12,
        padding: '14px 16px', borderRadius: 12,
        background: pal.soft,
        border: `1px solid ${hovered ? pal.warm : pal.accent + '25'}`,
        color: pal.ink, fontSize: 13.5, cursor: 'pointer',
        textAlign: 'left', fontFamily: 'inherit',
        transform: hovered ? 'translateY(-1px)' : 'translateY(0)',
        transition: 'all .2s',
      }}>
      <div style={{ width: 32, height: 32, borderRadius: 8, background: `${pal.accent}20`, color: pal.warm, display: 'grid', placeItems: 'center', fontSize: 14, flexShrink: 0, fontWeight: 600 }}>
        {s.icon}
      </div>
      <div style={{ lineHeight: 1.35 }}>{s.label}</div>
    </button>
  );
}

function TypingIndicator({ pal }) {
  return (
    <div style={{ display: 'flex', gap: 12, marginBottom: 18, alignItems: 'center' }}>
      <div style={{
        width: 36, height: 36, borderRadius: '50%',
        background: `conic-gradient(from 200deg, ${pal.accent}, ${pal.gold}, ${pal.accent2}, ${pal.accent})`,
        animation: 'spin 3s linear infinite',
        display: 'grid', placeItems: 'center', flexShrink: 0,
      }}>
        <div style={{ width: 30, height: 30, borderRadius: '50%', background: pal.panel }}/>
      </div>
      <div style={{ display: 'flex', gap: 5, padding: '10px 16px', borderRadius: 16, background: pal.panel, border: `1px solid ${pal.accent}25` }}>
        {[0, 1, 2].map(i => (
          <div key={i} style={{
            width: 6, height: 6, borderRadius: '50%', background: pal.accent,
            animation: `bounce 1.2s ${i * 0.15}s infinite ease-in-out`,
          }}/>
        ))}
        <div style={{ marginLeft: 6, fontSize: 12, color: pal.mute, alignSelf: 'center', fontStyle: 'italic' }}>
          đang nhớ lại câu chuyện…
        </div>
      </div>
    </div>
  );
}
