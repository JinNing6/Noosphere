const {
  buildSkillCandidate,
  clusterEligibleMemories,
  extractSkillCandidate,
} = require("./dynamic-skills.cjs");

function tombstonedIssues(manifest) {
  return new Set((manifest?.withdrawn_issues || []).map((entry) => Number(entry.issue_number)));
}

function buildCanonicalSkillCandidates(memories, tombstones) {
  const withdrawn = tombstonedIssues(tombstones);
  const active = (memories || []).filter((memory) => !withdrawn.has(Number(memory.promoted_from_issue)));
  const candidates = [];
  for (const cluster of clusterEligibleMemories(active)) {
    try {
      candidates.push(buildSkillCandidate(cluster));
    } catch (error) {
      console.warn(`Skipping non-publishable Skill candidate ${cluster.id}: ${error.message}`);
    }
  }
  return candidates.sort((left, right) => left.id.localeCompare(right.id));
}

function planCandidateIssueSync(candidates, issues) {
  const activeById = new Map(candidates.map((candidate) => [candidate.id, candidate]));
  const issueById = new Map();
  const duplicateIssues = [];
  for (const issue of issues || []) {
    const candidate = extractSkillCandidate(issue.body);
    if (!candidate?.id) continue;
    const existing = issueById.get(candidate.id);
    if (!existing) {
      issueById.set(candidate.id, { issue, candidate });
      continue;
    }
    const existingPreferred = (
      (existing.issue.state === "open" && issue.state !== "open") ||
      (
        existing.issue.state === issue.state &&
        Number(existing.issue.number) < Number(issue.number)
      )
    );
    if (existingPreferred) duplicateIssues.push(issue);
    else {
      duplicateIssues.push(existing.issue);
      issueById.set(candidate.id, { issue, candidate });
    }
  }
  return {
    create: candidates.filter((candidate) => !issueById.has(candidate.id)),
    update: candidates.filter((candidate) => {
      const existing = issueById.get(candidate.id);
      return existing && existing.candidate.candidate_sha256 !== candidate.candidate_sha256;
    }).map((candidate) => ({ candidate, issue: issueById.get(candidate.id).issue })),
    supersede: [
      ...duplicateIssues.filter((issue) => issue.state === "open"),
      ...[...issueById.entries()]
        .filter(([id, entry]) => !activeById.has(id) && entry.issue.state === "open")
        .map(([, entry]) => entry.issue),
    ].filter((issue, index, all) => all.findIndex((item) => item.number === issue.number) === index),
  };
}

module.exports = {
  buildCanonicalSkillCandidates,
  planCandidateIssueSync,
};
