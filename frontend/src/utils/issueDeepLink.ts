export const NOOSPHERE_HOME_URL = 'https://jinning6.github.io/Noosphere/';

export function createNoosphereIssueUrl(issueNumber: number, baseUrl = NOOSPHERE_HOME_URL): string {
  const url = new URL(baseUrl);
  url.searchParams.set('issue', String(issueNumber));
  return url.toString();
}

export function readIssueNumberFromSearch(search: string): number | null {
  const rawIssue = new URLSearchParams(search).get('issue')?.trim();
  if (!rawIssue) return null;

  const issueNumber = Number.parseInt(rawIssue, 10);
  return Number.isFinite(issueNumber) && issueNumber > 0 ? issueNumber : null;
}

export function findNodeByIssueNumber<T extends { issueNumber?: number | null }>(
  nodes: T[],
  issueNumber: number | null,
): T | null {
  if (!issueNumber) return null;
  return nodes.find(node => node.issueNumber === issueNumber) || null;
}
