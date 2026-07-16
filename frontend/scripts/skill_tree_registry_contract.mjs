export function validateRegistry(registry) {
  if (registry?.schema_version !== '1.0' || !Number.isInteger(registry?.revision) || !Array.isArray(registry?.skills)) {
    throw new Error('shared_skills/registry.json does not match schema version 1.0');
  }
  for (const skill of registry.skills) {
    if (!skill?.name || !Array.isArray(skill?.releases) || !('latest' in skill)) {
      throw new Error(`Malformed published Skill registry entry: ${skill?.name || 'unknown'}`);
    }
    const activeReleases = skill.releases.filter((release) => release.status === 'active');
    if (skill.latest === null && activeReleases.length > 0) {
      throw new Error(`Withdrawn Skill still has active releases: ${skill.name}`);
    }
    if (skill.latest !== null && !activeReleases.some((release) => release.version === skill.latest)) {
      throw new Error(`Published Skill latest does not identify an active release: ${skill.name}`);
    }
  }
}
