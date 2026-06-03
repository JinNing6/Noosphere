import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { readdir, readFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(scriptDir, '..', '..');
const payloadsDir = path.join(repoRoot, 'consciousness_payloads');
const indexPath = path.join(repoRoot, 'frontend', 'public', 'consciousness_index.json');

function stableSoulId(text) {
  return `soul-${createHash('md5').update(text).digest('hex').slice(0, 8)}`;
}

function normalizePayload(fileName, payload) {
  const text = String(payload.thought_vector_text || '').trim();
  if (!text) return null;

  const type = payload.consciousness_type || 'epiphany';
  return {
    sourceFile: fileName,
    id: stableSoulId(text),
    creator: payload.creator_signature || '匿名意识',
    type,
    text,
    context: payload.context_environment || '',
    tags: Array.isArray(payload.tags) ? payload.tags : [],
    uploaded_at: payload.uploaded_at || '',
    anonymous: Boolean(payload.is_anonymous),
    issue_number: Number.isInteger(payload.promoted_from_issue) && payload.promoted_from_issue > 0
      ? payload.promoted_from_issue
      : null,
    parent_id: payload.parent_id ?? null,
    media_type: ['image', 'video', 'voice'].includes(type) ? type : null,
    media_url: type === 'image'
      ? payload.image_url || null
      : type === 'video'
        ? payload.video_url || null
        : type === 'voice'
          ? payload.audio_url || null
          : null,
    media_category: type === 'image'
      ? payload.image_category || 'photo'
      : type === 'video'
        ? payload.video_genre || 'other'
        : type === 'voice'
          ? payload.audio_species || 'human'
          : null,
    embedded: Array.isArray(payload.embedding) && payload.embedding.length > 0,
    embedding_model: payload.embedding_model || null,
    embedding_input_modalities: Array.isArray(payload.embedding_input_modalities)
      ? payload.embedding_input_modalities
      : [],
  };
}

const payloadFiles = (await readdir(payloadsDir))
  .filter(file => file.endsWith('.json'))
  .sort();

const expectedByText = new Map();
for (const file of payloadFiles) {
  const payload = JSON.parse(await readFile(path.join(payloadsDir, file), 'utf8'));
  const normalized = normalizePayload(file, payload);
  if (!normalized || expectedByText.has(normalized.text)) continue;
  expectedByText.set(normalized.text, normalized);
}

const expected = Array.from(expectedByText.values())
  .sort((a, b) => (b.uploaded_at || b.id).localeCompare(a.uploaded_at || a.id));
const index = JSON.parse(await readFile(indexPath, 'utf8'));
const indexById = new Map(index.map(entry => [entry.id, entry]));

assert.equal(index.length, expected.length, 'public consciousness index should include every unique payload memory');
assert.deepEqual(
  index.map(entry => entry.id),
  expected.map(entry => entry.id),
  'public consciousness index should be sorted newest-first using payload timestamps',
);

for (const memory of expected) {
  const indexed = indexById.get(memory.id);
  assert.ok(indexed, `missing indexed memory ${memory.id} from ${memory.sourceFile}`);
  assert.equal(indexed.type, memory.type, `${memory.id} should preserve consciousness type`);
  assert.equal(indexed.text, memory.text, `${memory.id} should preserve thought text`);
  assert.equal(indexed.context, memory.context, `${memory.id} should preserve context`);
  assert.deepEqual(indexed.tags, memory.tags, `${memory.id} should preserve tags`);
  assert.equal(indexed.issue_number, memory.issue_number, `${memory.id} should preserve promoted issue number`);
  assert.equal(indexed.parent_id, memory.parent_id, `${memory.id} should preserve parent id`);
  assert.equal(indexed.media_type, memory.media_type, `${memory.id} should preserve media type`);
  assert.equal(indexed.media_url, memory.media_url, `${memory.id} should preserve media URL`);
  assert.equal(indexed.media_category, memory.media_category, `${memory.id} should preserve media category`);
  assert.equal('embedding' in indexed, false, `${memory.id} should not expose raw embedding vectors in the public index`);
  if (memory.embedded) {
    assert.equal(indexed.embedding_model, memory.embedding_model, `${memory.id} should preserve embedding model metadata`);
    assert.deepEqual(
      indexed.embedding_input_modalities,
      memory.embedding_input_modalities,
      `${memory.id} should preserve embedding input modalities`,
    );
    assert.ok(
      Array.isArray(indexed.resonates_with) && indexed.resonates_with.length > 0,
      `${memory.id} should expose nearest public resonance neighbors`,
    );
    for (const neighbor of indexed.resonates_with) {
      assert.equal(typeof neighbor.id, 'string', `${memory.id} resonance neighbor should include an id`);
      assert.equal(typeof neighbor.score, 'number', `${memory.id} resonance neighbor should include a numeric score`);
      assert.ok(neighbor.score >= 0 && neighbor.score <= 1, `${memory.id} resonance score should be normalized`);
      assert.notEqual(neighbor.id, indexed.id, `${memory.id} should not resonate with itself`);
      assert.ok(indexById.has(neighbor.id), `${memory.id} resonance neighbor ${neighbor.id} should exist in the public index`);
    }
  }
}

const mediaMemories = index.filter(entry => entry.media_type);
assert.ok(mediaMemories.length >= 1, 'public index should expose at least one real media memory');
assert.ok(
  index.some(entry => entry.issue_number === 23),
  'public index should include the latest promoted payload issue #23',
);
assert.ok(
  index.some(entry => Array.isArray(entry.resonates_with) && entry.resonates_with.length > 0),
  'public index should expose at least one embedding-backed resonance edge',
);

console.log(`consciousness index ok: ${index.length} unique memories from ${payloadFiles.length} payload files`);
