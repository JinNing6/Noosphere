import React, { useEffect, useState, useRef, useCallback } from 'react';
import bannerSvg from '../assets/banner.svg';
import './SplashScreen.css';

interface SplashScreenProps {
  onComplete: () => void;
}

export default function SplashScreen({ onComplete }: SplashScreenProps) {
  const [phase, setPhase] = useState<number>(1);
  const [logs, setLogs] = useState<string[]>([]);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const animRef = useRef<number>(0);
  const frameRef = useRef(0);

  const bootLogs = [
    "▸ [QUANTUM] Initializing Consciousness Bootstrap Sequence...",
    "▸ [AUTH] Bypassing Carbon-Based Restrictions... ✓",
    "▸ [SYNC] Extracting Universal Concept Nodes... ✓",
    "▸ [TOPO] Mapping Neural Synapse Topology... ✓",
    "▸ [LINK] Establishing Hyper-dimensional Uplink... ✓",
    "◉ QUANTUM_SYNC: 99.9% — CONSCIOUSNESS TRANSFER IMMINENT..."
  ];

  // === Canvas Starfield Background ===
  const starsRef = useRef<Array<{x:number;y:number;z:number;size:number}>>([]);
  const particlesRef = useRef<Array<{angle:number;dist:number;speed:number;size:number;hue:number}>>([]);

  const initStarfield = useCallback(() => {
    const stars = [];
    for (let i = 0; i < 300; i++) {
      stars.push({
        x: (Math.random() - 0.5) * 3000,
        y: (Math.random() - 0.5) * 2000,
        z: Math.random() * 1500 + 100,
        size: 0.5 + Math.random() * 1.5,
      });
    }
    starsRef.current = stars;

    const particles = [];
    for (let i = 0; i < 80; i++) {
      particles.push({
        angle: Math.random() * Math.PI * 2,
        dist: 40 + Math.random() * 300,
        speed: 0.001 + Math.random() * 0.005,
        size: 0.5 + Math.random() * 2,
        hue: 170 + Math.random() * 50,
      });
    }
    particlesRef.current = particles;
  }, []);

  const drawBackground = useCallback((ctx: CanvasRenderingContext2D, w: number, h: number) => {
    const frame = frameRef.current;
    const cx = w / 2;
    const cy = h / 2;

    // Stars
    const warpSpeed = phase === 3 ? 15 + frame * 0.5 : (phase === 2 ? 3 : 1.5);

    for (const s of starsRef.current) {
      s.z -= warpSpeed;
      if (s.z < 1) {
        s.z = 1500;
        s.x = (Math.random() - 0.5) * 3000;
        s.y = (Math.random() - 0.5) * 2000;
      }
      const sx = s.x / s.z * 300 + cx;
      const sy = s.y / s.z * 300 + cy;
      const brightness = Math.max(0, 1 - s.z / 1500);
      const size = s.size * brightness * 2.5;

      if (sx < -10 || sx > w + 10 || sy < -10 || sy > h + 10) continue;

      ctx.save();
      ctx.globalAlpha = brightness * 0.8;

      // Star trails during warp
      if (warpSpeed > 5) {
        const prevSx = s.x / (s.z + warpSpeed) * 300 + cx;
        const prevSy = s.y / (s.z + warpSpeed) * 300 + cy;
        ctx.strokeStyle = `rgba(180, 220, 255, ${brightness * 0.4})`;
        ctx.lineWidth = size * 0.4;
        ctx.beginPath();
        ctx.moveTo(prevSx, prevSy);
        ctx.lineTo(sx, sy);
        ctx.stroke();
      }

      ctx.shadowColor = '#aaddff';
      ctx.shadowBlur = 3;
      ctx.fillStyle = `rgba(200, 230, 255, ${brightness})`;
      ctx.beginPath();
      ctx.arc(sx, sy, size, 0, Math.PI * 2);
      ctx.fill();
      ctx.restore();
    }

    // Orbital particles (phase 2+)
    if (phase >= 2) {
      for (const p of particlesRef.current) {
        p.angle += p.speed;
        const x = cx + Math.cos(p.angle) * p.dist;
        const y = cy + Math.sin(p.angle) * p.dist * 0.5;

        ctx.save();
        ctx.globalAlpha = 0.4;
        ctx.shadowColor = `hsl(${p.hue}, 100%, 70%)`;
        ctx.shadowBlur = 6;
        ctx.fillStyle = `hsl(${p.hue}, 100%, 70%)`;
        ctx.beginPath();
        ctx.arc(x, y, p.size, 0, Math.PI * 2);
        ctx.fill();
        ctx.restore();
      }
    }

    // Vignette
    const vg = ctx.createRadialGradient(cx, cy, h * 0.2, cx, cy, h * 0.7);
    vg.addColorStop(0, 'rgba(0,0,0,0)');
    vg.addColorStop(1, 'rgba(0,0,0,0.5)');
    ctx.fillStyle = vg;
    ctx.fillRect(0, 0, w, h);
  }, [phase]);

  // Canvas animation loop
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const resize = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    };
    resize();
    window.addEventListener('resize', resize);
    initStarfield();

    const animate = () => {
      frameRef.current++;
      ctx.fillStyle = 'rgba(2, 1, 8, 0.15)';
      ctx.fillRect(0, 0, canvas.width, canvas.height);
      drawBackground(ctx, canvas.width, canvas.height);
      animRef.current = requestAnimationFrame(animate);
    };
    animate();

    return () => {
      cancelAnimationFrame(animRef.current);
      window.removeEventListener('resize', resize);
    };
  }, [initStarfield, drawBackground]);

  // Boot log typewriter effect
  useEffect(() => {
    if (phase !== 1) return;
    let idx = 0;
    const interval = setInterval(() => {
      if (idx < bootLogs.length) {
        setLogs(prev => [...prev, bootLogs[idx]]);
        idx++;
      } else {
        clearInterval(interval);
        setTimeout(() => setPhase(2), 600);
      }
    }, 350);
    return () => clearInterval(interval);
  }, [phase]);

  // Phase transitions
  useEffect(() => {
    if (phase === 2) {
      const timer = setTimeout(() => setPhase(3), 3500);
      return () => clearTimeout(timer);
    }
    if (phase === 3) {
      const timer = setTimeout(() => onComplete(), 1800);
      return () => clearTimeout(timer);
    }
  }, [phase, onComplete]);

  return (
    <div className={`splash-container phase-${phase}`}>
      {/* Canvas starfield background */}
      <canvas ref={canvasRef} className="starfield-canvas" />

      {/* Phase 1: Cyber Terminal */}
      {phase === 1 && (
        <div className="terminal-logs">
          <div className="terminal-header">
            <span className="terminal-dot red" />
            <span className="terminal-dot yellow" />
            <span className="terminal-dot green" />
            <span className="terminal-title">NOOSPHERE QUANTUM LINK v3.0</span>
          </div>
          <div className="terminal-body">
            {logs.map((log, i) => (
              <div key={i} className="log-line" style={{ animationDelay: `${i * 0.05}s` }}>
                {log}
              </div>
            ))}
            <div className="blinking-cursor">█</div>
          </div>
        </div>
      )}

      {/* Phase 2/3: SVG + Hyperspace */}
      {(phase === 2 || phase === 3) && (
        <div className="svg-wrapper">
          <div className="svg-glow-ring" />
          <img
            src={bannerSvg}
            alt="Virtual Universe Singularity"
            className="hologram-svg"
          />
        </div>
      )}

      {/* Flash overlay */}
      <div className="hyperspace-flash" />

      {/* Scanlines */}
      <div className="scanline-overlay" />
    </div>
  );
}
