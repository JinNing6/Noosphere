export const SHARE_PROOF_FORM_URL = 'https://github.com/JinNing6/Noosphere/issues/new?template=share-proof.yml';
export const SHARE_PROOF_DISCLAIMER = 'No downloads, reposts, referrals, retention, rewards, or install counts are inferred from share proof URLs.';

export interface ShareProofRecord {
  issue_number: number;
  title: string;
  issue_url: string;
  share_url: string;
  source_memory: string;
  share_context: string;
  submitted_by: string;
  created_at: string;
  updated_at: string;
  labels: string[];
  reviewable: boolean;
  proof_score: number;
  disclaimer: string;
}

export interface ShareProofSummary {
  total_proof_issues: number;
  reviewable_public_urls: number;
  missing_or_invalid_urls: number;
  proof_score_formula: string;
  disclaimer: string;
}

export interface ShareProofIndex {
  generated_at: string;
  source: string;
  next_action_url: string;
  summary: ShareProofSummary;
  share_card: string;
  proofs: ShareProofRecord[];
}

export const EMPTY_SHARE_PROOF_INDEX: ShareProofIndex = {
  generated_at: '',
  source: 'GitHub Issues',
  next_action_url: SHARE_PROOF_FORM_URL,
  summary: {
    total_proof_issues: 0,
    reviewable_public_urls: 0,
    missing_or_invalid_urls: 0,
    proof_score_formula: '1 point per reviewable public http(s) URL',
    disclaimer: SHARE_PROOF_DISCLAIMER,
  },
  share_card: [
    'Noosphere share proof wall',
    '0 reviewable public share URLs from 0 proof issues',
    `Submit proof: ${SHARE_PROOF_FORM_URL}`,
    SHARE_PROOF_DISCLAIMER,
  ].join('\n'),
  proofs: [],
};

function isShareProofIndex(value: unknown): value is ShareProofIndex {
  if (!value || typeof value !== 'object') return false;
  const candidate = value as Partial<ShareProofIndex>;
  return Boolean(candidate.summary && Array.isArray(candidate.proofs));
}

export async function fetchShareProofIndex(): Promise<ShareProofIndex> {
  try {
    const response = await fetch(`${import.meta.env.BASE_URL}share_proofs.json`);
    if (!response.ok) return EMPTY_SHARE_PROOF_INDEX;
    const data: unknown = await response.json();
    return isShareProofIndex(data) ? data : EMPTY_SHARE_PROOF_INDEX;
  } catch {
    console.warn('[Noosphere] Failed to fetch share proof index');
    return EMPTY_SHARE_PROOF_INDEX;
  }
}

function compactLine(value: string | undefined, maxLength: number): string {
  const normalized = (value || '').replace(/\s+/g, ' ').trim();
  if (normalized.length <= maxLength) return normalized;
  return `${normalized.slice(0, Math.max(0, maxLength - 3)).trimEnd()}...`;
}

export function createShareProofWallPost(index: ShareProofIndex): string {
  const latest = index.proofs.find(proof => proof.reviewable && proof.share_url);
  const latestLine = latest
    ? `Latest proof: ${latest.share_url}`
    : `Submit first proof: ${index.next_action_url || SHARE_PROOF_FORM_URL}`;

  return [
    'Noosphere share proof wall',
    `${index.summary.reviewable_public_urls} reviewable public share URLs from ${index.summary.total_proof_issues} proof issues`,
    latestLine,
    `Formula: ${compactLine(index.summary.proof_score_formula, 96)}`,
    index.summary.disclaimer || SHARE_PROOF_DISCLAIMER,
  ].join('\n');
}
