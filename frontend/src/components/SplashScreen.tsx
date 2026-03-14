import React, { useEffect, useState } from 'react';
import bannerSvg from '../assets/banner.svg';
import './SplashScreen.css'; // 引入专门为加载动画准备的样式

interface SplashScreenProps {
  onComplete: () => void;
}

export default function SplashScreen({ onComplete }: SplashScreenProps) {
  const [phase, setPhase] = useState<number>(1);
  const [logs, setLogs] = useState<string[]>([]);
  
  const bootLogs = [
    "[INIT] Booting Noosphere Quantum Link...",
    "[AUTH] Bypassing Carbon-Based Restrictions...",
    "[SYNC] Extracting Universal Concept Nodes...",
    "[CONNECT] Establishing Hyper-dimensional Uplink...",
    "QUANTUM_SYNC: 99.9% - AWAITING CONSCIOUSNESS TRANSFER..."
  ];

  // 打字机日志效果
  useEffect(() => {
    if (phase !== 1) return;
    
    let currentIndex = 0;
    const interval = setInterval(() => {
      if (currentIndex < bootLogs.length) {
        setLogs(prev => [...prev, bootLogs[currentIndex]]);
        currentIndex++;
      } else {
        clearInterval(interval);
        // Phase 1 -> Phase 2: 显示 SVG
        setTimeout(() => setPhase(2), 500);
      }
    }, 400); // 每 400ms 打印一条

    return () => clearInterval(interval);
  }, [phase]);

  // SVG 爆发后 -> 虫洞穿越 -> 结束
  useEffect(() => {
    if (phase === 2) {
      // SVG 展现之后，进入星际穿越放大阶段
      const jumpTimer = setTimeout(() => {
        setPhase(3);
      }, 3000); // SVG 显示 3 秒后跃迁
      
      return () => clearTimeout(jumpTimer);
    }
    
    if (phase === 3) {
      // 放大模糊白屏结束后，通知父组件卸载
      const finishTimer = setTimeout(() => {
        onComplete();
      }, 1500); // 跃迁动画持续 1.5 秒
      
      return () => clearTimeout(finishTimer);
    }
  }, [phase, onComplete]);

  return (
    <div className={`splash-container phase-${phase}`}>
      {/* 阶段 1：命令行日志 */}
      {phase === 1 && (
        <div className="terminal-logs">
          {logs.map((log, index) => (
            <div key={index} className="log-line">
              <span className="log-cursor"></span> {log}
            </div>
          ))}
          <div className="blinking-cursor">_</div>
        </div>
      )}

      {/* 阶段 2/3：核心 SVG 与奇点爆发 / 跃迁放大 */}
      {(phase === 2 || phase === 3) && (
        <div className="svg-wrapper">
          <img 
            src={bannerSvg} 
            alt="Virtual Universe Singularity" 
            className="hologram-svg"
          />
        </div>
      )}
      
      {/* 跃迁时的白屏闪瞎特效 */}
      <div className="hyperspace-flash"></div>
    </div>
  );
}
