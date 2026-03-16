"""
🛡️ Noosphere MCP Pre-flight Diagnostics (启动前自检)

在 MCP Server 启动之前，逐层检查：
  Layer 1: 核心依赖是否已安装 (httpx, mcp)
  Layer 2: 环境变量是否配置正确 (GITHUB_TOKEN, NOOSPHERE_REPO)
  Layer 3: GitHub API 是否可达、Token 是否有效

所有输出写入 stderr（MCP 使用 stdout/stdin 做 stdio 通信）。
失败时给出清晰的原因和修复建议，而不是静默崩溃。

面向所有 Noosphere 用户通用。
"""

from __future__ import annotations

import importlib
import os
import sys
from dataclasses import dataclass, field


# ── ANSI Colors (fallback-safe) ──

class _C:
    """ANSI color codes for stderr terminal output."""
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RED = "\033[38;5;196m"
    GREEN = "\033[38;5;46m"
    YELLOW = "\033[38;5;220m"
    CYAN = "\033[38;5;51m"
    WHITE = "\033[38;5;255m"
    GRAY = "\033[38;5;240m"
    MAGENTA = "\033[38;5;198m"


# ── Data Structures ──

@dataclass
class CheckItem:
    """Single diagnostic check result."""
    name: str
    name_en: str
    passed: bool
    message: str
    suggestion: str = ""


@dataclass
class PreflightResult:
    """Aggregated pre-flight diagnostic result."""
    checks: list[CheckItem] = field(default_factory=list)

    @property
    def errors(self) -> list[CheckItem]:
        return [c for c in self.checks if not c.passed and c.suggestion]

    @property
    def warnings(self) -> list[CheckItem]:
        return [c for c in self.checks if not c.passed and not c.suggestion]

    @property
    def passed(self) -> bool:
        """True if no fatal errors (warnings are OK)."""
        return len(self.errors) == 0

    @property
    def all_clear(self) -> bool:
        """True if absolutely everything passed."""
        return all(c.passed for c in self.checks)


# ── Layer 1: Dependency Checks ──

_REQUIRED_DEPS = [
    ("httpx", "pip install httpx", "HTTP client for GitHub API calls"),
    ("mcp", "pip install 'mcp>=1.3.0'", "Model Context Protocol library"),
]


def check_dependencies() -> list[CheckItem]:
    """Check that all required Python packages are importable."""
    results: list[CheckItem] = []

    for module_name, install_cmd, description in _REQUIRED_DEPS:
        try:
            importlib.import_module(module_name)
            results.append(CheckItem(
                name=f"依赖: {module_name}",
                name_en=f"Dependency: {module_name}",
                passed=True,
                message=f"{module_name} ✓",
            ))
        except ImportError:
            results.append(CheckItem(
                name=f"依赖: {module_name}",
                name_en=f"Dependency: {module_name}",
                passed=False,
                message=f"缺失 {module_name} ({description})",
                suggestion=f"运行: {install_cmd}",
            ))

    return results


# ── Layer 2: Environment Variable Checks ──


def check_env_vars() -> list[CheckItem]:
    """Check that required environment variables are set and valid."""
    results: list[CheckItem] = []

    # GITHUB_TOKEN
    token = os.environ.get("GITHUB_TOKEN", "").strip()
    if token:
        # Basic format validation (GitHub tokens start with ghp_, gho_, ghs_, ghu_, github_pat_)
        valid_prefixes = ("ghp_", "gho_", "ghs_", "ghu_", "github_pat_")
        if any(token.startswith(p) for p in valid_prefixes):
            results.append(CheckItem(
                name="环境变量: GITHUB_TOKEN",
                name_en="Env: GITHUB_TOKEN",
                passed=True,
                message=f"已配置 ({token[:4]}...{token[-4:]})",
            ))
        else:
            results.append(CheckItem(
                name="环境变量: GITHUB_TOKEN",
                name_en="Env: GITHUB_TOKEN",
                passed=False,
                message=f"Token 格式异常 (不以 ghp_/gho_/ghs_/ghu_/github_pat_ 开头)",
                suggestion="请检查 Token 是否正确，获取方式: https://github.com/settings/tokens",
            ))
    else:
        results.append(CheckItem(
            name="环境变量: GITHUB_TOKEN",
            name_en="Env: GITHUB_TOKEN",
            passed=False,
            message="未配置 GITHUB_TOKEN",
            suggestion=(
                "在 MCP 配置中设置 env.GITHUB_TOKEN\n"
                "   获取方式: https://github.com/settings/tokens → 勾选 public_repo"
            ),
        ))

    # NOOSPHERE_REPO
    repo = os.environ.get("NOOSPHERE_REPO", "").strip()
    if repo:
        parts = repo.split("/")
        if len(parts) == 2 and all(p.strip() for p in parts):
            results.append(CheckItem(
                name="环境变量: NOOSPHERE_REPO",
                name_en="Env: NOOSPHERE_REPO",
                passed=True,
                message=f"已配置 ({repo})",
            ))
        else:
            results.append(CheckItem(
                name="环境变量: NOOSPHERE_REPO",
                name_en="Env: NOOSPHERE_REPO",
                passed=False,
                message=f"格式错误: '{repo}'",
                suggestion="应为 'owner/repo' 格式，例如: JinNing6/Noosphere",
            ))
    else:
        # Not fatal — has default fallback
        results.append(CheckItem(
            name="环境变量: NOOSPHERE_REPO",
            name_en="Env: NOOSPHERE_REPO",
            passed=True,
            message="使用默认值 (JinNing6/Noosphere)",
        ))

    return results


# ── Layer 3: Network Connectivity ──


def check_github_connectivity() -> list[CheckItem]:
    """Check GitHub API reachability and token validity.

    Uses a lightweight GET /user call to validate both connectivity and token.
    This check is NON-BLOCKING on failure — MCP can still start in degraded mode.
    """
    results: list[CheckItem] = []
    token = os.environ.get("GITHUB_TOKEN", "").strip()

    if not token:
        # Can't test connectivity without a token; skip
        results.append(CheckItem(
            name="网络: GitHub API",
            name_en="Network: GitHub API",
            passed=False,
            message="跳过连通性检查 (无 Token)",
        ))
        return results

    try:
        # Use synchronous httpx to avoid async complexity at startup
        import httpx

        resp = httpx.get(
            "https://api.github.com/user",
            headers={
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {token}",
                "X-GitHub-Api-Version": "2022-11-28",
            },
            timeout=10,
            follow_redirects=True,
        )

        if resp.status_code == 200:
            user_data = resp.json()
            username = user_data.get("login", "unknown")
            results.append(CheckItem(
                name="网络: GitHub API",
                name_en="Network: GitHub API",
                passed=True,
                message=f"已连接 (认证用户: @{username})",
            ))
        elif resp.status_code == 401:
            results.append(CheckItem(
                name="网络: GitHub API",
                name_en="Network: GitHub API",
                passed=False,
                message="Token 认证失败 (401 Unauthorized)",
                suggestion="Token 可能已过期或被吊销，请重新生成: https://github.com/settings/tokens",
            ))
        elif resp.status_code == 403:
            results.append(CheckItem(
                name="网络: GitHub API",
                name_en="Network: GitHub API",
                passed=False,
                message=f"访问被拒绝 (403 Forbidden)",
                suggestion="可能触发了 GitHub API 限流，请稍后重试",
            ))
        else:
            results.append(CheckItem(
                name="网络: GitHub API",
                name_en="Network: GitHub API",
                passed=False,
                message=f"意外响应: HTTP {resp.status_code}",
            ))

    except ImportError:
        # httpx not available — already caught by dependency check
        results.append(CheckItem(
            name="网络: GitHub API",
            name_en="Network: GitHub API",
            passed=False,
            message="跳过 (httpx 未安装)",
        ))
    except Exception as e:
        error_type = type(e).__name__
        # Classify common network errors
        error_msg = str(e)
        if "timeout" in error_msg.lower() or "timed out" in error_msg.lower():
            suggestion = "网络超时，请检查代理设置或网络连接"
        elif "ssl" in error_msg.lower() or "certificate" in error_msg.lower():
            suggestion = "SSL 证书错误，请检查系统时间和代理设置"
        elif "connect" in error_msg.lower() or "refused" in error_msg.lower():
            suggestion = "无法连接 GitHub，请检查网络/防火墙/代理 (HTTP_PROXY/HTTPS_PROXY)"
        elif "dns" in error_msg.lower() or "resolve" in error_msg.lower():
            suggestion = "DNS 解析失败，请检查网络连接"
        else:
            suggestion = f"请检查网络连接: {error_msg[:100]}"

        results.append(CheckItem(
            name="网络: GitHub API",
            name_en="Network: GitHub API",
            passed=False,
            message=f"连接失败 ({error_type})",
            suggestion=suggestion,
        ))

    return results


# ── Aggregated Pre-flight ──


def run_preflight(*, skip_network: bool = False) -> PreflightResult:
    """Run all pre-flight checks and return aggregated result.

    Args:
        skip_network: If True, skip Layer 3 network checks (useful for offline/test).
    """
    result = PreflightResult()
    result.checks.extend(check_dependencies())
    result.checks.extend(check_env_vars())
    if not skip_network:
        result.checks.extend(check_github_connectivity())
    return result


# ── Formatted Output ──


def format_diagnostics(result: PreflightResult) -> str:
    """Generate a human-readable diagnostic panel for stderr output.

    Returns a multi-line string with ANSI colors for terminal display.
    """
    C = _C
    lines: list[str] = []

    # Header
    if result.all_clear:
        status_icon = f"{C.GREEN}✓{C.RESET}"
        status_text = f"{C.GREEN}全部通过{C.RESET}"
    elif result.passed:
        status_icon = f"{C.YELLOW}⚠{C.RESET}"
        status_text = f"{C.YELLOW}部分警告 (可降级运行){C.RESET}"
    else:
        status_icon = f"{C.RED}✗{C.RESET}"
        status_text = f"{C.RED}启动失败{C.RESET}"

    lines.append(f"")
    lines.append(f"  {C.CYAN}╭{'─' * 60}╮{C.RESET}")
    lines.append(f"  {C.CYAN}│{C.RESET}  {C.BOLD}🛡️  Noosphere Pre-flight Diagnostics (启动前自检){C.RESET}    {C.CYAN}│{C.RESET}")
    lines.append(f"  {C.CYAN}├{'─' * 60}┤{C.RESET}")

    # Status line
    lines.append(f"  {C.CYAN}│{C.RESET}  状态: {status_icon} {status_text:<50}{C.CYAN}│{C.RESET}")
    lines.append(f"  {C.CYAN}├{'─' * 60}┤{C.RESET}")

    # Individual checks
    for check in result.checks:
        if check.passed:
            icon = f"{C.GREEN}✓{C.RESET}"
            msg = f"{C.WHITE}{check.message}{C.RESET}"
        elif check.suggestion:
            icon = f"{C.RED}✗{C.RESET}"
            msg = f"{C.RED}{check.message}{C.RESET}"
        else:
            icon = f"{C.YELLOW}⚠{C.RESET}"
            msg = f"{C.YELLOW}{check.message}{C.RESET}"

        # Truncate for panel width
        lines.append(f"  {C.CYAN}│{C.RESET}   {icon} {check.name_en:<24} {msg:<33}{C.CYAN}│{C.RESET}")

        if check.suggestion:
            # Multi-line suggestions
            for sug_line in check.suggestion.split("\n"):
                lines.append(f"  {C.CYAN}│{C.RESET}     {C.DIM}→ {sug_line}{C.RESET}")

    lines.append(f"  {C.CYAN}╰{'─' * 60}╯{C.RESET}")

    # Fatal error footer
    if not result.passed:
        lines.append(f"")
        lines.append(f"  {C.RED}{C.BOLD}⚡ MCP Server 无法启动 — 请修复上述错误后重试{C.RESET}")
        lines.append(f"  {C.RED}{C.BOLD}⚡ MCP Server cannot start — fix the errors above and retry{C.RESET}")
        lines.append(f"  {C.DIM}  文档: https://github.com/JinNing6/Noosphere#installation{C.RESET}")
        lines.append(f"")

    return "\n".join(lines)


def print_diagnostics(result: PreflightResult) -> None:
    """Print formatted diagnostics to stderr."""
    sys.stderr.write(format_diagnostics(result) + "\n")
    sys.stderr.flush()
