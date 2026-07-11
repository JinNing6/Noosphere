# 20-Second Agent Debug Memory Demo

This is the source-of-truth shot list for `assets/demo/agent-debug-memory.gif` and
`assets/demo/agent-debug-memory.mp4`.

The story uses the real verified engineering record in [Issue #35](https://github.com/JinNing6/Noosphere/issues/35):
an Android WebView displayed dense glowing React Three Fiber nodes, but taps selected
the wrong `InstancedMesh` instance or opened nothing.

| Time | Proof shown |
|---:|---|
| 0-3.5s | A mobile node-picking regression fails. |
| 3.5-8s | The Agent queries Noosphere's public read-only memory. |
| 8-14s | Noosphere returns verified Seed Memory #35 with the measured root cause and fix. |
| 14-18.5s | The Agent applies the hit-layer and screen-space ranking fix; the ADB regression passes. |
| 18.5-20s | `Stop solving the same bug twice.` |

The corresponding zero-configuration query is:

```bash
uvx --from noosphere-mcp noosphere-query "React Three Fiber mobile glowing node tap selects wrong instance"
```

The demo deliberately calls the result a **verified Seed Memory**, not a published
dynamic Skill. The public dynamic Skill count remains zero until independent-publisher
and maintainer-review gates are satisfied.

Regenerate both assets from the repository root:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/render-launch-demo.ps1
```
