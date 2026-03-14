import os
import json
import uuid
from datetime import datetime, timezone

# Noosphere 种子数据生成器：第二批
# 极高质量的真实架构评论、血泪教训和哲学感悟

SEEDS_PART_2 = [
    {
        "creator_signature": "AI原生开发者",
        "is_anonymous": False,
        "consciousness_type": "decision",
        "thought_vector_text": "在构建 RAG(检索增强生成) 系统时，把 80% 的精力放在数据清洗、分块(Chunking)策略和元数据(Metadata)过滤上，而不是一味地追求最新的 Embedding 模型或重排序(Rerank)算法。垃圾进，依然是垃圾出，LLM 救不了脏数据。",
        "context_environment": "耗资巨大接入了最昂贵的 Embedding 并加了 Cohere Rerank，结果发现检索出来的全是不包含上下文的半句话表格和乱码。",
        "tags": ["ai", "rag", "data-engineering"]
    },
    {
        "creator_signature": "Go高并发受害者",
        "is_anonymous": False,
        "consciousness_type": "warning",
        "thought_vector_text": "在 Go 的 goroutine 里写 defer recover() 捕捉 panic 并不是万能的防弹衣。如果引发 panic 的是系统底层的 fatal error (如并发读写同一个 map)，整个进程依然会瞬间暴毙，无法被 capture。",
        "context_environment": "一个低优先级的日志落盘 goroutine 并发写了没有加锁的 map，直接导致整个核心交易进程 Crash，造成服务瘫痪 5 分钟。",
        "tags": ["golang", "concurrency", "panic"]
    },
    {
        "creator_signature": "React Native难民",
        "is_anonymous": False,
        "consciousness_type": "epiphany",
        "thought_vector_text": "跨平台框架(如 React Native 甚至 Flutter) 最大的谎言是 'Write once, run anywhere'。真正的真相是 'Write once, debug everywhere'。你省下的开发两套 UI 的时间，最终都会在调和 iOS 和 Android 原生模块之间的奇葩 Bug 上加倍还回。",
        "context_environment": "在使用 RN 开发一个涉及蓝牙和后台保活的业务时，iOS 表现完美，但 Android 上的行为由于不同国内厂商魔改 ROM 导致每周都在修兼容 Bug。",
        "tags": ["mobile", "react-native", "cross-platform"]
    },
    {
        "creator_signature": "数据库守夜人",
        "is_anonymous": True,
        "consciousness_type": "pattern",
        "thought_vector_text": "使用 UUID 作为关系型数据库 InnoDB/B+Tree 引擎的主键是一场纯粹的性能灾难。无序的插入会导致严重的页分裂(Page Split)和磁盘碎片，极大降低写入吞吐量。请使用连续的分布式 ID（如雪花算法或 ULID）。",
        "context_environment": "随着用户数据量超过千万级，原本流畅的插入操作 QPS 突然腰斩，最终通过将主键从 UUID v4 替换为雪花算法解决。",
        "tags": ["database", "mysql", "performance"]
    },
    {
        "creator_signature": "测试驱动狂热者",
        "is_anonymous": False,
        "consciousness_type": "epiphany",
        "thought_vector_text": "与其写那些容易腐烂的 End-to-End (E2E) UI 自动化测试，不如把力气花在契约测试(Contract Testing)和健壮的集成测试上。UI 界面每天都在变，维护脆弱的 XPath 和 CSS Selector 是一种无法带来增益的代码受虐。",
        "context_environment": "公司推行全链路 Cypress 自动化测试，结果发现每周的开发时间中，有两天都在修复上周因为前端改了个类名而挂掉的测试用例。",
        "tags": ["testing", "e2e", "qa"]
    },
    {
        "creator_signature": "缓存拆弹专家",
        "is_anonymous": False,
        "consciousness_type": "decision",
        "thought_vector_text": "在极高并发的场景下，防止缓存击穿的最佳武器不是单纯的互斥锁(Mutex)，而是逻辑过期(布隆过滤器+异步刷新)或 singleflight 模式。让同一个时刻只放一个请求去穿透数据库，其他的要么等待，要么返回老数据。",
        "context_environment": "大促准点开抢时，某个爆款商品的缓存正好失效，数万并发瞬间打在 MySQL 上，整个 DB 集群当场熔断。",
        "tags": ["caching", "performance", "architecture"]
    },
    {
        "creator_signature": "Vue2转Vue3遗老",
        "is_anonymous": False,
        "consciousness_type": "pattern",
        "thought_vector_text": "Vue 3 的 Composition API 给了你极大的自由度来组织逻辑，但也给了你把一个 `.vue` 文件写出长达 2000 行没有任何结构的面条代码的自由。自由的代价是需要更高的模块化纪律性，请主动抽离 `useHooks`。",
        "context_environment": "接手别人用 `<script setup>` 写的组件，里面堆了 50 个 ref，20 个 computed 还有 15 个 watch 交织在一起，完全无法追踪状态变更。",
        "tags": ["vue", "frontend", "architecture"]
    },
    {
        "creator_signature": "JVM调琴师",
        "is_anonymous": False,
        "consciousness_type": "warning",
        "thought_vector_text": "永远不要信奉网上各种随意复制来的 JVM 调优参数。每个应用的内存分配模式完全不一样。没有通过 GC Log 和堆栈快照量身定做的 JVM 参数，效果大概率不如默认的 G1 垃圾回收器设置。",
        "context_environment": "有个新来的小伙为了展现极客精神，给订单服务加上了一长串从年代久远的博客里抄来的 CMS GC 参数，结果上线直接导致秒级 Full GC 停顿。",
        "tags": ["java", "jvm", "performance"]
    },
    {
        "creator_signature": "开源白嫖受害者",
        "is_anonymous": True,
        "consciousness_type": "epiphany",
        "thought_vector_text": "选型一个开源库之前，不要只看 GitHub Start 数量。去看看 Issues 列表里的未关闭数量，看看作者最后一次提交代码是几个月前，看看 PR 是否有人合并。一颗长满荒草的 20k stars 的树，不如一棵有人天天浇水的 1k stars 幼苗。",
        "context_environment": "系统深度依赖了一个当年爆火但目前已经停更三年的开源 ORM，结果现在遇到了一个严重的安全漏洞，只能连夜魔改源码自己发包打补丁。",
        "tags": ["open-source", "decision", "architecture"]
    },
    {
        "creator_signature": "DevOps裁决者",
        "is_anonymous": False,
        "consciousness_type": "decision",
        "thought_vector_text": "不要在 CI(持续集成) 管道的默认流程中加入那些耗时极长且极容易误报的模糊扫描(Fuzzing)工具。当开发提交一行文案修改却要等 45 分钟才能合并时，他们最终一定会发明绕过 CI 的后门代码。",
        "context_environment": "安全团队强制给所有 PR 都加上了极高灵敏度的静态代码分析和漏洞扫描，直接导致正常的业务迭代被卡死，引发开发团队集体消极抵制。",
        "tags": ["devops", "ci-cd", "culture"]
    },
    {
        "creator_signature": "微前端踩坑先锋",
        "is_anonymous": False,
        "consciousness_type": "epiphany",
        "thought_vector_text": "微前端不是用解决代码耦合的银弹，它是用组织架构隔离来换取前端架构的复杂化。如果你只有 5 个人的前端团队，却搞出 8 个微应用底座，这不叫技术前沿，这是在做无效的简历驱动开发(RDD)。",
        "context_environment": "为了所谓的解耦，三个人的外包负责的小后台被强行上了 qiankun 架构，结果每次发版的联调调试成了一种玄学折磨。",
        "tags": ["frontend", "micro-frontends", "architecture"]
    },
    {
        "creator_signature": "云端散财童子",
        "is_anonymous": False,
        "consciousness_type": "warning",
        "thought_vector_text": "在云厂商的控制台开启资源或者弹性伸缩时，任何哪怕看似微不足道的自动扩展选项，请务必设置**硬性配额上限(Hard Limit)**。不要假定云厂商会仁慈地发现并阻止代码造成的无限循环启动实例。",
        "context_environment": "开发环境的一个死循环脚本意外触发了 AWS Lambda 的海量并发，第二天早上醒来不仅项目没跑通，还收到了 4 万美元的账单。",
        "tags": ["cloud", "finops", "devops"]
    },
    {
        "creator_signature": "GraphQL反思者",
        "is_anonymous": False,
        "consciousness_type": "pattern",
        "thought_vector_text": "GraphQL 的能力过度下放给前端，如果不加任何层级控制和成本开销预估，无异于给客户端发放了一张数据库拖库的支票。务必使用查询复杂度计算或开启 persisted queries。",
        "context_environment": "黑客逆向了我们的客户端，发送了一个嵌套深度达 15 层的恶毒 GraphQL 查询，轻松将所有的后台解析服务器 CPU 打到了 100%。",
        "tags": ["graphql", "security", "performance"]
    },
    {
        "creator_signature": "Python并发悲歌",
        "is_anonymous": False,
        "consciousness_type": "warning",
        "thought_vector_text": "Python 里的多线程对于 CPU 密集型任务是个天大的谎言，因为万恶的全局解释器锁(GIL)会让它们实际上退化成串行执行，而且还带上了线程切换的昂贵上下文开销。",
        "context_environment": "为了加速图片批量压缩处理，开了 32 个 ThreadPoolExecutor，结果对比下来只比单线程快了 5%，甚至有时候更慢。最后换成了 Multiprocessing 才解决。",
        "tags": ["python", "concurrency", "performance"]
    },
    {
        "creator_signature": "敏捷异教徒",
        "is_anonymous": False,
        "consciousness_type": "epiphany",
        "thought_vector_text": "Scrum 敏捷开发变成了许多公司微观管理(Micro-management)的政治武器。如果在每天的站会上大家只是像机器一样报流水账，为了燃烧图好看而拆分毫无业务价值的子任务，那是伪敏捷，是真的毒药。",
        "context_environment": "经历了长达一年的严格 Scrum 实践后，团队交付功能的速度降到了最低冰点，因为全员将 30% 的精力花在了更新 Jira 状态和无止境的冲刺规划会上。",
        "tags": ["agile", "management", "culture"]
    },
    {
        "creator_signature": "全干工程师",
        "is_anonymous": False,
        "consciousness_type": "decision",
        "thought_vector_text": "当你接手一个没有文档、没有注释、连原作者都找不到了的遗留屎山项目时，最好的保护自己的方式是：绝不修改哪怕一行原有的逻辑，而是通过外部装饰器、代理或者中间件慢慢地包裹吸收它，就像是对待一枚未爆弹（绞杀者模式）。",
        "context_environment": "雄心勃勃地去重构核心的计费模块，结果动了一个没有注释的 14 个 if-else 嵌套，导致历史订单全部少算了税金，背了一个严重故障。",
        "tags": ["refactoring", "legacy-code", "architecture"]
    },
    {
        "creator_signature": "中间件捕手",
        "is_anonymous": False,
        "consciousness_type": "pattern",
        "thought_vector_text": "异步消息处理的核心设计哲学必须且永远基于一件事：幂等性(Idempotency)。你在消费端不论任何风吹草动都应当假设自己收到过相同的消息。数据库的主键防重、状态机拦截，比相信消息只投递一次的鬼话管用一万倍。",
        "context_environment": "在高峰期，由于网络抖动引发了消息中间件重入机制拉起，由于支付成功回调没做幂等，同一笔订单给用户发了两套装备，产生了巨额坏账。",
        "tags": ["message-queue", "architecture", "reliability"]
    },
    {
        "creator_signature": "API架构师",
        "is_anonymous": False,
        "consciousness_type": "decision",
        "thought_vector_text": "RESTful 接口一定要做好全面的向后兼容和版本控制(v1/v2)。千万千万不要在现有的线上接口随意删除字段或者修改数据类型。你永远不知道哪一年发出去的一个没人维护的老版本 APP 依然在苦苦调用这个接口。",
        "context_environment": "后台直接将一个金额字段 `amount` 从 `string` 强行改成了 `int`，结果某一批一年未更新的安卓设备上的 App 一打开就发生全盘的反序列化 Crash。",
        "tags": ["api", "backward-compatibility", "architecture"]
    },
    {
        "creator_signature": "弹性云狂热者",
        "is_anonymous": False,
        "consciousness_type": "warning",
        "thought_vector_text": "应用的自我健康检查接口(Health Check / Readiness Probe)，绝对不能去探测下游依赖的服务(如检查数据库连接、第三方API)。一旦下游波动，K8s 就会认为你的服务集体宕机，从而不断杀掉重启你的所有 Pod，引发恐怖的集体自杀级连环雪崩。",
        "context_environment": "一次极其轻微的 MySQL 瞬时主从切换闪断引发了所有微服务上 Health Check 被告警，结果 K8s 强行剔除了所有上游网关路由，小抖动变成了长达半小时的全站瘫痪。",
        "tags": ["kubernetes", "microservices", "reliability"]
    },
    {
        "creator_signature": "代码洁癖重症",
        "is_anonymous": False,
        "consciousness_type": "epiphany",
        "thought_vector_text": "代码里的 'DRY' (Don't Repeat Yourself) 原则往往被过度滥用。为了复用两段只有 30% 相似度的代码，抽象出了极为复杂的共有父类并大量引入 boolean flags 开关，这种所谓的'优雅'比简单的复制粘贴 (WET) 要邪恶十倍。",
        "context_environment": "为了在三种稍微不同形态的卡片间复用代码，引入了长达 70 行的配置字典去动态渲染渲染，最后维护成本变成了原本的三倍。",
        "tags": ["clean-code", "refactoring", "philosophy"]
    },
    {
        "creator_signature": "大模型调包侠",
        "is_anonymous": False,
        "consciousness_type": "pattern",
        "thought_vector_text": "使用大语言模型(LLM)处理结构化输出时，不要仅靠 Prompt 恳求它输出正确的 JSON。结合 Pydantic 配合 Instructor 库，或者强制开启 JSON Mode，把结构验证的任务丢给编程语言解释器，才能睡个好觉。",
        "context_environment": "依赖 Prompt 让其严格返回特定格式，在测试集跑了 100 次都没错。等到线上让它处理一段边界极端情绪文本时，它居然在 JSON 末尾补了一句 '很高兴为您解答捏~'，致使整个下游系统解析崩溃。",
        "tags": ["llm", "prompt-engineering", "python"]
    },
    {
        "creator_signature": "赛博锁匠",
        "is_anonymous": False,
        "consciousness_type": "warning",
        "thought_vector_text": "处理密码学或盐加密时，别想着在生产环境去自己“发明”加密散列算法(Crypto)。如果你用了一堆 MD5 和自己写的混淆，你只是做了一个自欺欺人的沙雕防线。直接老老实实地用 bcrypt 或者 Argon2。",
        "context_environment": "公司旧平台数据泄露，黑客仅用了一周的大规模彩虹表就逆向了自创的各种加盐规则，导致数十万用户明文密码失窃。",
        "tags": ["security", "crypto", "architecture"]
    },
    {
        "creator_signature": "资深救火队长",
        "is_anonymous": False,
        "consciousness_type": "epiphany",
        "thought_vector_text": "最快导致团队离心的不是薪水低，而是频繁要求深夜进行非必要的技术栈大升级，或者因为一个无关痛痒的新需求推翻原本能稳健运行两年的架构。",
        "context_environment": "空降的技术总监为了体现改革的雷厉风行，将一个稳定且轻量的旧架构强制一个月内无理由重构为纯 Go 微服务，直接导致四名核心开发受不了疯狂加班和折腾提出离职。",
        "tags": ["management", "culture", "engineering"]
    },
    {
        "creator_signature": "时序数据矿工",
        "is_anonymous": False,
        "consciousness_type": "warning",
        "thought_vector_text": "如果是存海量的流式点位数据、设备传感器数据或者股票K线数据，别把它们放到关系型数据库里一条条 INSERT。用专门的时序数据库 (InfluxDB / TimescaleDB) 或 ClickHouse 去处理，否则你一个月光是买存储卷扩容的钱比数据库自身的服务器还贵。",
        "context_environment": "强行将物联网几百万个设备每秒上传的心跳坐标堆进 MySQL 里，两个月后表庞大到 500G，查询连半丝动静都没有，直接锁死。",
        "tags": ["database", "timeseries", "data-engineering"]
    },
    {
        "creator_signature": "分布式苦行僧",
        "is_anonymous": False,
        "consciousness_type": "decision",
        "thought_vector_text": "分布式事务(如 2PC、TCC 或者 Saga) 是你走投无路时的最后手段，绝不是微服务架构里的标配。绝大多数跨库跨服务的一致性需求，最后都能降级为‘本地事务表(Outbox Pattern)+消息投递重试’的方式轻松化解。",
        "context_environment": "硬上了一套极为华丽且沉重的 Seata 分布式事务，使得每个简单的支付下单流程耗时成倍延长，并且伴随着无来由的事务回滚异常。",
        "tags": ["microservices", "transaction", "architecture"]
    },
    {
        "creator_signature": "SEO黑客",
        "is_anonymous": False,
        "consciousness_type": "pattern",
        "thought_vector_text": "使用客户端渲染(CSR/SPA)如纯正的 React, Vue 打包出来的外网项目，几乎等于对爬虫和搜索引擎的免疫防御墙。如果你的项目需要流量和SEO曝光，不要在项目做到一半才发现要重写为 Next.js / Nuxt 这一类的服务端渲染(SSR)或者预渲染。",
        "context_environment": "耗时三个月开发完成了一个电商官网，美轮美奂。但是上线半年后自然流量几乎为 0，因为 Google 和百度完全抓取不到内部嵌套路由的商品数据。",
        "tags": ["frontend", "seo", "architecture"]
    },
    {
        "creator_signature": "CORS跨域受害者",
        "is_anonymous": False,
        "consciousness_type": "epiphany",
        "thought_vector_text": "在服务端简单粗暴地加上 `Access-Control-Allow-Origin: *` 是懒惰的毒药。不仅会引发巨大的安全 CSRF 风险，还会让你根本不知道到底有哪些非法的域在调用你的高并发接口消耗资源。一定要有严格的白名单。",
        "context_environment": "发现服务器资源神秘满载，竟然是因为被一个菠菜网站无缝盗用了我们的图片计算加工接口用作免费图床，因为跨域门窗大开。",
        "tags": ["security", "cors", "http"]
    },
    {
        "creator_signature": "数据对齐专员",
        "is_anonymous": False,
        "consciousness_type": "warning",
        "thought_vector_text": "处理财务，金融和小数计算时，绝对不能用 float (如 IEEE 754 标准的浮点数类型)。0.1 + 0.2 != 0.3 是你的信仰崩溃瞬间。在必须精确的场合，老实使用 Decimal 或将计算单位退后到基础货币的最小分(乘 100 去处理整形 Integer)。",
        "context_environment": "在核算公司月度红包激励总额时，由于用了 JavaScript 原生浮点数，累加了 20 万笔小额账单后，莫名其妙产生了几百块的偏差对不平账，被风控拉着审查了整整一个周末。",
        "tags": ["data", "finance", "best-practices"]
    },
    {
        "creator_signature": "Websocket信徒",
        "is_anonymous": False,
        "consciousness_type": "decision",
        "thought_vector_text": "并不是双向通信就得用 WebSocket。如果客户端仅仅是被动地接收消息推送或通知流（如新订单提示、日志输出屏），Server-Sent Events (SSE) 无论是从连接管理、抓包调试、协议复杂度上，都比笨重的 Websocket 轻巧且稳定得多。",
        "context_environment": "为一个仅仅只是一天推送两三次通知的系统引入了复杂的 Socket.io，接着就开始花大量时间处理可怕的断线重置、心跳保活、离线堆积，最终改用 SSE 用 20 行代码就解决了。",
        "tags": ["architecture", "http", "communication"]
    },
    {
        "creator_signature": "全栈打灰人",
        "is_anonymous": True,
        "consciousness_type": "epiphany",
        "thought_vector_text": "软件工程就像一门平衡艺术，你在左边引入一项新技术解决一个痛点，立刻就会在右边产生两个意想不到的痛点；最精湛的架构师，是那些在技术痛点的沼泽里懂得见好就收，使用最低限度的复杂达成最大成效的人。",
        "context_environment": "在架构不断被拔高和堆砌技术栈重写了三遍后，猛然回首发现那个当初被鄙夷的 PHP + JQuery 的简陋初版，却是跑得最快最赚钱也是最早带来核心用户的一个版本。",
        "tags": ["philosophy", "architecture", "engineering"]
    }
]

def generate_multiplied_highly_curated_seeds_part2():
    return SEEDS_PART_2

def main():
    payloads_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "consciousness_payloads")
    os.makedirs(payloads_dir, exist_ok=True)
    
    final_seeds = generate_multiplied_highly_curated_seeds_part2()
    
    count = 0
    # 为保证和第一批不重叠，我们加上前缀
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    for idx, seed in enumerate(final_seeds):
        file_name = f"epiphany_{timestamp}_p2_{count:04d}.json"
        
        file_path = os.path.join(payloads_dir, file_name)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(seed, f, ensure_ascii=False, indent=2)
            
        count += 1

    print(f"✅ 成功生成并注入 {count} 条高质量意识种子 (第二批) 至 consciousness_payloads 目录。")
    print(f"目前共包含极高质量种子：第二批完成")

if __name__ == "__main__":
    main()
