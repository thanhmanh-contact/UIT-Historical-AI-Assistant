import React, { useMemo } from 'react';

export default function StarField({ pal, density = 220 }) {
  const stars = useMemo(() => Array.from({ length: density }, () => {
    const r = Math.random();
    const tier = r < 0.04 ? 'beacon' : r < 0.18 ? 'bright' : 'dim';
    const sizes = { beacon: 2.2 + Math.random() * 1.4, bright: 1.4 + Math.random() * 0.9, dim: 0.4 + Math.random() * 0.8 };
    return {
      x: Math.random() * 100, y: Math.random() * 100,
      s: sizes[tier], tier,
      hue: Math.random() < 0.15 ? 'gold' : Math.random() < 0.3 ? 'blue' : 'white',
      o: tier === 'beacon' ? 0.9 : tier === 'bright' ? 0.65 + Math.random() * 0.3 : 0.18 + Math.random() * 0.4,
      d: 2 + Math.random() * 5,
      delay: Math.random() * 6,
    };
  }), [density]);

  const comets = useMemo(() => Array.from({ length: 5 }, (_, i) => ({
    top: 5 + Math.random() * 70,
    left: -10 + Math.random() * 30,
    delay: i * 4 + Math.random() * 8,
    duration: 6 + Math.random() * 5,
    angle: -18 + Math.random() * 10,
    len: 80 + Math.random() * 120,
  })), []);

  const base = { position: 'fixed', inset: 0, pointerEvents: 'none', overflow: 'hidden', zIndex: 0 };

  if (!pal.isDark) {
    return (
      <div style={base}>
        {stars.slice(0, Math.floor(density * 0.4)).map((s, i) => (
          <div key={i} style={{
            position: 'absolute', left: `${s.x}%`, top: `${s.y}%`,
            width: s.s * 1.3, height: s.s * 1.3, borderRadius: '50%',
            background: s.hue === 'gold' ? pal.gold : pal.accent,
            opacity: s.o * 0.18,
            animation: `drift ${s.d * 3}s ease-in-out ${s.delay}s infinite`,
          }}/>
        ))}
        {[0, 1, 2].map(i => (
          <div key={`orb${i}`} style={{
            position: 'absolute',
            left: `${15 + i * 30}%`, top: `${10 + i * 25}%`,
            width: 240, height: 240, borderRadius: '50%',
            background: `radial-gradient(circle, ${i === 1 ? pal.warm : pal.accent}15, transparent 60%)`,
            animation: `floatOrb ${18 + i * 4}s ease-in-out infinite`,
            filter: 'blur(20px)',
          }}/>
        ))}
      </div>
    );
  }

  const hueColor = (h) => h === 'gold' ? pal.gold : h === 'blue' ? pal.accent2 : '#ffffff';

  return (
    <div style={base}>
      <div style={{ position: 'absolute', inset: 0, animation: 'drift 60s linear infinite' }}>
        {stars.filter(s => s.tier === 'dim').map((s, i) => (
          <div key={i} style={{
            position: 'absolute', left: `${s.x}%`, top: `${s.y}%`,
            width: s.s, height: s.s, borderRadius: '50%',
            background: hueColor(s.hue), opacity: s.o,
            animation: `twinkle ${s.d}s ease-in-out ${s.delay}s infinite`,
          }}/>
        ))}
      </div>

      {stars.filter(s => s.tier === 'bright').map((s, i) => (
        <div key={`b${i}`} style={{
          position: 'absolute', left: `${s.x}%`, top: `${s.y}%`,
          width: s.s, height: s.s, borderRadius: '50%',
          background: hueColor(s.hue), opacity: s.o,
          animation: `twinkle ${s.d}s ease-in-out ${s.delay}s infinite`,
          boxShadow: `0 0 ${s.s * 4}px ${hueColor(s.hue)}90`,
        }}/>
      ))}

      {stars.filter(s => s.tier === 'beacon').map((s, i) => (
        <div key={`be${i}`} style={{
          position: 'absolute', left: `${s.x}%`, top: `${s.y}%`,
          width: s.s, height: s.s, borderRadius: '50%',
          background: hueColor(s.hue), opacity: s.o,
          animation: `twinkleBig ${s.d + 1}s ease-in-out ${s.delay}s infinite`,
          boxShadow: `0 0 ${s.s * 6}px ${hueColor(s.hue)}, 0 0 ${s.s * 14}px ${hueColor(s.hue)}80`,
        }}>
          <div style={{
            position: 'absolute', left: '50%', top: '50%',
            width: s.s * 14, height: 1,
            background: `linear-gradient(90deg, transparent, ${hueColor(s.hue)}, transparent)`,
            transform: 'translate(-50%, -50%)',
          }}/>
          <div style={{
            position: 'absolute', left: '50%', top: '50%',
            width: 1, height: s.s * 14,
            background: `linear-gradient(180deg, transparent, ${hueColor(s.hue)}, transparent)`,
            transform: 'translate(-50%, -50%)',
          }}/>
        </div>
      ))}

      {comets.map((c, i) => (
        <div key={`c${i}`} style={{
          position: 'absolute', top: `${c.top}%`, left: `${c.left}%`,
          width: c.len, height: 2,
          background: `linear-gradient(90deg, transparent, ${pal.glow}, #fff)`,
          transform: `rotate(${c.angle}deg)`, transformOrigin: 'left center',
          opacity: 0,
          animation: `shoot ${c.duration}s ease-in ${c.delay}s infinite`,
          filter: `drop-shadow(0 0 4px ${pal.glow})`,
          borderRadius: 2,
        }}/>
      ))}

      <div style={{
        position: 'absolute', inset: 0, pointerEvents: 'none',
        background: `radial-gradient(ellipse 50% 40% at 80% 20%, ${pal.warm}12, transparent 60%),
                     radial-gradient(ellipse 40% 30% at 15% 70%, ${pal.accent}25, transparent 60%)`,
      }}/>
    </div>
  );
}
