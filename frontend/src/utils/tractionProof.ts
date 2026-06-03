import { CONTRIBUTION_ACTION, NOOSPHERE_HOME_URL } from './growthCopy';
import { SHARE_PROOF_FORM_URL } from './shareProofs';

export const TRACTION_PROOF_DISCLOSURE = 'No downloads, reposts, referrals, retention, rewards, or install counts are inferred from public repository, IssueOps, Pull Request, or URL snapshots.';

export interface TractionRepoSnapshot {
  status: string;
  full_name: string;
  html_url: string;
  stars: number;
  forks: number;
  open_issues: number;
}

export interface TractionMemorySnapshot {
  public_memories: number;
  promoted_issue_memories: number;
  media_memories: number;
  resonance_events: number;
  embedding_neighbor_edges: number;
}

export interface TractionShareProofSnapshot {
  total_proof_issues: number;
  reviewable_public_urls: number;
  missing_or_invalid_urls: number;
  latest_reviewable_url: string;
  form_url: string;
}

export interface TractionTargetProgress {
  target_contributor_count: number;
  real_contributor_identities: number;
  contributors: string[];
  progress_percent: number;
  counting_rule: string;
}

export interface TractionBottleneck {
  stage: string;
  reason: string;
  next_action: string;
  next_action_url: string;
}

export interface TractionVelocity {
  status: string;
  baseline_generated_at: string;
  current_generated_at: string;
  days_elapsed: number;
  deltas: {
    stars: number;
    forks: number;
    open_issues: number;
    public_memories: number;
    reviewable_public_urls: number;
    real_contributor_identities: number;
  };
  per_day: {
    stars: number;
    reviewable_public_urls: number;
    real_contributor_identities: number;
  };
}

export interface TractionHistorySummary {
  mode: string;
  history_url: string;
  record_workflow_url: string;
  recording_policy: string;
  snapshots_recorded: number;
  latest_velocity: TractionVelocity;
}

export interface TractionProofSnapshot {
  generated_at: string;
  source: string;
  repo: TractionRepoSnapshot;
  memory: TractionMemorySnapshot;
  share_proof: TractionShareProofSnapshot;
  target_progress: TractionTargetProgress;
  bottleneck: TractionBottleneck;
  history: TractionHistorySummary;
  access_issues: string[];
  share_card: string;
  disclaimer: string;
}

export const EMPTY_TRACTION_PROOF: TractionProofSnapshot = {
  generated_at: '',
  source: 'Generated Noosphere traction_proof.json',
  repo: {
    status: 'unavailable',
    full_name: 'JinNing6/Noosphere',
    html_url: 'https://github.com/JinNing6/Noosphere',
    stars: 0,
    forks: 0,
    open_issues: 0,
  },
  memory: {
    public_memories: 0,
    promoted_issue_memories: 0,
    media_memories: 0,
    resonance_events: 0,
    embedding_neighbor_edges: 0,
  },
  share_proof: {
    total_proof_issues: 0,
    reviewable_public_urls: 0,
    missing_or_invalid_urls: 0,
    latest_reviewable_url: '',
    form_url: SHARE_PROOF_FORM_URL,
  },
  target_progress: {
    target_contributor_count: 10,
    real_contributor_identities: 0,
    contributors: [],
    progress_percent: 0,
    counting_rule: 'Counts real public contribution identities only.',
  },
  bottleneck: {
    stage: 'public share proof',
    reason: 'Waiting for public share proof URLs.',
    next_action: 'Share one memory publicly, then record the URL.',
    next_action_url: SHARE_PROOF_FORM_URL,
  },
  history: {
    mode: 'manual append-only',
    history_url: 'https://jinning6.github.io/Noosphere/traction_history.json',
    record_workflow_url: 'https://github.com/JinNing6/Noosphere/actions/workflows/record-traction-history.yml',
    recording_policy: 'Manual append-only history. Velocity is computed only from prior recorded snapshots.',
    snapshots_recorded: 0,
    latest_velocity: {
      status: 'baseline-only',
      baseline_generated_at: '',
      current_generated_at: '',
      days_elapsed: 0,
      deltas: {
        stars: 0,
        forks: 0,
        open_issues: 0,
        public_memories: 0,
        reviewable_public_urls: 0,
        real_contributor_identities: 0,
      },
      per_day: {
        stars: 0,
        reviewable_public_urls: 0,
        real_contributor_identities: 0,
      },
    },
  },
  access_issues: [],
  share_card: [
    'Noosphere public traction proof',
    '0 real contributors from public IssueOps and Pull Request evidence',
    `Record public share proof: ${SHARE_PROOF_FORM_URL}`,
    TRACTION_PROOF_DISCLOSURE,
  ].join('\n'),
  disclaimer: TRACTION_PROOF_DISCLOSURE,
};

function isTractionProofSnapshot(value: unknown): value is TractionProofSnapshot {
  if (!value || typeof value !== 'object') return false;
  const candidate = value as Partial<TractionProofSnapshot>;
  return Boolean(candidate.repo && candidate.memory && candidate.share_proof && candidate.target_progress && candidate.bottleneck && candidate.history);
}

function unit(count: number, singular: string, plural: string): string {
  return count === 1 ? singular : plural;
}

export async function fetchTractionProof(): Promise<TractionProofSnapshot> {
  try {
    const response = await fetch(`${import.meta.env.BASE_URL}traction_proof.json`);
    if (!response.ok) return EMPTY_TRACTION_PROOF;
    const data: unknown = await response.json();
    return isTractionProofSnapshot(data) ? data : EMPTY_TRACTION_PROOF;
  } catch {
    console.warn('[Noosphere] Failed to fetch traction proof snapshot');
    return EMPTY_TRACTION_PROOF;
  }
}

export function createTractionProofPost(snapshot: TractionProofSnapshot): string {
  const bottleneck = snapshot.bottleneck.stage || 'public share proof';
  const nextActionUrl = snapshot.bottleneck.next_action_url || SHARE_PROOF_FORM_URL;
  const velocity = snapshot.history.latest_velocity;

  return [
    'Noosphere public traction proof',
    `Repo: ${snapshot.repo.stars} ${unit(snapshot.repo.stars, 'star', 'stars')}, ${snapshot.repo.forks} ${unit(snapshot.repo.forks, 'fork', 'forks')}, ${snapshot.repo.open_issues} open ${unit(snapshot.repo.open_issues, 'issue', 'issues')}`,
    `Memory graph: ${snapshot.memory.public_memories} public ${unit(snapshot.memory.public_memories, 'memory', 'memories')}, ${snapshot.memory.media_memories} media ${unit(snapshot.memory.media_memories, 'memory', 'memories')}, ${snapshot.memory.embedding_neighbor_edges} embedding neighbor ${unit(snapshot.memory.embedding_neighbor_edges, 'edge', 'edges')}`,
    `Share proof: ${snapshot.share_proof.reviewable_public_urls} reviewable public URLs from ${snapshot.share_proof.total_proof_issues} proof ${unit(snapshot.share_proof.total_proof_issues, 'issue', 'issues')}`,
    `Sprint: ${snapshot.target_progress.real_contributor_identities}/${snapshot.target_progress.target_contributor_count} real contributors`,
    `Velocity: ${velocity.deltas.stars >= 0 ? '+' : ''}${velocity.deltas.stars} stars, ${velocity.deltas.reviewable_public_urls >= 0 ? '+' : ''}${velocity.deltas.reviewable_public_urls} proof URLs, ${velocity.deltas.real_contributor_identities >= 0 ? '+' : ''}${velocity.deltas.real_contributor_identities} real contributors since ${velocity.baseline_generated_at || 'baseline'}`,
    `History: ${snapshot.history.history_url}`,
    `Bottleneck: ${bottleneck}`,
    `Next: ${nextActionUrl}`,
    `Upload memory: ${CONTRIBUTION_ACTION.url}`,
    `Open graph: ${NOOSPHERE_HOME_URL}`,
    snapshot.disclaimer || TRACTION_PROOF_DISCLOSURE,
  ].join('\n');
}
