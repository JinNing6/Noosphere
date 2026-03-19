/**
 * @preview
 * NoosphereGlobe — 万物智识圈 3D 核心（无限粒子版 v3）
 *
 * 视觉特性：
 *   🔥 等离子体内核（自定义 Shader 脉动）
 *   💫 氛围光环（替代线框，气体感）
 *   ✨ GPU 驱动粒子层 × 3（物质/生命/文明）
 *   🌌 无限意识体云（预分配 10 万容量池）
 *   ⚡ 能量脉冲连线（合并 LineSegments）
 *   🌀 意识星云（GPU Points 替代旧尘埃）
 *   🎬 电影级入场动画（镜头推进 + 涟漪展开）
 *   🌌 后处理：Bloom + Vignette
 *
 * 性能架构（v3 — 无限粒子）：
 *   🚀 所有粒子动画在 GPU Vertex Shader 中并行计算
 *   🧱 InstancedMesh 预分配容量池，动态 count 控制
 *   ♻️ 每帧 O(1) — 仅更新 uTime uniform (4 bytes)
 *   📦 InstancedBufferAttribute + DynamicDrawUsage 增量更新
 *   📐 DPR 上限 1.5 + Bloom 固定分辨率 512
 *   🎯 最大支持：100,000+ 粒子流畅渲染
 */

import { useRef, useMemo, useState, useCallback, useEffect } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls, Stars } from '@react-three/drei';
import { EffectComposer, Bloom, Vignette } from '@react-three/postprocessing';
import { BlendFunction } from 'postprocessing';
import * as THREE from 'three';
import { useTranslation } from 'react-i18next';

import type { KnowledgeNode, Discipline } from '../data/knowledge';
import {
  ALL_NODES, EMERGENCE_LINKS,
  DISCIPLINE_COLORS, LAYER_COLORS,
  DISCIPLINE_GRAVITY_CENTERS,
  gravityClusterPoint,
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

/* ═══════════════ 工具函数 ═══════════════ */

function getNodeColor(node: KnowledgeNode): string {
  if (node.layer === 'matter') return LAYER_COLORS.matter;
  if (node.layer === 'life') return LAYER_COLORS.life;
  return DISCIPLINE_COLORS[node.discipline || 'ai'] || LAYER_COLORS.civilization;
}

/* ═══════════════ 预计算索引映射（O(1) 查找） ═══════════════ */

const NODE_BY_ID = new Map(ALL_NODES.map(n => [n.id, n]));
const NODE_INDEX_IN_LAYER = new Map<string, number>();
const LAYER_COUNTS: Record<string, number> = { matter: 0, life: 0, civilization: 0 };

// 统计各层节点数量
ALL_NODES.forEach(n => {
  LAYER_COUNTS[n.layer] = (LAYER_COUNTS[n.layer] || 0) + 1;
});
// 构建每个节点在其所属层内的索引
const _layerCounters: Record<string, number> = { matter: 0, life: 0, civilization: 0 };
ALL_NODES.forEach(n => {
  NODE_INDEX_IN_LAYER.set(n.id, _layerCounters[n.layer]++);
});
// 层 → 球面半径映射
const LAYER_RADIUS: Record<string, number> = { matter: 1.5, life: 2.8, civilization: 4.5 };


/* ═══════════════ 预计算静态粒子数据 ═══════════════ */

/** 将所有静态节点预转换为 GPU 粒子数据 */
function buildLayerParticles(layer: 'matter' | 'life' | 'civilization'): ParticleData[] {
  const nodes = ALL_NODES.filter(n => n.layer === layer);
  const radius = LAYER_RADIUS[layer];

  // 轨道速度按层设置
  const orbitSpeeds: Record<string, number> = {
    matter: 0.0,    // 物质层：静态呼吸
    life: 0.06,     // 生命层：缓慢轨道
    civilization: 0.0, // 文明层：引力聚落呼吸
  };

  return nodes.map((node, i) => {
    let position: [number, number, number];

    if (layer === 'civilization') {
      // 文明层使用引力聚落分布
      const discipline = (node.discipline || 'ai') as Discipline;
      const discNodes = nodes.filter(n => (n.discipline || 'ai') === discipline);
      const discIdx = discNodes.indexOf(node);
      position = gravityClusterPoint(node, discIdx, discNodes.length, radius);
    } else {
      // 物质/生命层使用黄金角球面分布
      position = goldenSpherePoint(i, nodes.length, radius);
    }

    const color = new THREE.Color(getNodeColor(node));

    return nodeToParticle(
      position,
      color,
      node.importance,
      i,
      orbitSpeeds[layer],
    );
  });
}

// 模块级预计算
const MATTER_PARTICLES = buildLayerParticles('matter');
const LIFE_PARTICLES = buildLayerParticles('life');
const CIVILIZATION_PARTICLES = buildLayerParticles('civilization');


/* ═══════════════ 等离子体内核组件 ═══════════════ */

function PlasmaCore() {
  const glow1Ref = useRef<THREE.Mesh>(null);
  const glow2Ref = useRef<THREE.Mesh>(null);
  const glow3Ref = useRef<THREE.Mesh>(null);

  const plasmaMat = useMemo(() => new THREE.ShaderMaterial({
    uniforms: {
      uTime: { value: 0 },
      uColor1: { value: new THREE.Color('#ff6b35') },
      uColor2: { value: new THREE.Color('#7b61ff') },
      uColor3: { value: new THREE.Color('#00e878') },
    },
    vertexShader: `
      varying vec3 vPosition;
      varying vec3 vNormal;
      uniform float uTime;
      void main() {
        vPosition = position;
        vNormal = normalize(normalMatrix * normal);
        vec3 pos = position;
        float noise = sin(pos.x * 3.0 + uTime * 0.8) * sin(pos.y * 4.0 + uTime * 0.6) * sin(pos.z * 3.5 + uTime * 0.7);
        pos += normal * noise * 0.08;
        gl_Position = projectionMatrix * modelViewMatrix * vec4(pos, 1.0);
      }
    `,
    fragmentShader: `
      varying vec3 vPosition;
      varying vec3 vNormal;
      uniform float uTime;
      uniform vec3 uColor1;
      uniform vec3 uColor2;
      uniform vec3 uColor3;
      float hash(vec3 p) {
        p = fract(p * 0.3183099 + 0.1);
        p *= 17.0;
        return fract(p.x * p.y * p.z * (p.x + p.y + p.z));
      }
      float noise3d(vec3 x) {
        vec3 i = floor(x);
        vec3 f = fract(x);
        f = f * f * (3.0 - 2.0 * f);
        return mix(mix(mix(hash(i), hash(i + vec3(1,0,0)), f.x),
                       mix(hash(i + vec3(0,1,0)), hash(i + vec3(1,1,0)), f.x), f.y),
                   mix(mix(hash(i + vec3(0,0,1)), hash(i + vec3(1,0,1)), f.x),
                       mix(hash(i + vec3(0,1,1)), hash(i + vec3(1,1,1)), f.x), f.y), f.z);
      }
      void main() {
        float n = noise3d(vPosition * 3.0 + uTime * 0.3);
        float n2 = noise3d(vPosition * 5.0 - uTime * 0.2);
        float n3 = noise3d(vPosition * 8.0 + uTime * 0.5);
        float pattern = n * 0.5 + n2 * 0.3 + n3 * 0.2;
        vec3 color = mix(uColor1, uColor2, pattern);
        color = mix(color, uColor3, n3 * 0.3);
        float fresnel = pow(1.0 - abs(dot(vNormal, vec3(0,0,1))), 2.0);
        color += fresnel * 0.4;
        float brightness = 1.2 + sin(uTime * 0.8) * 0.3;
        gl_FragColor = vec4(color * brightness, 0.85);
      }
    `,
    transparent: true,
    toneMapped: false,
  }), []);

  useFrame(({ clock }) => {
    const t = clock.getElapsedTime();
    plasmaMat.uniforms.uTime.value = t;
    if (glow1Ref.current) {
      const s = 1.3 + Math.sin(t * 0.5) * 0.1;
      glow1Ref.current.scale.setScalar(s);
      (glow1Ref.current.material as THREE.MeshBasicMaterial).opacity = 0.08 + Math.sin(t * 0.3) * 0.03;
    }
    if (glow2Ref.current) {
      const s = 1.7 + Math.sin(t * 0.35) * 0.15;
      glow2Ref.current.scale.setScalar(s);
      (glow2Ref.current.material as THREE.MeshBasicMaterial).opacity = 0.04 + Math.sin(t * 0.25) * 0.02;
    }
    if (glow3Ref.current) {
      const s = 2.2 + Math.sin(t * 0.2) * 0.2;
      glow3Ref.current.scale.setScalar(s);
      (glow3Ref.current.material as THREE.MeshBasicMaterial).opacity = 0.02 + Math.sin(t * 0.15) * 0.01;
    }
  });

  // 共享辉光球几何体（减少 GPU 资源重复）
  const glowGeo = useMemo(() => new THREE.SphereGeometry(0.8, 32, 32), []);

  return (
    <group>
      {/* 等离子体核心 */}
      <mesh material={plasmaMat}>
        <sphereGeometry args={[0.8, 48, 48]} />
      </mesh>
      {/* 三层渐变辉光 — 共享 geometry */}
      <mesh ref={glow1Ref} geometry={glowGeo}>
        <meshBasicMaterial color="#ff6b35" transparent opacity={0.08} side={THREE.BackSide} toneMapped={false} />
      </mesh>
      <mesh ref={glow2Ref} geometry={glowGeo}>
        <meshBasicMaterial color="#7b61ff" transparent opacity={0.04} side={THREE.BackSide} toneMapped={false} />
      </mesh>
      <mesh ref={glow3Ref} geometry={glowGeo}>
        <meshBasicMaterial color="#00e878" transparent opacity={0.02} side={THREE.BackSide} toneMapped={false} />
      </mesh>
    </group>
  );
}

/* ═══════════════ 氛围光环（替代线框） ═══════════════ */

function AtmosphereRings() {
  const ring1Ref = useRef<THREE.Mesh>(null);
  const ring2Ref = useRef<THREE.Mesh>(null);

  useFrame(({ clock }) => {
    const t = clock.getElapsedTime();
    if (ring1Ref.current) {
      ring1Ref.current.rotation.x = Math.sin(t * 0.05) * 0.1;
      ring1Ref.current.rotation.z = t * 0.02;
    }
    if (ring2Ref.current) {
      ring2Ref.current.rotation.y = Math.cos(t * 0.04) * 0.15;
      ring2Ref.current.rotation.z = -t * 0.015;
    }
  });

  return (
    <group>
      {/* 内环 — 物质→生命过渡 */}
      <mesh ref={ring1Ref} rotation={[Math.PI * 0.5, 0, 0]}>
        <torusGeometry args={[2.1, 0.15, 16, 100]} />
        <meshBasicMaterial color={LAYER_COLORS.matter} transparent opacity={0.04} toneMapped={false} side={THREE.DoubleSide} />
      </mesh>
      {/* 外环 — 生命→文明过渡 */}
      <mesh ref={ring2Ref} rotation={[Math.PI * 0.4, 0.3, 0]}>
        <torusGeometry args={[3.6, 0.12, 16, 100]} />
        <meshBasicMaterial color={LAYER_COLORS.life} transparent opacity={0.03} toneMapped={false} side={THREE.DoubleSide} />
      </mesh>
    </group>
  );
}

/* ═══════════════ 能量脉冲连线（完全 GPU 驱动版） ═══════════════ */

function EnergyLines() {
  const lineRef = useRef<THREE.LineSegments>(null);

  // 预计算：合并所有曲线到单一几何体 + GPU 脉冲曲线数据
  const { mergedPositions, mergedColors, pulseCurves } = useMemo(() => {
    const POINTS_PER_CURVE = 31;

    const validLinks: { fromPos: [number,number,number]; toPos: [number,number,number]; mid: [number,number,number]; fromColor: THREE.Color; toColor: THREE.Color }[] = [];

    EMERGENCE_LINKS.forEach((link, i) => {
      const fromNode = NODE_BY_ID.get(link.from);
      const toNode = NODE_BY_ID.get(link.to);
      if (!fromNode || !toNode) return;

      const fromIdx = NODE_INDEX_IN_LAYER.get(fromNode.id) ?? 0;
      const fromTotal = LAYER_COUNTS[fromNode.layer] ?? 1;
      const toIdx = NODE_INDEX_IN_LAYER.get(toNode.id) ?? 0;
      const toTotal = LAYER_COUNTS[toNode.layer] ?? 1;

      const fromR = LAYER_RADIUS[fromNode.layer] ?? 4.5;
      const toR = LAYER_RADIUS[toNode.layer] ?? 4.5;

      const fromPos = goldenSpherePoint(fromIdx, fromTotal, fromR);
      const toPos = goldenSpherePoint(toIdx, toTotal, toR);

      const mid: [number, number, number] = [
        (fromPos[0] + toPos[0]) * 0.5 + Math.sin(i * 2.7) * 1.0,
        (fromPos[1] + toPos[1]) * 0.5 + Math.cos(i * 1.3) * 1.0,
        (fromPos[2] + toPos[2]) * 0.5 + Math.sin(i * 3.1) * 1.0,
      ];

      const fromColor = new THREE.Color(getNodeColor(fromNode));
      const toColor = new THREE.Color(getNodeColor(toNode));
      validLinks.push({ fromPos, toPos, mid, fromColor, toColor });
    });

    // 构建合并 LineSegments 几何体
    const SEGMENTS_PER_CURVE = POINTS_PER_CURVE - 1;
    const VERTS_PER_CURVE = SEGMENTS_PER_CURVE * 2;
    const totalVerts = validLinks.length * VERTS_PER_CURVE;
    const positions = new Float32Array(totalVerts * 3);
    const colors = new Float32Array(totalVerts * 3);
    const interpColor = new THREE.Color();

    // GPU 脉冲数据
    const gpuPulses: PulseCurveData[] = [];

    validLinks.forEach((vl, linkI) => {
      const curve = new THREE.QuadraticBezierCurve3(
        new THREE.Vector3(...vl.fromPos),
        new THREE.Vector3(...vl.mid),
        new THREE.Vector3(...vl.toPos),
      );
      const points = curve.getPoints(POINTS_PER_CURVE - 1);
      const baseVert = linkI * VERTS_PER_CURVE;

      for (let seg = 0; seg < SEGMENTS_PER_CURVE; seg++) {
        const v0 = baseVert + seg * 2;
        const v1 = v0 + 1;
        const p0 = points[seg];
        const p1 = points[seg + 1];

        positions[v0 * 3]     = p0.x; positions[v0 * 3 + 1] = p0.y; positions[v0 * 3 + 2] = p0.z;
        positions[v1 * 3]     = p1.x; positions[v1 * 3 + 1] = p1.y; positions[v1 * 3 + 2] = p1.z;

        const t0 = seg / SEGMENTS_PER_CURVE;
        const t1 = (seg + 1) / SEGMENTS_PER_CURVE;
        interpColor.copy(vl.fromColor).lerp(vl.toColor, t0);
        colors[v0 * 3] = interpColor.r; colors[v0 * 3 + 1] = interpColor.g; colors[v0 * 3 + 2] = interpColor.b;
        interpColor.copy(vl.fromColor).lerp(vl.toColor, t1);
        colors[v1 * 3] = interpColor.r; colors[v1 * 3 + 1] = interpColor.g; colors[v1 * 3 + 2] = interpColor.b;
      }

      // 收集 GPU 脉冲数据
      gpuPulses.push({
        start: vl.fromPos,
        mid: vl.mid,
        end: vl.toPos,
        fromColor: [vl.fromColor.r, vl.fromColor.g, vl.fromColor.b],
        toColor: [vl.toColor.r, vl.toColor.g, vl.toColor.b],
        phaseOffset: linkI * 0.15,
      });
    });

    return { mergedPositions: positions, mergedColors: colors, pulseCurves: gpuPulses };
  }, []);

  const lineGeometry = useMemo(() => {
    const geo = new THREE.BufferGeometry();
    geo.setAttribute('position', new THREE.BufferAttribute(mergedPositions, 3));
    geo.setAttribute('color', new THREE.BufferAttribute(mergedColors, 3));
    return geo;
  }, [mergedPositions, mergedColors]);

  const lineMaterial = useMemo(() => new THREE.LineBasicMaterial({
    vertexColors: true, transparent: true, opacity: 0.15, toneMapped: false,
  }), []);

  // 仅线条呼吸 — O(1)
  useFrame(({ clock }) => {
    lineMaterial.opacity = 0.1 + Math.sin(clock.getElapsedTime() * 0.4) * 0.06;
  });

  useEffect(() => {
    return () => { lineGeometry.dispose(); lineMaterial.dispose(); };
  }, [lineGeometry, lineMaterial]);

  return (
    <group>
      <lineSegments ref={lineRef} geometry={lineGeometry} material={lineMaterial} />
      {/* GPU 驱动脉冲光点 — 零 JS 端遍历 */}
      <GPUPulsePoints curves={pulseCurves} />
    </group>
  );
}

/* ═══════════════ GPU 粒子层组件适配器 ═══════════════ */

/**
 * StaticGPULayer — 将预计算的静态粒子数据渲染到 GPU 粒子层
 */
function StaticGPULayer({
  particles,
  onSelect,
  nodes,
  orbitEnabled = false,
  breathScale = 1.0,
  driftScale = 1.0,
}: {
  particles: ParticleData[];
  onSelect: (n: KnowledgeNode) => void;
  nodes: KnowledgeNode[];
  orbitEnabled?: boolean;
  breathScale?: number;
  driftScale?: number;
}) {
  const handleClick = useCallback(
    (instanceId: number) => {
      if (instanceId < nodes.length) {
        onSelect(nodes[instanceId]);
      }
    },
    [nodes, onSelect]
  );

  return (
    <GPUParticleLayer
      maxCapacity={Math.max(particles.length, 1000)}
      initialParticles={particles}
      onClick={handleClick}
      orbitEnabled={orbitEnabled}
      breathScale={breathScale}
      driftScale={driftScale}
    />
  );
}

/**
 * DynamicFlowLines — 动态意识体间的真实关联流光连线
 * 
 * 连线策略（基于真实数据）:
 * 1. 演化链连线（强流光）: parentId 有值的意识体 → 与其父意识之间绘制明亮流光
 * 2. 共振连线（弱流光）: 拥有相同 tags 的意识体之间绘制淡流光
 * 3. 距离近邻补充: 上述连线不足时，补充最近邻连线
 */
function DynamicFlowLines({
  particles,
  nodes,
}: {
  particles: ParticleData[];
  nodes: KnowledgeNode[];
}) {
  const pulseCurves = useMemo(() => {
    if (particles.length < 2 || nodes.length < 2) return [];

    const curves: PulseCurveData[] = [];
    const used = new Set<string>();
    const nodeIdToIdx = new Map<string, number>();
    nodes.forEach((n, i) => nodeIdToIdx.set(n.id, i));

    // 辅助函数：生成两点之间的贝塞尔流光数据
    const createCurve = (i: number, j: number): PulseCurveData | null => {
      if (i >= particles.length || j >= particles.length || i === j) return null;
      const key = `${Math.min(i, j)}-${Math.max(i, j)}`;
      if (used.has(key)) return null;
      used.add(key);

      const pi = particles[i];
      const pj = particles[j];
      const mid: [number, number, number] = [
        (pi.position[0] + pj.position[0]) * 0.5 + (Math.sin(i * 2.7 + j * 1.3) * 0.6),
        (pi.position[1] + pj.position[1]) * 0.5 + (Math.cos(i * 1.3 + j * 2.7) * 0.6),
        (pi.position[2] + pj.position[2]) * 0.5 + (Math.sin(i * 3.1 + j * 0.7) * 0.6),
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

    // ── 策略1: 演化链连线（parentId → 父节点）──
    for (let i = 0; i < nodes.length; i++) {
      const node = nodes[i];
      if (node.parentId) {
        const parentIdx = nodeIdToIdx.get(node.parentId);
        if (parentIdx !== undefined) {
          const curve = createCurve(i, parentIdx);
          if (curve) curves.push(curve);
        }
      }
    }

    // ── 策略2: 共振连线（共享标签）──
    // 构建 tag → node indices 映射
    const tagToNodes = new Map<string, number[]>();
    nodes.forEach((n, i) => {
      for (const tag of n.tags) {
        // 跳过 by: 前缀和类型标签，只用实质标签
        if (tag.startsWith('by:') || ['epiphany', 'warning', 'pattern', 'decision'].includes(tag)) continue;
        const list = tagToNodes.get(tag) || [];
        list.push(i);
        tagToNodes.set(tag, list);
      }
    });

    // 对共享标签的意识体配对（限制每个 tag 最多 3 条连线防止过密）
    for (const [, indices] of tagToNodes) {
      if (indices.length < 2) continue;
      let tagCurves = 0;
      for (let a = 0; a < indices.length && tagCurves < 3; a++) {
        for (let b = a + 1; b < indices.length && tagCurves < 3; b++) {
          const curve = createCurve(indices[a], indices[b]);
          if (curve) {
            curves.push(curve);
            tagCurves++;
          }
        }
      }
    }

    // ── 策略3: 距离近邻补充（当连线数不足时）──
    if (curves.length < 5 && particles.length >= 2) {
      for (let i = 0; i < Math.min(particles.length, 20); i++) {
        if (curves.length >= 15) break;  // 上限 15 条连线
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
    }

    return curves;
  }, [particles, nodes]);

  if (pulseCurves.length === 0) return null;
  return <GPUPulsePoints curves={pulseCurves} />;
}

/**
 * DynamicConsciousnessCloud — 无限意识体云
 * 使用 GPUParticleLayer 的 ref API 实现增量添加
 * ✨ 新增：birthTime 标记新入场粒子 + 流光连线
 */
function DynamicConsciousnessCloud({
  nodes,
  onSelect,
}: {
  nodes: KnowledgeNode[];
  onSelect: (n: KnowledgeNode) => void;
}) {
  const layerRef = useRef<GPUParticleLayerHandle>(null);
  const prevCountRef = useRef(0);
  const birthTimeRef = useRef<number>(0);

  // 记录组件挂载时间作为初始 birthTime 基线
  useFrame(({ clock }) => {
    birthTimeRef.current = clock.getElapsedTime();
  });

  // 当 nodes 变化时转换为 ParticleData
  const particles = useMemo(() => {
    return nodes.map((node, i) => {
      const position = goldenSpherePoint(i, Math.max(nodes.length, 1), 5.5);
      const color = new THREE.Color('#00d4ff');
      // 新粒子标记当前时间用于闪烁入场效果
      const bt = i >= prevCountRef.current ? birthTimeRef.current : -10;
      return nodeToParticle(position, color, node.importance, i, 0.03, bt);
    });
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [nodes]);

  // 当新粒子被添加时，使用增量更新
  useEffect(() => {
    const layer = layerRef.current;
    if (!layer) return;

    if (nodes.length > prevCountRef.current) {
      // 有新增节点 — 增量添加
      const newParticles = particles.slice(prevCountRef.current);
      layer.addParticles(newParticles);
    } else if (nodes.length < prevCountRef.current) {
      // 节点减少（不太常见） — 全量重建
      layer.clear();
      layer.addParticles(particles);
    }

    prevCountRef.current = nodes.length;
  }, [nodes, particles]);

  const handleClick = useCallback(
    (instanceId: number) => {
      if (instanceId < nodes.length) {
        onSelect(nodes[instanceId]);
      }
    },
    [nodes, onSelect]
  );

  if (nodes.length === 0) return null;

  return (
    <group>
      <GPUParticleLayer
        ref={layerRef}
        maxCapacity={100_000}
        initialParticles={particles}
        onClick={handleClick}
        orbitEnabled={true}
        breathScale={1.2}
        driftScale={1.5}
        enableFlicker={true}
      />
      {/* 动态意识体间的流光连线 — 基于 parentId 和 tags 真实关联 */}
      <DynamicFlowLines particles={particles} nodes={nodes} />
    </group>
  );
}


/* ═══════════════ 场景内容（渐进式加载） ═══════════════ */

/**
 * 性能优化：分阶段挂载重型组件，避免一帧内编译所有 Shader / 创建所有 Geometry
 *
 * Stage 0 (立即):    灯光 + PlasmaCore + OrbitControls
 * Stage 1 (+100ms):  Stars + AtmosphereRings
 * Stage 2 (+250ms):  三层 GPU 粒子意识节点
 * Stage 3 (+500ms):  EnergyLines + ConsciousnessNebula + EffectComposer + DynamicCloud
 */
function SceneContent({ onSelect, introPhase, dynamicNodes }: { onSelect: (n: KnowledgeNode) => void; introPhase: number; dynamicNodes: KnowledgeNode[] }) {
  const controlsRef = useRef<any>(null);
  const [loadStage, setLoadStage] = useState(0);

  // 静态节点列表（模块级缓存）
  const matterNodes = useMemo(() => ALL_NODES.filter(n => n.layer === 'matter'), []);
  const lifeNodes = useMemo(() => ALL_NODES.filter(n => n.layer === 'life'), []);
  const civNodes = useMemo(() => ALL_NODES.filter(n => n.layer === 'civilization'), []);

  // 渐进式加载调度
  useEffect(() => {
    const t1 = setTimeout(() => setLoadStage(1), 100);
    const t2 = setTimeout(() => setLoadStage(2), 250);
    const t3 = setTimeout(() => setLoadStage(3), 500);
    return () => { clearTimeout(t1); clearTimeout(t2); clearTimeout(t3); };
  }, []);

  // 入场相机动画
  useFrame(({ camera, clock }) => {
    if (introPhase < 2) {
      const t = clock.getElapsedTime();
      const progress = Math.min(t / 4, 1);
      const ease = 1 - Math.pow(1 - progress, 3); // easeOutCubic
      const startDist = 25;
      const endDist = 10;
      const dist = startDist - (startDist - endDist) * ease;
      camera.position.set(
        Math.sin(t * 0.1) * dist * 0.2,
        2 + (1 - ease) * 3,
        dist
      );
      camera.lookAt(0, 0, 0);
    }
  });

  return (
    <>
      {/* ── Stage 0: 核心骨架（立即） ── */}
      <ambientLight intensity={0.15} />
      <pointLight position={[0, 0, 0]} intensity={0.5} color="#ff6b35" distance={8} decay={2} />
      <PlasmaCore />
      <OrbitControls
        ref={controlsRef}
        enablePan={false}
        minDistance={3}
        maxDistance={18}
        autoRotate
        autoRotateSpeed={0.2}
        dampingFactor={0.05}
        enableDamping
      />

      {/* ── Stage 1: 背景层 (+100ms) ── */}
      {loadStage >= 1 && (
        <>
          <Stars radius={80} depth={100} count={1500} factor={4} saturation={0.3} fade speed={0.3} />
          <AtmosphereRings />
        </>
      )}

      {/* ── Stage 2: GPU 粒子意识节点 (+250ms) ── */}
      {loadStage >= 2 && (
        <>
          {/* 物质记忆层 — 静态呼吸脉动 */}
          <StaticGPULayer
            particles={MATTER_PARTICLES}
            nodes={matterNodes}
            onSelect={onSelect}
            orbitEnabled={false}
            breathScale={0.8}
            driftScale={0.6}
          />
          {/* 生命经验层 — 缓慢轨道 */}
          <StaticGPULayer
            particles={LIFE_PARTICLES}
            nodes={lifeNodes}
            onSelect={onSelect}
            orbitEnabled={true}
            breathScale={1.0}
            driftScale={1.0}
          />
          {/* 文明智慧层 — 引力聚落呼吸 */}
          <StaticGPULayer
            particles={CIVILIZATION_PARTICLES}
            nodes={civNodes}
            onSelect={onSelect}
            orbitEnabled={false}
            breathScale={1.2}
            driftScale={0.8}
          />
        </>
      )}

      {/* ── Stage 3: 装饰 + 后处理 + 无限意识体云 (+500ms) ── */}
      {loadStage >= 3 && (
        <>
          <EnergyLines />
          {/* 意识星云（GPU Points — 8000 粒子 + 分层颜色） */}
          <ConsciousnessNebula count={8000} innerRadius={0.5} outerRadius={8.0} />
          {/* 无限意识体云（动态加载，预分配 10 万容量） */}
          <DynamicConsciousnessCloud nodes={dynamicNodes} onSelect={onSelect} />
          <EffectComposer multisampling={0}>
            <Bloom
              luminanceThreshold={0.1}
              luminanceSmoothing={0.4}
              intensity={1.5}
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

/* ═══════════════ 电影级入场覆盖 ═══════════════ */

function CinematicIntro({ phase, onComplete }: { phase: number; onComplete: () => void }) {
  const { t } = useTranslation();

  useEffect(() => {
    const timer = setTimeout(onComplete, 5000);
    return () => clearTimeout(timer);
  }, [onComplete]);

  if (phase >= 2) return null;

  return (
    <div style={{
      position: 'absolute', inset: 0, zIndex: 100,
      pointerEvents: 'none',
      display: 'flex', flexDirection: 'column',
      alignItems: 'center', justifyContent: 'center',
    }}>
      {/* 文字覆盖 */}
      <div style={{
        textAlign: 'center', color: '#e0e0ff',
        fontFamily: "'Inter', sans-serif",
        animation: phase === 0 ? 'fadeIn 2s ease forwards' : 'fadeOut 2s ease forwards',
      }}>
        {/* 光点 */}
        <div style={{
          width: 6, height: 6, borderRadius: '50%',
          background: 'radial-gradient(circle, #ff6b35, #7b61ff)',
          margin: '0 auto 32px',
          boxShadow: '0 0 40px rgba(255, 107, 53, 0.6), 0 0 80px rgba(123, 97, 255, 0.3)',
          animation: 'coreExpand 3s ease-out forwards',
        }} />

        <div style={{
          fontSize: 11, letterSpacing: '0.5em', opacity: 0.5,
          marginBottom: 12,
          animation: 'slideUp 2s ease 0.5s both',
        }}>
          {t('intro.subtitle')}
        </div>

        <div style={{
          fontSize: 28, fontWeight: 200, letterSpacing: '0.2em',
          animation: 'slideUp 2s ease 1s both',
          background: 'linear-gradient(135deg, #ff6b35, #7b61ff, #00e878)',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent',
        }}>
          NOOSPHERE
        </div>

        <div style={{
          fontSize: 12, letterSpacing: '0.15em', opacity: 0.3,
          marginTop: 16,
          animation: 'slideUp 2s ease 1.5s both',
        }}>
          {t('intro.tagline')}
        </div>
      </div>
    </div>
  );
}

/* ═══════════════ 主组件 ═══════════════ */

interface NoosphereGlobeProps {
  onSelectNode: (node: KnowledgeNode) => void;
  onBackgroundClick?: () => void;
  searchQuery?: string;
  dynamicNodes?: KnowledgeNode[];
}

export default function NoosphereGlobe({ onSelectNode, onBackgroundClick, dynamicNodes = [] }: NoosphereGlobeProps) {
  const [introPhase, setIntroPhase] = useState(0);

  const handleIntroComplete = useCallback(() => {
    setIntroPhase(1);
    setTimeout(() => setIntroPhase(2), 2000);
  }, []);

  return (
    <div style={{ position: 'relative', width: '100%', height: '100%' }}>
      <CinematicIntro phase={introPhase} onComplete={handleIntroComplete} />

      <Canvas
        camera={{ position: [0, 5, 25], fov: 50 }}
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
        <SceneContent onSelect={onSelectNode} introPhase={introPhase} dynamicNodes={dynamicNodes} />
      </Canvas>
    </div>
  );
}
