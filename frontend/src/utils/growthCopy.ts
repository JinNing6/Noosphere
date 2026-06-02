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

export const SHARE_POST = [
  'Stop solving the same agent bug twice.',
  'Noosphere = shared debug memory for Claude Code + Codex agents.',
  'Install: /plugin marketplace add JinNing6/Noosphere',
  'https://jinning6.github.io/Noosphere/',
].join('\n');

export const CLIPBOARD_ACTIONS = [
  ...INSTALL_OPTIONS,
  {
    id: 'share',
    label: 'Share',
    idleLabel: 'post',
    ariaLabel: 'Copy Noosphere share post',
    command: SHARE_POST,
  },
] as const;
