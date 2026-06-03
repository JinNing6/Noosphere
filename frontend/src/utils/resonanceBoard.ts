import type { KnowledgeNode } from '../data/knowledge';
import { createNoosphereIssueUrl, NOOSPHERE_HOME_URL } from './issueDeepLink';
import { CONTRIBUTION_ACTION, MARKETPLACE_INSTALL_COMMAND } from './growthCopy';

export interface ResonanceTypeRow {
  type: string;
  count: number;
}

export interface ResonanceCreatorRow {
  creator: string;
  count: number;
}

export interface ResonanceBoardSummary {
  totalMemories: number;
  mediaMemories: number;
  totalResonance: number;
  typeRows: ResonanceTypeRow[];
  topCreators: ResonanceCreatorRow[];
  latestMemory: KnowledgeNode | null;
}

const TYPE_ORDER = ['warning', 'pattern', 'decision', 'epiphany', 'image', 'video', 'voice'];

function compactLine(value: string | undefined, maxLength: number): string {
  const normalized = (value || '').replace(/\s+/g, ' ').trim();
  if (normalized.length <= maxLength) return normalized;
  return `${normalized.slice(0, Math.max(0, maxLength - 3)).trimEnd()}...`;
}

function readCreator(node: KnowledgeNode): string {
  const byTag = node.tags.find(tag => tag.startsWith('by:'))?.slice(3).trim();
  const creator = byTag || node.title_en || 'Anonymous';
  if (!creator || creator === '\u533f\u540d' || creator === 'Anonymous Consciousness') return 'Anonymous';
  return creator;
}

function readType(node: KnowledgeNode): string {
  return node.consciousnessType || node.mediaType || 'memory';
}

export function summarizeResonanceBoard(nodes: KnowledgeNode[]): ResonanceBoardSummary {
  const typeCounts = new Map<string, number>();
  const creatorCounts = new Map<string, number>();

  for (const node of nodes) {
    const type = readType(node);
    const creator = readCreator(node);
    typeCounts.set(type, (typeCounts.get(type) || 0) + 1);
    creatorCounts.set(creator, (creatorCounts.get(creator) || 0) + 1);
  }

  const typeRows = Array.from(typeCounts, ([type, count]) => ({ type, count }))
    .sort((a, b) => {
      if (b.count !== a.count) return b.count - a.count;
      const orderA = TYPE_ORDER.indexOf(a.type);
      const orderB = TYPE_ORDER.indexOf(b.type);
      return (orderA === -1 ? 99 : orderA) - (orderB === -1 ? 99 : orderB);
    });

  const topCreators = Array.from(creatorCounts, ([creator, count]) => ({ creator, count }))
    .sort((a, b) => b.count - a.count || a.creator.localeCompare(b.creator))
    .slice(0, 4);

  return {
    totalMemories: nodes.length,
    mediaMemories: nodes.filter(node => Boolean(node.mediaType)).length,
    totalResonance: nodes.reduce((total, node) => total + (node.resonanceCount || 0), 0),
    typeRows,
    topCreators,
    latestMemory: nodes[0] || null,
  };
}

export function createResonanceBoardSharePost(summary: ResonanceBoardSummary): string {
  const latest = summary.latestMemory;
  const latestTitle = latest
    ? compactLine(latest.title_zh || latest.title_en || latest.id, 74)
    : 'Be the first to upload a reusable Agent memory';
  const latestUrl = latest?.issueNumber
    ? createNoosphereIssueUrl(latest.issueNumber)
    : NOOSPHERE_HOME_URL;

  return [
    'Noosphere live memory network',
    `${summary.totalMemories} real memories - ${summary.mediaMemories} media memories - ${summary.totalResonance} resonance`,
    `Latest: ${latestTitle}`,
    `Open: ${latestUrl}`,
    `Install: ${MARKETPLACE_INSTALL_COMMAND}`,
    `Upload: ${CONTRIBUTION_ACTION.url}`,
  ].join('\n');
}
