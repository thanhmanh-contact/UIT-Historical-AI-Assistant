import React, { useContext } from 'react';
import { ChatModeContext } from '../context/ChatModeContext';
import { sendChatMessage } from '../api';

export default function Timeline({ pal, brand, timeline }) {
  const { mode, focusYear, setFocusYear, addMessage, setIsLoading } = useContext(ChatModeContext);

  const handlePick = async (item) => {
    setFocusYear(item.year);
    const q = `Hãy kể câu chuyện năm ${item.year} — "${item.title}".`;
    addMessage({ role: 'user', text: q });
    setIsLoading(true);
    const data = await sendChatMessage(q, mode);
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

  return (
    <aside style={{
      background: pal.isDark ? pal.panel : '#ffffff',
      borderRadius: 20, padding: '18px 16px 20px',
      border: `1px solid ${pal.accent}${pal.isDark ? '30' : '22'}`,
      boxShadow: pal.isDark ? 'none' : '0 20px 60px -30px rgba(29,78,216,0.18)',
      display: 'flex', flexDirection: 'column',
      position: 'sticky', top: 22,
      maxHeight: 'calc(100vh - 44px)',
      overflowY: 'auto',
    }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 14, padding: '0 8px' }}>
        <div>
          <div style={{ fontSize: 11, color: pal.warm, letterSpacing: '0.2em', fontWeight: 700 }}>HÀNH TRÌNH</div>
          <div style={{ fontFamily: "'Fraunces', serif", fontSize: 17, marginTop: 2, color: pal.ink }}>{brand.timelineTitle}</div>
        </div>
        <div style={{ fontSize: 11, fontFamily: "'JetBrains Mono', monospace", color: pal.mute, padding: '3px 8px', borderRadius: 6, background: `${pal.accent}15` }}>
          {focusYear}
        </div>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: 0, position: 'relative', flex: 1 }}>
        <div style={{
          position: 'absolute', left: 11, top: 6, bottom: 6, width: 1,
          background: `linear-gradient(to bottom, transparent, ${pal.accent}80, ${pal.gold}, ${pal.accent}80, transparent)`,
        }} />
        {timeline.map((t) => {
          const active = t.year === focusYear;
          return (
            <div key={t.year} onClick={() => handlePick(t)} style={{
              display: 'grid', gridTemplateColumns: '24px 1fr', gap: 14,
              padding: '10px 4px 10px 0', cursor: 'default', position: 'relative',
              opacity: active ? 1 : (pal.isDark ? 0.72 : 0.85),
              transition: 'opacity .25s',
            }}>
              <div style={{ position: 'relative', height: 24, display: 'grid', placeItems: 'center' }}>
                <div style={{
                  width: active ? 14 : 8, height: active ? 14 : 8, borderRadius: '50%',
                  background: active ? pal.gold : pal.accent,
                  boxShadow: active
                    ? `0 0 0 4px ${pal.gold}25, 0 0 18px ${pal.gold}80`
                    : `0 0 0 3px ${pal.accent}20`,
                  transition: 'all .3s',
                }} />
              </div>
              <div>
                <div style={{ display: 'flex', alignItems: 'baseline', gap: 10 }}>
                  <div style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: 13, color: active ? pal.gold : pal.accent2, letterSpacing: '0.08em', fontWeight: 600 }}>
                    {t.year}
                  </div>
                  <div style={{ fontSize: 13, color: pal.ink, fontWeight: 500 }}>{t.title}</div>
                </div>
                <div style={{ fontSize: 12, color: pal.mute, lineHeight: 1.5, marginTop: 3 }}>{t.body}</div>
              </div>
            </div>
          );
        })}
      </div>
    </aside>
  );
}
