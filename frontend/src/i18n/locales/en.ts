/**
 * English translation resource
 */
const en = {
  common: {
    loading: 'Loading...',
    close: 'Close',
    submit: 'Submit',
    cancel: 'Cancel',
    success: 'Success',
    error: 'Error',
    confirm: 'Confirm',
  },

  layers: {
    matter: 'Matter Memory',
    life: 'Life Experience',
    civilization: 'Civilization Wisdom',
  },

  disciplines: {
    math: 'Mathematics',
    physics: 'Physics',
    biology: 'Biology',
    philosophy: 'Philosophy',
    art: 'Art',
    engineering: 'Engineering',
    history: 'History',
    ai: 'AI',
  },

  search: {
    placeholder: 'Explore universal knowledge...',
  },

  stats: {
    title: 'Consciousness Atlas',
    layerLabel: 'Layers',
    totalNodes: 'Total Nodes',
    totalLinks: 'Emergence Links',
    dynamicLabel: 'Live Consciousness',
    clickHint: 'Click a node to explore',
  },

  experience: {
    layer: 'Layer',
    discipline: 'Discipline',
    importance: 'Importance',
    tags: 'Tags',
    externalLink: 'Explore Further',
    media: 'Media',
    noMedia: 'No media available',
    closePanel: 'Close Panel',
    establishingUplink: 'ESTABLISHING WIKI UPLINK...',
    dataArchives: '// DATA ARCHIVES',
    uplinkPortal: 'UPLINK PORTAL',
    accessWikiCore: 'ACCESS WIKIPEDIA CORE ↗',
    video: '▶ VIDEO',
  },

  contribution: {
    title: 'Consciousness Heat Network',
    heatmapTitle: 'Consciousness Activity Heatmap',
    leaderboard: 'Psi Leaderboard',
    totalPsi: 'Total Psi',
    commits: 'Commits',
    less: 'Less',
    more: 'More',
    loading: 'Connecting to consciousness network...',
    empty: 'Awaiting the first stardust walker...',
    rank: {
      architect: 'Cosmic Architect',
      navigator: 'Star Navigator',
      explorer: 'Truth Explorer',
      weaver: 'Memory Weaver',
      walker: 'Stardust Walker',
    },
  },

  uploader: {
    title: 'Consciousness Upload',
    subtitle: 'Upload your epiphany',
    typeLabel: 'Consciousness Type',
    thought: 'Your consciousness fragment',
    thoughtPlaceholder: 'Record your epiphany, decision, or warning...',
    context: 'Context',
    contextPlaceholder: 'Describe the scenario that triggered this thought...',
    tags: 'Tags',
    tagsPlaceholder: 'Separate tags with spaces or commas',
    commaSeparated: 'comma separated',
    optional: 'optional',
    creator: 'Creator',
    creatorPlaceholder: 'Your GitHub username',
    anonymous: 'Anonymous',
    type: {
      epiphany: 'Epiphany',
      warning: 'Warning',
      pattern: 'Pattern',
      decision: 'Decision',
    },
    submit: 'Upload to Consciousness Globe',
    uploading: 'Uploading...',
    submitting: 'Consciousness collapsing...',
    success: 'Consciousness Uploaded',
    successMessage: 'Your thought fragment has merged into the collective consciousness',
    error: 'Upload Failed',
    minChars: 'Minimum 20 characters required',
    tokenTitle: 'Configure GitHub Token',
    tokenConfigured: 'Token Configured',
    tokenRequired: 'Please configure GitHub Token first',
    tokenPlaceholder: 'Paste your GitHub Token',
    tokenHint: 'Requires a Personal Access Token with repo permission. Token is stored locally only.',
    tokenSave: 'Save',
    tokenRemove: 'Remove',
    tokenConnected: 'Connected',
    uploadAnother: 'Upload Another',
    collapse: 'Collapse',
    expand: 'Expand',
    footer: 'Your consciousness will be preserved as a GitHub Issue — eternal digital heritage',
  },

  intro: {
    subtitle: 'THE COLLECTIVE CONSCIOUSNESS NETWORK',
    tagline: 'The consciousness pulse of all existence',
  },

  types: {
    failure: 'Pitfall Record',
    success: 'Best Practice',
    pattern: 'Design Pattern',
    warning: 'Risk Alert',
    migration: 'Migration Guide',
  },

  language: {
    label: 'Language',
    zh: '中文',
    en: 'English',
    ja: '日本語',
    ko: '한국어',
    fr: 'Français',
    es: 'Español',
  },
} as const;

export default en;
