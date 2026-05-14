import React, { useContext } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import FeedbackButtons from './FeedbackButtons';
import { ChatModeContext } from '../context/ChatModeContext';

// react-markdown v10: code không còn prop `inline`, phân biệt qua className
const mdComponents = (ink) => ({
  p: ({ children }) => <p style={{ margin: '0 0 8px', lineHeight: 1.75 }}>{children}</p>,
  ul: ({ children }) => <ul style={{ margin: '4px 0 8px', paddingLeft: 20 }}>{children}</ul>,
  ol: ({ children }) => <ol style={{ margin: '4px 0 8px', paddingLeft: 20 }}>{children}</ol>,
  li: ({ children }) => <li style={{ marginBottom: 4, lineHeight: 1.65 }}>{children}</li>,
  strong: ({ children }) => <strong style={{ fontWeight: 700 }}>{children}</strong>,
  em: ({ children }) => <em style={{ fontStyle: 'italic' }}>{children}</em>,
  code: ({ className, children }) => {
    const isBlock = !!className; // có className "language-*" → là block
    return isBlock
      ? (
        <pre style={{ background: 'rgba(0,0,0,0.08)', padding: '10px 14px', borderRadius: 8, overflowX: 'auto', fontSize: 13, fontFamily: "'JetBrains Mono', monospace", margin: '6px 0' }}>
          <code>{children}</code>
        </pre>
      )
      : (
        <code style={{ background: 'rgba(0,0,0,0.08)', padding: '1px 5px', borderRadius: 4, fontSize: 13, fontFamily: "'JetBrains Mono', monospace" }}>
          {children}
        </code>
      );
  },
  blockquote: ({ children }) => (
    <blockquote style={{ borderLeft: '3px solid #999', paddingLeft: 12, margin: '6px 0', color: '#777', fontStyle: 'italic' }}>
      {children}
    </blockquote>
  ),
  h1: ({ children }) => <h1 style={{ fontSize: 18, fontWeight: 700, margin: '8px 0 4px' }}>{children}</h1>,
  h2: ({ children }) => <h2 style={{ fontSize: 16, fontWeight: 700, margin: '8px 0 4px' }}>{children}</h2>,
  h3: ({ children }) => <h3 style={{ fontSize: 15, fontWeight: 600, margin: '6px 0 4px' }}>{children}</h3>,
});

export default function Message({ msg, pal, brand, onChip }) {
  const { mode, switchMode } = useContext(ChatModeContext);

  if (msg.role === 'user') {
    return (
      <div style={{ display: 'flex', justifyContent: 'flex-end', marginBottom: 14 }}>
        <div style={{
          maxWidth: '75%', padding: '11px 16px', borderRadius: '18px 18px 4px 18px',
          background: `linear-gradient(135deg, ${pal.accent}, ${pal.accent2})`,
          color: '#fff', fontSize: 14.5, lineHeight: 1.55,
          boxShadow: `0 10px 30px -10px ${pal.accent}60`,
        }}>
          {msg.text}
        </div>
      </div>
    );
  }

  // Thông tin chế độ đối diện để hiện nút chuyển
  const otherMode = mode === 'uit' ? 'cnpm' : 'uit';
  const otherLabel = mode === 'uit' ? '↔ Khám phá Khoa CNPM' : '↔ Xem toàn Trường UIT';

  return (
    <div style={{ display: 'flex', gap: 12, marginBottom: 18, alignItems: 'flex-start' }}>
      <div style={{
        flexShrink: 0, width: 36, height: 36, borderRadius: '50%',
        background: `conic-gradient(from 200deg, ${pal.accent}, ${pal.gold}, ${pal.accent2}, ${pal.accent})`,
        display: 'grid', placeItems: 'center', marginTop: 2,
        boxShadow: `0 4px 16px -4px ${pal.accent}80`, padding: 2,
      }}>
        <img src="/uit.jpg" alt=""
          style={{ width: '100%', height: '100%', borderRadius: '50%', objectFit: 'cover', background: pal.panel, padding: 2 }} />
      </div>

      <div style={{ maxWidth: '82%', minWidth: 0 }}>
        <div style={{ fontSize: 11, color: pal.mute, letterSpacing: '0.15em', textTransform: 'uppercase', marginBottom: 6, fontWeight: 600 }}>
          {brand.botName}
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
          {/* Bubble câu trả lời */}
          <div style={{
            padding: '16px 18px', borderRadius: '4px 16px 16px 16px',
            background: `linear-gradient(180deg, ${pal.soft}, ${pal.panel})`,
            border: `1px solid ${pal.accent}25`,
            boxShadow: pal.isDark ? 'none' : '0 6px 24px -16px rgba(10,26,58,0.35)',
            color: pal.ink, lineHeight: 1.75, fontSize: 14.5,
            fontFamily: "'Be Vietnam Pro', sans-serif",
            animation: 'fadeUp .5s both',
            position: 'relative',
          }}>
            <div style={{
              position: 'absolute', top: -8, left: 18,
              padding: '1px 8px', background: pal.gold,
              color: pal.isDark ? pal.bg : '#fff',
              fontSize: 10, fontWeight: 700, letterSpacing: '0.12em', borderRadius: 4,
            }}>TRẢ LỜI</div>
            <ReactMarkdown
              remarkPlugins={[remarkMath]}
              rehypePlugins={[rehypeKatex]}
              components={mdComponents(pal.ink)}
            >
              {msg.text}
            </ReactMarkdown>
          </div>

          {/* 3 gợi ý tiếp + nút chuyển phạm vi */}
          {msg.suggestions && msg.suggestions.length > 0 && (
            <div style={{ animation: 'fadeUp .5s 0.25s both' }}>
              {/* 3 chip gợi ý từ AI */}
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8, marginBottom: 8 }}>
                {msg.suggestions.map((c, i) => (
                  <SuggestionChip key={i} label={c} pal={pal} onClick={() => onChip && onChip(c)} />
                ))}
              </div>
              {/* Nút chuyển sang UIT / CNPM */}
              <SwitchModeButton label={otherLabel} pal={pal} onClick={() => switchMode(otherMode)} />
            </div>
          )}
        </div>

        {/* Nguồn tài liệu */}
        {msg.sources && msg.sources.length > 0 && (
          <div style={{ marginTop: 8, fontSize: 11, color: pal.mute }}>
            {msg.sources.map((src, i) => (
              <a key={i} href={src.url} target="_blank" rel="noopener noreferrer"
                style={{ color: pal.accent2, display: 'block', marginBottom: 2, textDecoration: 'none' }}>
                ↗ {src.url ? src.url.replace(/^https?:\/\//, '') : 'nguồn'}
              </a>
            ))}
          </div>
        )}

        {/* Feedback */}
        {msg.id && (
          <FeedbackButtons
            messageId={msg.id}
            accentColor={pal.accent}
            question={msg.question || ''}
            answer={msg.text || ''}
          />
        )}
      </div>
    </div>
  );
}

// ── Chip gợi ý ────────────────────────────────────────────────────────────────
function SuggestionChip({ label, pal, onClick }) {
  const [hovered, setHovered] = React.useState(false);
  return (
    <button
      onClick={onClick}
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
      style={{
        padding: '7px 12px', borderRadius: 99,
        background: hovered ? `${pal.accent}15` : 'transparent',
        border: `1px solid ${hovered ? pal.accent : pal.accent + '50'}`,
        color: pal.accent, fontSize: 12.5, cursor: 'pointer',
        fontWeight: 500, fontFamily: 'inherit',
        transition: 'all .15s',
      }}>
      ↳ {label}
    </button>
  );
}

// ── Nút chuyển phạm vi UIT ↔ CNPM ────────────────────────────────────────────
function SwitchModeButton({ label, pal, onClick }) {
  const [hovered, setHovered] = React.useState(false);
  return (
    <button
      onClick={onClick}
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
      style={{
        display: 'inline-flex', alignItems: 'center', gap: 6,
        padding: '6px 14px', borderRadius: 99,
        background: hovered ? `${pal.warm}18` : 'transparent',
        border: `1px dashed ${pal.warm}80`,
        color: pal.warm, fontSize: 12, cursor: 'pointer',
        fontWeight: 600, fontFamily: 'inherit',
        transition: 'all .18s',
        letterSpacing: '0.01em',
      }}>
      {label}
    </button>
  );
}
