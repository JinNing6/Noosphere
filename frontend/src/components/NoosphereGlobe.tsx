/**
 * @preview
 * NoosphereGlobe — 万物智识圈 3D 核心（极致科幻版）
 *
 * 视觉特性：
 *   🔥 等离子体内核（自定义 Shader 脉动）
 *   💫 氛围光环（替代线框，气体感）
 *   ✨ 自发光节点（emissive glow）
 *   ⚡ 能量脉冲连线（动态光点）
 *   🎬 电影级入场动画（镜头推进 + 涟漪展开）
 *   🌌 后处理：Bloom + Vignette + ChromaticAberration
 */

import { useRef, useMemo, useState, useCallback, useEffect } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls, Stars } from '@react-three/drei';
import { EffectComposer, Bloom, Vignette, ChromaticAberration } from '@react-three/postprocessing';
import { BlendFunction } from 'postprocessing';
import * as THREE from 'three';

import type { KnowledgeNode, Discipline } from '../data/knowledge';
import {
  ALL_NODES, EMERGENCE_LINKS,
  DISCIPLINE_COLORS, LAYER_COLORS,
  DISCIPLINE_GRAVITY_CENTERS,
  gravityClusterPoint,
} from '../data/knowledge';

/* ═══════════════ 工具函数 ═══════════════ */

function goldenSpherePoint(index: number, total: number, radius: number): [number, number, number] {
  const phi = Math.acos(1 - 2 * (index + 0.5) / total);
  const theta = Math.PI * (1 + Math.sqrt(5)) * index;
  return [
    radius * Math.sin(phi) * Math.cos(theta),
    radius * Math.sin(phi) * Math.sin(theta),
    radius * Math.cos(phi),
  ];
}

function getNodeColor(node: KnowledgeNode): string {
  if (node.layer === 'matter') return LAYER_COLORS.matter;
  if (node.layer === 'life') return LAYER_COLORS.life;
  return DISCIPLINE_COLORS[node.discipline || 'ai'] || LAYER_COLORS.civilization;
}


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

  return (
    <group>
      {/* 等离子体核心 */}
      <mesh material={plasmaMat}>
        <sphereGeometry args={[0.8, 64, 64]} />
      </mesh>
      {/* 三层渐变辉光 */}
      <mesh ref={glow1Ref}>
        <sphereGeometry args={[0.8, 32, 32]} />
        <meshBasicMaterial color="#ff6b35" transparent opacity={0.08} side={THREE.BackSide} toneMapped={false} />
      </mesh>
      <mesh ref={glow2Ref}>
        <sphereGeometry args={[0.8, 32, 32]} />
        <meshBasicMaterial color="#7b61ff" transparent opacity={0.04} side={THREE.BackSide} toneMapped={false} />
      </mesh>
      <mesh ref={glow3Ref}>
        <sphereGeometry args={[0.8, 32, 32]} />
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

/* ═══════════════ 物质记忆层（内层 · 自发光） ═══════════════ */

function MatterLayer({ onSelect }: { onSelect: (n: KnowledgeNode) => void }) {
  const nodes = useMemo(() => ALL_NODES.filter(n => n.layer === 'matter'), []);
  const meshRef = useRef<THREE.InstancedMesh>(null);
  const dummy = useMemo(() => new THREE.Object3D(), []);

  const positions = useMemo(() =>
    nodes.map((_, i) => goldenSpherePoint(i, nodes.length, 1.5)),
    [nodes]
  );

  useFrame(({ clock }) => {
    if (!meshRef.current) return;
    const t = clock.getElapsedTime();
    positions.forEach((pos, i) => {
      const drift = Math.sin(t * 0.3 + i) * 0.08;
      dummy.position.set(pos[0] + drift, pos[1] + drift * 0.3, pos[2] + drift);
      const s = 0.1 + (nodes[i].importance / 10) * 0.1;
      dummy.scale.setScalar(s * (1 + Math.sin(t * 0.6 + i * 2) * 0.25));
      dummy.updateMatrix();
      meshRef.current!.setMatrixAt(i, dummy.matrix);
    });
    meshRef.current.instanceMatrix.needsUpdate = true;
  });

  const handleClick = useCallback((e: { stopPropagation: () => void; instanceId?: number }) => {
    e.stopPropagation();
    if (e.instanceId !== undefined && e.instanceId < nodes.length) {
      onSelect(nodes[e.instanceId]);
    }
  }, [nodes, onSelect]);

  return (
    <instancedMesh ref={meshRef} args={[undefined, undefined, nodes.length]} onClick={handleClick}>
      <sphereGeometry args={[1, 16, 16]} />
      <meshStandardMaterial
        color={LAYER_COLORS.matter}
        emissive={LAYER_COLORS.matter}
        emissiveIntensity={2.5}
        toneMapped={false}
      />
    </instancedMesh>
  );
}

/* ═══════════════ 生命经验层（中层 · 有机轨道） ═══════════════ */

function LifeLayer({ onSelect }: { onSelect: (n: KnowledgeNode) => void }) {
  const nodes = useMemo(() => ALL_NODES.filter(n => n.layer === 'life'), []);
  const meshRef = useRef<THREE.InstancedMesh>(null);
  const dummy = useMemo(() => new THREE.Object3D(), []);

  useFrame(({ clock }) => {
    if (!meshRef.current) return;
    const t = clock.getElapsedTime();
    nodes.forEach((node, i) => {
      const angle = (i / nodes.length) * Math.PI * 2 + t * 0.06;
      const r = 2.8 + Math.sin(t * 0.15 + i * 3) * 0.15;
      const y = Math.sin(angle * 2 + t * 0.08) * 0.6;
      dummy.position.set(Math.cos(angle) * r, y, Math.sin(angle) * r);
      const s = 0.12 + (node.importance / 10) * 0.1;
      dummy.scale.setScalar(s * (1 + Math.sin(t + i * 1.5) * 0.2));
      dummy.updateMatrix();
      meshRef.current!.setMatrixAt(i, dummy.matrix);
    });
    meshRef.current.instanceMatrix.needsUpdate = true;
  });

  const handleClick = useCallback((e: { stopPropagation: () => void; instanceId?: number }) => {
    e.stopPropagation();
    if (e.instanceId !== undefined && e.instanceId < nodes.length) {
      onSelect(nodes[e.instanceId]);
    }
  }, [nodes, onSelect]);

  return (
    <instancedMesh ref={meshRef} args={[undefined, undefined, nodes.length]} onClick={handleClick}>
      <sphereGeometry args={[1, 16, 16]} />
      <meshStandardMaterial
        color={LAYER_COLORS.life}
        emissive={LAYER_COLORS.life}
        emissiveIntensity={2.0}
        toneMapped={false}
      />
    </instancedMesh>
  );
}

/* ═══════════════ 文明智慧层（引力聚落 + 呼吸脉动） ═══════════════ */

function CivilizationLayer({ onSelect }: { onSelect: (n: KnowledgeNode) => void }) {
  const nodes = useMemo(() => ALL_NODES.filter(n => n.layer === 'civilization'), []);
  const meshRef = useRef<THREE.InstancedMesh>(null);
  const dummy = useMemo(() => new THREE.Object3D(), []);

  // 按学科分组计数
  const disciplineCounts = useMemo(() => {
    const counts: Record<string, number> = {};
    const indices: Record<string, number> = {};
    nodes.forEach(n => {
      const d = n.discipline || 'ai';
      counts[d] = (counts[d] || 0) + 1;
      indices[d] = 0;
    });
    return { counts, indices };
  }, [nodes]);

  // 引力聚落初始位置（确定性）
  const basePositions = useMemo(() => {
    const idxTracker: Record<string, number> = {};
    return nodes.map((node) => {
      const d = node.discipline || 'ai';
      if (idxTracker[d] === undefined) idxTracker[d] = 0;
      const idx = idxTracker[d]++;
      const total = disciplineCounts.counts[d] || 1;
      return gravityClusterPoint(node, idx, total, 4.5);
    });
  }, [nodes, disciplineCounts]);

  // 颜色
  const colorsArray = useMemo(() => {
    const arr = new Float32Array(nodes.length * 3);
    nodes.forEach((node, i) => {
      const c = new THREE.Color(getNodeColor(node));
      arr[i * 3] = c.r;
      arr[i * 3 + 1] = c.g;
      arr[i * 3 + 2] = c.b;
    });
    return arr;
  }, [nodes]);

  // 动画帧：呼吸脉动
  useFrame(({ clock }) => {
    if (!meshRef.current) return;
    const t = clock.getElapsedTime();

    nodes.forEach((node, i) => {
      const pos = basePositions[i];
      const discipline = (node.discipline || 'ai') as Discipline;
      const center = DISCIPLINE_GRAVITY_CENTERS[discipline];

      // 呼吸因子：星团周期性收缩-扩散（±8%）
      const breathPhase = Math.sin(t * (2 * Math.PI / center.breathPeriod)) * 0.08;
      const breathScale = 1 + breathPhase;

      // 方向向量（从原点到节点）
      const len = Math.sqrt(pos[0] ** 2 + pos[1] ** 2 + pos[2] ** 2);
      const nx = pos[0] / len, ny = pos[1] / len, nz = pos[2] / len;

      // 呼吸 + 微漂移
      const drift = Math.sin(t * 0.1 + i * 0.7) * 0.05;
      dummy.position.set(
        pos[0] * breathScale + nx * drift,
        pos[1] * breathScale + ny * drift,
        pos[2] * breathScale + nz * drift,
      );

      const s = 0.08 + (node.importance / 10) * 0.08;
      dummy.scale.setScalar(s * (1 + Math.sin(t * 0.3 + i) * 0.1));
      dummy.updateMatrix();
      meshRef.current!.setMatrixAt(i, dummy.matrix);
    });
    meshRef.current.instanceMatrix.needsUpdate = true;
  });

  const handleClick = useCallback((e: { stopPropagation: () => void; instanceId?: number }) => {
    e.stopPropagation();
    if (e.instanceId !== undefined && e.instanceId < nodes.length) {
      onSelect(nodes[e.instanceId]);
    }
  }, [nodes, onSelect]);

  useEffect(() => {
    if (meshRef.current) {
      meshRef.current.geometry.setAttribute(
        'color',
        new THREE.InstancedBufferAttribute(colorsArray, 3)
      );
    }
  }, [colorsArray]);

  return (
    <instancedMesh ref={meshRef} args={[undefined, undefined, nodes.length]} onClick={handleClick}>
      <sphereGeometry args={[1, 12, 12]} />
      <meshStandardMaterial
        vertexColors
        emissive="#ffffff"
        emissiveIntensity={1.5}
        toneMapped={false}
      />
    </instancedMesh>
  );
}

/* ═══════════════ 能量脉冲连线 ═══════════════ */

function EnergyLines() {
  const groupRef = useRef<THREE.Group>(null);
  const pulsePointsRef = useRef<THREE.Points>(null);

  // 构建曲线 + 脉冲光点
  const { lines, pulseCount, curveData } = useMemo(() => {
    const lineObjs: THREE.Line[] = [];
    const curves: { curve: THREE.QuadraticBezierCurve3; fromColor: THREE.Color; toColor: THREE.Color }[] = [];
    let count = 0;

    EMERGENCE_LINKS.forEach((link, i) => {
      const fromNode = ALL_NODES.find(n => n.id === link.from);
      const toNode = ALL_NODES.find(n => n.id === link.to);
      if (!fromNode || !toNode) return;

      const fromIdx = ALL_NODES.filter(n => n.layer === fromNode.layer).indexOf(fromNode);
      const fromTotal = ALL_NODES.filter(n => n.layer === fromNode.layer).length;
      const toIdx = ALL_NODES.filter(n => n.layer === toNode.layer).indexOf(toNode);
      const toTotal = ALL_NODES.filter(n => n.layer === toNode.layer).length;

      const fromR = fromNode.layer === 'matter' ? 1.5 : fromNode.layer === 'life' ? 2.8 : 4.5;
      const toR = toNode.layer === 'matter' ? 1.5 : toNode.layer === 'life' ? 2.8 : 4.5;

      const fromPos = goldenSpherePoint(fromIdx, fromTotal, fromR);
      const toPos = goldenSpherePoint(toIdx, toTotal, toR);

      const mid: [number, number, number] = [
        (fromPos[0] + toPos[0]) * 0.5 + Math.sin(i * 2.7) * 1.0,
        (fromPos[1] + toPos[1]) * 0.5 + Math.cos(i * 1.3) * 1.0,
        (fromPos[2] + toPos[2]) * 0.5 + Math.sin(i * 3.1) * 1.0,
      ];

      const curve = new THREE.QuadraticBezierCurve3(
        new THREE.Vector3(...fromPos),
        new THREE.Vector3(...mid),
        new THREE.Vector3(...toPos),
      );
      const points = curve.getPoints(50);
      const geometry = new THREE.BufferGeometry().setFromPoints(points);

      // 渐变色
      const fromColor = new THREE.Color(getNodeColor(fromNode));
      const toColor = new THREE.Color(getNodeColor(toNode));
      const colors = new Float32Array(points.length * 3);
      points.forEach((_, pi) => {
        const t = pi / (points.length - 1);
        const c = fromColor.clone().lerp(toColor, t);
        colors[pi * 3] = c.r;
        colors[pi * 3 + 1] = c.g;
        colors[pi * 3 + 2] = c.b;
      });
      geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));

      const material = new THREE.LineBasicMaterial({
        vertexColors: true, transparent: true, opacity: 0.15, toneMapped: false,
      });

      lineObjs.push(new THREE.Line(geometry, material));
      curves.push({ curve, fromColor, toColor });
      count++;
    });

    return { lines: lineObjs, pulseCount: count, curveData: curves };
  }, []);

  // 脉冲光点动画
  useFrame(({ clock }) => {
    if (!pulsePointsRef.current) return;
    const t = clock.getElapsedTime();
    const posArr = pulsePointsRef.current.geometry.attributes.position.array as Float32Array;
    const colArr = pulsePointsRef.current.geometry.attributes.color.array as Float32Array;

    curveData.forEach((cd, i) => {
      const progress = (t * 0.15 + i * 0.15) % 1;
      const pt = cd.curve.getPoint(progress);
      posArr[i * 3] = pt.x;
      posArr[i * 3 + 1] = pt.y;
      posArr[i * 3 + 2] = pt.z;
      const c = cd.fromColor.clone().lerp(cd.toColor, progress);
      colArr[i * 3] = c.r;
      colArr[i * 3 + 1] = c.g;
      colArr[i * 3 + 2] = c.b;
    });
    pulsePointsRef.current.geometry.attributes.position.needsUpdate = true;
    pulsePointsRef.current.geometry.attributes.color.needsUpdate = true;

    // 连线呼吸
    lines.forEach((line, i) => {
      (line.material as THREE.LineBasicMaterial).opacity = 0.1 + Math.sin(t * 0.4 + i * 1.3) * 0.06;
    });
  });

  // 脉冲光点初始化
  const pulseGeo = useMemo(() => {
    const pos = new Float32Array(pulseCount * 3);
    const col = new Float32Array(pulseCount * 3);
    return { pos, col };
  }, [pulseCount]);

  return (
    <group ref={groupRef}>
      {lines.map((line, i) => (
        <primitive key={i} object={line} />
      ))}
      <points ref={pulsePointsRef}>
        <bufferGeometry>
          <bufferAttribute attach="attributes-position" args={[pulseGeo.pos, 3]} />
          <bufferAttribute attach="attributes-color" args={[pulseGeo.col, 3]} />
        </bufferGeometry>
        <pointsMaterial size={0.08} vertexColors transparent opacity={0.9} toneMapped={false} sizeAttenuation />
      </points>
    </group>
  );
}

/* ═══════════════ 浮游意识尘埃 ═══════════════ */

function ConsciousnessDust() {
  const count = 500;
  const pointsRef = useRef<THREE.Points>(null);

  const [positions, velocities, colors] = useMemo(() => {
    const pos = new Float32Array(count * 3);
    const vel = new Float32Array(count * 3);
    const col = new Float32Array(count * 3);
    const palette = [
      new THREE.Color('#ff6b35'), new THREE.Color('#7b61ff'),
      new THREE.Color('#00e878'), new THREE.Color('#4488ff'),
      new THREE.Color('#ffd700'), new THREE.Color('#e0e0ff'),
    ];
    for (let i = 0; i < count; i++) {
      const r = 0.5 + Math.random() * 7;
      const theta = Math.random() * Math.PI * 2;
      const phi = Math.acos(2 * Math.random() - 1);
      pos[i * 3] = r * Math.sin(phi) * Math.cos(theta);
      pos[i * 3 + 1] = r * Math.sin(phi) * Math.sin(theta);
      pos[i * 3 + 2] = r * Math.cos(phi);
      vel[i * 3] = (Math.random() - 0.5) * 0.001;
      vel[i * 3 + 1] = (Math.random() - 0.5) * 0.001;
      vel[i * 3 + 2] = (Math.random() - 0.5) * 0.001;
      const c = palette[Math.floor(Math.random() * palette.length)];
      col[i * 3] = c.r;
      col[i * 3 + 1] = c.g;
      col[i * 3 + 2] = c.b;
    }
    return [pos, vel, col];
  }, []);

  useFrame(() => {
    if (!pointsRef.current) return;
    const posAttr = pointsRef.current.geometry.attributes.position as THREE.BufferAttribute;
    const arr = posAttr.array as Float32Array;
    for (let i = 0; i < count; i++) {
      arr[i * 3] += velocities[i * 3];
      arr[i * 3 + 1] += velocities[i * 3 + 1];
      arr[i * 3 + 2] += velocities[i * 3 + 2];
      const dist = Math.sqrt(arr[i * 3] ** 2 + arr[i * 3 + 1] ** 2 + arr[i * 3 + 2] ** 2);
      if (dist > 8 || dist < 0.5) {
        velocities[i * 3] *= -1;
        velocities[i * 3 + 1] *= -1;
        velocities[i * 3 + 2] *= -1;
      }
    }
    posAttr.needsUpdate = true;
  });

  return (
    <points ref={pointsRef}>
      <bufferGeometry>
        <bufferAttribute attach="attributes-position" args={[positions, 3]} />
        <bufferAttribute attach="attributes-color" args={[colors, 3]} />
      </bufferGeometry>
      <pointsMaterial
        size={0.015}
        vertexColors
        transparent
        opacity={0.4}
        toneMapped={false}
        sizeAttenuation
        blending={THREE.AdditiveBlending}
        depthWrite={false}
      />
    </points>
  );
}

/* ═══════════════ 场景内容 ═══════════════ */

function SceneContent({ onSelect, introPhase }: { onSelect: (n: KnowledgeNode) => void; introPhase: number }) {
  const controlsRef = useRef<any>(null);

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
      <ambientLight intensity={0.15} />
      <pointLight position={[0, 0, 0]} intensity={0.5} color="#ff6b35" distance={8} decay={2} />

      {/* 深空星云 */}
      <Stars radius={80} depth={100} count={5000} factor={4} saturation={0.3} fade speed={0.3} />

      {/* 等离子体内核 */}
      <PlasmaCore />

      {/* 氛围光环 */}
      <AtmosphereRings />

      {/* 三层意识 */}
      <MatterLayer onSelect={onSelect} />
      <LifeLayer onSelect={onSelect} />
      <CivilizationLayer onSelect={onSelect} />

      {/* 能量脉冲连线 */}
      <EnergyLines />

      {/* 意识尘埃 */}
      <ConsciousnessDust />

      {/* 后处理 — 电影级 */}
      <EffectComposer multisampling={0}>
        <Bloom
          luminanceThreshold={0.1}
          luminanceSmoothing={0.4}
          intensity={1.5}
          mipmapBlur
        />
        <Vignette offset={0.3} darkness={0.7} blendFunction={BlendFunction.NORMAL} />
        <ChromaticAberration
          offset={new THREE.Vector2(0.0006, 0.0006)}
          blendFunction={BlendFunction.NORMAL}
          radialModulation={true}
          modulationOffset={0.5}
        />
      </EffectComposer>

      {/* 控制器 */}
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
    </>
  );
}

/* ═══════════════ 电影级入场覆盖 ═══════════════ */

function CinematicIntro({ phase, onComplete }: { phase: number; onComplete: () => void }) {
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
          THE COLLECTIVE CONSCIOUSNESS NETWORK
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
          万物存在本身的意识脉动
        </div>
      </div>
    </div>
  );
}

/* ═══════════════ 主组件 ═══════════════ */

interface NoosphereGlobeProps {
  onSelectNode: (node: KnowledgeNode) => void;
  searchQuery?: string;
}

export default function NoosphereGlobe({ onSelectNode }: NoosphereGlobeProps) {
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
        gl={{
          antialias: true,
          alpha: false,
          powerPreference: 'high-performance',
          toneMapping: THREE.ACESFilmicToneMapping,
          toneMappingExposure: 1.0,
        }}
      >
        <SceneContent onSelect={onSelectNode} introPhase={introPhase} />
      </Canvas>
    </div>
  );
}
