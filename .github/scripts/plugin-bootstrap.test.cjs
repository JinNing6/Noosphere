const assert = require('node:assert/strict')
const fs = require('node:fs')
const path = require('node:path')
const test = require('node:test')
const { spawnSync } = require('node:child_process')

const ROOT = path.resolve(__dirname, '..', '..')
const CODEX_SKILL = path.join(
  ROOT,
  'plugins',
  'noosphere',
  'skills',
  'using-noosphere',
  'SKILL.md',
)
const CLAUDE_SKILL = path.join(
  ROOT,
  'plugins',
  'claude-noosphere',
  'skills',
  'using-noosphere',
  'SKILL.md',
)
const HOOK_CONFIG = path.join(
  ROOT,
  'plugins',
  'claude-noosphere',
  'hooks',
  'hooks.json',
)
const HOOK_SCRIPT = path.join(
  ROOT,
  'plugins',
  'claude-noosphere',
  'scripts',
  'noosphere-session-start.cjs',
)
const CI_WORKFLOW = path.join(ROOT, '.github', 'workflows', 'ci.yml')

test('Codex and Claude Code share one control-plane Skill contract', () => {
  const codex = fs.readFileSync(CODEX_SKILL, 'utf8')
  const claude = fs.readFileSync(CLAUDE_SKILL, 'utf8')

  assert.equal(claude, codex)
  assert.match(codex, /list_shared_skills/)
  assert.match(codex, /get_shared_skill/)
  assert.match(codex, /explicit user consent/i)
  assert.match(codex, /do not use/i)
})

test('Claude Code activates the control Skill at every stable session boundary', () => {
  const config = JSON.parse(fs.readFileSync(HOOK_CONFIG, 'utf8'))
  const sessionStart = config.hooks.SessionStart

  assert.equal(sessionStart.length, 1)
  assert.equal(sessionStart[0].matcher, 'startup|resume|clear|compact')
  assert.equal(sessionStart[0].hooks[0].type, 'command')
  assert.equal(sessionStart[0].hooks[0].command, 'node')
  assert.deepEqual(sessionStart[0].hooks[0].args, [
    '${CLAUDE_PLUGIN_ROOT}/scripts/noosphere-session-start.cjs',
  ])
})

test('SessionStart emits valid bounded context without network access', () => {
  const result = spawnSync(process.execPath, [HOOK_SCRIPT], {
    encoding: 'utf8',
    input: JSON.stringify({ hook_event_name: 'SessionStart', source: 'startup' }),
    timeout: 2000,
  })

  assert.equal(result.status, 0, result.stderr)
  const output = JSON.parse(result.stdout)
  const context = output.hookSpecificOutput.additionalContext
  assert.equal(output.hookSpecificOutput.hookEventName, 'SessionStart')
  assert.match(context, /noosphere:using-noosphere/)
  assert.match(context, /software engineering failure/i)
  assert.match(context, /read-only discovery/i)
  assert.match(context, /explicit user consent/i)
  assert.ok(context.length <= 700)
})

test('every plugin artifact change enters the shared Skill supply-chain gate', () => {
  const workflow = fs.readFileSync(CI_WORKFLOW, 'utf8')

  assert.match(workflow, /plugins\/\(noosphere\|claude-noosphere\)\/\|/)
})
