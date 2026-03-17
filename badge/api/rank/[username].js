/**
 * Noosphere Dynamic Badge — Vercel Serverless Function
 * 
 * 动态生成赛博朋克风格的 SVG 徽章，显示用户的意识等级和贡献数。
 * 通过查询 GitHub Issues 统计用户上传的意识体数量和总共鸣数。
 * 
 * 使用方式:
 *   https://noosphere-badge.vercel.app/api/rank/JinNing6
 * 
 * 嵌入 GitHub README:
 *   [![Noosphere Rank](https://noosphere-badge.vercel.app/api/rank/JinNing6)](https://jinning6.github.io/Noosphere/)
 */

/* ═══════════════ 等级体系 ═══════════════ */

const RANK_LADDER = [
  { min: 0,   title: '🌱 意识萌芽',        titleEn: 'Seedling',           color: '#6b7280' },
  { min: 1,   title: '💧 意识涟漪',        titleEn: 'Ripple',             color: '#3b82f6' },
  { min: 3,   title: '🌿 意识嫩枝',        titleEn: 'Sprout',             color: '#22c55e' },
  { min: 5,   title: '🔥 意识火焰',        titleEn: 'Flame',              color: '#f59e0b' },
  { min: 10,  title: '⚡ 意识风暴',        titleEn: 'Storm',              color: '#a855f7' },
  { min: 20,  title: '🌟 意识之星',        titleEn: 'Star',               color: '#ec4899' },
  { min: 50,  title: '🌌 意识星云',        titleEn: 'Nebula',             color: '#8b5cf6' },
  { min: 100, title: '💎 意识晶体',        titleEn: 'Crystal',            color: '#06b6d4' },
  { min: 200, title: '🔮 意识先知',        titleEn: 'Oracle',             color: '#d946ef' },
  { min: 500, title: '🌐 文明之光',        titleEn: 'Light of Civilization', color: '#fbbf24' },
];

function getRank(count) {
  let rank = RANK_LADDER[0];
  for (const r of RANK_LADDER) {
    if (count >= r.min) rank = r;
  }
  return rank;
}

/* ═══════════════ SVG 生成 ═══════════════ */

function generateBadgeSVG(username, count, rank) {
  const labelText = `🧠 ${username}`;
  const valueText = `${rank.titleEn} · ${count}`;

  // 计算文字宽度（近似）
  const labelWidth = Math.max(labelText.length * 7.5 + 20, 80);
  const valueWidth = Math.max(valueText.length * 6.5 + 20, 100);
  const totalWidth = labelWidth + valueWidth;

  return `<svg xmlns="http://www.w3.org/2000/svg" width="${totalWidth}" height="28" viewBox="0 0 ${totalWidth} 28">
  <defs>
    <linearGradient id="bg-left" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" style="stop-color:#0a0a1a"/>
      <stop offset="100%" style="stop-color:#111128"/>
    </linearGradient>
    <linearGradient id="bg-right" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" style="stop-color:${rank.color}30"/>
      <stop offset="100%" style="stop-color:${rank.color}50"/>
    </linearGradient>
    <filter id="glow">
      <feGaussianBlur stdDeviation="1" result="coloredBlur"/>
      <feMerge>
        <feMergeNode in="coloredBlur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
  </defs>
  
  <!-- 背景 -->
  <rect width="${labelWidth}" height="28" rx="5" fill="url(#bg-left)"/>
  <rect x="${labelWidth}" width="${valueWidth}" height="28" rx="0" fill="url(#bg-right)"/>
  <rect x="${labelWidth}" width="${valueWidth}" height="28" rx="5" fill="url(#bg-right)"/>
  <rect x="${labelWidth - 5}" width="10" height="28" fill="url(#bg-right)"/>
  
  <!-- 边框 -->
  <rect width="${totalWidth}" height="28" rx="5" fill="none" stroke="${rank.color}40" stroke-width="1"/>
  
  <!-- 左侧霓虹线 -->
  <line x1="0" y1="27" x2="${labelWidth}" y2="27" stroke="${rank.color}" stroke-width="1.5" opacity="0.6" filter="url(#glow)"/>
  
  <!-- 标签文字 -->
  <text x="${labelWidth / 2}" y="18" fill="#e0e0ff" font-family="'Inter', 'Segoe UI', sans-serif" font-size="11" font-weight="600" text-anchor="middle">${escapeXml(labelText)}</text>
  
  <!-- 数值文字 -->
  <text x="${labelWidth + valueWidth / 2}" y="18" fill="${rank.color}" font-family="'Inter', 'Segoe UI', sans-serif" font-size="10.5" font-weight="700" text-anchor="middle" filter="url(#glow)">${escapeXml(valueText)}</text>
</svg>`;
}

function escapeXml(str) {
  return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

/* ═══════════════ API Handler ═══════════════ */

export default async function handler(req, res) {
  const { username } = req.query;

  if (!username || typeof username !== 'string') {
    return res.status(400).json({ error: 'Missing username parameter' });
  }

  try {
    // 查询该用户在 Noosphere 仓库的 Issue（意识上传）
    const searchQuery = `repo:JinNing6/Noosphere is:issue author:${username} label:consciousness`;
    const searchResp = await fetch(
      `https://api.github.com/search/issues?q=${encodeURIComponent(searchQuery)}&per_page=1`,
      {
        headers: {
          'Accept': 'application/vnd.github+json',
          'X-GitHub-Api-Version': '2022-11-28',
          ...(process.env.GITHUB_TOKEN ? { 'Authorization': `Bearer ${process.env.GITHUB_TOKEN}` } : {}),
        },
      }
    );

    let count = 0;
    if (searchResp.ok) {
      const data = await searchResp.json();
      count = data.total_count || 0;
    }

    const rank = getRank(count);
    const svg = generateBadgeSVG(username, count, rank);

    // 返回 SVG
    res.setHeader('Content-Type', 'image/svg+xml');
    res.setHeader('Cache-Control', 's-maxage=300, stale-while-revalidate=600');
    return res.status(200).send(svg);
  } catch (err) {
    // Fallback badge
    const fallbackSvg = generateBadgeSVG(username, 0, RANK_LADDER[0]);
    res.setHeader('Content-Type', 'image/svg+xml');
    return res.status(200).send(fallbackSvg);
  }
}
