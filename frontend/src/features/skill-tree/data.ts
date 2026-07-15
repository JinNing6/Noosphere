import { normalizeSkillIndex } from './taxonomy';
import type { SkillTreeData, SkillTreeIndex } from './types';

function validateIndex(value: unknown): asserts value is SkillTreeIndex {
  const index = value as Partial<SkillTreeIndex> | null;
  if (!index
    || index.schema_version !== '1.0'
    || !Array.isArray(index.published_skills)
    || !Array.isArray(index.static_skills)
    || !Array.isArray(index.verified_seeds)
    || !index.counts
    || !index.source) {
    throw new Error('Noosphere Skill Tree index is malformed.');
  }
}

export async function loadSkillTreeData(signal?: AbortSignal): Promise<SkillTreeData> {
  const response = await fetch(`${import.meta.env.BASE_URL}skill-tree-index.json`, {
    signal,
    cache: 'no-cache',
  });
  if (!response.ok) {
    throw new Error(`Unable to load Skill Tree index (${response.status}).`);
  }
  const index: unknown = await response.json();
  validateIndex(index);
  return {
    index,
    records: normalizeSkillIndex(index),
  };
}

export function matchesSkillQuery(record: SkillTreeData['records'][number], query: string): boolean {
  const terms = query.trim().toLowerCase().split(/\s+/).filter(Boolean);
  if (terms.length === 0) return true;
  const evidence = record.evidence
    ? Object.values(record.evidence).flat().join(' ')
    : '';
  const haystack = [record.name, record.description, record.tags.join(' '), evidence].join(' ').toLowerCase();
  return terms.every((term) => haystack.includes(term));
}
