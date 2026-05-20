import React, { useContext, useState } from 'react';
import { ChatModeContext } from '../context/ChatModeContext';
import StarField from '../components/StarField';
import ChatBox from '../components/ChatBox';
import Timeline from '../components/Timeline';
import ApiKeyModal from '../components/ApiKeyModal';

const API_KEY_STORAGE = 'uit20_gemini_key';

// ── Palettes ────────────────────────────────────────────────────────────────

const UIT_PAL = {
  isDark: true,
  bg: '#06122e', panel: '#0f2447', soft: '#16315e',
  ink: '#eaf1ff', mute: '#9fb3d9',
  accent: '#4f8cff', accent2: '#79c2ff', glow: '#a8d5ff',
  gold: '#f4c969', warm: '#ff7a3d',
};

const CNPM_PAL = {
  isDark: false,
  bg: '#f3f6fb', panel: '#ffffff', soft: '#eaf0fa',
  ink: '#0a1a3a', mute: '#5d6f8e',
  accent: '#1d4ed8', accent2: '#3b82f6', glow: '#bcd2ff',
  gold: '#1e3a8a', warm: '#ea580c',
};

// ── Brand copy ───────────────────────────────────────────────────────────────

const BRAND = {
  uit: {
    schoolName: 'Trường Đại học Công nghệ Thông tin',
    tagline: 'Kỷ niệm 20 năm · 2006 — 2026',
    eyebrow: 'HÃY HỎI CÂU CHUYỆN CỦA CHÚNG TÔI',
    heroTitle: ['Hai mươi năm,', 'một câu chuyện', ' vẫn đang được kể tiếp.'],
    heroBody: 'Trò chuyện với người kể chuyện AI của Trường — một hành trình hai thập kỷ qua giảng đường, phòng lab và những con người đã làm nên nơi này.',
    botName: "Người kể chuyện UIT'20",
    placeholder: 'Hỏi về 20 năm UIT…',
    timelineTitle: '20 năm, 6 chương',
    version: 'v20.0 · uit.edu.vn',
    stats: [['20', 'ngành đào tạo'], ['40,000', 'cựu sinh viên'], ['120', 'phòng thí nghiệm']],
  },
  cnpm: {
    schoolName: 'Khoa Công nghệ Phần mềm',
    tagline: 'Software Engineering · UIT',
    eyebrow: 'TRÒ CHUYỆN VỚI KHOA',
    heroTitle: ['Người viết phần mềm,', 'viết tiếp', ' hai thập kỷ.'],
    heroBody: 'Trò chuyện với trợ lý của Khoa Công nghệ Phần mềm — câu chuyện riêng của một khoa đã đào tạo nên hàng nghìn kỹ sư phần mềm Việt Nam.',
    botName: 'Trợ lý Khoa CNPM',
    placeholder: 'Hỏi về khoa CNPM…',
    timelineTitle: '18 năm của một Khoa',
    version: 'v18.0 · se.uit.edu.vn',
    stats: [['12', 'môn chuyên ngành'], ['8,500', 'kỹ sư phần mềm'], ['35', 'doanh nghiệp đối tác']],
  },
};

// ── Timelines ────────────────────────────────────────────────────────────────

const TIMELINES = {
  uit: [
    { year: '2006', title: 'Khởi nguyên', body: 'Trường được thành lập với khát vọng đặt nền móng cho ngành CNTT tại miền Nam.' },
    { year: '2010', title: 'Mở đường', body: 'Những khóa kỹ sư đầu tiên ra trường, mang theo niềm tin và những dòng code khởi đầu.' },
    { year: '2014', title: 'Bứt phá', body: 'Phòng lab An toàn thông tin và Trí tuệ nhân tạo lần lượt thành hình.' },
    { year: '2018', title: 'Vươn xa', body: 'Sinh viên giành huy chương quốc tế ICPC, CTF — đặt dấu chân trên bản đồ thế giới.' },
    { year: '2022', title: 'Đổi mới', body: 'Chuyển mình toàn diện theo định hướng đại học số, kết nối doanh nghiệp.' },
    { year: '2026', title: 'Hai mươi', body: 'Hai thập kỷ — không chỉ là thời gian, mà là một thế hệ ước mơ đã thành hiện thực.' },
  ],
  cnpm: [
    { year: '2008', title: 'Thành lập Khoa', body: 'Khoa CNPM chính thức ra đời, đào tạo kỹ sư cho ngành công nghiệp phần mềm non trẻ.' },
    { year: '2012', title: 'Khoá đầu tốt nghiệp', body: 'Lứa kỹ sư phần mềm đầu tiên rời Khoa, mang theo tinh thần xây dựng phần mềm Việt.' },
    { year: '2016', title: 'Phòng lab SELab', body: 'Phòng thí nghiệm Kỹ nghệ Phần mềm và Agile được thành lập, hợp tác cùng doanh nghiệp.' },
    { year: '2019', title: 'Capstone Project', body: 'Mô hình đồ án tốt nghiệp gắn với doanh nghiệp trở thành chuẩn mực của Khoa.' },
    { year: '2023', title: 'AI for SE', body: 'Khoa mở định hướng AI4SE — đào tạo kỹ sư phần mềm trong kỷ nguyên trợ lý AI.' },
    { year: '2026', title: 'Cùng Trường 20', body: 'Khoa bước cùng Trường vào dấu mốc 20 năm, với thế hệ kỹ sư mới đã sẵn sàng.' },
  ],
};

// ── Suggested prompts ────────────────────────────────────────────────────────

const SUGGESTED = {
  uit: [
    { label: 'Trường được thành lập như thế nào?', q: 'Hãy kể cho tôi câu chuyện về ngày Trường được thành lập.' },
    { label: 'Những cột mốc đáng nhớ', q: 'Những cột mốc nào đã làm nên 20 năm của Trường?' },
    { label: 'Ngành học nào nổi bật?', q: 'Trường có những ngành học và phòng thí nghiệm nào nổi bật?' },
    { label: 'Cựu sinh viên truyền cảm hứng', q: 'Hãy kể về một cựu sinh viên truyền cảm hứng của Trường.' },
    { label: 'Đời sống sinh viên', q: 'Một ngày trong đời một sinh viên năm nhất ở đây sẽ ra sao?' },
    { label: 'Tương lai 10 năm tới', q: 'Trường hình dung 10 năm tiếp theo sẽ như thế nào?' },
  ],
  cnpm: [
    { label: 'Khoa CNPM ra đời thế nào?', q: 'Hãy kể cho tôi nghe Khoa Công nghệ Phần mềm đã ra đời như thế nào.' },
    { label: 'Học gì ở Khoa CNPM?', q: 'Sinh viên Khoa Công nghệ Phần mềm sẽ học những gì?' },
    { label: 'Capstone Project là gì?', q: 'Đồ án tốt nghiệp Capstone của Khoa hoạt động ra sao?' },
    { label: 'Cựu kỹ sư phần mềm', q: 'Hãy kể về một cựu sinh viên kỹ sư phần mềm đáng nhớ.' },
    { label: 'Doanh nghiệp đối tác', q: 'Khoa hợp tác với những doanh nghiệp nào?' },
    { label: 'AI thay đổi kỹ sư phần mềm?', q: 'Trong kỷ nguyên AI, kỹ sư phần mềm của Khoa sẽ thay đổi ra sao?' },
  ],
};

// ── Home ─────────────────────────────────────────────────────────────────────

export default function Home() {
  const { mode, switchMode } = useContext(ChatModeContext);

  const pal = mode === 'uit' ? UIT_PAL : CNPM_PAL;
  const brand = BRAND[mode];
  const timeline = TIMELINES[mode];
  const suggested = SUGGESTED[mode];

  const [apiKey, setApiKey] = useState(() => {
    try { return sessionStorage.getItem(API_KEY_STORAGE) || ''; } catch { return ''; }
  });
  const [showApiModal, setShowApiModal] = useState(() => {
    try { return !sessionStorage.getItem(API_KEY_STORAGE); } catch { return true; }
  });

  const saveApiKey = (k) => {
    try { if (k) sessionStorage.setItem(API_KEY_STORAGE, k); } catch { }
    setApiKey(k);
    setShowApiModal(false);
  };

  const bgGradient = pal.isDark
    ? `radial-gradient(ellipse at 20% -10%, ${pal.accent}25, transparent 50%), radial-gradient(ellipse at 110% 110%, ${pal.warm}18, transparent 50%)`
    : `radial-gradient(ellipse at 20% -10%, ${pal.accent}10, transparent 50%), radial-gradient(ellipse at 110% 110%, ${pal.warm}08, transparent 50%)`;

  return (
    <div style={{
      minHeight: '100vh',
      background: pal.bg,
      backgroundImage: bgGradient,
      color: pal.ink,
      fontFamily: "'Be Vietnam Pro', sans-serif",
      position: 'relative',
      transition: 'background 0.5s, color 0.5s',
    }}>
      <StarField pal={pal} density={220} />
      <ApiKeyModal pal={pal} open={showApiModal} savedKey={apiKey} onSave={saveApiKey} />

      <div style={{ maxWidth: 1280, margin: '0 auto', padding: '22px 28px 28px', position: 'relative', zIndex: 1 }}>

        {/* ── Header ── */}
        <header style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 20, gap: 20, flexWrap: 'wrap' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
            <img src="/uit.jpg" alt="UIT"
              style={{
                width: 46, height: 46, objectFit: 'contain', borderRadius: 8,
                filter: 'drop-shadow(0 2px 6px rgba(79,140,255,0.4))'
              }} />
            <div>
              <div style={{ fontFamily: "'Fraunces', serif", fontSize: 17, color: pal.ink, lineHeight: 1.1, letterSpacing: '-0.01em', fontWeight: 500 }}>
                {brand.schoolName}
              </div>
              <div style={{ fontSize: 11, color: pal.mute, letterSpacing: '0.18em', textTransform: 'uppercase', marginTop: 4 }}>
                {brand.tagline}
              </div>
            </div>
          </div>

          <div style={{
            display: 'flex', alignItems: 'center', gap: 6,
            padding: 5, borderRadius: 99,
            background: pal.isDark ? `${pal.panel}cc` : pal.soft,
            border: `1px solid ${pal.accent}25`,
            backdropFilter: 'blur(8px)',
          }}>
            <div style={{ fontSize: 10, color: pal.mute, padding: '0 8px 0 10px', letterSpacing: '0.18em', fontWeight: 700, textTransform: 'uppercase' }}>
              Chế độ
            </div>
            <ModePill pal={pal} active={mode === 'uit'} sub="U" label="Toàn Trường" onClick={() => switchMode('uit')} />
            <ModePill pal={pal} active={mode === 'cnpm'} sub="SE" label="Khoa CNPM" onClick={() => switchMode('cnpm')} />
          </div>
        </header>

        {/* ── Hero ── */}
        <section
          className="flex flex-col-reverse md:grid md:grid-cols-[1fr_auto] gap-6 md:gap-8 items-center p-6 md:px-8 md:py-6 rounded-2xl mb-5 relative overflow-hidden"
          style={{
            background: pal.isDark
              ? `linear-gradient(120deg, ${pal.panel} 0%, ${pal.soft} 100%)`
              : 'linear-gradient(120deg, #ffffff 0%, ' + pal.soft + ' 100%)',
            border: `1px solid ${pal.accent}${pal.isDark ? '30' : '25'}`,
            boxShadow: pal.isDark ? 'none' : '0 20px 60px -30px rgba(29,78,216,0.25)',
          }}>
          <div style={{
            position: 'absolute', right: -60, top: -60, width: 320, height: 320, borderRadius: '50%',
            background: `radial-gradient(circle, ${pal.warm}${pal.isDark ? '22' : '12'}, transparent 60%)`,
            pointerEvents: 'none',
          }} />
          <div style={{ position: 'relative' }}>
            <div style={{ fontSize: 11, color: pal.warm, letterSpacing: '0.28em', fontWeight: 700 }}>{brand.eyebrow}</div>
            <h1 style={{ fontFamily: "'Fraunces', serif", fontSize: 'clamp(32px, 6vw, 40px)', lineHeight: 1.1, margin: '10px 0 12px', letterSpacing: '-0.02em', fontWeight: 500, color: pal.ink, maxWidth: 620 }}>
              {brand.heroTitle[0]}{' '}
              <em style={{ color: pal.warm, fontStyle: 'italic' }}>{brand.heroTitle[1]}</em>
              {brand.heroTitle[2]}
            </h1>
            <p style={{ color: pal.mute, fontSize: 14.5, maxWidth: 580, lineHeight: 1.65, margin: 0 }}>
              {brand.heroBody}
            </p>
          </div>
          <img src="/uit.jpg" alt="UIT 20 năm"
            className="w-24 h-24 md:w-[150px] md:h-[150px] object-contain rounded-2xl flex-shrink-0"
            style={{
              filter: 'drop-shadow(0 12px 30px rgba(79,140,255,0.45)) drop-shadow(0 4px 12px rgba(255,122,61,0.25))',
            }} />
        </section>

        {/* ── Main grid ── */}
        <main className="grid grid-cols-1 lg:grid-cols-[1fr_300px] gap-5 items-start flex-col flex lg:grid">
          <ChatBox pal={pal} brand={brand} suggested={suggested} apiKey={apiKey} />
          <Timeline pal={pal} brand={brand} timeline={timeline} />
        </main>

        {/* ── Footer ── */}
        <footer style={{
          marginTop: 22, display: 'flex', justifyContent: 'space-between', alignItems: 'center',
          padding: '14px 22px', borderRadius: 14,
          background: pal.isDark
            ? `linear-gradient(90deg, ${pal.panel}, ${pal.soft})`
            : `linear-gradient(90deg, #ffffff, ${pal.soft})`,
          border: `1px solid ${pal.accent}${pal.isDark ? '25' : '20'}`,
          fontSize: 12, color: pal.mute,
          boxShadow: pal.isDark ? 'none' : '0 8px 30px -20px rgba(29,78,216,0.2)',
          flexWrap: 'wrap', gap: 12,
        }}>
          <div>© 2026 · {mode === 'uit' ? 'Lễ kỷ niệm 20 năm thành lập Trường' : 'Khoa Công nghệ Phần mềm · UIT'}</div>
          <div style={{ display: 'flex', gap: 18 }}>
            {brand.stats.map(([n, l], i) => (
              <span key={i}>{n}<span style={{ color: pal.warm }}>+</span> {l}</span>
            ))}
          </div>
        </footer>
      </div>
    </div>
  );
}

// ── ModePill ─────────────────────────────────────────────────────────────────

function ModePill({ active, label, sub, onClick, pal }) {
  return (
    <button onClick={onClick} style={{
      display: 'flex', alignItems: 'center', gap: 10,
      padding: '7px 14px 7px 11px', borderRadius: 99,
      background: active ? `linear-gradient(135deg, ${pal.accent}, ${pal.accent2})` : 'transparent',
      border: `1px solid ${active ? 'transparent' : pal.accent + '40'}`,
      color: active ? '#fff' : pal.ink,
      cursor: 'pointer', fontFamily: 'inherit',
      boxShadow: active ? `0 8px 20px -8px ${pal.accent}` : 'none',
      transition: 'all .2s',
    }}>
      <div style={{
        width: 22, height: 22, borderRadius: '50%',
        background: active ? 'rgba(255,255,255,0.2)' : `${pal.accent}15`,
        display: 'grid', placeItems: 'center',
        fontSize: 11, fontWeight: 700, color: active ? '#fff' : pal.accent,
      }}>{sub}</div>
      <div style={{ fontSize: 12.5, fontWeight: 600, letterSpacing: '0.01em' }}>{label}</div>
    </button>
  );
}
