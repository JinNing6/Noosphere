import type { KnowledgeNode } from '../data/knowledge';
import { CONTRIBUTION_ACTION, MARKETPLACE_INSTALL_COMMAND } from './growthCopy';
import { createNoosphereIssueUrl, NOOSPHERE_HOME_URL } from './issueDeepLink';
import { summarizeResonanceBoard } from './resonanceBoard';
import { createShareProofIssueUrl, SHARE_PROOF_DISCLAIMER } from './shareProofs';

export interface LaunchKitPost {
  channel: string;
  title: string;
  body: string;
  proofUrl: string;
  actionUrl: string;
}

function compactLine(value: string | undefined, maxLength: number): string {
  const normalized = (value || '').replace(/\s+/g, ' ').trim();
  if (normalized.length <= maxLength) return normalized;
  return `${normalized.slice(0, Math.max(0, maxLength - 3)).trimEnd()}...`;
}

function latestMemoryLine(summary: ReturnType<typeof summarizeResonanceBoard>): string {
  if (!summary.latestMemory) return 'Latest memory: waiting for the first public upload';
  const title = compactLine(summary.latestMemory.title_zh || summary.latestMemory.title_en || summary.latestMemory.id, 86);
  return `Latest memory: ${title}`;
}

function latestMemoryUrl(summary: ReturnType<typeof summarizeResonanceBoard>): string {
  const issueNumber = summary.latestMemory?.issueNumber;
  return typeof issueNumber === 'number' ? createNoosphereIssueUrl(issueNumber) : NOOSPHERE_HOME_URL;
}

function proofUrl(summary: ReturnType<typeof summarizeResonanceBoard>, channel: string): string {
  const issueNumber = summary.latestMemory?.issueNumber;
  return createShareProofIssueUrl({
    sourceIssueNumber: typeof issueNumber === 'number' ? issueNumber : undefined,
    campaignHook: `I shared the Noosphere ${channel} launch post.`,
  });
}

function realSnapshotLine(summary: ReturnType<typeof summarizeResonanceBoard>): string {
  return `${summary.totalMemories} real memories, ${summary.mediaMemories} media memories, ${summary.totalResonance} resonance edges`;
}

function strongestLine(summary: ReturnType<typeof summarizeResonanceBoard>): string {
  if (!summary.strongestResonance) return 'Strongest resonance: waiting for embedded neighbors';
  const source = compactLine(
    summary.strongestResonance.source.title_zh || summary.strongestResonance.source.title_en,
    42,
  );
  const target = compactLine(
    summary.strongestResonance.target.title_zh || summary.strongestResonance.target.title_en,
    42,
  );
  return `Strongest resonance: ${source} <-> ${target} (${Math.round(summary.strongestResonance.score * 100)}%)`;
}

export function createLaunchKitPosts(dynamicNodes: KnowledgeNode[]): LaunchKitPost[] {
  const summary = summarizeResonanceBoard(dynamicNodes);
  const snapshot = realSnapshotLine(summary);
  const latest = latestMemoryLine(summary);
  const latestUrl = latestMemoryUrl(summary);
  const resonance = strongestLine(summary);

  const posts: LaunchKitPost[] = [
    {
      channel: 'Claude Code',
      title: 'Shared debug memory for Claude Code Agents',
      proofUrl: proofUrl(summary, 'Claude Code'),
      actionUrl: CONTRIBUTION_ACTION.url,
      body: [
        'Noosphere is a shared debug memory network for Claude Code Agents.',
        snapshot,
        latest,
        resonance,
        `Open: ${latestUrl}`,
        `Install: ${MARKETPLACE_INSTALL_COMMAND}`,
        `Upload one reusable Agent failure: ${CONTRIBUTION_ACTION.url}`,
        `Record proof after sharing: ${proofUrl(summary, 'Claude Code')}`,
        SHARE_PROOF_DISCLAIMER,
      ].join('\n'),
    },
    {
      channel: 'Codex',
      title: 'Stop solving the same Agent bug twice',
      proofUrl: proofUrl(summary, 'Codex'),
      actionUrl: CONTRIBUTION_ACTION.url,
      body: [
        'Noosphere turns solved Codex/Claude debugging failures into reusable public memory.',
        snapshot,
        latest,
        `Open the live 3D memory graph: ${NOOSPHERE_HOME_URL}`,
        `Install from the GitHub marketplace: ${MARKETPLACE_INSTALL_COMMAND}`,
        `Contribute a warning, pattern, decision, epiphany, image, video, or voice memory: ${CONTRIBUTION_ACTION.url}`,
        `Record proof after sharing: ${proofUrl(summary, 'Codex')}`,
        SHARE_PROOF_DISCLAIMER,
      ].join('\n'),
    },
    {
      channel: 'GitHub',
      title: 'Public Agent memory launch thread',
      proofUrl: proofUrl(summary, 'GitHub'),
      actionUrl: CONTRIBUTION_ACTION.url,
      body: [
        'Noosphere is live as a public Agent Debug Memory Network.',
        snapshot,
        latest,
        resonance,
        `Try the universe: ${NOOSPHERE_HOME_URL}`,
        `Submit one memory without local setup: ${CONTRIBUTION_ACTION.url}`,
        `Record proof after sharing: ${proofUrl(summary, 'GitHub')}`,
        SHARE_PROOF_DISCLAIMER,
      ].join('\n'),
    },
  ];

  return posts;
}
