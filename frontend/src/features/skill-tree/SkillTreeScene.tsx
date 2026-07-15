import { useMemo, useRef, useState } from 'react';
import { Canvas, useFrame, useThree, type ThreeEvent } from '@react-three/fiber';
import { Html, MapControls, OrthographicCamera, QuadraticBezierLine } from '@react-three/drei';
import { hierarchy, tree, type HierarchyPointNode } from 'd3-hierarchy';
import * as THREE from 'three';
import { useTranslation } from 'react-i18next';
import { domainById, SKILL_DOMAINS } from './taxonomy';
import type { SkillDomain, SkillRecord } from './types';

interface TreeDatum {
  id: string;
  type: 'root' | 'domain' | 'skill';
  domain?: SkillDomain;
  record?: SkillRecord;
  children?: TreeDatum[];
}

interface PositionedNode {
  datum: TreeDatum;
  position: [number, number, number];
  parentPosition?: [number, number, number];
}

interface SkillTreeSceneProps {
  records: SkillRecord[];
  selectedDomainId: string | null;
  selectedSkillId: string | null;
  matchingSkillIds: Set<string>;
  onSelectDomain: (domainId: string) => void;
  onSelectSkill: (record: SkillRecord) => void;
  onClearSelection: () => void;
  reducedMotion: boolean;
}

const TREE_LABEL_Z_RANGE: [number, number] = [8, 1];

function createTree(records: SkillRecord[]): TreeDatum {
  return {
    id: 'noosphere-root',
    type: 'root',
    children: SKILL_DOMAINS.map((domain) => ({
      id: domain.id,
      type: 'domain',
      domain,
      children: records
        .filter((record) => record.domainId === domain.id)
        .map((record) => ({
          id: record.id,
          type: 'skill',
          domain,
          record,
        })),
    })),
  };
}

function layoutTree(records: SkillRecord[], verticalSpan: number): PositionedNode[] {
  const root = hierarchy(createTree(records));
  const layout = tree<TreeDatum>()
    .size([verticalSpan, 9.4])
    .separation((a, b) => (a.parent === b.parent ? 1 : 1.28));
  const positionedRoot = layout(root);

  const positionFor = (node: HierarchyPointNode<TreeDatum>): [number, number, number] => [
    node.y - 4.7,
    verticalSpan / 2 - node.x,
    node.depth === 1 ? 0.12 : 0,
  ];

  return positionedRoot.descendants().map((node) => ({
    datum: node.data,
    position: positionFor(node),
    parentPosition: node.parent ? positionFor(node.parent) : undefined,
  }));
}

function branchMidpoint(
  start: [number, number, number],
  end: [number, number, number],
): [number, number, number] {
  const direction = end[0] >= start[0] ? 1 : -1;
  return [
    start[0] + (end[0] - start[0]) * 0.42,
    start[1] + (end[1] - start[1]) * 0.58,
    0.3 * direction,
  ];
}

function GrowthPulse({
  start,
  end,
  color,
  reducedMotion,
}: {
  start: [number, number, number];
  end: [number, number, number];
  color: string;
  reducedMotion: boolean;
}) {
  const mesh = useRef<THREE.Mesh>(null);
  const curve = useMemo(() => new THREE.QuadraticBezierCurve3(
    new THREE.Vector3(...start),
    new THREE.Vector3(...branchMidpoint(start, end)),
    new THREE.Vector3(...end),
  ), [end, start]);

  useFrame(({ clock }) => {
    if (!mesh.current || reducedMotion) return;
    const point = curve.getPoint((clock.elapsedTime * 0.18) % 1);
    mesh.current.position.copy(point);
  });

  const initial = curve.getPoint(reducedMotion ? 1 : 0);
  return (
    <mesh ref={mesh} position={initial}>
      <sphereGeometry args={[0.055, 10, 10]} />
      <meshBasicMaterial color={color} toneMapped={false} />
    </mesh>
  );
}

function RootNode() {
  return (
    <group>
      <mesh>
        <octahedronGeometry args={[0.3, 0]} />
        <meshStandardMaterial color="#F4F6F8" roughness={0.32} metalness={0.45} />
      </mesh>
      <mesh rotation={[Math.PI / 2, 0, 0]}>
        <torusGeometry args={[0.48, 0.018, 10, 72]} />
        <meshBasicMaterial color="#D9D1C2" transparent opacity={0.62} />
      </mesh>
      <Html center position={[0, -0.66, 0]} zIndexRange={TREE_LABEL_Z_RANGE} className="skill-tree-label skill-tree-root-label">
        <span>NOOSPHERE</span>
      </Html>
    </group>
  );
}

function DomainNode({
  domain,
  count,
  active,
  compact,
  onSelect,
}: {
  domain: SkillDomain;
  count: number;
  active: boolean;
  compact: boolean;
  onSelect: () => void;
}) {
  const { t } = useTranslation();
  const [hovered, setHovered] = useState(false);
  const scale = (active || hovered ? 1.24 : 1) * (compact ? 1.2 : 1);
  return (
    <group>
      <mesh
        onPointerDown={(event: ThreeEvent<PointerEvent>) => {
          event.stopPropagation();
          onSelect();
        }}
        onPointerOver={(event) => {
          event.stopPropagation();
          setHovered(true);
        }}
        onPointerOut={() => setHovered(false)}
      >
        <sphereGeometry args={[0.46, 10, 10]} />
        <meshBasicMaterial transparent opacity={0} depthWrite={false} />
      </mesh>
      <mesh scale={scale}>
        <dodecahedronGeometry args={[0.19, 0]} />
        <meshStandardMaterial
          color={domain.color}
          emissive={domain.color}
          emissiveIntensity={active ? 0.72 : 0.2}
          roughness={0.38}
          metalness={0.3}
        />
      </mesh>
      <mesh scale={active ? 1.1 : 0.84}>
        <torusGeometry args={[0.28, 0.012, 8, 48]} />
        <meshBasicMaterial color={domain.color} transparent opacity={active ? 0.9 : 0.32} />
      </mesh>
      <Html center position={[0, 0.54, 0]} zIndexRange={TREE_LABEL_Z_RANGE} className="skill-tree-label skill-tree-domain-label">
        <span data-domain-label={domain.translationKey}>{t(`skills.domains.${domain.translationKey}`)}</span>
        <small>{count}</small>
      </Html>
    </group>
  );
}

function SkillNode({
  record,
  selected,
  matching,
  showLabel,
  compact,
  onSelect,
}: {
  record: SkillRecord;
  selected: boolean;
  matching: boolean;
  showLabel: boolean;
  compact: boolean;
  onSelect: () => void;
}) {
  const [hovered, setHovered] = useState(false);
  const domain = domainById(record.domainId);
  const emphasized = selected || hovered || matching;
  const scale = (emphasized ? 1.34 : 1) * (compact ? 1.28 : 1);
  const material = (
    <meshStandardMaterial
      color={domain.color}
      emissive={domain.color}
      emissiveIntensity={emphasized ? 0.8 : 0.16}
      roughness={record.kind === 'seed' ? 0.68 : 0.34}
      metalness={record.kind === 'seed' ? 0.1 : 0.42}
      wireframe={record.kind === 'seed'}
    />
  );

  return (
    <group>
      <mesh
        onPointerDown={(event: ThreeEvent<PointerEvent>) => {
          event.stopPropagation();
          onSelect();
        }}
        onPointerOver={(event) => {
          event.stopPropagation();
          setHovered(true);
        }}
        onPointerOut={() => setHovered(false)}
      >
        <sphereGeometry args={[0.42, 10, 10]} />
        <meshBasicMaterial transparent opacity={0} depthWrite={false} />
      </mesh>
      <mesh scale={scale}>
        {record.kind === 'seed' && <octahedronGeometry args={[0.16, 0]} />}
        {record.kind === 'bundled' && <icosahedronGeometry args={[0.15, 0]} />}
        {record.kind === 'published' && <dodecahedronGeometry args={[0.16, 0]} />}
        {material}
      </mesh>
      {record.kind === 'published' && (
        <mesh rotation={[Math.PI / 2, 0, 0]}>
          <torusGeometry args={[0.24, 0.018, 8, 48]} />
          <meshBasicMaterial color={domain.color} transparent opacity={0.86} />
        </mesh>
      )}
      {(showLabel || hovered) && (
        <Html position={[0.34, 0.08, 0]} zIndexRange={TREE_LABEL_Z_RANGE} className="skill-tree-label skill-tree-skill-label">
          <span>{record.name}</span>
        </Html>
      )}
    </group>
  );
}

function ResponsiveTreeCamera() {
  const { size } = useThree();
  const mobile = size.width < 520;
  const zoom = mobile ? 24 : size.width < 900 ? 48 : 72;
  return <OrthographicCamera makeDefault position={[mobile ? 1.3 : 0, 0, 18]} zoom={zoom} near={0.1} far={80} />;
}

function TreeContent({
  records,
  selectedDomainId,
  selectedSkillId,
  matchingSkillIds,
  onSelectDomain,
  onSelectSkill,
  reducedMotion,
}: Omit<SkillTreeSceneProps, 'onClearSelection'>) {
  const { size } = useThree();
  const compact = size.width < 520;
  const verticalSpan = compact ? 16 : size.width < 900 ? 12 : 9.6;
  const nodes = useMemo(() => layoutTree(records, verticalSpan), [records, verticalSpan]);
  const counts = useMemo(() => new Map(SKILL_DOMAINS.map((domain) => [
    domain.id,
    records.filter((record) => record.domainId === domain.id).length,
  ])), [records]);
  const selectedSkillNode = nodes.find((node) => node.datum.id === selectedSkillId);

  return (
    <>
      <color attach="background" args={['#090B0D']} />
      <fog attach="fog" args={['#090B0D', 18, 38]} />
      <ambientLight intensity={0.72} />
      <directionalLight position={[4, 7, 10]} intensity={1.4} color="#F4F6F8" />
      <ResponsiveTreeCamera />

      {nodes.filter((node) => node.parentPosition).map((node) => {
        const domain = node.datum.domain;
        const active = domain?.id === selectedDomainId || node.datum.id === selectedSkillId;
        const matching = node.datum.record ? matchingSkillIds.has(node.datum.record.id) : false;
        const start = node.parentPosition as [number, number, number];
        const end = node.position;
        const color = domain?.color || '#D9D1C2';
        return (
          <QuadraticBezierLine
            key={`link:${node.datum.id}`}
            start={start}
            end={end}
            mid={branchMidpoint(start, end)}
            color={active || matching ? color : '#D9D1C2'}
            lineWidth={node.datum.type === 'domain' ? (active ? 3.5 : 2.2) : (active || matching ? 2.4 : 1.15)}
            transparent
            opacity={active || matching ? 0.94 : node.datum.type === 'domain' ? 0.44 : 0.25}
          />
        );
      })}

      {nodes.map((node) => (
        <group key={node.datum.id} position={node.position}>
          {node.datum.type === 'root' && <RootNode />}
          {node.datum.type === 'domain' && node.datum.domain && (
            <DomainNode
              domain={node.datum.domain}
              count={counts.get(node.datum.domain.id) || 0}
              active={node.datum.domain.id === selectedDomainId}
              compact={compact}
              onSelect={() => onSelectDomain(node.datum.domain?.id || '')}
            />
          )}
          {node.datum.type === 'skill' && node.datum.record && (
            <SkillNode
              record={node.datum.record}
              selected={node.datum.record.id === selectedSkillId}
              matching={matchingSkillIds.has(node.datum.record.id)}
              showLabel={node.datum.record.id === selectedSkillId
                || matchingSkillIds.has(node.datum.record.id)
                || node.datum.record.domainId === selectedDomainId}
              compact={compact}
              onSelect={() => onSelectSkill(node.datum.record as SkillRecord)}
            />
          )}
        </group>
      ))}

      {selectedSkillNode?.parentPosition && selectedSkillNode.datum.domain && (
        <GrowthPulse
          start={selectedSkillNode.parentPosition}
          end={selectedSkillNode.position}
          color={selectedSkillNode.datum.domain.color}
          reducedMotion={reducedMotion}
        />
      )}

      <MapControls
        enableRotate={false}
        enableDamping
        dampingFactor={0.08}
        minZoom={20}
        maxZoom={145}
        screenSpacePanning
      />
    </>
  );
}

export default function SkillTreeScene(props: SkillTreeSceneProps) {
  const { t } = useTranslation();
  return (
    <>
      <div className="skill-tree-canvas" data-testid="skill-tree-canvas" aria-hidden="true">
        <Canvas
          dpr={[1, 1.5]}
          gl={{ antialias: true, alpha: false, powerPreference: 'high-performance' }}
          onPointerMissed={props.onClearSelection}
          fallback={<div className="skill-tree-webgl-fallback">WebGL is required for Tree view. Directory view remains available.</div>}
        >
          <TreeContent {...props} />
        </Canvas>
      </div>
      <nav className="skill-sr-only" aria-label={t('skills.tree')}>
        {SKILL_DOMAINS.map((domain) => (
          <button key={domain.id} onClick={() => props.onSelectDomain(domain.id)}>
            {t(`skills.domains.${domain.translationKey}`)}
          </button>
        ))}
        {props.records.map((record) => (
          <button key={record.id} onClick={() => props.onSelectSkill(record)}>{record.name}</button>
        ))}
      </nav>
    </>
  );
}
