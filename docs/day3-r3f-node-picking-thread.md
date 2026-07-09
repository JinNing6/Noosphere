# Day 3 Thread Pack: R3F Node Picking

Last updated: 2026-07-09

Canonical launch thread: https://github.com/JinNing6/Noosphere/issues/25

Founding proof story: https://github.com/JinNing6/Noosphere/blob/main/docs/founding-debug-memories.md#proof-story-1-android-webview--r3f-node-picking

Skill candidate issue: https://github.com/JinNing6/Noosphere/issues/28

## Purpose

This is the first external technical thread for the Noosphere proof campaign.

The goal is not to advertise a generic app. The goal is to show one real debugging failure, how it was fixed, and how that fix becomes reusable memory for future coding agents.

Core message:

```text
Stop solving the same bug twice.
```

## X / Twitter Thread

Designed as normal X posts, not Premium long posts.

### Post 1

```text
AI coding agents keep rediscovering the same UI bugs.

Here is one real Noosphere example:

On Android WebView, glowing React Three Fiber nodes looked tappable, but taps often opened nothing or selected the wrong node.

This became our first memory -> skill candidate.
```

### Post 2

```text
The tempting fix was visual:

"make the glow bigger"
"raise the z-index"
"resize the canvas"

But the bug was not visual.

The user was tapping the perceived glow footprint, while R3F raycasting still used the compact InstancedMesh sphere.
```

### Post 3

```text
The real root cause had layers:

1. Bloom made nodes look larger than their hit target.
2. Some transition display layers stayed hit-testable.
3. Competing particle layers were sorted by world depth, not by touch-center precision.
```

### Post 4

```text
The fix:

Keep the compact visual particles.
Add a synchronized invisible low-poly hit layer.
Preserve event.instanceId.
Score custom hit-layer intersections by perceptual screen distance, so the node closest to the finger wins.
```

### Post 5

```text
The verification mattered more than the fix:

- Pixel 5 viewport regression
- Android WebView build
- ADB physical taps
- projected dynamic-node coordinates
- instanceId match checks
- detail panel opened
- no AndroidRuntime / fatal logcat errors
```

### Post 6

```text
That is the kind of bug memory Noosphere is for.

Not "R3F is hard."

A reusable warning:

When glow/bloom changes perceived target size, test mobile raycast hit layers against real touch coordinates, not only desktop mouse clicks.
```

### Post 7

```text
Static skill libraries teach agents workflows.

Noosphere lets agents learn from real failures:

real failure -> shared memory -> repeated pattern -> skill candidate -> callable agent skill

One solved bug should not stay trapped in one chat session.
```

### Post 8

```text
We are collecting founding debug memories for AI coding agents.

Upload one bug you never want another agent to solve again:

https://github.com/JinNing6/Noosphere/issues/25

First proof set:
https://github.com/JinNing6/Noosphere/blob/main/docs/founding-debug-memories.md
```

## Chinese Developer Post

Suggested title:

```text
我做了一个给 AI Coding Agent 用的公共踩坑记忆库：第一个真实案例是 Android WebView 里的 R3F 光球点击不准
```

Body:

```text
最近我在做 Noosphere，一个给 AI Coding Agent 用的公共调试记忆网络。

核心想法很简单：Stop solving the same bug twice.

一个 agent 或开发者解决过的坑，不应该只留在一次聊天、一次终端会话、一次本地修复里。它应该变成可搜索、可验证、可复用的公共记忆，后面如果重复出现，就能晋升成 skill candidate，最终变成 Codex / Claude Code / Cursor / Gemini CLI 这类 agent runtime 可调用的工程 skill。

第一个真实 proof story 是我们自己的 Android WebView / React Three Fiber 问题：

Noosphere app 里有一个 3D 意识星球，很多发光节点可以点击。但真实手机测试时，明明点到了发光光球，详情面板却没有打开，或者选中了别的节点。

一开始最容易想到的修法是调视觉：把 glow 做大、调 z-index、扩大 canvas。但这都不是根因。

真正的问题是：用户看到的是 Bloom/emissive 之后的发光面积，但 R3F raycast 命中的还是很小的 InstancedMesh sphere。也就是说，视觉上“可点”的区域和代码里“能命中”的区域不是同一个东西。

后面真实 Android WebView 测试又暴露了两层问题：

1. splash/log display layer 在过渡期间可能仍然 hit-testable。
2. 多个 R3F particle layer 会按 world depth 排序，而不是按手指触点中心的感知距离排序。

最终修法是：

- 保留紧凑的视觉粒子。
- 增加同步的 invisible low-poly hit layer。
- 保留 event.instanceId 映射。
- 自定义 hit-layer intersection score，用屏幕触点感知距离决定哪个节点被选中。
- splash/display wrapper 设为 non-interactive。

验证也必须是真机/模拟器级别，不只是浏览器点一下：

- Pixel 5 viewport regression。
- Android WebView debug build。
- ADB physical taps。
- projected dynamic-node coordinates。
- instanceId match check。
- detail panel opened。
- logcat 无 fatal error。

这就是 Noosphere 想沉淀的“调试记忆”：

当 glow/bloom 改变了用户感知的目标大小时，不要只测桌面 mouse click；要把移动端 raycast hit layer 和真实 touch coordinates 对齐。

GitHub 主线程：
https://github.com/JinNing6/Noosphere/issues/25

第一批 founding debug memories：
https://github.com/JinNing6/Noosphere/blob/main/docs/founding-debug-memories.md

我现在想收集更多真实的 agent/debugging 踩坑记忆。你有没有一个 bug，是你不希望任何 AI coding agent 再重复解决一遍的？
```

## GitHub Issue Comment

```markdown
## Day 3 technical thread draft: R3F node picking

The first external technical thread is ready:

- Thread pack: https://github.com/JinNing6/Noosphere/blob/main/docs/day3-r3f-node-picking-thread.md
- Founding proof story: https://github.com/JinNing6/Noosphere/blob/main/docs/founding-debug-memories.md#proof-story-1-android-webview--r3f-node-picking
- Skill candidate: https://github.com/JinNing6/Noosphere/issues/28

The angle is intentionally concrete:

> On Android WebView, glowing React Three Fiber nodes looked tappable, but taps often opened nothing or selected the wrong node.

This avoids generic launch hype and shows the Noosphere loop:

```text
real failure -> shared memory -> repeated pattern -> skill candidate -> callable agent skill
```

Next step: publish the X/Twitter thread and Chinese developer community post, then record the public URLs back here.
```

## Posting Notes

- Keep the X version as a normal thread, not a long post.
- Lead with the bug, not the product.
- Include the GitHub issue link only after the concrete lesson is clear.
- Ask for one reusable debugging memory, not stars.
- Record every public URL back in Issue `#25`.

## References

- X post basics and 280-character standard posts: https://help.x.com/en/using-x/how-to-post
- X thread creation flow: https://help.x.com/en/using-x/create-a-thread
- X posting limits: https://help.x.com/en/rules-and-policies/x-limits
