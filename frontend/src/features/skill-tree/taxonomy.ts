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

const SKILL_DOMAIN_OVERRIDES: Record<string, string> = {
  'agent-debug-memory': 'testing-reliability',
  'binary-credential-format-boundary': 'security-trust',
  'browser-actionability-debug': 'frontend-mobile',
  'cloudflare-pages-stale-assets': 'build-release',
  'debug-async-ui': 'frontend-mobile',
  'docker-git-bind-mount-push-debug': 'data-infrastructure',
  'dynamic-shared-skills': 'agent-runtime',
  'fastapi-response-contract-boundary': 'languages-frameworks',
  'frontend-layering-specificity-debug': 'frontend-mobile',
  'github-actions-public-ci-diagnostics': 'build-release',
  'upload-debug-memory': 'agent-runtime',
  'windows-child-process-lifecycle': 'testing-reliability',
  'windows-npm-run-script-shell': 'build-release',
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

function assignDomains(name: string, description: string, tags: string[], declaredDomain?: string) {
  const override = declaredDomain && SKILL_DOMAINS.some((domain) => domain.id === declaredDomain)
    ? declaredDomain
    : SKILL_DOMAIN_OVERRIDES[name];
  const scores = scoreDomains([name, description, ...tags].join(' '));
  const primary = override || scores.find((entry) => entry.score > 0)?.id || 'agent-runtime';
  const secondary = scores
    .filter((entry) => entry.score > 0 && entry.id !== primary)
    .slice(0, 2)
    .map((entry) => entry.id);
  return { primary, secondary };
}

function lifecycleForVerification(level?: string): SkillRecord['lifecycle'] {
  if (level === 'established') return 'established';
  if (level === 'outcome-proven') return 'proven';
  if (level === 'independently-reproduced') return 'reproduced';
  return 'maintainer';
}

export function normalizeSkillIndex(index: SkillTreeIndex): SkillRecord[] {
  const published = index.published_skills.map((skill): SkillRecord => {
    const activeRelease = skill.releases.find((release) => release.version === skill.latest && release.status === 'active');
    const tags = skill.tags || [];
    const domains = assignDomains(skill.name, skill.description, tags, skill.domain);
    const verificationLevel = activeRelease?.verification?.level;
    return {
      id: `published:${skill.name}`,
      name: skill.name,
      description: skill.description,
      kind: 'published',
      lifecycle: lifecycleForVerification(verificationLevel),
      domainId: domains.primary,
      secondaryDomainIds: domains.secondary,
      tags,
      version: skill.latest,
      digest: activeRelease?.artifact?.sha256,
      sourceUrl: `https://github.com/JinNing6/Noosphere/blob/main/${activeRelease?.artifact?.path || 'shared_skills/registry.json'}`,
      sourcePath: activeRelease?.artifact?.path || 'shared_skills/registry.json',
      sourceCount: activeRelease?.source_count,
      publisherCount: activeRelease?.publisher_count,
      creator: skill.originators?.[0],
      verificationLevel,
    };
  });

  const seeds = index.verified_seeds.map((seed): SkillRecord => {
    const domains = assignDomains(seed.name, seed.description, seed.tags);
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

  return [...published, ...seeds].sort((a, b) => a.name.localeCompare(b.name));
}

export function domainById(domainId: string): SkillDomain {
  return SKILL_DOMAINS.find((domain) => domain.id === domainId) || SKILL_DOMAINS[0];
}
