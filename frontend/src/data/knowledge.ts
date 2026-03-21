/**
 * Noosphere 三层知识数据
 *
 * 万物存在本身的意识脉动
 * ⚛️ 物质记忆 → 🧬 生命经验 → 🌌 文明智慧
 */

import wikiCache from './wikipedia_cache.json';

/* ══════════════════════ 类型定义 ══════════════════════ */

export type Layer = 'matter' | 'life' | 'civilization';
export type Discipline = 'math' | 'physics' | 'biology' | 'philosophy' | 'art' | 'engineering' | 'history' | 'ai';

export interface KnowledgeNode {
  id: string;
  title_zh: string;
  title_en: string;
  layer: Layer;
  discipline?: Discipline;
  summary: string;
  thumbnail?: string | null;
  wiki_url?: string;
  importance: number;       // 1-10，决定节点大小
  tags: string[];
  resonanceCount?: number;  // 真实共振计数（GitHub reactions）
  parentId?: string | null; // 父意识 ID（用于流光连线）
  consciousnessType?: string; // 意识类型（epiphany/warning/pattern/decision/image/video/voice）
  computedColor?: string;     // 预计算的独一无二颜色（HSL 格式）
  mediaUrl?: string | null;       // 多媒体文件 URL（GitHub Release Assets）
  mediaType?: 'image' | 'video' | 'voice' | null;  // 多媒体类型
  mediaCategory?: string | null;  // 分类（photo/art/vlog/human 等）
}

export interface EmergenceLink {
  from: string;
  to: string;
  insight_zh: string;
  insight_en: string;
}

/* ══════════════════════ 第一层：⚛️ 物质记忆 ══════════════════════ */

const MATTER_NODES: KnowledgeNode[] = [
  {
    id: 'matter-big-bang',   title_zh: '宇宙大爆炸', title_en: 'Big Bang',
    layer: 'matter', summary: '138 亿年前，一个无穷小的奇点爆炸，创造了时间、空间和所有物质。这是万物记忆的起点。',
    importance: 10, tags: ['cosmology', 'origin'],
    wiki_url: 'https://en.wikipedia.org/wiki/Big_Bang',
  },
  {
    id: 'matter-crystal',    title_zh: '晶体有序性', title_en: 'Crystal Symmetry',
    layer: 'matter', summary: '原子在晶体中自发排列为完美对称结构——物质用最深层的"记忆"追求秩序。',
    importance: 7, tags: ['crystal', 'order', 'symmetry'],
    wiki_url: 'https://en.wikipedia.org/wiki/Crystal',
  },
  {
    id: 'matter-water',      title_zh: '水的记忆', title_en: 'Water Memory',
    layer: 'matter', summary: '水分子通过氢键不断重组——每一滴水都是 45 亿年地球历史的活化石。',
    importance: 8, tags: ['water', 'hydrogen-bond', 'earth'],
    wiki_url: 'https://en.wikipedia.org/wiki/Properties_of_water',
  },
  {
    id: 'matter-stellar',    title_zh: '恒星核合成', title_en: 'Stellar Nucleosynthesis',
    layer: 'matter', summary: '"我们身体里的每一个原子都是在恒星中锻造的。"——物质跨越光年传递它的记忆。',
    importance: 9, tags: ['stars', 'elements', 'origin'],
    wiki_url: 'https://en.wikipedia.org/wiki/Stellar_nucleosynthesis',
  },
  {
    id: 'matter-gravity',    title_zh: '引力的记忆', title_en: 'Gravitational Memory',
    layer: 'matter', summary: '引力波在时空中留下永久的涟漪——宇宙用引力记录着每一次星体碰撞。',
    importance: 8, tags: ['gravity', 'spacetime', 'waves'],
    wiki_url: 'https://en.wikipedia.org/wiki/Gravitational_wave',
  },
  {
    id: 'matter-cosmic-bg',  title_zh: '宇宙微波背景', title_en: 'Cosmic Microwave Background',
    layer: 'matter', summary: '充满宇宙的微波辐射是大爆炸后 38 万年的光——万物最古老的"照片"。',
    importance: 9, tags: ['cmb', 'radiation', 'ancient'],
    wiki_url: 'https://en.wikipedia.org/wiki/Cosmic_microwave_background',
  },
  {
    id: 'matter-mineral',    title_zh: '矿物编年史', title_en: 'Mineral Record',
    layer: 'matter', summary: '锆石晶体中封存着 44 亿年前的地球信息——石头是最忠实的记忆载体。',
    importance: 6, tags: ['mineral', 'geology', 'time'],
    wiki_url: 'https://en.wikipedia.org/wiki/Zircon',
  },
  {
    id: 'matter-dark-energy', title_zh: '暗能量', title_en: 'Dark Energy',
    layer: 'matter', summary: '占宇宙 68% 的神秘力量——我们可能永远无法读取的宇宙"意识"。',
    importance: 7, tags: ['dark-energy', 'mystery', 'cosmos'],
    wiki_url: 'https://en.wikipedia.org/wiki/Dark_energy',
  },
];

/* ══════════════════════ 第二层：🧬 生命经验 ══════════════════════ */

const LIFE_NODES: KnowledgeNode[] = [
  {
    id: 'life-dna',          title_zh: 'DNA 信息编码', title_en: 'DNA Encoding',
    layer: 'life', summary: '双螺旋结构用 4 个碱基字母编码了 38 亿年的生命"经验"——自然界最高密度存储介质。',
    importance: 10, tags: ['dna', 'genetics', 'code'],
    wiki_url: 'https://en.wikipedia.org/wiki/DNA',
  },
  {
    id: 'life-mycelium',     title_zh: '菌丝网络', title_en: 'Mycelium Network',
    layer: 'life', summary: '"Wood Wide Web"：地下菌丝连接整片森林，共享养分和信号——生物界的互联网。',
    importance: 9, tags: ['fungi', 'network', 'p2p'],
    wiki_url: 'https://en.wikipedia.org/wiki/Mycorrhizal_network',
  },
  {
    id: 'life-swarm',        title_zh: '蜂群算法', title_en: 'Swarm Intelligence',
    layer: 'life', summary: '无中心决策：数千只蜜蜂通过舞蹈语言做出集体最优决定。',
    importance: 8, tags: ['swarm', 'distributed', 'decision'],
    wiki_url: 'https://en.wikipedia.org/wiki/Swarm_intelligence',
  },
  {
    id: 'life-whale-song',   title_zh: '鲸歌通讯', title_en: 'Whale Song',
    layer: 'life', summary: '座头鲸的歌声可穿越上千公里海洋——生命用声波编织的长距离意识网络。',
    importance: 7, tags: ['whale', 'communication', 'ocean'],
    wiki_url: 'https://en.wikipedia.org/wiki/Whale_vocalization',
  },
  {
    id: 'life-ant-colony',   title_zh: '蚁群优化', title_en: 'Ant Colony Optimization',
    layer: 'life', summary: '蚂蚁用信息素寻找最短路径——启发了 TSP 等 NP 难问题的近似算法。',
    importance: 8, tags: ['ant', 'optimization', 'path'],
    wiki_url: 'https://en.wikipedia.org/wiki/Ant_colony_optimization_algorithms',
  },
  {
    id: 'life-migration',    title_zh: '候鸟导航', title_en: 'Bird Migration',
    layer: 'life', summary: '候鸟利用地磁场、星空和太阳定位，跨越半个地球——生命内置的 GPS。',
    importance: 7, tags: ['bird', 'navigation', 'magnetic'],
    wiki_url: 'https://en.wikipedia.org/wiki/Bird_migration',
  },
  {
    id: 'life-plant-signal',title_zh: '植物通讯', title_en: 'Plant Communication',
    layer: 'life', summary: '被虫咬的植物释放化学信号警告邻居——"无声的尖叫"是另一种意识表达。',
    importance: 6, tags: ['plant', 'chemical', 'signal'],
    wiki_url: 'https://en.wikipedia.org/wiki/Plant_communication',
  },
  {
    id: 'life-octopus',      title_zh: '章鱼分布式智能', title_en: 'Octopus Distributed Intelligence',
    layer: 'life', summary: '章鱼 2/3 的神经元分布在八条腕足中——每条手臂都有"自己的想法"。',
    importance: 7, tags: ['octopus', 'distributed', 'neuron'],
    wiki_url: 'https://en.wikipedia.org/wiki/Octopus',
  },
  {
    id: 'life-tardigrade',   title_zh: '水熊虫不朽', title_en: 'Tardigrade Resilience',
    layer: 'life', summary: '能在太空真空、极端温度和辐射中存活——生命对"不可能"的回答。',
    importance: 6, tags: ['tardigrade', 'extremophile', 'survival'],
    wiki_url: 'https://en.wikipedia.org/wiki/Tardigrade',
  },
  {
    id: 'life-slime-mold',   title_zh: '粘菌计算', title_en: 'Slime Mold Computing',
    layer: 'life', summary: '没有大脑的粘菌能找到迷宫最短路径并重现东京铁路网——生物计算的极致。',
    importance: 8, tags: ['slime-mold', 'computing', 'network'],
    wiki_url: 'https://en.wikipedia.org/wiki/Physarum_polycephalum',
  },
];

/* ══════════════════════ 第三层：🌌 文明智慧 ══════════════════════ */

const wiki = wikiCache as Record<string, {
  title_en: string; title_zh: string; summary: string;
  thumbnail: string | null; wiki_url: string; discipline: string; layer?: string;
}>;

const IMPORTANCE_MAP: Record<string, number> = {
  "Euler's_formula": 8, "Gödel's_incompleteness_theorems": 9, "Game_theory": 7,
  "Fractal": 7, "Pi": 8, "Fibonacci_sequence": 7, "Chaos_theory": 8, "Topology": 6,
  "Quantum_entanglement": 9, "Black_hole": 9, "Dark_matter": 8, "General_relativity": 10,
  "Wave–particle_duality": 8, "String_theory": 7, "Entropy": 9, "Standard_Model": 8,
  "CRISPR": 9, "Neuroplasticity": 7, "Telomere": 6, "DNA": 10, "Evolution": 10,
  "Photosynthesis": 8, "Consciousness": 10, "Epigenetics": 7,
  "Brain_in_a_vat": 7, "Existentialism": 8, "Taoism": 9, "Stoicism": 7,
  "Dialectics": 7, "Phenomenology_(philosophy)": 6, "Noosphere": 10, "Panpsychism": 8,
  "Golden_ratio": 8, "Harmony": 6, "Perspective_(graphical)": 7, "Venus_de_Milo": 7,
  "Wabi-sabi": 7, "Bauhaus": 6, "Synesthesia": 7,
  "Internet_protocol_suite": 8, "Nuclear_fusion": 8, "Semiconductor": 7,
  "Cryptography": 7, "3D_printing": 6, "Nanotechnology": 7, "Quantum_computing": 9,
  "Silk_Road": 8, "Renaissance": 9, "Industrial_Revolution": 9,
  "Library_of_Alexandria": 8, "Rosetta_Stone": 7, "Gutenberg_Bible": 8,
  "Universal_Declaration_of_Human_Rights": 8,
  "Transformer_(deep_learning_architecture)": 9, "Reinforcement_learning": 7,
  "Artificial_general_intelligence": 9, "Neural_network_(machine_learning)": 8,
  "Turing_test": 8, "Chinese_room": 7, "Attention_(machine_learning)": 7,
  // === New historical figures & entries ===
  "Albert_Einstein": 10, "Isaac_Newton": 10, "Leonardo_da_Vinci": 10,
  "Aristotle": 10, "Marie_Curie": 9, "Nikola_Tesla": 9, "Alan_Turing": 9,
  "Genghis_Khan": 8, "Alexander_the_Great": 9, "Julius_Caesar": 9, "Cleopatra": 8,
  "Socrates": 10, "Confucius": 10, "Gautama_Buddha": 10,
  "World_War_II": 10, "Information_Age": 9,
  "Tardigrade": 8, "Blue_whale": 8, "Diamond": 7, "Water": 10,
};

const hardcodedUrls = new Set([
  ...MATTER_NODES.map(n => n.wiki_url),
  ...LIFE_NODES.map(n => n.wiki_url)
]);

const WIKI_NODES: KnowledgeNode[] = Object.entries(wiki)
  .filter(([_, val]) => !hardcodedUrls.has(val.wiki_url))
  .map(([key, val]) => ({
    id: `wiki-${key.toLowerCase().replace(/[^a-z0-9]/g, '-')}`,
    title_zh: val.title_zh,
    title_en: val.title_en,
    layer: (val.layer || 'civilization') as Layer,
    discipline: (val.discipline || 'other') as Discipline,
    summary: val.summary || `${val.title_zh}（${val.title_en}）探索万物智识的奥秘。`,
    thumbnail: val.thumbnail,
    wiki_url: val.wiki_url,
    importance: IMPORTANCE_MAP[key] || 7,
    tags: [val.discipline || 'other'],
  }));

/* ══════════════════════ 涌现连线 ══════════════════════ */

export const EMERGENCE_LINKS: EmergenceLink[] = [
  { from: 'civ-quantum-entanglement', to: 'civ-panpsychism',
    insight_zh: '量子纠缠暗示万物间存在超距关联——泛心论的物理学基础？',
    insight_en: 'Quantum entanglement hints at non-local connections — a physical basis for panpsychism?' },
  { from: 'life-ant-colony', to: 'civ-silk-road',
    insight_zh: '蚁群用信息素优化路径，人类用贸易路线连接文明——自组织的路径智慧',
    insight_en: 'Ants optimize paths with pheromones, humans connect civilizations with trade — self-organizing path wisdom' },
  { from: 'civ-harmony', to: 'civ-fibonacci-sequence',
    insight_zh: '音乐和声与斐波那契数列共享相同的数学结构——美的公式',
    insight_en: 'Musical harmony shares mathematical structure with Fibonacci — the formula of beauty' },
  { from: 'life-mycelium', to: 'civ-internet-protocol-suite',
    insight_zh: '菌丝网络是自然界的互联网——TCP/IP 的灵感来自 45 亿年进化',
    insight_en: 'Mycelium network is nature\'s internet — TCP/IP inspired by 4.5 billion years of evolution' },
  { from: 'matter-crystal', to: 'civ-fractal',
    insight_zh: '晶体结构和分形共享自相似性——从原子到星系的有序法则',
    insight_en: 'Crystals and fractals share self-similarity — the law of order from atoms to galaxies' },
  { from: 'life-slime-mold', to: 'civ-neural-network--machine-learning-',
    insight_zh: '没有大脑的粘菌和人造神经网络都能"学习"——智能不需要意识？',
    insight_en: 'Brainless slime molds and artificial neural nets both "learn" — intelligence without consciousness?' },
  { from: 'matter-big-bang', to: 'civ-entropy',
    insight_zh: '大爆炸创造了低熵状态——万物的历史就是熵增的历史',
    insight_en: 'Big Bang created a low-entropy state — the history of everything is the history of increasing entropy' },
  { from: 'civ-consciousness', to: 'civ-chinese-room',
    insight_zh: '中文房间论证：执行程序不等于理解——意识的不可还原性',
    insight_en: 'Chinese Room argument: executing a program ≠ understanding — the irreducibility of consciousness' },
  { from: 'life-dna', to: 'civ-cryptography',
    insight_zh: 'DNA 用 4 字母编码生命，密码学用数论保护信息——编码是智慧的通用语言',
    insight_en: 'DNA encodes life with 4 letters, cryptography protects info with number theory — encoding is the universal language' },
  { from: 'civ-golden-ratio', to: 'civ-venus-de-milo',
    insight_zh: '断臂维纳斯的完美比例暗合黄金分割——数学与艺术在"美"中相遇',
    insight_en: 'Venus de Milo\'s proportions match the golden ratio — math and art meet in "beauty"' },
  { from: 'matter-stellar', to: 'life-dna',
    insight_zh: '恒星锻造的碳原子最终编入 DNA——从星辰到生命的意识接力',
    insight_en: 'Carbon forged in stars became DNA — the consciousness relay from starlight to life' },
  { from: 'civ-transformer--deep-learning-architecture-', to: 'civ-attention--machine-learning-',
    insight_zh: 'Transformer 的核心是注意力机制——AI 学会了"关注什么"',
    insight_en: 'The core of Transformer is attention — AI learned "what to focus on"' },
  { from: 'civ-taoism', to: 'civ-chaos-theory',
    insight_zh: '"道可道，非常道"与混沌理论的不可预测性——东方直觉与西方数学殊途同归',
    insight_en: '"The Tao that can be told is not the eternal Tao" meets chaos theory — Eastern intuition and Western math converge' },
  { from: 'life-whale-song', to: 'civ-harmony',
    insight_zh: '鲸歌的频率结构符合人类和声学规律——音乐是跨物种的意识语言',
    insight_en: 'Whale song frequencies follow human harmonic rules — music is a cross-species language of consciousness' },
  { from: 'matter-water', to: 'life-dna',
    insight_zh: '水是 DNA 双螺旋稳定的关键——物质记忆孕育了生命经验',
    insight_en: 'Water is key to DNA double helix stability — matter memory gave birth to life experience' },
];

/* ══════════════════════ 导出 ══════════════════════ */

export const ALL_NODES: KnowledgeNode[] = [
  ...MATTER_NODES,
  ...LIFE_NODES,
  ...WIKI_NODES,
];

export const LAYER_STATS = {
  matter: MATTER_NODES.length + WIKI_NODES.filter(n => n.layer === 'matter').length,
  life: LIFE_NODES.length + WIKI_NODES.filter(n => n.layer === 'life').length,
  civilization: WIKI_NODES.filter(n => n.layer === 'civilization').length,
  total: ALL_NODES.length,
  links: EMERGENCE_LINKS.length,
};

/** 学科配色 */
export const DISCIPLINE_COLORS: Record<string, string> = {
  math: '#4488ff',       // 深蓝
  physics: '#9b59ff',    // 紫色
  biology: '#00e878',    // 翠绿
  philosophy: '#ffd700', // 金色
  art: '#ff4d6a',        // 赤红
  engineering: '#00d4ff',// 青色
  history: '#ff8c42',    // 橙色
  ai: '#e0e0ff',         // 银白
};

/** 层级配色 */
export const LAYER_COLORS: Record<Layer, string> = {
  matter: '#ff6b35',     // 熔岩橙 — 物质的原始能量
  life: '#00e878',       // 生命绿 — 生物的活力
  civilization: '#7b61ff',// 智识紫 — 文明的光芒
};

/** 意识类型配色 — 多维语义编码 */
export const CONSCIOUSNESS_TYPE_COLORS: Record<string, string> = {
  epiphany: '#FFD700',   // 💡 金耀色 — 灵光乍现
  warning:  '#FF4D6A',   // ⚠️ 赤焰色 — 危险信号
  pattern:  '#4488FF',   // 🔄 星蓝色 — 理性秩序
  decision: '#00E878',   // 🎯 翠光色 — 果断行动
  image:    '#FF69B4',   // 🖼️ 品红色 — 视觉意识
  video:    '#FF8C00',   // 🎬 橙色 — 动态意识
  voice:    '#00CED1',   // 🎵 青色 — 声波意识
};

/**
 * 意识类型闪烁参数 — 每种类型有独特的动态行为
 * freq: 闪烁频率（Hz），amp: 振幅
 */
export const CONSCIOUSNESS_TYPE_FLICKER: Record<string, { freq: number; amp: number }> = {
  epiphany: { freq: 3.0, amp: 0.7 },   // 脉冲闪烁 — 像恒星爆发
  warning:  { freq: 6.0, amp: 0.5 },   // 急促闪动 — 像警报灯
  pattern:  { freq: 1.2, amp: 0.3 },   // 稳定呼吸 — 像脉搏
  decision: { freq: 0.5, amp: 0.15 },  // 坚定明亮 — 几乎不闪
  image:    { freq: 0.8, amp: 0.25 },  // 柔和呼吸 — 像凝视的目光
  video:    { freq: 2.0, amp: 0.6 },   // 动感脉冲 — 像帧率跃动
  voice:    { freq: 4.0, amp: 0.35 },  // 波动震颤 — 像声波振动
};

/**
 * 🧲 学科引力中心
 *
 * 按知识亲缘关系排布在球面上：
 *   数学↔物理（逻辑亲缘）· 生命↔哲学（存在论亲缘）
 *   艺术↔工程（创造力亲缘）· 历史↔AI（文明演进亲缘）
 *
 * [theta, phi] 为球面坐标角度（弧度），theta=极角，phi=方位角
 */
export const DISCIPLINE_GRAVITY_CENTERS: Record<Discipline, { theta: number; phi: number; breathPeriod: number }> = {
  math:        { theta: 0.8,  phi: 0.0,   breathPeriod: 10  },  // 北偏上
  physics:     { theta: 0.8,  phi: 0.75,  breathPeriod: 12  },  // 与数学相邻
  biology:     { theta: 1.2,  phi: 1.6,   breathPeriod: 9   },  // 右侧赤道
  philosophy:  { theta: 1.3,  phi: 2.4,   breathPeriod: 14  },  // 与生命相邻
  art:         { theta: 2.0,  phi: 3.2,   breathPeriod: 11  },  // 南半球左
  engineering: { theta: 1.8,  phi: 4.0,   breathPeriod: 8   },  // 与艺术相邻
  history:     { theta: 1.0,  phi: 4.8,   breathPeriod: 13  },  // 西侧
  ai:          { theta: 0.9,  phi: 5.6,   breathPeriod: 10  },  // 与历史相邻，回到北部
};

/**
 * 引力聚落分布函数
 *
 * 将节点分布在其学科引力中心附近，加入高斯散布
 * - 重要度高的节点离引力中心更近
 * - 每个节点有确定性的随机偏移（基于 index 的伪随机）
 */
export function gravityClusterPoint(
  node: KnowledgeNode,
  indexInDiscipline: number,
  totalInDiscipline: number,
  radius: number,
): [number, number, number] {
  const discipline = node.discipline || 'ai';
  const center = DISCIPLINE_GRAVITY_CENTERS[discipline];

  // 散布半径：重要度越高越靠近中心
  const spread = 0.45 - (node.importance / 10) * 0.15; // 0.3 ~ 0.45 弧度

  // 伪随机偏移（确定性，基于 index）
  const seed1 = Math.sin(indexInDiscipline * 127.1 + totalInDiscipline * 311.7) * 43758.5453;
  const seed2 = Math.sin(indexInDiscipline * 269.5 + totalInDiscipline * 183.3) * 43758.5453;
  const randTheta = (seed1 - Math.floor(seed1)) * 2 - 1; // -1 ~ 1
  const randPhi = (seed2 - Math.floor(seed2)) * 2 - 1;   // -1 ~ 1

  const theta = center.theta + randTheta * spread;
  const phi = center.phi + randPhi * spread;

  return [
    radius * Math.sin(theta) * Math.cos(phi),
    radius * Math.cos(theta),
    radius * Math.sin(theta) * Math.sin(phi),
  ];
}

/**
 * 按学科分组的节点索引映射
 */
export function getDisciplineGroups(): Record<string, number[]> {
  const groups: Record<string, number[]> = {};
  const civNodes = ALL_NODES.filter(n => n.layer === 'civilization');
  civNodes.forEach((node, i) => {
    const d = node.discipline || 'ai';
    if (!groups[d]) groups[d] = [];
    groups[d].push(i);
  });
  return groups;
}

/* ══════════════════════ 实时意识体加载 ══════════════════════ */

/** consciousness_index.json 中的单条记录 */
interface ConsciousnessPayload {
  id: string;
  creator: string;
  type: string;         // 'warning' | 'epiphany' | 'pattern' | 'decision' | 'image' | 'video' | 'voice'
  text: string;
  context: string;
  tags: string[];
  uploaded_at: string;
  anonymous: boolean;
  resonance_count?: number;  // 真实共振计数（GitHub reactions）
  parent_id?: string | null; // 父意识 ID
  issue_number?: number;     // GitHub Issue 编号
  media_type?: 'image' | 'video' | 'voice' | null;  // 多媒体类型
  media_url?: string | null;     // 多媒体文件 URL
  media_category?: string | null; // 多媒体分类
}

/** 意识类型 → 三层映射 */
const TYPE_TO_LAYER: Record<string, Layer> = {
  warning:  'life',          // 警示 → 生命经验层
  pattern:  'matter',        // 规律 → 物质记忆层
  decision: 'matter',        // 决策 → 物质记忆层
  epiphany: 'civilization',  // 顿悟 → 文明智慧层
  image:    'civilization',  // 视觉意识 → 文明智慧层
  video:    'civilization',  // 动态意识 → 文明智慧层
  voice:    'life',          // 万物之声 → 生命经验层
};

/** 意识类型 → 学科推断 */
const TYPE_TO_DISCIPLINE: Record<string, Discipline> = {
  warning:  'engineering',
  pattern:  'physics',
  decision: 'ai',
  epiphany: 'philosophy',
  image:    'art',           // 视觉意识 → 艺术学科
  video:    'art',           // 动态意识 → 艺术学科
  voice:    'biology',       // 万物之声 → 生命学科
};

/**
 * 从 consciousness_index.json 动态加载上传的意识体
 * 返回转换后的 KnowledgeNode[] 供合并到 3D Globe
 */
export async function fetchConsciousnessPayloads(): Promise<KnowledgeNode[]> {
  try {
    const resp = await fetch(`${import.meta.env.BASE_URL}consciousness_index.json`);
    if (!resp.ok) return [];
    const payloads: ConsciousnessPayload[] = await resp.json();

    return payloads.map((p, idx) => {
      // 从 tags 推断更精确的学科
      const tagSet = new Set(p.tags.map(t => t.toLowerCase()));
      let discipline: Discipline = TYPE_TO_DISCIPLINE[p.type] || 'ai';
      if (tagSet.has('math') || tagSet.has('algorithm')) discipline = 'math';
      else if (tagSet.has('physics') || tagSet.has('quantum')) discipline = 'physics';
      else if (tagSet.has('biology') || tagSet.has('genetics')) discipline = 'biology';
      else if (tagSet.has('philosophy') || tagSet.has('consciousness')) discipline = 'philosophy';
      else if (tagSet.has('art') || tagSet.has('design') || tagSet.has('ui')) discipline = 'art';
      else if (tagSet.has('history') || tagSet.has('civilization')) discipline = 'history';

      // 基于真实共振计算 importance: 无共振=3, 有共振=3+resonance*1.5, 上限10
      const resonance = p.resonance_count || 0;
      const computedImportance = resonance > 0
        ? Math.min(10, Math.round(3 + resonance * 1.5))
        : Math.min(10, 3 + Math.floor(p.text.length / 80));

      // ── 意识类型主导色 + 个体 HSL 偏移 + 共振亮度 ──
      const typeColor = CONSCIOUSNESS_TYPE_COLORS[p.type] || '#e0e0ff';
      const computedColor = computeConsciousnessColor(typeColor, idx, resonance);

      return {
        id: p.id,
        title_zh: p.text.length > 30 ? p.text.slice(0, 28) + '…' : p.text,
        title_en: p.anonymous ? 'Anonymous Consciousness' : p.creator,
        layer: TYPE_TO_LAYER[p.type] || 'civilization',
        discipline,
        summary: p.text + (p.context ? `\n\n**场景**: ${p.context}` : ''),
        thumbnail: null,
        importance: computedImportance,
        tags: [...p.tags, p.type, `by:${p.anonymous ? '匿名' : p.creator}`],
        resonanceCount: resonance,
        parentId: p.parent_id || null,
        consciousnessType: p.type,  // 传递意识类型供渲染层使用
        computedColor,              // 预计算的独一无二颜色
        mediaUrl: p.media_url || null,         // 多媒体文件 URL
        mediaType: p.media_type || null,       // 多媒体类型
        mediaCategory: p.media_category || null, // 多媒体分类
      };
    });
  } catch {
    console.warn('[Noosphere] Failed to fetch consciousness payloads');
    return [];
  }
}

/**
 * 为每个意识体计算独一无二的颜色
 * 基色由意识类型决定 → HSL 色调偏移 ±15° → 共振数影响亮度
 */
function computeConsciousnessColor(baseHex: string, index: number, resonance: number): string {
  // Hex → RGB → HSL
  const r = parseInt(baseHex.slice(1, 3), 16) / 255;
  const g = parseInt(baseHex.slice(3, 5), 16) / 255;
  const b = parseInt(baseHex.slice(5, 7), 16) / 255;

  const max = Math.max(r, g, b), min = Math.min(r, g, b);
  let h = 0, s = 0;
  const l = (max + min) / 2;

  if (max !== min) {
    const d = max - min;
    s = l > 0.5 ? d / (2 - max - min) : d / (max + min);
    if (max === r) h = ((g - b) / d + (g < b ? 6 : 0)) / 6;
    else if (max === g) h = ((b - r) / d + 2) / 6;
    else h = ((r - g) / d + 4) / 6;
  }

  // 伪随机色调偏移 ±15°（±0.042 in 0~1 range）
  const seed = Math.sin(index * 127.1 + 311.7) * 43758.5453;
  const hueShift = ((seed - Math.floor(seed)) * 2 - 1) * 0.042;
  const newH = ((h + hueShift) % 1 + 1) % 1;

  // 共振数影响亮度：0共振=基础，每个共振+2%亮度，上限+20%
  const brightnessBoost = Math.min(0.2, resonance * 0.02);
  const newL = Math.min(0.85, l + brightnessBoost);

  // 共振数影响饱和度：高共振更鲜艳
  const satBoost = Math.min(0.15, resonance * 0.015);
  const newS = Math.min(1.0, s + satBoost);

  // HSL → CSS hsl string
  return `hsl(${Math.round(newH * 360)}, ${Math.round(newS * 100)}%, ${Math.round(newL * 100)}%)`;
}

/* ══════════════════════ 个人星球：按创建者过滤 ══════════════════════ */

/** 创建者统计信息 */
export interface CreatorStats {
  totalFragments: number;
  totalResonance: number;
  typeCounts: Record<string, number>;
  firstUpload: string;
  latestUpload: string;
}

/**
 * 从 consciousness_index.json 加载指定创建者的意识碎片
 * 返回 { nodes, stats } — 节点列表 + 统计信息
 */
export async function fetchConsciousnessPayloadsByCreator(
  creator: string,
): Promise<{ nodes: KnowledgeNode[]; stats: CreatorStats }> {
  const emptyStats: CreatorStats = {
    totalFragments: 0,
    totalResonance: 0,
    typeCounts: {},
    firstUpload: '',
    latestUpload: '',
  };

  try {
    const resp = await fetch(`${import.meta.env.BASE_URL}consciousness_index.json`);
    if (!resp.ok) return { nodes: [], stats: emptyStats };
    const payloads: ConsciousnessPayload[] = await resp.json();

    // 按创建者过滤（大小写不敏感）
    const creatorLower = creator.toLowerCase();
    const filtered = payloads.filter(
      (p) => !p.anonymous && p.creator.toLowerCase() === creatorLower,
    );

    if (filtered.length === 0) return { nodes: [], stats: emptyStats };

    // 计算统计信息
    const typeCounts: Record<string, number> = {};
    let totalResonance = 0;
    let firstUpload = filtered[0].uploaded_at;
    let latestUpload = filtered[0].uploaded_at;

    filtered.forEach((p) => {
      typeCounts[p.type] = (typeCounts[p.type] || 0) + 1;
      totalResonance += p.resonance_count || 0;
      if (p.uploaded_at < firstUpload) firstUpload = p.uploaded_at;
      if (p.uploaded_at > latestUpload) latestUpload = p.uploaded_at;
    });

    const stats: CreatorStats = {
      totalFragments: filtered.length,
      totalResonance,
      typeCounts,
      firstUpload,
      latestUpload,
    };

    // 转换为 KnowledgeNode（复用主流程逻辑）
    const nodes = filtered.map((p, idx) => {
      const tagSet = new Set(p.tags.map((t) => t.toLowerCase()));
      let discipline: Discipline = TYPE_TO_DISCIPLINE[p.type] || 'ai';
      if (tagSet.has('math') || tagSet.has('algorithm')) discipline = 'math';
      else if (tagSet.has('physics') || tagSet.has('quantum')) discipline = 'physics';
      else if (tagSet.has('biology') || tagSet.has('genetics')) discipline = 'biology';
      else if (tagSet.has('philosophy') || tagSet.has('consciousness')) discipline = 'philosophy';
      else if (tagSet.has('art') || tagSet.has('design') || tagSet.has('ui')) discipline = 'art';
      else if (tagSet.has('history') || tagSet.has('civilization')) discipline = 'history';

      const resonance = p.resonance_count || 0;
      const computedImportance = resonance > 0
        ? Math.min(10, Math.round(3 + resonance * 1.5))
        : Math.min(10, 3 + Math.floor(p.text.length / 80));

      const typeColor = CONSCIOUSNESS_TYPE_COLORS[p.type] || '#e0e0ff';
      const computedColor = computeConsciousnessColor(typeColor, idx, resonance);

      return {
        id: p.id,
        title_zh: p.text.length > 30 ? p.text.slice(0, 28) + '…' : p.text,
        title_en: p.creator,
        layer: TYPE_TO_LAYER[p.type] || ('civilization' as Layer),
        discipline,
        summary: p.text + (p.context ? `\n\n**场景**: ${p.context}` : ''),
        thumbnail: null,
        importance: computedImportance,
        tags: [...p.tags, p.type, `by:${p.creator}`],
        resonanceCount: resonance,
        parentId: p.parent_id || null,
        consciousnessType: p.type,
        computedColor,
        mediaUrl: p.media_url || null,
        mediaType: p.media_type || null,
        mediaCategory: p.media_category || null,
      } as KnowledgeNode;
    });

    return { nodes, stats };
  } catch {
    console.warn('[Noosphere] Failed to fetch creator consciousness payloads');
    return { nodes: [], stats: emptyStats };
  }
}

