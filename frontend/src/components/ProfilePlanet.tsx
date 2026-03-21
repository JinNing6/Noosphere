/**
 * @preview
 * ProfilePlanet — 个人意识星球 3D 组件
 *
 * 精简版 NoosphereGlobe，仅渲染指定用户的意识碎片。
 * 用于个人可分享页面（类似 GitHub Skyline）。
 *
 * 视觉特性：
 *   🔥 小型等离子体内核
 *   ✨ GPU 粒子（用户意识碎片）
 *   🌌 背景星空 + Bloom 后处理
 *   🌀 自动旋转（适合截图/分享）
 */

import { useRef, useMemo, useState, useCallback, useEffect } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls, Stars } from '@react-three/drei';
import { EffectComposer, Bloom, Vignette } from '@react-three/postprocessing';
import { BlendFunction } from 'postprocessing';
import * as THREE from 'three';

import type { KnowledgeNode } from '../data/knowledge';
import {
  CONSCIOUSNESS_TYPE_COLORS,
  CONSCIOUSNESS_TYPE_FLICKER,
} from '../data/knowledge';

import {
  GPUParticleLayer,
  ConsciousnessNebula,
  GPUPulsePoints,
  goldenSpherePoint,
  nodeToParticle,
  type ParticleData,
  type PulseCurveData,
  type GPUParticleLayerHandle,
} from './InfiniteParticleEngine';

/* ═══════════════ 辅助函数 ═══════════════ */

function parseColorToThreeColor(colorStr: string): THREE.Color {
  if (colorStr.startsWith('hsl')) {
    const match = colorStr.match(/hsl\((\d+),\s*(\d+)%,\s*(\d+)%\)/);
    if (match) {
      const h = parseInt(match[1]) / 360;
      const s = parseInt(match[2]) / 100;
      const l = parseInt(match[3]) / 100;
      return new THREE.Color().setHSL(h, s, l);
    }
  }
  return new THREE.Color(colorStr);
}

/* ═══════════════ 个人等离子内核（精简版） ═══════════════ */

function ProfileCore({ fragmentCount }: { fragmentCount: number }) {
  const glow1Ref = useRef<THREE.Mesh>(null);
  const glow2Ref = useRef<THREE.Mesh>(null);

  // 内核大小随碎片数量动态缩放
  const coreScale = useMemo(() => {
    return 0.4 + Math.min(fragmentCount / 50, 0.6);
  }, [fragmentCount]);

  const plasmaMat = useMemo(() => new THREE.ShaderMaterial({
    uniforms: {
      uTime: { value: 0 },
      uColor1: { value: new THREE.Color('#7b61ff') },
      uColor2: { value: new THREE.Color('#00e878') },
    },
    vertexShader: `
      varying vec3 vNormal;
      uniform float uTime;
      void main() {
        vNormal = normalize(normalMatrix * normal);
        vec3 pos = position;
        float noise = sin(pos.x * 4.0 + uTime) * sin(pos.y * 3.0 + uTime * 0.7) * 0.06;
        pos += normal * noise;
        gl_Position = projectionMatrix * modelViewMatrix * vec4(pos, 1.0);
      }
    `,
    fragmentShader: `
      varying vec3 vNormal;
      uniform float uTime;
      uniform vec3 uColor1;
      uniform vec3 uColor2;
      void main() {
        float fresnel = pow(1.0 - abs(dot(vNormal, vec3(0,0,1))), 2.0);
        float t = sin(uTime * 0.5) * 0.5 + 0.5;
        vec3 color = mix(uColor1, uColor2, t);
        color += fresnel * 0.5;
        float brightness = 1.0 + sin(uTime * 0.6) * 0.2;
        gl_FragColor = vec4(color * brightness, 0.9);
      }
    `,
    transparent: true,
    toneMapped: false,
  }), []);

  const glowGeo = useMemo(() => new THREE.SphereGeometry(coreScale, 32, 32), [coreScale]);

  useFrame(({ clock }) => {
    const t = clock.getElapsedTime();
    plasmaMat.uniforms.uTime.value = t;
    if (glow1Ref.current) {
      const s = 1.4 + Math.sin(t * 0.4) * 0.1;
      glow1Ref.current.scale.setScalar(s);
      (glow1Ref.current.material as THREE.MeshBasicMaterial).opacity = 0.06 + Math.sin(t * 0.3) * 0.02;
    }
    if (glow2Ref.current) {
      const s = 2.0 + Math.sin(t * 0.25) * 0.15;
      glow2Ref.current.scale.setScalar(s);
      (glow2Ref.current.material as THREE.MeshBasicMaterial).opacity = 0.03 + Math.sin(t * 0.2) * 0.01;
    }
  });

  return (
    <group>
      <mesh material={plasmaMat}>
        <sphereGeometry args={[coreScale, 40, 40]} />
      </mesh>
      <mesh ref={glow1Ref} geometry={glowGeo}>
        <meshBasicMaterial color="#7b61ff" transparent opacity={0.06} side={THREE.BackSide} toneMapped={false} />
      </mesh>
      <mesh ref={glow2Ref} geometry={glowGeo}>
        <meshBasicMaterial color="#00e878" transparent opacity={0.03} side={THREE.BackSide} toneMapped={false} />
      </mesh>
    </group>
  );
}

/* ═══════════════ 个人意识碎片云 ═══════════════ */

function ProfileConsciousnessCloud({
  nodes,
  onSelect,
}: {
  nodes: KnowledgeNode[];
  onSelect: (n: KnowledgeNode) => void;
}) {
  const layerRef = useRef<GPUParticleLayerHandle>(null);

  const particles = useMemo(() => {
    const radius = 2.0 + Math.min(nodes.length / 20, 2.0);
    return nodes.map((node, i) => {
      const position = goldenSpherePoint(i, Math.max(nodes.length, 1), radius);

      let color: THREE.Color;
      if (node.computedColor) {
        color = parseColorToThreeColor(node.computedColor);
      } else if (node.consciousnessType && CONSCIOUSNESS_TYPE_COLORS[node.consciousnessType]) {
        color = new THREE.Color(CONSCIOUSNESS_TYPE_COLORS[node.consciousnessType]);
      } else {
        color = new THREE.Color('#e0e0ff');
      }

      const flicker = CONSCIOUSNESS_TYPE_FLICKER[node.consciousnessType || 'epiphany'] || { freq: 2.0, amp: 0.4 };
      return nodeToParticle(position, color, node.importance, i, 0.04, -10, flicker.freq, flicker.amp);
    });
  }, [nodes]);

  // 流光连线（距离近邻 + 共享标签）
  const pulseCurves = useMemo(() => {
    if (particles.length < 2) return [];

    const curves: PulseCurveData[] = [];
    const used = new Set<string>();

    const createCurve = (i: number, j: number): PulseCurveData | null => {
      if (i >= particles.length || j >= particles.length || i === j) return null;
      const key = `${Math.min(i, j)}-${Math.max(i, j)}`;
      if (used.has(key)) return null;
      used.add(key);

      const pi = particles[i];
      const pj = particles[j];
      const mid: [number, number, number] = [
        (pi.position[0] + pj.position[0]) * 0.5 + Math.sin(i * 2.7 + j * 1.3) * 0.4,
        (pi.position[1] + pj.position[1]) * 0.5 + Math.cos(i * 1.3 + j * 2.7) * 0.4,
        (pi.position[2] + pj.position[2]) * 0.5 + Math.sin(i * 3.1 + j * 0.7) * 0.4,
      ];

      return {
        start: pi.position,
        mid,
        end: pj.position,
        fromColor: pi.color,
        toColor: pj.color,
        phaseOffset: (i * 0.618 + j * 0.382) % 1.0,
      };
    };

    // 近邻连线
    for (let i = 0; i < Math.min(particles.length, 30); i++) {
      if (curves.length >= 20) break;
      const pi = particles[i];
      const distances: { idx: number; dist: number }[] = [];
      for (let j = 0; j < particles.length; j++) {
        if (j === i) continue;
        const pj = particles[j];
        const dx = pi.position[0] - pj.position[0];
        const dy = pi.position[1] - pj.position[1];
        const dz = pi.position[2] - pj.position[2];
        distances.push({ idx: j, dist: Math.sqrt(dx * dx + dy * dy + dz * dz) });
      }
      distances.sort((a, b) => a.dist - b.dist);
      for (let k = 0; k < Math.min(2, distances.length); k++) {
        const curve = createCurve(i, distances[k].idx);
        if (curve) curves.push(curve);
      }
    }

    return curves;
  }, [particles]);

  const handleClick = useCallback(
    (instanceId: number) => {
      if (instanceId < nodes.length) {
        onSelect(nodes[instanceId]);
      }
    },
    [nodes, onSelect],
  );

  if (nodes.length === 0) return null;

  return (
    <group>
      <GPUParticleLayer
        ref={layerRef}
        maxCapacity={10_000}
        initialParticles={particles}
        onClick={handleClick}
        orbitEnabled={true}
        breathScale={1.2}
        driftScale={1.5}
        enableFlicker={true}
      />
      {pulseCurves.length > 0 && <GPUPulsePoints curves={pulseCurves} />}
    </group>
  );
}

/* ═══════════════ 场景内容 ═══════════════ */

function ProfileSceneContent({
  nodes,
  onSelect,
}: {
  nodes: KnowledgeNode[];
  onSelect: (n: KnowledgeNode) => void;
}) {
  const [ready, setReady] = useState(false);

  useEffect(() => {
    const timer = setTimeout(() => setReady(true), 300);
    return () => clearTimeout(timer);
  }, []);

  // 相机缓慢靠近
  useFrame(({ camera, clock }) => {
    const t = clock.getElapsedTime();
    if (t < 4) {
      const progress = Math.min(t / 4, 1);
      const ease = 1 - Math.pow(1 - progress, 3);
      const dist = 12 - ease * 4;
      camera.position.set(
        Math.sin(t * 0.15) * dist * 0.15,
        1.5 + (1 - ease) * 2,
        dist,
      );
      camera.lookAt(0, 0, 0);
    }
  });

  return (
    <>
      <ambientLight intensity={0.15} />
      <pointLight position={[0, 0, 0]} intensity={0.4} color="#7b61ff" distance={6} decay={2} />
      <ProfileCore fragmentCount={nodes.length} />
      <OrbitControls
        enablePan={false}
        minDistance={2}
        maxDistance={14}
        autoRotate
        autoRotateSpeed={0.4}
        dampingFactor={0.05}
        enableDamping
      />
      <Stars radius={60} depth={80} count={1200} factor={3} saturation={0.3} fade speed={0.3} />

      {ready && (
        <>
          <ProfileConsciousnessCloud nodes={nodes} onSelect={onSelect} />
          <ConsciousnessNebula count={3000} innerRadius={0.3} outerRadius={5.0} />
          <EffectComposer multisampling={0}>
            <Bloom
              luminanceThreshold={0.1}
              luminanceSmoothing={0.4}
              intensity={1.8}
              mipmapBlur
              width={512}
              height={512}
            />
            <Vignette offset={0.3} darkness={0.7} blendFunction={BlendFunction.NORMAL} />
          </EffectComposer>
        </>
      )}
    </>
  );
}

/* ═══════════════ 主组件 ═══════════════ */

interface ProfilePlanetProps {
  nodes: KnowledgeNode[];
  onSelectNode: (node: KnowledgeNode) => void;
  onBackgroundClick?: () => void;
}

export default function ProfilePlanet({ nodes, onSelectNode, onBackgroundClick }: ProfilePlanetProps) {
  return (
    <div style={{ position: 'relative', width: '100%', height: '100%' }}>
      <Canvas
        camera={{ position: [0, 3, 12], fov: 45 }}
        style={{ background: '#050510' }}
        dpr={[1, 1.5]}
        onPointerMissed={onBackgroundClick}
        gl={{
          antialias: true,
          alpha: false,
          powerPreference: 'high-performance',
          toneMapping: THREE.ACESFilmicToneMapping,
          toneMappingExposure: 1.0,
        }}
      >
        <ProfileSceneContent nodes={nodes} onSelect={onSelectNode} />
      </Canvas>
    </div>
  );
}
