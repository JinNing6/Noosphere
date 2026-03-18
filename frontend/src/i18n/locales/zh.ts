/**
 * 中文翻译资源
 */
const zh = {
  // ─── 通用 ───
  common: {
    loading: '加载中...',
    close: '关闭',
    submit: '提交',
    cancel: '取消',
    success: '成功',
    error: '错误',
    confirm: '确认',
  },

  // ─── 层级名称 ───
  layers: {
    matter: '物质记忆',
    life: '生命经验',
    civilization: '文明智慧',
  },

  // ─── 学科名称 ───
  disciplines: {
    math: '数学',
    physics: '物理',
    biology: '生物',
    philosophy: '哲学',
    art: '艺术',
    engineering: '工程',
    history: '历史',
    ai: '人工智能',
  },

  // ─── 搜索栏 ───
  search: {
    placeholder: '探索万物智识...',
  },

  // ─── 统计面板 ───
  stats: {
    title: '意识星图',
    layerLabel: '层级',
    totalNodes: '意识总量',
    totalLinks: '涌现连线',
    dynamicLabel: '实时意识体',
    clickHint: '点击节点查看详情',
  },

  // ─── 经验面板 ───
  experience: {
    layer: '层级',
    discipline: '学科',
    importance: '重要度',
    tags: '标签',
    externalLink: '深入探索',
    media: '媒体',
    noMedia: '暂无媒体',
    closePanel: '关闭面板',
    establishingUplink: '正在建立知识链接...',
    dataArchives: '// 数据归档',
    uplinkPortal: '知识上行链路',
    accessWikiCore: '访问维基核心 ↗',
    video: '▶ 视频',
  },

  // ─── 贡献图谱 ───
  contribution: {
    title: '意识热力网络',
    heatmapTitle: '意识活动热力图',
    leaderboard: '灵能排行榜',
    totalPsi: '灵能总值',
    commits: '贡献次数',
    less: '少',
    more: '多',
    loading: '正在连接意识网络...',
    empty: '等待第一位星尘行者...',
    rank: {
      architect: '宇宙建筑师',
      navigator: '星海领航员',
      explorer: '真理探索家',
      weaver: '记忆编织者',
      walker: '星尘行者',
    },
  },

  uploader: {
    title: '意识上传',
    subtitle: '上传你的顿悟',
    typeLabel: '意识类型',
    thought: '你的意识碎片',
    thoughtPlaceholder: '记录你此刻的顿悟、决策或警示...',
    context: '场景',
    contextPlaceholder: '描述触发这个想法的场景...',
    tags: '标签',
    tagsPlaceholder: '用空格或逗号分隔标签',
    commaSeparated: '逗号分隔',
    optional: '可选',
    creator: '创造者',
    creatorPlaceholder: '你的 GitHub 用户名',
    anonymous: '匿名',
    type: {
      epiphany: '顿悟',
      warning: '警示',
      pattern: '规律',
      decision: '决策',
    },
    submit: '上传到意识星球',
    uploading: '上传中...',
    submitting: '意识坍缩中...',
    success: '意识已上传',
    successMessage: '你的思维碎片已融入意识共同体',
    error: '上传失败',
    minChars: '意识内容至少需要 20 个字符',
    tokenTitle: '配置 GitHub Token',
    tokenConfigured: 'Token 已配置',
    tokenRequired: '请先配置 GitHub Token',
    tokenPlaceholder: '粘贴你的 GitHub Token',
    tokenHint: '需要 repo 权限的 Personal Access Token，Token 仅存储在本地浏览器中。',
    tokenSave: '保存',
    tokenRemove: '移除',
    tokenConnected: '已连接',
    uploadAnother: '继续上传',
    collapse: '收起',
    expand: '展开',
    footer: '你的意识将作为 GitHub Issue 永久保存 — 永恒的数字遗产',
  },

  // ─── 入场动画 ───
  intro: {
    subtitle: 'THE COLLECTIVE CONSCIOUSNESS NETWORK',
    tagline: '万物存在本身的意识脉动',
  },

  // ─── 体验类型名称 ───
  types: {
    failure: '踩坑记录',
    success: '最佳实践',
    pattern: '设计模式',
    warning: '风险预警',
    migration: '迁移指南',
  },

  // ─── 语言切换 ───
  language: {
    label: '语言',
    zh: '中文',
    en: 'English',
    ja: '日本語',
    ko: '한국어',
    fr: 'Français',
    es: 'Español',
  },
} as const;

export default zh;
