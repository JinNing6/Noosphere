/**
 * Noosphere Contributor Badge — Vercel Serverless Function
 * 
 * 生成 "I contributed to the Noosphere 🧠" 可分享横幅式 SVG 徽章。
 * 支持多种风格：cyberpunk（默认）、flat、banner
 * 
 * 使用方式:
 *   https://noosphere-badge.vercel.app/api/badge/JinNing6
 *   https://noosphere-badge.vercel.app/api/badge/JinNing6?style=banner
 *   https://noosphere-badge.vercel.app/api/badge/JinNing6?style=flat
 * 
 * 嵌入 GitHub README:
 *   [![Noosphere Badge](https://noosphere-badge.vercel.app/api/badge/JinNing6)](https://jinning6.github.io/Noosphere/?profile=JinNing6)
 */

/* ═══════════════ 等级体系 ═══════════════ */

const RANK_LADDER = [
  { min: 0,   title: 'Seedling',           icon: '🌱', color: '#6b7280' },
  { min: 1,   title: 'Ripple',             icon: '💧', color: '#3b82f6' },
  { min: 3,   title: 'Sprout',             icon: '🌿', color: '#22c55e' },
  { min: 5,   title: 'Flame',              icon: '🔥', color: '#f59e0b' },
  { min: 10,  title: 'Storm',              icon: '⚡', color: '#a855f7' },
  { min: 20,  title: 'Star',               icon: '🌟', color: '#ec4899' },
  { min: 50,  title: 'Nebula',             icon: '🌌', color: '#8b5cf6' },
  { min: 100, title: 'Crystal',            icon: '💎', color: '#06b6d4' },
  { min: 200, title: 'Oracle',             icon: '🔮', color: '#d946ef' },
  { min: 500, title: 'Light of Civilization', icon: '🌐', color: '#fbbf24' },
];

function getRank(count) {
  let rank = RANK_LADDER[0];
  for (const r of RANK_LADDER) {
    if (count >= r.min) rank = r;
  }
  return rank;
}

function escapeXml(str) {
  return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

/* ═══════════════ Cyberpunk 风格（默认） ═══════════════ */

function generateCyberpunkBadge(username, count, rank) {
  const totalWidth = 400;
  const height = 36;

  return `<svg xmlns="http://www.w3.org/2000/svg" width="${totalWidth}" height="${height}" viewBox="0 0 ${totalWidth} ${height}">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" style="stop-color:#0a0a1a"/>
      <stop offset="50%" style="stop-color:#111128"/>
      <stop offset="100%" style="stop-color:#0a0a1a"/>
    </linearGradient>
    <linearGradient id="accent" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" style="stop-color:${rank.color}"/>
      <stop offset="100%" style="stop-color:#7b61ff"/>
    </linearGradient>
    <filter id="glow">
      <feGaussianBlur stdDeviation="1.5" result="coloredBlur"/>
      <feMerge>
        <feMergeNode in="coloredBlur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
  </defs>
  
  <!-- 背景 -->
  <rect width="${totalWidth}" height="${height}" rx="6" fill="url(#bg)"/>
  
  <!-- 边框 -->
  <rect width="${totalWidth}" height="${height}" rx="6" fill="none" stroke="${rank.color}30" stroke-width="1"/>
  
  <!-- 底部霓虹线 -->
  <line x1="10" y1="${height - 1}" x2="${totalWidth - 10}" y2="${height - 1}" stroke="url(#accent)" stroke-width="2" opacity="0.6" filter="url(#glow)"/>
  
  <!-- 🧠 图标 -->
  <text x="14" y="23" font-size="16">🧠</text>
  
  <!-- 主文字 -->
  <text x="36" y="22" fill="#e0e0ff" font-family="'Inter', 'Segoe UI', sans-serif" font-size="12" font-weight="600">
    I contributed to the Noosphere
  </text>
  
  <!-- 分隔线 -->
  <line x1="262" y1="8" x2="262" y2="${height - 8}" stroke="${rank.color}40" stroke-width="1"/>
  
  <!-- 等级 -->
  <text x="274" y="22" fill="${rank.color}" font-family="'Inter', 'Segoe UI', sans-serif" font-size="11" font-weight="700" filter="url(#glow)">
    ${escapeXml(rank.icon)} ${escapeXml(rank.title)} · ${count}
  </text>
</svg>`;
}

/* ═══════════════ Flat 风格 ═══════════════ */

function generateFlatBadge(username, count, rank) {
  const leftText = '🧠 Noosphere';
  const rightText = `${rank.title} · ${count}`;
  const leftWidth = 120;
  const rightWidth = Math.max(rightText.length * 7 + 16, 100);
  const totalWidth = leftWidth + rightWidth;

  return `<svg xmlns="http://www.w3.org/2000/svg" width="${totalWidth}" height="20" viewBox="0 0 ${totalWidth} 20">
  <rect width="${leftWidth}" height="20" rx="3" fill="#555"/>
  <rect x="${leftWidth}" width="${rightWidth}" height="20" rx="0" fill="${rank.color}"/>
  <rect x="${leftWidth}" width="${rightWidth}" height="20" rx="3" fill="${rank.color}"/>
  <rect x="${leftWidth - 3}" width="6" height="20" fill="${rank.color}"/>
  <rect width="${totalWidth}" height="20" rx="3" fill="none"/>
  <text x="${leftWidth / 2}" y="14" fill="#fff" font-family="'Verdana', sans-serif" font-size="11" text-anchor="middle">${escapeXml(leftText)}</text>
  <text x="${leftWidth + rightWidth / 2}" y="14" fill="#fff" font-family="'Verdana', sans-serif" font-size="11" font-weight="bold" text-anchor="middle">${escapeXml(rightText)}</text>
</svg>`;
}

/* ═══════════════ Banner 风格 ═══════════════ */

function generateBannerBadge(username, count, rank) {
  const totalWidth = 500;
  const height = 48;

  return `<svg xmlns="http://www.w3.org/2000/svg" width="${totalWidth}" height="${height}" viewBox="0 0 ${totalWidth} ${height}">
  <defs>
    <linearGradient id="banner-bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#0a0a1a"/>
      <stop offset="50%" style="stop-color:#1a1040"/>
      <stop offset="100%" style="stop-color:#0a0a1a"/>
    </linearGradient>
    <filter id="banner-glow">
      <feGaussianBlur stdDeviation="2" result="coloredBlur"/>
      <feMerge>
        <feMergeNode in="coloredBlur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
  </defs>
  
  <rect width="${totalWidth}" height="${height}" rx="8" fill="url(#banner-bg)"/>
  <rect width="${totalWidth}" height="${height}" rx="8" fill="none" stroke="${rank.color}25" stroke-width="1"/>
  
  <!-- 左侧发光条 -->
  <rect x="0" y="0" width="4" height="${height}" rx="2" fill="${rank.color}" opacity="0.7" filter="url(#banner-glow)"/>
  
  <!-- 脑图标 -->
  <text x="20" y="32" font-size="22">🧠</text>
  
  <!-- 主标题 -->
  <text x="50" y="22" fill="#e0e0ff" font-family="'Inter', 'Segoe UI', sans-serif" font-size="14" font-weight="700" letter-spacing="0.5">
    I contributed to the Noosphere
  </text>
  
  <!-- 副标题 -->
  <text x="50" y="38" fill="${rank.color}" font-family="'Inter', 'Segoe UI', sans-serif" font-size="11" opacity="0.8">
    ${escapeXml(username)} · ${escapeXml(rank.icon)} ${escapeXml(rank.title)} · ${count} consciousness uploads
  </text>
  
  <!-- 右侧星球标志 -->
  <text x="${totalWidth - 36}" y="32" font-size="20" opacity="0.6">🌍</text>
</svg>`;
}

/* ═══════════════ API Handler ═══════════════ */

export default async function handler(req, res) {
  const { username } = req.query;
  const style = req.query.style || 'cyberpunk';

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
    
    let svg;
    switch (style) {
      case 'flat':
        svg = generateFlatBadge(username, count, rank);
        break;
      case 'banner':
        svg = generateBannerBadge(username, count, rank);
        break;
      case 'cyberpunk':
      default:
        svg = generateCyberpunkBadge(username, count, rank);
        break;
    }

    // 返回 SVG
    res.setHeader('Content-Type', 'image/svg+xml');
    res.setHeader('Cache-Control', 's-maxage=300, stale-while-revalidate=600');
    return res.status(200).send(svg);
  } catch (err) {
    // Fallback badge
    const fallbackSvg = generateCyberpunkBadge(username, 0, RANK_LADDER[0]);
    res.setHeader('Content-Type', 'image/svg+xml');
    return res.status(200).send(fallbackSvg);
  }
}
