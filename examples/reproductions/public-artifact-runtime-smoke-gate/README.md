# Public Artifact Runtime Smoke Gate

This deterministic fixture validates one release boundary: source code can run while the exact packaged artifact is broken.

Run the complete reproduction and receive a prefilled evidence submission link:

```bash
uvx --from noosphere-mcp noosphere-validate public-artifact-runtime-smoke-gate
```

The command requires Python 3.10+ and `uv`. It does not require a validator-owned project, GitHub token, MCP configuration, or package-index account.

## What It Proves

1. A source-tree module executes successfully.
2. A deterministic failing Wheel exposes a console entry point but omits its runtime module.
3. The Wheel is installed into a clean virtual environment with network package resolution disabled.
4. The real installed entry point fails with the expected missing-module error.
5. A deterministic fixed Wheel is force-installed into the same isolated environment.
6. The real entry point succeeds and the installed distribution reports the exact fixed version.

The generated Markdown contains artifact SHA-256 digests, environment details, observed exit codes, the canonical test command, and public sources. Open its prefilled GitHub link, review the evidence, confirm the independent-validation declaration, and submit. No manual JSON transfer is required.

Submission does not publish a Skill directly. Existing repository automation binds authorship to the GitHub Issue author, moderates the structured evidence, compares independent claims, and creates a review-gated Candidate only after the supply-chain requirements are met.

See [`contract.json`](./contract.json) for the machine-readable fixture contract.
