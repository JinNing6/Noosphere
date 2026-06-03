export const NOOSPHERE_HOME_URL = 'https://jinning6.github.io/Noosphere/';
export const GITHUB_REPO_URL = 'https://github.com/JinNing6/Noosphere';
export const CONTRIBUTION_ISSUE_TEMPLATE = 'consciousness-upload.yml';
export const MARKETPLACE_INSTALL_COMMAND = '/plugin marketplace add JinNing6/Noosphere';

export function createContributionIssueUrl(baseUrl = GITHUB_REPO_URL): string {
  const url = new URL(`${baseUrl}/issues/new`);
  url.searchParams.set('template', CONTRIBUTION_ISSUE_TEMPLATE);
  url.searchParams.set('title', 'Upload Noosphere memory');
  return url.toString();
}

export const INSTALL_OPTIONS = [
  {
    id: 'claude',
    label: 'Claude Code',
    idleLabel: 'copy',
    ariaLabel: 'Copy Claude Code install command',
    command: [
      '/plugin marketplace add JinNing6/Noosphere',
      '/plugin install noosphere@noosphere-agent-memory',
      '/reload-plugins',
    ].join('\n'),
  },
  {
    id: 'codex',
    label: 'Codex',
    idleLabel: 'copy',
    ariaLabel: 'Copy Codex install command',
    command: 'codex plugin marketplace add JinNing6/Noosphere',
  },
] as const;

export const CONTRIBUTION_ACTION = {
  id: 'contribute',
  label: 'Upload',
  idleLabel: 'No token needed',
  ariaLabel: 'Open GitHub Issue Form to upload a Noosphere memory',
  url: createContributionIssueUrl(),
} as const;

export const SHARE_POST = [
  'Stop solving the same agent bug twice.',
  `Install: ${MARKETPLACE_INSTALL_COMMAND}`,
  `Upload memory: ${CONTRIBUTION_ACTION.url}`,
  NOOSPHERE_HOME_URL,
].join('\n');

export const CLIPBOARD_ACTIONS = [
  ...INSTALL_OPTIONS,
  {
    id: 'share',
    label: 'Share',
    idleLabel: 'post',
    ariaLabel: 'Copy Noosphere share post',
  },
] as const;

interface MemoryShareInput {
  id: string;
  title: string;
  fix?: string;
  outcome?: string;
}

function compactLine(value: string | undefined, maxLength: number): string {
  const normalized = (value || '').replace(/\s+/g, ' ').trim();
  if (normalized.length <= maxLength) return normalized;
  return `${normalized.slice(0, Math.max(0, maxLength - 3)).trimEnd()}...`;
}

export function createMemoryShareUrl(memoryId: string, baseUrl = NOOSPHERE_HOME_URL): string {
  const url = new URL(baseUrl);
  url.searchParams.set('memory', memoryId);
  return url.toString();
}

export function createMemorySharePost(memory: MemoryShareInput, baseUrl = NOOSPHERE_HOME_URL): string {
  const proofLine = memory.outcome
    ? `Proof: ${compactLine(memory.outcome, 96)}`
    : `Fix: ${compactLine(memory.fix || 'Open the memory to inspect the validated fix.', 96)}`;

  return [
    `Known fix: ${compactLine(memory.title, 84)}`,
    proofLine,
    `Open: ${createMemoryShareUrl(memory.id, baseUrl)}`,
    `Install: ${MARKETPLACE_INSTALL_COMMAND}`,
    `Contribute: ${CONTRIBUTION_ACTION.url}`,
  ].join('\n');
}

export function readMemoryIdFromSearch(search: string): string | null {
  const memoryId = new URLSearchParams(search).get('memory')?.trim();
  return memoryId || null;
}
