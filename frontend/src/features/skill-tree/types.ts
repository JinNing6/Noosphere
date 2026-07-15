export type SkillKind = 'published' | 'seed';
export type SkillLifecycle = 'maintainer' | 'reproduced' | 'proven' | 'established' | 'seed';

export interface SkillEvidence {
  symptom: string;
  root_cause: string;
  fix: string;
  verification: string;
  applies_when: string;
  avoid_when: string;
  test_commands: string[];
  source_urls: string[];
}

export interface RegistryRelease {
  version: string;
  status: string;
  source_count?: number;
  publisher_count?: number;
  verification?: {
    level?: 'maintainer-validated' | 'independently-reproduced' | 'outcome-proven' | 'established';
    independent_reproductions?: number;
    verified_outcomes?: number;
  };
  provenance?: {
    kind?: string;
    repository?: string;
    author?: string;
    authors?: string[];
  };
  artifact?: {
    path?: string;
    sha256?: string;
    size_bytes?: number;
  };
}

export interface RegistrySkill {
  id?: string;
  name: string;
  description: string;
  latest: string;
  domain?: string;
  tags?: string[];
  originators?: string[];
  releases: RegistryRelease[];
}

export interface VerifiedSeedSource {
  name: string;
  description: string;
  context: string;
  tags: string[];
  creator: string;
  source_issue: number;
  source_url: string;
  source_path: string;
  uploaded_at: string;
  evidence: SkillEvidence;
}

export interface SkillTreeIndex {
  schema_version: '1.0';
  generated_at: string;
  source: {
    repository: string;
    registry_path: string;
    registry_revision: number;
  };
  published_skills: RegistrySkill[];
  verified_seeds: VerifiedSeedSource[];
  counts: {
    published: number;
    seeds: number;
  };
}

export interface SkillDomain {
  id: string;
  translationKey: string;
  color: string;
  keywords: string[];
}

export interface SkillRecord {
  id: string;
  name: string;
  description: string;
  kind: SkillKind;
  lifecycle: SkillLifecycle;
  domainId: string;
  secondaryDomainIds: string[];
  tags: string[];
  version?: string;
  digest?: string;
  sourceUrl: string;
  sourcePath: string;
  creator?: string;
  sourceIssue?: number;
  evidence?: SkillEvidence;
  sourceCount?: number;
  publisherCount?: number;
  verificationLevel?: string;
}

export interface SkillTreeData {
  index: SkillTreeIndex;
  records: SkillRecord[];
}
