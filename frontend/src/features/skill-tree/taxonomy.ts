import type { SkillDomain, SkillRecord, SkillTreeIndex } from './types';

export const SKILL_DOMAINS: SkillDomain[] = [
  {
    id: 'agent-runtime',
    translationKey: 'agentRuntime',
    color: '#8D7CFF',
    keywords: ['agent', 'agents', 'codex', 'claude', 'cursor', 'skill', 'workflow', 'context'],
  },
  {
    id: 'mcp-tools',
    translationKey: 'mcpTools',
    color: '#33D6C4',
    keywords: ['mcp', 'tool', 'tools', 'protocol', 'stdio', 'server', 'client'],
  },
  {
    id: 'build-release',
    translationKey: 'buildRelease',
    color: '#F0C75E',
    keywords: ['build', 'release', 'deploy', 'deployment', 'pypi', 'package', 'packaging', 'runtime', 'ci'],
  },
  {
    id: 'testing-reliability',
    translationKey: 'testingReliability',
    color: '#35D07F',
    keywords: ['test', 'testing', 'debug', 'failure', 'reliability', 'recovery', 'regression', 'error'],
  },
  {
    id: 'security-trust',
    translationKey: 'securityTrust',
    color: '#F26B5E',
    keywords: ['security', 'trust', 'provenance', 'supply-chain', 'digest', 'rollback', 'safe'],
  },
  {
    id: 'frontend-mobile',
    translationKey: 'frontendMobile',
    color: '#5FA8FF',
    keywords: ['frontend', 'react', 'r3f', 'three', 'webview', 'android', 'mobile', 'ui', 'node-picking'],
  },
  {
    id: 'data-infrastructure',
    translationKey: 'dataInfrastructure',
    color: '#F28B4B',
    keywords: ['data', 'database', 'storage', 'cloud', 'docker', 'infrastructure', 'cache', 'index'],
  },
  {
    id: 'languages-frameworks',
    translationKey: 'languagesFrameworks',
    color: '#E65AB0',
    keywords: ['python', 'typescript', 'javascript', 'framework', 'library', 'api', 'migration', 'language'],
  },
];

const STATIC_DOMAIN_OVERRIDES: Record<string, string> = {
  'agent-debug-memory': 'testing-reliability',
  'dynamic-shared-skills': 'agent-runtime',
  'upload-debug-memory': 'agent-runtime',
};

function scoreDomains(text: string): Array<{ id: string; score: number }> {
  const haystack = text.toLowerCase();
  return SKILL_DOMAINS
    .map((domain) => ({
      id: domain.id,
      score: domain.keywords.reduce((score, keyword) => score + (haystack.includes(keyword) ? 1 : 0), 0),
    }))
    .sort((a, b) => b.score - a.score || a.id.localeCompare(b.id));
}

function assignDomains(name: string, description: string, tags: string[], kind: SkillRecord['kind']) {
  const override = kind === 'bundled' ? STATIC_DOMAIN_OVERRIDES[name] : undefined;
  const scores = scoreDomains([name, description, ...tags].join(' '));
  const primary = override || scores.find((entry) => entry.score > 0)?.id || 'agent-runtime';
  const secondary = scores
    .filter((entry) => entry.score > 0 && entry.id !== primary)
    .slice(0, 2)
    .map((entry) => entry.id);
  return { primary, secondary };
}

export function normalizeSkillIndex(index: SkillTreeIndex): SkillRecord[] {
  const published = index.published_skills.map((skill): SkillRecord => {
    const activeRelease = skill.releases.find((release) => release.version === skill.latest && release.status === 'active');
    const tags = skill.tags || [];
    const domains = assignDomains(skill.name, skill.description, tags, 'published');
    return {
      id: `published:${skill.name}`,
      name: skill.name,
      description: skill.description,
      kind: 'published',
      lifecycle: 'established',
      domainId: domains.primary,
      secondaryDomainIds: domains.secondary,
      tags,
      version: skill.latest,
      digest: activeRelease?.artifact?.sha256,
      sourceUrl: `https://github.com/JinNing6/Noosphere/blob/main/${activeRelease?.artifact?.path || 'shared_skills/registry.json'}`,
      sourcePath: activeRelease?.artifact?.path || 'shared_skills/registry.json',
      sourceCount: activeRelease?.source_count,
      publisherCount: activeRelease?.publisher_count,
    };
  });

  const bundled = index.static_skills.map((skill): SkillRecord => {
    const domains = assignDomains(skill.name, skill.description, [], 'bundled');
    return {
      id: `bundled:${skill.name}`,
      name: skill.name,
      description: skill.description,
      kind: 'bundled',
      lifecycle: 'proven',
      domainId: domains.primary,
      secondaryDomainIds: domains.secondary,
      tags: [],
      sourceUrl: `https://github.com/JinNing6/Noosphere/blob/main/${skill.source_path}`,
      sourcePath: skill.source_path,
    };
  });

  const seeds = index.verified_seeds.map((seed): SkillRecord => {
    const domains = assignDomains(seed.name, seed.description, seed.tags, 'seed');
    return {
      id: `seed:${seed.name}`,
      name: seed.name,
      description: seed.description,
      kind: 'seed',
      lifecycle: 'seed',
      domainId: domains.primary,
      secondaryDomainIds: domains.secondary,
      tags: seed.tags,
      sourceUrl: seed.source_url,
      sourcePath: seed.source_path,
      creator: seed.creator,
      sourceIssue: seed.source_issue,
      evidence: seed.evidence,
    };
  });

  return [...published, ...bundled, ...seeds].sort((a, b) => a.name.localeCompare(b.name));
}

export function domainById(domainId: string): SkillDomain {
  return SKILL_DOMAINS.find((domain) => domain.id === domainId) || SKILL_DOMAINS[0];
}
