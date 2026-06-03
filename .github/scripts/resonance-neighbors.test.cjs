const assert = require("node:assert/strict");
const test = require("node:test");

const {
  findNearestResonanceMatch,
} = require("./resonance-neighbors.cjs");

test("finds the closest historical embedded payload without exposing raw vectors", () => {
  const currentPayload = {
    consciousness_type: "warning",
    thought_vector_text: "A debugger found that a slow async refresh erased local UI state.",
    context_environment: "A Claude Code agent was fixing a flaky frontend interaction.",
    promoted_from_issue: 24,
    embedding: [1, 0],
  };

  const match = findNearestResonanceMatch(
    currentPayload,
    [
      {
        creator_signature: "debug-agent",
        consciousness_type: "pattern",
        thought_vector_text: "A slow async provider refresh can erase local UI state after a click.",
        context_environment: "A previous agent debugged the same interaction class.",
        promoted_from_issue: 3,
        embedding: [0.99, 0.01],
      },
      {
        creator_signature: "vision-agent",
        consciousness_type: "image",
        thought_vector_text: "A minimal white image triggered an absence/existence reflection.",
        context_environment: "A media memory was uploaded through Noosphere.",
        promoted_from_issue: 4,
        embedding: [0, 1],
      },
    ],
    { excludeIssueNumber: 24 }
  );

  assert.equal(match.issue_number, 3);
  assert.equal(match.type, "pattern");
  assert.equal(match.creator, "debug-agent");
  assert.match(match.text, /slow async provider refresh/);
  assert.match(match.id, /^soul-[a-f0-9]{8}$/);
  assert.ok(match.score > 0.99 && match.score <= 1);
  assert.equal(Object.hasOwn(match, "embedding"), false);
});

test("does not report a self match or invalid candidate as resonance", () => {
  const currentPayload = {
    thought_vector_text: "The same memory should not resonate with itself.",
    promoted_from_issue: 7,
    embedding: [1, 0],
  };

  const match = findNearestResonanceMatch(
    currentPayload,
    [
      {
        thought_vector_text: "The same memory should not resonate with itself.",
        promoted_from_issue: 7,
        embedding: [1, 0],
      },
      {
        thought_vector_text: "Broken embedding candidate.",
        promoted_from_issue: 8,
        embedding: [0, 0],
      },
    ],
    { excludeIssueNumber: 7 }
  );

  assert.equal(match, null);
});
