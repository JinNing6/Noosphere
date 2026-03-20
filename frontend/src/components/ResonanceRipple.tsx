/**
 * @preview
 * ResonanceRipple — 共振涟漪 GPU 渲染组件
 *
 * 当意识体收到共振时，从粒子位置向外扩散圆环光波。
 * 
 * 触发方式：
 *   1. URL 参数 ?ripple=<nodeId> — MCP 共振后用户点击链接进入
 *   2. 轮询检测 resonance_count 变化 — 后台自动触发
 *   3. 手动触发 — 通过 ref API
 *
 * GPU 架构：
 *   - 环形缓冲区预分配 MAX_RIPPLES 个涟漪槽位
 *   - 每个涟漪 = 1 个扩散圆环 (RingGeometry + ShaderMaterial)
 *   - 生命周期 3 秒：快速扩张 + 渐渐透明
 *   - 额外的闪光爆发粒子 (Points) 8 个方向飞散
 */

import { useRef, useMemo, useCallback, useImperativeHandle, forwardRef } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';

/* ═══════════════ 类型定义 ═══════════════ */

export interface RippleEvent {
  position: [number, number, number];
  color: [number, number, number];
  intensity?: number;  // 1.0 = 普通, 2.0+ = 超级共振
}

export interface ResonanceRippleHandle {
  triggerRipple: (event: RippleEvent) => void;
}

/* ═══════════════ 常量 ═══════════════ */

const MAX_RIPPLES = 20;
const RIPPLE_DURATION = 3.0; // 秒
const RIPPLE_MAX_RADIUS = 3.0;
const BURST_PARTICLES_PER_RIPPLE = 8;

/* ═══════════════ Shader — 涟漪光环 ═══════════════ */

const RIPPLE_RING_VERTEX = /* glsl */ `
  uniform float uTime;
  uniform float uBirthTime;
  uniform float uIntensity;
  uniform vec3 uCenter;
  
  varying float vAlpha;
  varying vec3 vColor;
  
  void main() {
    float age = uTime - uBirthTime;
    if (age < 0.0 || age > ${RIPPLE_DURATION.toFixed(1)}) {
      gl_Position = vec4(0.0, 0.0, -999.0, 1.0);
      vAlpha = 0.0;
      return;
    }
    
    // 扩张进度: easeOutCubic
    float progress = age / ${RIPPLE_DURATION.toFixed(1)};
    float ease = 1.0 - pow(1.0 - progress, 3.0);
    float radius = ease * ${RIPPLE_MAX_RADIUS.toFixed(1)} * uIntensity;
    
    // 扩张圆环
    vec3 pos = position * radius + uCenter;
    
    vec4 mvPosition = modelViewMatrix * vec4(pos, 1.0);
    gl_Position = projectionMatrix * mvPosition;
    
    // 透明度: 快速出现，缓慢消失
    float fadeIn = smoothstep(0.0, 0.1, progress);
    float fadeOut = 1.0 - smoothstep(0.3, 1.0, progress);
    vAlpha = fadeIn * fadeOut * 0.8 * uIntensity;
  }
`;

const RIPPLE_RING_FRAGMENT = /* glsl */ `
  uniform vec3 uColor;
  varying float vAlpha;
  
  void main() {
    if (vAlpha < 0.01) discard;
    // 环形辉光
    vec3 glow = uColor * (1.5 + vAlpha);
    gl_FragColor = vec4(glow, vAlpha);
  }
`;

/* ═══════════════ Shader — 爆发粒子 ═══════════════ */

const BURST_VERTEX = /* glsl */ `
  attribute vec3 aDirection;
  attribute float aBurstId;
  
  uniform float uTime;
  uniform float uBirthTimes[${MAX_RIPPLES}];
  uniform vec3 uCenters[${MAX_RIPPLES}];
  uniform vec3 uColors[${MAX_RIPPLES}];
  uniform float uIntensities[${MAX_RIPPLES}];
  
  varying vec3 vColor;
  varying float vAlpha;
  
  void main() {
    int id = int(aBurstId);
    float birthTime = uBirthTimes[id];
    float age = uTime - birthTime;
    
    if (age < 0.0 || age > ${RIPPLE_DURATION.toFixed(1)}) {
      gl_Position = vec4(0.0, 0.0, -999.0, 1.0);
      vAlpha = 0.0;
      return;
    }
    
    float progress = age / ${RIPPLE_DURATION.toFixed(1)};
    float ease = 1.0 - pow(1.0 - progress, 2.0);
    float intensity = uIntensities[id];
    
    // 粒子径向飞散
    vec3 pos = uCenters[id] + aDirection * ease * 2.5 * intensity;
    
    vec4 mvPosition = modelViewMatrix * vec4(pos, 1.0);
    gl_Position = projectionMatrix * mvPosition;
    
    // 粒子大小脉冲
    float sizePulse = (1.0 - progress) * (1.0 + sin(age * 15.0) * 0.3);
    gl_PointSize = (8.0 * sizePulse * intensity) * (200.0 / -mvPosition.z);
    
    vColor = uColors[id] * (2.0 - progress);
    vAlpha = (1.0 - smoothstep(0.4, 1.0, progress)) * 0.9;
  }
`;

const BURST_FRAGMENT = /* glsl */ `
  varying vec3 vColor;
  varying float vAlpha;
  
  void main() {
    if (vAlpha < 0.01) discard;
    vec2 center = gl_PointCoord - 0.5;
    float dist = length(center);
    if (dist > 0.5) discard;
    
    float core = exp(-dist * 8.0);
    float glow = exp(-dist * 3.0) * 0.4;
    float alpha = (core + glow) * vAlpha;
    
    gl_FragColor = vec4(vColor * (core * 2.0 + glow), alpha);
  }
`;

/* ═══════════════ 组件 ═══════════════ */

export const ResonanceRipple = forwardRef<ResonanceRippleHandle>(
  function ResonanceRipple(_, ref) {
    const nextSlotRef = useRef(0);

    // ── 涟漪圆环数据 ──
    const ringRefs = useRef<THREE.Mesh[]>([]);
    const ringMaterials = useMemo(() => {
      return Array.from({ length: MAX_RIPPLES }, () =>
        new THREE.ShaderMaterial({
          uniforms: {
            uTime: { value: 0 },
            uBirthTime: { value: -999 },
            uCenter: { value: new THREE.Vector3(0, 0, 0) },
            uColor: { value: new THREE.Color(1, 1, 1) },
            uIntensity: { value: 1.0 },
          },
          vertexShader: RIPPLE_RING_VERTEX,
          fragmentShader: RIPPLE_RING_FRAGMENT,
          transparent: true,
          toneMapped: false,
          depthWrite: false,
          blending: THREE.AdditiveBlending,
          side: THREE.DoubleSide,
        })
      );
    }, []);

    // 共享圆环几何体
    const ringGeo = useMemo(() => new THREE.RingGeometry(0.85, 1.0, 64), []);

    // ── 爆发粒子 ──
    const burstUniforms = useMemo(() => ({
      uTime: { value: 0 },
      uBirthTimes: { value: new Float32Array(MAX_RIPPLES).fill(-999) },
      uCenters: { value: Array.from({ length: MAX_RIPPLES }, () => new THREE.Vector3()) },
      uColors: { value: Array.from({ length: MAX_RIPPLES }, () => new THREE.Color()) },
      uIntensities: { value: new Float32Array(MAX_RIPPLES).fill(1.0) },
    }), []);

    const { burstPositions, burstDirections, burstIds } = useMemo(() => {
      const total = MAX_RIPPLES * BURST_PARTICLES_PER_RIPPLE;
      const pos = new Float32Array(total * 3);
      const dir = new Float32Array(total * 3);
      const ids = new Float32Array(total);

      for (let r = 0; r < MAX_RIPPLES; r++) {
        for (let p = 0; p < BURST_PARTICLES_PER_RIPPLE; p++) {
          const idx = r * BURST_PARTICLES_PER_RIPPLE + p;
          const angle = (p / BURST_PARTICLES_PER_RIPPLE) * Math.PI * 2;
          const elevation = (Math.random() - 0.5) * 0.6;

          dir[idx * 3] = Math.cos(angle) * Math.cos(elevation);
          dir[idx * 3 + 1] = Math.sin(elevation);
          dir[idx * 3 + 2] = Math.sin(angle) * Math.cos(elevation);
          ids[idx] = r;
        }
      }

      return { burstPositions: pos, burstDirections: dir, burstIds: ids };
    }, []);

    const burstMaterial = useMemo(() =>
      new THREE.ShaderMaterial({
        uniforms: burstUniforms,
        vertexShader: BURST_VERTEX,
        fragmentShader: BURST_FRAGMENT,
        transparent: true,
        toneMapped: false,
        depthWrite: false,
        blending: THREE.AdditiveBlending,
      }),
    [burstUniforms]);

    // ── 触发涟漪 ──
    const triggerRipple = useCallback((event: RippleEvent) => {
      const slot = nextSlotRef.current % MAX_RIPPLES;
      nextSlotRef.current++;

      const time = performance.now() / 1000; // 近似全局时间
      const intensity = event.intensity ?? 1.0;

      // 更新圆环 material
      const mat = ringMaterials[slot];
      mat.uniforms.uBirthTime.value = time;
      mat.uniforms.uCenter.value.set(...event.position);
      mat.uniforms.uColor.value.setRGB(...event.color);
      mat.uniforms.uIntensity.value = intensity;

      // 更新爆发粒子 uniforms
      burstUniforms.uBirthTimes.value[slot] = time;
      burstUniforms.uCenters.value[slot].set(...event.position);
      burstUniforms.uColors.value[slot].setRGB(...event.color);
      burstUniforms.uIntensities.value[slot] = intensity;
    }, [ringMaterials, burstUniforms]);

    useImperativeHandle(ref, () => ({ triggerRipple }), [triggerRipple]);

    // ── 每帧更新时间 ──
    useFrame(({ clock }) => {
      const t = clock.getElapsedTime();
      ringMaterials.forEach(mat => { mat.uniforms.uTime.value = t; });
      burstMaterial.uniforms.uTime.value = t;
    });

    return (
      <group>
        {/* 涟漪圆环 */}
        {ringMaterials.map((mat, i) => (
          <mesh
            key={`ripple-ring-${i}`}
            ref={(el) => { if (el) ringRefs.current[i] = el; }}
            material={mat}
            geometry={ringGeo}
          />
        ))}

        {/* 爆发粒子 */}
        <points material={burstMaterial}>
          <bufferGeometry>
            <bufferAttribute attach="attributes-position" args={[burstPositions, 3]} />
            <bufferAttribute attach="attributes-aDirection" args={[burstDirections, 3]} />
            <bufferAttribute attach="attributes-aBurstId" args={[burstIds, 1]} />
          </bufferGeometry>
        </points>
      </group>
    );
  }
);
