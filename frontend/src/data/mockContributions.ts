/**
 * Noosphere 贡献者数据源
 *
 * 从 GitHub REST API 获取真实贡献者数据 (基于 commit 数量)
 * 灵能总值 (Psi) = commits × 10
 */

const REPO_OWNER = 'JinNing6';
const REPO_NAME = 'Noosphere';
const PSI_MULTIPLIER = 10;

export interface Contributor {
  id: string;
  login: string;
  name: string;
  avatarUrl: string;
  commits: number;
  totalScore: number; // Psi = commits × 10
}

export function calculateTitle(score: number): { label: string; color: string; icon: string; glow: string } {
  if (score >= 3000) return { label: '宇宙建筑师', color: '#ffd700', icon: '👑', glow: '0 0 16px rgba(255, 215, 0, 0.6)' };
  if (score >= 1000) return { label: '星海领航员', color: '#7b61ff', icon: '🪐', glow: '0 0 12px rgba(123, 97, 255, 0.5)' };
  if (score >= 500)  return { label: '真理探索家', color: '#00e878', icon: '🌌', glow: '0 0 8px rgba(0, 232, 120, 0.4)' };
  if (score >= 100)  return { label: '记忆编织者', color: '#00d4ff', icon: '💫', glow: '0 0 8px rgba(0, 212, 255, 0.3)' };
  return { label: '星尘行者', color: 'rgba(255,255,255,0.6)', icon: '🌟', glow: 'none' };
}

/**
 * 从 GitHub API 获取真实贡献者列表
 *
 * 使用 GET /repos/{owner}/{repo}/contributors 端点
 * 自动过滤 bot 账号，按 commit 数降序排列
 */
export async function fetchGitHubContributors(): Promise<Contributor[]> {
  const url = `https://api.github.com/repos/${REPO_OWNER}/${REPO_NAME}/contributors?per_page=30`;

  try {
    const response = await fetch(url, {
      headers: {
        'Accept': 'application/vnd.github.v3+json',
        'User-Agent': 'Noosphere-Frontend',
      },
    });

    if (response.status === 202) {
      // GitHub 正在计算统计数据，返回空数组，下次会有数据
      console.warn('[Noosphere] GitHub is computing contributor stats, will retry later.');
      return [];
    }

    if (!response.ok) {
      console.error(`[Noosphere] GitHub API error: ${response.status} ${response.statusText}`);
      return [];
    }

    const raw = await response.json();

    if (!Array.isArray(raw)) {
      console.error('[Noosphere] Unexpected API response format');
      return [];
    }

    return raw
      .filter((c: { type?: string; login?: string }) => {
        // 过滤 bot
        if (c.type === 'Bot') return false;
        if (c.login?.endsWith('[bot]') || c.login?.endsWith('-bot')) return false;
        return true;
      })
      .map((c: { login: string; avatar_url: string; contributions: number; id: number }) => ({
        id: `gh-${c.id}`,
        login: c.login,
        name: c.login,
        avatarUrl: c.avatar_url,
        commits: c.contributions,
        totalScore: c.contributions * PSI_MULTIPLIER,
      }))
      .sort((a: Contributor, b: Contributor) => b.totalScore - a.totalScore);

  } catch (err) {
    console.error('[Noosphere] Failed to fetch contributors:', err);
    return [];
  }
}

/**
 * 生成模拟过去 52 周，每周 7 天的热力图数据
 * 值域：0 ~ 4 (代表活跃度等级)
 *
 * 热力图为装饰性视觉元素，保持随机生成
 */
export function generateHeatmapData(): number[][] {
  const weeks = 52;
  const days = 7;
  const data: number[][] = [];

  for (let w = 0; w < weeks; w++) {
    const weekData: number[] = [];
    for (let d = 0; d < days; d++) {
      let activity = 0;
      const baseProb = Math.random();

      if (w > 40 && w < 48) {
        activity = baseProb > 0.3 ? Math.floor(Math.random() * 4) + 1 : 0;
      } else {
        if (baseProb > 0.7) {
          activity = 1;
        } else if (baseProb > 0.85) {
          activity = 2;
        } else if (baseProb > 0.95) {
          activity = 3 + (Math.random() > 0.8 ? 1 : 0);
        }
      }
      weekData.push(activity);
    }
    data.push(weekData);
  }

  return data;
}

export const MOCK_HEATMAP_DATA = generateHeatmapData();
