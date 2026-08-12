# Codex Sidebar Doctor

Diagnose why **Last updated** does not control the Codex Desktop sidebar without
uploading project names, paths, task IDs, conversation content, or the saved ordering
identifiers themselves.

[中文说明](#中文说明)

## Quick start

Download and inspect
[`Invoke-CodexSidebarDoctor.ps1`](Invoke-CodexSidebarDoctor.ps1), then run it with
PowerShell 7. The default action is read-only:

```powershell
pwsh -NoProfile -File .\Invoke-CodexSidebarDoctor.ps1
```

The doctor reads `%USERPROFILE%\.codex\.codex-global-state.json` locally and reports
only state kinds, counts, settings, and a bounded classification.

| Classification | Meaning | Automatic write |
|---|---|---|
| `legacy-single-layer-match` | Matches the published Windows `project-order` recovery boundary | Available only through the explicit repair flag |
| `second-layer-present` | A newer `unified-sidebar-project-order-v1` layer is populated | Refused; collect evidence |
| `no-persisted-project-order` | The known top-level order is already empty | Refused; investigate task recency or render/cache ordering |
| `not-applicable-sort-mode` | Project + Last updated is not selected | None |
| `unsupported-state-shape` | The state format is outside the published boundary | Refused; collect evidence |

## Submit one redacted report

With [GitHub CLI](https://cli.github.com/) authenticated, one explicit command creates
a public Noosphere Issue. The repository Agent then validates the report, binds the
authenticated author, writes an accepted record under
[`community_evidence/codex-sidebar/`](../../community_evidence/codex-sidebar/), and
closes the Issue automatically:

```powershell
pwsh -NoProfile -File .\Invoke-CodexSidebarDoctor.ps1 `
  -CodexVersion "26.803.41515 (build 6321)" `
  -ObservedScope project-groups `
  -SubmitPublicEvidence
```

`-SubmitPublicEvidence` is an external public write. It cannot be combined with repair
or machine-only JSON output, requires a live state file, a supplied Codex version, and
an explicit observed scope, and is never activated by default. Use `project-groups` for
top-level project order, `tasks-within-project` for order inside an expanded project,
`both` only when both were directly observed, or `unsure` when the visible boundary is
unclear.

Without GitHub CLI, export the exact same identifier-free JSON and paste it into the
[Sidebar Diagnostic form](https://github.com/JinNing6/Noosphere/issues/new?template=codex-sidebar-diagnostic.yml):

```powershell
pwsh -NoProfile -File .\Invoke-CodexSidebarDoctor.ps1 `
  -CodexVersion "26.803.41515 (build 6321)" `
  -ObservedScope project-groups `
  -Json `
  -ExportEvidencePath .\codex-sidebar-evidence.json
```

Automated acceptance means that the generated structure, internal state relationships,
privacy flags, tool version, consent, and authenticated source passed deterministic
checks. It is not an OpenAI response, independent reproduction, or proof that one repair
works for every sidebar-ordering failure. This path uses public GitHub Actions and does
not require a paid API or hosted service.

## Apply the published Windows recovery

Only use this after the read-only result is `legacy-single-layer-match`. Fully exit
Codex first; the doctor refuses a live-state repair while Codex or ChatGPT processes are
running:

```powershell
pwsh -NoProfile -File .\Invoke-CodexSidebarDoctor.ps1 -RepairLegacySingleLayer
```

The repair follows
[`codex-project-recency-sort-recovery@1.0.0`](../../shared_skills/releases/1.0.0/codex-project-recency-sort-recovery/SKILL.md):

1. create a timestamped backup beside the state file;
2. clear only the top-level `project-order` array;
3. preserve project roots, task assignments, preferences, and unrelated state;
4. serialize through a temporary UTF-8 file and parse it again;
5. replace the original only after validation, or restore the backup on failure.

The immutable `1.0.0` release remains Windows-only and single-layer-only. The doctor
does not extend that claim to macOS, task ordering inside a project, or the newer unified
ordering layer.

## 中文说明

Codex Sidebar Doctor 用于判断 Codex Desktop 的“按最近更新排序”为何失效。默认命令只读，
不会导出项目名称、项目路径、任务或会话 ID、对话内容，也不会导出原始排序 ID 数组。

只读检查：

```powershell
pwsh -NoProfile -File .\Invoke-CodexSidebarDoctor.ps1
```

如果已经安装并登录 GitHub CLI，可在查看本地输出后，通过一个显式命令公开提交脱敏证据：

```powershell
pwsh -NoProfile -File .\Invoke-CodexSidebarDoctor.ps1 `
  -CodexVersion "你的 Codex 完整版本号" `
  -ObservedScope project-groups `
  -SubmitPublicEvidence
```

GitHub Agent 会自动校验、绑定提交者身份、写入规范目录并关闭通过的 Issue。结构校验通过只代表
这是一份格式和隐私边界合格的社区诊断，不代表 OpenAI 官方确认、独立复现或普遍有效的修复。

只有结果明确为 `legacy-single-layer-match`、Codex 已完全退出时，才可以显式运行：

```powershell
pwsh -NoProfile -File .\Invoke-CodexSidebarDoctor.ps1 -RepairLegacySingleLayer
```

出现 `second-layer-present` 或其他分类时，工具会拒绝套用旧修复，只允许生成脱敏证据。整个入口
使用公开仓库与 GitHub Actions，不需要付费 API 或常驻服务器。
