import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import https from 'https';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const OUTPUT_PATH = path.join(__dirname, '../src/data/wikipedia_cache.json');

const ARTICLES = [
  // ================= ⚛️ 物质记忆层 (matter) =================
  // --- 宇宙与星体 ---
  ...[
    { en: "Big_Bang", zh: "宇宙大爆炸", disc: "physics" },
    { en: "Cosmic_microwave_background", zh: "宇宙微波背景", disc: "physics" },
    { en: "Dark_matter", zh: "暗物质", disc: "physics" },
    { en: "Black_hole", zh: "黑洞", disc: "physics" },
    { en: "Neutron_star", zh: "中子星", disc: "physics" },
    { en: "Quasar", zh: "类星体", disc: "physics" },
    { en: "Oort_cloud", zh: "奥尔特云", disc: "physics" },
    { en: "Supernova", zh: "超新星", disc: "physics" },
    { en: "Nebula", zh: "星云", disc: "physics" },
    { en: "Exoplanet", zh: "系外行星", disc: "physics" },
  ].map(i => ({ ...i, layer: "matter" })),
  // --- 矿物、石头与地球历史 ---
  ...[
    { en: "Diamond", zh: "钻石", disc: "history" },
    { en: "Quartz", zh: "石英", disc: "history" },
    { en: "Meteorite", zh: "陨石", disc: "history" },
    { en: "Zircon", zh: "锆石", disc: "history" },
    { en: "Obsidian", zh: "黑曜石", disc: "history" },
    { en: "Amber", zh: "琥珀", disc: "history" },
    { en: "Uranium", zh: "铀矿", disc: "physics" },
    { en: "Graphene", zh: "石墨烯", disc: "engineering" },
    { en: "Antimatter", zh: "反物质", disc: "physics" },
    { en: "Water", zh: "水", disc: "physics" },
    { en: "Tectonic_plate", zh: "地壳构造板块", disc: "history" },
    { en: "Fossil", zh: "化石", disc: "history" },
  ].map(i => ({ ...i, layer: "matter" })),

  // ================= 🧬 生命经验层 (life) =================
  // --- 各类神奇生物 ---
  ...[
    { en: "Tardigrade", zh: "水熊虫", disc: "biology" },
    { en: "Octopus", zh: "章鱼", disc: "biology" },
    { en: "Blue_whale", zh: "蓝鲸", disc: "biology" },
    { en: "Tyrannosaurus", zh: "霸王龙", disc: "biology" },
    { en: "Physarum_polycephalum", zh: "多头绒泡菌 (粘菌)", disc: "biology" },
    { en: "Mycorrhizal_network", zh: "菌根网络", disc: "biology" },
    { en: "Honey_bee", zh: "蜜蜂", disc: "biology" },
    { en: "Ant", zh: "蚂蚁", disc: "biology" },
    { en: "Cyanobacteria", zh: "蓝细菌", disc: "biology" },
    { en: "Sequoiadendron_giganteum", zh: "巨杉", disc: "biology" },
    { en: "Axolotl", zh: "美西螈 (六角恐龙)", disc: "biology" },
    { en: "Mitochondrion", zh: "线粒体", disc: "biology" },
    { en: "Chloroplast", zh: "叶绿体", disc: "biology" },
    { en: "Virus", zh: "病毒", disc: "biology" },
    { en: "Archaea", zh: "古菌", disc: "biology" },
    { en: "DNA", zh: "DNA", disc: "biology" },
    { en: "Evolution", zh: "进化论", disc: "biology" },
    { en: "CRISPR", zh: "CRISPR 基因编辑", disc: "biology" },
    { en: "Neuroplasticity", zh: "神经可塑性", disc: "biology" },
    { en: "Telomere", zh: "端粒", disc: "biology" },
    { en: "Photosynthesis", zh: "光合作用", disc: "biology" },
    { en: "Consciousness", zh: "意识", disc: "philosophy" },
    { en: "Epigenetics", zh: "表观遗传学", disc: "biology" },
    { en: "Turritopsis_dohrnii", zh: "灯塔水母 (永生水母)", disc: "biology" },
    { en: "Coelacanth", zh: "腔棘鱼", disc: "biology" },
    { en: "Velociraptor", zh: "迅猛龙", disc: "biology" },
    { en: "Rafflesia_arnoldii", zh: "大王花", disc: "biology" },
  ].map(i => ({ ...i, layer: "life" })),

  // ================= 🌌 文明智慧层 (civilization) =================
  // --- 历史名人 ---
  ...[
    { en: "Albert_Einstein", zh: "阿尔伯特·爱因斯坦", disc: "physics" },
    { en: "Isaac_Newton", zh: "艾萨克·牛顿", disc: "physics" },
    { en: "Leonardo_da_Vinci", zh: "列奥纳多·达·芬奇", disc: "art" },
    { en: "Aristotle", zh: "亚里士多德", disc: "philosophy" },
    { en: "Marie_Curie", zh: "玛丽·居里", disc: "physics" },
    { en: "Nikola_Tesla", zh: "尼古拉·特斯拉", disc: "engineering" },
    { en: "Alan_Turing", zh: "艾伦·图灵", disc: "ai" },
    { en: "Ada_Lovelace", zh: "阿达·洛芙莱斯", disc: "engineering" },
    { en: "Genghis_Khan", zh: "成吉思汗", disc: "history" },
    { en: "Alexander_the_Great", zh: "亚历山大大帝", disc: "history" },
    { en: "Julius_Caesar", zh: "尤利乌斯·凯撒", disc: "history" },
    { en: "Cleopatra", zh: "克娄巴特拉七世 (埃及艳后)", disc: "history" },
    { en: "Socrates", zh: "苏格拉底", disc: "philosophy" },
    { en: "Confucius", zh: "孔子", disc: "philosophy" },
    { en: "Gautama_Buddha", zh: "释迦牟尼 (佛陀)", disc: "philosophy" },
    { en: "Isaac_Asimov", zh: "艾萨克·阿西莫夫", disc: "history" },
    { en: "Galileo_Galilei", zh: "伽利略·伽利莱", disc: "physics" },
    { en: "Charles_Darwin", zh: "查尔斯·达尔文", disc: "biology" },
    { en: "Wolfgang_Amadeus_Mozart", zh: "沃尔夫冈·阿马德乌斯·莫扎特", disc: "art" },
    { en: "Vincent_van_Gogh", zh: "文森特·梵高", disc: "art" },
  ].map(i => ({ ...i, layer: "civilization" })),
  // --- 重大历史事件 ---
  ...[
    { en: "World_War_II", zh: "第二次世界大战", disc: "history" },
    { en: "French_Revolution", zh: "法国大革命", disc: "history" },
    { en: "Apollo_11", zh: "阿波罗11号登月", disc: "history" },
    { en: "Fall_of_the_Western_Roman_Empire", zh: "西罗马帝国灭亡", disc: "history" },
    { en: "Industrial_Revolution", zh: "工业革命", disc: "history" },
    { en: "Information_Age", zh: "信息时代", disc: "history" },
    { en: "Black_Death", zh: "黑死病", disc: "history" },
    { en: "Renaissance", zh: "文艺复兴", disc: "history" },
    { en: "Voyages_of_Christopher_Columbus", zh: "哥伦布发现新大陆", disc: "history" },
    { en: "French_Revolution", zh: "法国大革命", disc: "history" },
    { en: "Cuban_Missile_Crisis", zh: "古巴导弹危机", disc: "history" },
    { en: "Fall_of_the_Berlin_Wall", zh: "柏林墙倒塌", disc: "history" },
  ].map(i => ({ ...i, layer: "civilization" })),
  // --- 现有哲学艺术数学等词条 ---
  ...[
    { en: "Euler's_formula", zh: "欧拉公式", disc: "math" },
    { en: "Gödel's_incompleteness_theorems", zh: "哥德尔不完备定理", disc: "math" },
    { en: "Game_theory", zh: "博弈论", disc: "math" },
    { en: "Fractal", zh: "分形", disc: "math" },
    { en: "Pi", zh: "圆周率", disc: "math" },
    { en: "Fibonacci_sequence", zh: "斐波那契数列", disc: "math" },
    { en: "Chaos_theory", zh: "混沌理论", disc: "math" },
    { en: "Topology", zh: "拓扑学", disc: "math" },
    { en: "General_relativity", zh: "广义相对论", disc: "physics" },
    { en: "Wave–particle_duality", zh: "波粒二象性", disc: "physics" },
    { en: "String_theory", zh: "弦理论", disc: "physics" },
    { en: "Entropy", zh: "熵", disc: "physics" },
    { en: "Standard_Model", zh: "标准模型", disc: "physics" },
    { en: "Brain_in_a_vat", zh: "缸中之脑", disc: "philosophy" },
    { en: "Existentialism", zh: "存在主义", disc: "philosophy" },
    { en: "Taoism", zh: "道家思想", disc: "philosophy" },
    { en: "Stoicism", zh: "斯多葛主义", disc: "philosophy" },
    { en: "Dialectics", zh: "辩证法", disc: "philosophy" },
    { en: "Phenomenology_(philosophy)", zh: "现象学", disc: "philosophy" },
    { en: "Noosphere", zh: "智识圈", disc: "philosophy" },
    { en: "Panpsychism", zh: "泛心论", disc: "philosophy" },
    { en: "Golden_ratio", zh: "黄金分割", disc: "art" },
    { en: "Harmony", zh: "和声学", disc: "art" },
    { en: "Perspective_(graphical)", zh: "透视法", disc: "art" },
    { en: "Venus_de_Milo", zh: "断臂维纳斯", disc: "art" },
    { en: "Wabi-sabi", zh: "侘寂美学", disc: "art" },
    { en: "Bauhaus", zh: "包豪斯", disc: "art" },
    { en: "Synesthesia", zh: "联觉", disc: "art" },
    { en: "Internet_protocol_suite", zh: "互联网协议栈", disc: "engineering" },
    { en: "Nuclear_fusion", zh: "核聚变", disc: "engineering" },
    { en: "Semiconductor", zh: "半导体", disc: "engineering" },
    { en: "Cryptography", zh: "密码学", disc: "engineering" },
    { en: "3D_printing", zh: "3D 打印", disc: "engineering" },
    { en: "Nanotechnology", zh: "纳米技术", disc: "engineering" },
    { en: "Quantum_computing", zh: "量子计算", disc: "engineering" },
    { en: "Silk_Road", zh: "丝绸之路", disc: "history" },
    { en: "Library_of_Alexandria", zh: "亚历山大图书馆", disc: "history" },
    { en: "Rosetta_Stone", zh: "罗塞塔石碑", disc: "history" },
    { en: "Gutenberg_Bible", zh: "古腾堡圣经", disc: "history" },
    { en: "Universal_Declaration_of_Human_Rights", zh: "世界人权宣言", disc: "history" },
    { en: "Transformer_(deep_learning_architecture)", zh: "Transformer", disc: "ai" },
    { en: "Reinforcement_learning", zh: "强化学习", disc: "ai" },
    { en: "Artificial_general_intelligence", zh: "通用人工智能", disc: "ai" },
    { en: "Neural_network_(machine_learning)", zh: "神经网络", disc: "ai" },
    { en: "Turing_test", zh: "图灵测试", disc: "ai" },
    { en: "Chinese_room", zh: "中文房间", disc: "ai" },
    { en: "Attention_(machine_learning)", zh: "注意力机制", disc: "ai" },
  ].map(i => ({ ...i, layer: "civilization" }))
];

function fetchSummary(title) {
  return new Promise((resolve) => {
    const url = `https://en.wikipedia.org/api/rest_v1/page/summary/${encodeURIComponent(title)}`;
    https.get(url, {
      headers: {
        "User-Agent": "Noosphere/1.0 (https://github.com/JinNing6/Noosphere; noosphere@example.com)"
      }
    }, (res) => {
      let data = '';
      if (res.statusCode === 301 || res.statusCode === 302) {
        // Redirection handling can be complex, for Wikipedia API it's usually followable via simple retry if needed,
        // but wikipedia API rarely 301s the summary endpoint if exact title is used.
        // We'll just return null on non-200.
      }
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        if (res.statusCode === 200) {
          try {
            resolve(JSON.parse(data));
          } catch (e) {
            resolve(null);
          }
        } else {
          resolve(null);
        }
      });
    }).on('error', () => resolve(null));
  });
}

// remove duplicates just in case
const uniqueArticles = [];
const seen = new Set();
for (const a of ARTICLES) {
  if (!seen.has(a.en)) {
    seen.add(a.en);
    uniqueArticles.push(a);
  }
}

async function main() {
  console.log(`🧠 Noosphere 维基科教大千世界数据拉取`);
  console.log(`📊 共 ${uniqueArticles.length} 个条目...`);
  console.log("==================================================");

  const results = {};
  
  // 并发数为 5
  const CONCURRENCY = 5;
  for (let i = 0; i < uniqueArticles.length; i += CONCURRENCY) {
    const batch = uniqueArticles.slice(i, i + CONCURRENCY);
    const promises = batch.map(async (article, idx) => {
      const gIdx = i + idx + 1;
      process.stdout.write(`  [${gIdx}/${uniqueArticles.length}] ${article.zh} (${article.en})... `);
      const data = await fetchSummary(article.en);
      
      let thumbnail = null;
      let summary = "";
      if (data) {
        if (data.thumbnail && data.thumbnail.source) {
          thumbnail = data.thumbnail.source;
        }
        summary = data.extract || "";
        console.log("✅");
      } else {
        console.log("⚠️ fallback");
      }
      
      results[article.en] = {
        title_en: data?.title || article.en.replace(/_/g, " "),
        title_zh: article.zh,
        summary: summary,
        thumbnail: thumbnail,
        wiki_url: data?.content_urls?.desktop?.page || `https://en.wikipedia.org/wiki/${article.en}`,
        discipline: article.disc,
        layer: article.layer
      };
      
      return new Promise(r => setTimeout(r, 100)); // 礼貌延迟
    });
    
    await Promise.all(promises);
  }

  // 保存
  const dir = path.dirname(OUTPUT_PATH);
  if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
  fs.writeFileSync(OUTPUT_PATH, JSON.stringify(results, null, 2), "utf-8");

  console.log("==================================================");
  console.log(`✅ 数据已保存到 ${OUTPUT_PATH}`);
  const stats = fs.statSync(OUTPUT_PATH);
  console.log(`📦 文件大小: ${(stats.size / 1024).toFixed(1)} KB`);
  const thumbs = Object.values(results).filter(v => v.thumbnail).length;
  console.log(`📸 有缩略图: ${thumbs}/${Object.keys(results).length}`);
}

main();
