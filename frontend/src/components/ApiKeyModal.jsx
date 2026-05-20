import React, { useState, useEffect } from 'react';

export default function ApiKeyModal({ pal, open, onSave, savedKey = '' }) {
  const [key, setKey] = useState(savedKey);
  const [showKey, setShowKey] = useState(false);

  useEffect(() => {
    if (open) {
      setKey(savedKey || '');
      // Khoá cuộn trang nền (body scroll) để tránh tình trạng cuộn đúp (double scrollbar)
      document.body.style.overflow = 'hidden';
      return () => {
        // Khôi phục cuộn trang nền khi đóng modal hoặc component bị gỡ bỏ
        document.body.style.overflow = '';
      };
    }
  }, [open, savedKey]);

  if (!open) return null;

  const overlayBg = pal.isDark ? 'rgba(4,10,30,0.78)' : 'rgba(10,26,58,0.50)';
  const cardBg = pal.isDark ? pal.panel : '#ffffff';

  const steps = [
    {
      n: '01',
      title: 'Mở Google AI Studio',
      body: (
        <>
          Truy cập{' '}
          <a
            href="https://aistudio.google.com/app/apikey"
            target="_blank"
            rel="noreferrer"
            style={{ color: pal.accent, fontWeight: 600, textDecoration: 'underline', textUnderlineOffset: 3 }}
          >
            aistudio.google.com/app/apikey
          </a>{' '}
          và đăng nhập bằng tài khoản Google của bạn. Dịch vụ này hoàn toàn MIỄN PHÍ, không cần thẻ tín dụng.
        </>
      ),
    },
    {
      n: '02',
      title: 'Bấm "Create API key"',
      body: 'Trong trang vừa mở, bấm nút "Create API key" và chọn một project Google Cloud (hoặc để mặc định nếu bạn chưa có). Google sẽ tạo ra một chuỗi dài và thường bắt đầu bằng "AIza…".',
    },
    {
      n: '03',
      title: 'Sao chép API key',
      body: 'Bấm biểu tượng sao chép bên cạnh API key vừa tạo. Lưu ý: hãy giữ key này riêng tư, đừng chia sẻ công khai trên mạng xã hội hay GitHub.',
    },
    {
      n: '04',
      title: 'Dán vào ô bên dưới',
      body: 'Dán API key của bạn vào ô bên dưới và bấm "Lưu & Bắt đầu".',
    },
  ];

  const submit = () => { onSave(key.trim()); };

  return (
    <div
      style={{
        position: 'fixed', inset: 0, zIndex: 9999,
        background: overlayBg, backdropFilter: 'blur(8px)',
        display: 'grid', placeItems: 'center',
        animation: 'fadeIn .25s ease-out', padding: 24,
        overflowY: 'auto',
      }}
    >
      <div
        className="w-full sm:w-[min(880px,100%)] relative m-auto"
        style={{
          background: cardBg,
          borderRadius: 'clamp(16px, 4vw, 24px)', border: `1px solid ${pal.accent}30`,
          boxShadow: pal.isDark
            ? `0 50px 120px -30px ${pal.accent}90, 0 0 0 1px ${pal.accent}20 inset`
            : '0 50px 120px -30px rgba(29,78,216,0.5)',
          overflow: 'hidden',
          animation: 'popIn .4s cubic-bezier(.22,1.2,.4,1)',
        }}
      >
        {/* Header banner */}
        <div
          className="px-5 py-6 sm:px-9 sm:py-7 flex flex-col sm:flex-row items-start sm:items-center gap-4 sm:gap-5 relative"
          style={{
            background: pal.isDark
              ? `linear-gradient(135deg, ${pal.soft} 0%, ${pal.panel} 100%)`
              : `linear-gradient(135deg, ${pal.soft} 0%, #ffffff 100%)`,
            borderBottom: `1px solid ${pal.accent}25`,
          }}
        >
          <div style={{
            position: 'absolute', right: -40, top: -40, width: 200, height: 200, borderRadius: '50%',
            background: `radial-gradient(circle, ${pal.warm}25, transparent 60%)`, pointerEvents: 'none',
          }} />
          <div style={{
            position: 'absolute', left: -30, bottom: -60, width: 160, height: 160, borderRadius: '50%',
            background: `radial-gradient(circle, ${pal.accent}25, transparent 60%)`, pointerEvents: 'none',
          }} />
          <img
            src="/uit.jpg"
            alt=""
            style={{
              width: 56, height: 56, objectFit: 'contain', position: 'relative',
              filter: 'drop-shadow(0 8px 20px rgba(79,140,255,0.45))',
            }}
          />
          <div style={{ flex: 1, position: 'relative' }}>
            <div style={{ fontSize: 11, color: pal.warm, letterSpacing: '0.22em', fontWeight: 700 }}>
              CHÀO MỪNG ĐẾN VỚI UIT'20
            </div>
            <div style={{
              fontFamily: "'Fraunces', serif", fontSize: 'clamp(22px, 5vw, 26px)', color: pal.ink,
              marginTop: 4, letterSpacing: '-0.01em', fontWeight: 500, lineHeight: 1.2,
            }}>
              Thiết lập Google AI API key
            </div>
            <div style={{ fontSize: 13.5, color: pal.mute, marginTop: 6, lineHeight: 1.5, maxWidth: 560 }}>
              Để có trải nghiệm ổn định hơn và tránh giới hạn dùng chung, bạn nên dùng Gemini API key riêng. Nếu không có, hệ thống sẽ tự động dùng API key mặc định từ server.
            </div>
          </div>
        </div>

        {/* All steps visible at once */}
        <div className="px-5 sm:px-9 pt-5 sm:pt-6 pb-2">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3.5">
            {steps.map((s, i) => (
              <div
                key={i}
                style={{
                  position: 'relative',
                  padding: '16px 18px 16px 20px',
                  borderRadius: 14,
                  background: pal.isDark ? `${pal.soft}80` : `${pal.soft}70`,
                  border: `1px solid ${pal.accent}22`,
                  display: 'flex', gap: 14, alignItems: 'flex-start',
                }}
              >
                <div style={{
                  flex: '0 0 42px', width: 42, height: 42, borderRadius: 11,
                  background: `linear-gradient(135deg, ${pal.accent}, ${pal.accent2})`,
                  color: '#fff', display: 'grid', placeItems: 'center',
                  fontFamily: "'JetBrains Mono', monospace", fontSize: 15, fontWeight: 700,
                  boxShadow: `0 8px 20px -10px ${pal.accent}`,
                }}>
                  {s.n}
                </div>
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{
                    fontFamily: "'Fraunces', serif", fontSize: 16, color: pal.ink,
                    fontWeight: 500, letterSpacing: '-0.005em', lineHeight: 1.25,
                  }}>
                    {s.title}
                  </div>
                  <div style={{
                    fontSize: 13, color: pal.isDark ? pal.glow : pal.mute,
                    lineHeight: 1.55, marginTop: 6,
                  }}>
                    {s.body}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Key input */}
        <div className="px-5 sm:px-9 py-2">
          <label style={{
            fontSize: 11, color: pal.mute, letterSpacing: '0.16em',
            fontWeight: 600, textTransform: 'uppercase',
          }}>
            Gemini API key
          </label>
          <div style={{
            marginTop: 8, display: 'flex', alignItems: 'center', gap: 8,
            padding: '4px 4px 4px 16px', borderRadius: 14,
            background: pal.soft, border: `1px solid ${pal.accent}40`,
          }}>

            <input
              type={showKey ? 'text' : 'password'}
              value={key}
              onChange={(e) => setKey(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && submit()}
              placeholder="Dán API key vào đây"
              style={{
                flex: 1, background: 'transparent', border: 'none', outline: 'none',
                color: pal.ink, fontSize: 14, padding: '12px 0',
                fontFamily: "'JetBrains Mono', monospace", minWidth: 0
              }}
            />
            <button
              onClick={() => setShowKey((s) => !s)}
              className="flex-shrink-0"
              style={{
                padding: '9px 14px', borderRadius: 10, border: `1px solid ${pal.accent}30`,
                background: 'transparent', color: pal.mute, fontSize: 12, cursor: 'pointer',
                fontFamily: 'inherit',
              }}
            >
              {showKey ? 'Ẩn' : 'Hiện'}
            </button>
          </div>
        </div>

        {/* Session-only privacy notice */}
        <div className="px-5 sm:px-9 pt-3">
          <div style={{
            padding: '12px 16px', borderRadius: 12,
            background: `${pal.warm}12`,
            border: `1px solid ${pal.warm}35`,
            fontSize: 13, color: pal.ink, lineHeight: 1.55,
          }}>
            <span style={{ color: pal.warm, fontWeight: 700, letterSpacing: '0.06em' }}>LƯU Ý — </span>
            API key sẽ <strong style={{ color: pal.warm }}>chỉ áp dụng cho 1 session</strong> của trang web này và sẽ <strong style={{ color: pal.warm }}>được xóa hoàn toàn sau khi hết session</strong> (khi bạn đóng tab hoặc trình duyệt). Key được giữ tạm trong bộ nhớ của trình duyệt, không gửi tới bất kỳ máy chủ nào của chúng tôi.
          </div>
        </div>

        {/* Footer action */}
        <div 
          className="px-5 sm:px-9 py-5 sm:py-6 flex justify-end mt-3 sm:mt-4"
          style={{
            borderTop: `1px solid ${pal.accent}20`,
            background: pal.isDark ? 'transparent' : `${pal.soft}40`,
          }}>
          <button
            onClick={submit}
            className="w-full sm:w-auto flex justify-center items-center"
            style={{
              padding: '12px 28px', borderRadius: 12, border: 'none',
              background: `linear-gradient(135deg, ${pal.accent}, ${pal.accent2})`,
              color: '#fff', fontSize: 14, fontWeight: 600,
              cursor: 'pointer', gap: 8,
              boxShadow: `0 10px 28px -10px ${pal.accent}`,
              fontFamily: 'inherit', letterSpacing: '0.01em',
            }}
          >
            Lưu &amp; Bắt đầu hành trình <span style={{ fontSize: 15 }}>→</span>
          </button>
        </div>
      </div>
    </div>
  );
}
