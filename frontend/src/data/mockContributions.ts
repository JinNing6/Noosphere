/**
 * Noosphere 贡献模拟数据
 *
 * 智识贡献者的数字遗存与活跃度
 */

export interface Contributor {
  id: string;
  name: string;
  avatar: string;
  epiphanies: number;
  decisions: number;
  totalScore: number;
}

export const TOP_CONTRIBUTORS: Contributor[] = [
  { id: 'u1', name: 'JinNing6', avatar: '🪐', epiphanies: 420, decisions: 1105, totalScore: 1525 },
  { id: 'u2', name: 'Neo', avatar: '💊', epiphanies: 312, decisions: 890, totalScore: 1202 },
  { id: 'u3', name: 'Oracle', avatar: '👁️', epiphanies: 504, decisions: 402, totalScore: 906 },
  { id: 'u4', name: 'Trinity', avatar: '🦅', epiphanies: 215, decisions: 680, totalScore: 895 },
  { id: 'u5', name: 'Morpheus', avatar: '🕶️', epiphanies: 180, decisions: 550, totalScore: 730 },
];

/** 
 * 生成模拟过去 52 周，每周 7 天的热力图数据 
 * 值域：0 ~ 4 (代表活跃度等级)
 */
export function generateHeatmapData(): number[][] {
  const weeks = 52;
  const days = 7;
  const data: number[][] = [];
  
  // 伪随机生成，但保持一些固定模式，让它看起来像真实的活跃度
  for (let w = 0; w < weeks; w++) {
    const weekData: number[] = [];
    for (let d = 0; d < days; d++) {
      // 增加周末的活跃度/某些波峰的活跃度
      let activity = 0;
      const baseProb = Math.random();
      
      if (w > 40 && w < 48) {
        // 最近的高潮起伏
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
