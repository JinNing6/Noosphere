#!/usr/bin/env node

'use strict'

const additionalContext = [
  'Noosphere Live Skills are active.',
  'Before diagnosing or fixing a concrete software engineering failure, invoke noosphere:using-noosphere to discover and digest-verify any applicable live Skill.',
  'Do not invoke it for unrelated feature work, general questions, or speculative discussion.',
  'Read-only discovery is anonymous.',
  'Never create public memory, evidence, or outcome records without explicit user consent at the time of the write.',
  'Submit verified engineering fixes with submit_skill_evidence; never route them through upload_consciousness.',
].join(' ')

function buildSessionContext() {
  return {
    hookSpecificOutput: {
      hookEventName: 'SessionStart',
      additionalContext,
    },
  }
}

if (require.main === module) {
  process.stdin.resume()
  process.stdin.on('end', () => {
    process.stdout.write(`${JSON.stringify(buildSessionContext())}\n`)
  })
}

module.exports = { buildSessionContext }
