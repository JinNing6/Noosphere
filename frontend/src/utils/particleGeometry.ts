import type * as THREE from 'three';
import type { ParticleData } from '../components/InfiniteParticleEngine';

export function goldenSpherePoint(
  index: number,
  total: number,
  radius: number,
): [number, number, number] {
  const phi = Math.acos(1 - (2 * (index + 0.5)) / total);
  const theta = Math.PI * (1 + Math.sqrt(5)) * index;
  return [
    radius * Math.sin(phi) * Math.cos(theta),
    radius * Math.sin(phi) * Math.sin(theta),
    radius * Math.cos(phi),
  ];
}

export function nodeToParticle(
  position: [number, number, number],
  color: THREE.Color,
  importance: number,
  index: number,
  orbitSpeed: number = 0.03,
  birthTime: number = -10,
  flickerFreq?: number,
  flickerAmp?: number,
): ParticleData {
  return {
    position,
    color: [color.r, color.g, color.b],
    importance: importance / 10,
    seed: (index * 0.618033988749895) % 1.0,
    orbitSpeed,
    glowPhase: (index * 2.399963) % (Math.PI * 2),
    birthTime,
    flickerFreq,
    flickerAmp,
  };
}
