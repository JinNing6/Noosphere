const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");

const {
  DEFAULT_EMBEDDING_MODEL,
  applyEmbeddingToPayload,
  buildEmbeddingText,
  buildEmbedContentRequest,
  extractEmbeddingValues,
  generateEmbedding,
  runCheck,
} = require("./gemini-embedding.cjs");

const repoRoot = path.join(__dirname, "..", "..");

const basePayload = {
  creator_signature: "debug-agent",
  is_anonymous: true,
  consciousness_type: "image",
  thought_vector_text: "A white image triggered a discussion about absence and existence.",
  context_environment: "Uploaded through Noosphere media consciousness.",
  tags: ["philosophy", "visual-memory"],
  image_url: "https://example.com/white.png",
  image_format: "png",
  image_size_bytes: 1119,
  category: "art",
};

test("builds Gemini Embedding 2 requests with the stable multimodal public model", () => {
  const request = buildEmbedContentRequest(basePayload);

  assert.equal(DEFAULT_EMBEDDING_MODEL, "gemini-embedding-2");
  assert.equal(
    request.url,
    "https://generativelanguage.googleapis.com/v1beta/models/gemini-embedding-2:embedContent"
  );
  assert.equal(request.body.model, "models/gemini-embedding-2");
  assert.deepEqual(Object.keys(request.body.content), ["parts"]);
  assert.equal(request.body.content.parts.length, 1);
  assert.match(request.body.content.parts[0].text, /white image/);
  assert.doesNotMatch(JSON.stringify(request.body), /inline_data/);
});

test("includes media metadata in the unified text representation", () => {
  const text = buildEmbeddingText(basePayload);

  assert.match(text, /type: image/);
  assert.match(text, /thought: A white image/);
  assert.match(text, /context: Uploaded through Noosphere/);
  assert.match(text, /tags: philosophy, visual-memory/);
  assert.match(text, /image_url: https:\/\/example\.com\/white\.png/);
  assert.match(text, /image_format: png/);
  assert.match(text, /category: art/);
});

test("extracts embedding vectors from Gemini embedContent responses", () => {
  assert.deepEqual(extractEmbeddingValues({ embedding: { values: [0.1, 0.2] } }), [0.1, 0.2]);
  assert.deepEqual(extractEmbeddingValues({ embeddings: [{ values: [0.3, 0.4] }] }), [0.3, 0.4]);
  assert.equal(extractEmbeddingValues({ embedding: { values: [] } }), null);
});

test("generateEmbedding sends the API key in a header and never in the URL", async () => {
  let observed;
  const result = await generateEmbedding(basePayload, {
    apiKey: "test-secret",
    fetchImpl: async (url, options) => {
      observed = { url, options };
      return {
        ok: true,
        status: 200,
        async json() {
          return { embedding: { values: [0.5, 0.6, 0.7] } };
        },
      };
    },
  });

  assert.deepEqual(result.embedding, [0.5, 0.6, 0.7]);
  assert.equal(observed.url.includes("test-secret"), false);
  assert.equal(observed.options.headers["x-goog-api-key"], "test-secret");
  assert.equal(JSON.parse(observed.options.body).model, "models/gemini-embedding-2");
});

test("generateEmbedding includes reachable image media as inline data for multimodal embedding", async () => {
  const calls = [];

  const result = await generateEmbedding(basePayload, {
    apiKey: "test-secret",
    fetchImpl: async (url, options) => {
      calls.push({ url, options });
      if (url === basePayload.image_url) {
        return {
          ok: true,
          status: 200,
          headers: new Map([["content-type", "image/png"], ["content-length", "4"]]),
          async arrayBuffer() {
            return new Uint8Array([0x89, 0x50, 0x4e, 0x47]).buffer;
          },
        };
      }

      const body = JSON.parse(options.body);
      assert.equal(url, "https://generativelanguage.googleapis.com/v1beta/models/gemini-embedding-2:embedContent");
      assert.match(body.content.parts[0].text, /white image/);
      assert.deepEqual(body.content.parts[1], {
        inline_data: {
          mime_type: "image/png",
          data: Buffer.from([0x89, 0x50, 0x4e, 0x47]).toString("base64"),
        },
      });
      assert.equal(options.headers["x-goog-api-key"], "test-secret");

      return {
        ok: true,
        status: 200,
        async json() {
          return { embedding: { values: [0.9, 0.8, 0.7] } };
        },
      };
    },
  });

  assert.equal(result.status, "ok");
  assert.deepEqual(result.embedding, [0.9, 0.8, 0.7]);
  assert.deepEqual(result.inputModalities, ["text", "image"]);
  assert.equal(result.media.status, "included");
  assert.equal(result.media.mimeType, "image/png");
  assert.equal(calls[0].options.headers?.["x-goog-api-key"], undefined);
});

test("generateEmbedding falls back to text embedding when media cannot be fetched", async () => {
  const result = await generateEmbedding(basePayload, {
    apiKey: "test-secret",
    fetchImpl: async (url, options) => {
      if (url === basePayload.image_url) {
        return {
          ok: false,
          status: 404,
          headers: new Map(),
          async text() {
            return "not found";
          },
        };
      }

      const body = JSON.parse(options.body);
      assert.equal(body.content.parts.length, 1);
      assert.doesNotMatch(JSON.stringify(body), /inline_data/);

      return {
        ok: true,
        status: 200,
        async json() {
          return { embedding: { values: [0.4, 0.5, 0.6] } };
        },
      };
    },
  });

  assert.equal(result.status, "ok");
  assert.deepEqual(result.inputModalities, ["text"]);
  assert.equal(result.media.status, "skipped");
  assert.equal(result.media.reason, "media-fetch-failed");
});

test("generateEmbedding passes an abort signal to fetch", async () => {
  let observedSignal;
  const result = await generateEmbedding(basePayload, {
    apiKey: "test-secret",
    timeoutMs: 500,
    fetchImpl: async (_url, options) => {
      observedSignal = options.signal;
      return {
        ok: true,
        status: 200,
        async json() {
          return { embedding: { values: [0.1, 0.2, 0.3] } };
        },
      };
    },
  });

  assert.equal(result.status, "ok");
  assert.equal(observedSignal instanceof AbortSignal, true);
});

test("applyEmbeddingToPayload annotates successful payload embeddings", async () => {
  const payload = { ...basePayload };

  const result = await applyEmbeddingToPayload(payload, {
    apiKey: "test-secret",
    now: () => new Date("2026-05-28T12:00:00.000Z"),
    fetchImpl: async () => ({
      ok: true,
      status: 200,
      async json() {
        return { embedding: { values: [0.8, 0.9] } };
      },
    }),
  });

  assert.equal(result.status, "ok");
  assert.deepEqual(payload.embedding, [0.8, 0.9]);
  assert.equal(payload.embedding_model, "gemini-embedding-2");
  assert.deepEqual(payload.embedding_input_modalities, ["text"]);
  assert.equal(payload.embedding_generated_at, "2026-05-28T12:00:00.000Z");
});

test("keeps payload embedding null when the Gemini key is missing", async () => {
  const payload = { ...basePayload, embedding: [1, 2, 3] };

  const result = await applyEmbeddingToPayload(payload, { apiKey: "" });

  assert.equal(result.status, "missing-key");
  assert.equal(payload.embedding, null);
});

test("promotion workflow uses the shared Gemini embedding helper", () => {
  const workflow = fs.readFileSync(
    path.join(repoRoot, ".github", "workflows", "consciousness_promote.yml"),
    "utf8"
  );

  assert.match(workflow, /gemini-embedding\.cjs/);
  assert.match(workflow, /GEMINI_EMBEDDING_MODEL: gemini-embedding-2/);
  assert.doesNotMatch(workflow, /gemini-embedding-2-preview/);
});

test("manual key check workflow calls the safe Gemini probe command", () => {
  const workflow = fs.readFileSync(
    path.join(repoRoot, ".github", "workflows", "gemini_key_check.yml"),
    "utf8"
  );

  assert.match(workflow, /workflow_dispatch:/);
  assert.match(workflow, /model:/);
  assert.match(workflow, /mode:/);
  assert.match(workflow, /GEMINI_API_KEY: \$\{\{ secrets\.GEMINI_API_KEY \}\}/);
  assert.match(workflow, /GEMINI_EMBEDDING_MODEL: \$\{\{ inputs\.model \|\| 'gemini-embedding-2' \}\}/);
  assert.match(workflow, /node \.github\/scripts\/gemini-embedding\.cjs check/);
});

test("manual key check can isolate the official stable text embedding model", async () => {
  const calls = [];
  const messages = [];

  const exitCode = await runCheck(["--model", "gemini-embedding-001", "--text-only"], {
    env: {
      GEMINI_API_KEY: "test-secret",
      GEMINI_EMBEDDING_MODEL: "gemini-embedding-2",
    },
    log: (message) => messages.push(message),
    error: (message) => messages.push(message),
    fetchImpl: async (url, options) => {
      calls.push({ url, options });
      assert.equal(url, "https://generativelanguage.googleapis.com/v1beta/models/gemini-embedding-001:embedContent");
      const body = JSON.parse(options.body);
      assert.equal(body.model, "models/gemini-embedding-001");
      assert.equal(body.content.parts.length, 1);
      assert.match(body.content.parts[0].text, /Gemini API key validation probe/);

      return {
        ok: true,
        status: 200,
        async json() {
          return { embedding: { values: [0.1, 0.2, 0.3] } };
        },
      };
    },
  });

  assert.equal(exitCode, 0);
  assert.equal(calls.length, 1);
  assert.match(messages.join("\n"), /gemini-embedding-001/);
  assert.match(messages.join("\n"), /modalities text/);
});

test("manual key check validates a real multimodal image payload for Gemini Embedding 2", async () => {
  const calls = [];
  const messages = [];

  const exitCode = await runCheck([], {
    env: {
      GEMINI_API_KEY: "test-secret",
      GEMINI_EMBEDDING_MODEL: "gemini-embedding-2",
    },
    log: (message) => messages.push(message),
    error: (message) => messages.push(message),
    fetchImpl: async (url, options) => {
      calls.push({ url, options });

      if (url.includes("/releases/download/image-consciousness/")) {
        return {
          ok: true,
          status: 200,
          headers: new Map([["content-type", "image/png"], ["content-length", "4"]]),
          async arrayBuffer() {
            return new Uint8Array([0x89, 0x50, 0x4e, 0x47]).buffer;
          },
        };
      }

      const body = JSON.parse(options.body);
      assert.equal(url, "https://generativelanguage.googleapis.com/v1beta/models/gemini-embedding-2:embedContent");
      assert.match(body.content.parts[0].text, /health check image probe/);
      assert.deepEqual(body.content.parts[1], {
        inline_data: {
          mime_type: "image/png",
          data: Buffer.from([0x89, 0x50, 0x4e, 0x47]).toString("base64"),
        },
      });

      return {
        ok: true,
        status: 200,
        async json() {
          return { embedding: { values: [0.1, 0.2, 0.3] } };
        },
      };
    },
  });

  assert.equal(exitCode, 0);
  assert.equal(calls.length, 2);
  assert.equal(calls[0].options.headers?.["x-goog-api-key"], undefined);
  assert.equal(calls[1].options.headers["x-goog-api-key"], "test-secret");
  assert.match(messages.join("\n"), /text\+image/);
});

test("backfill workflow can update historical payload embeddings", () => {
  const workflow = fs.readFileSync(
    path.join(repoRoot, ".github", "workflows", "backfill_embeddings.yml"),
    "utf8"
  );

  assert.match(workflow, /workflow_dispatch:/);
  assert.match(workflow, /contents: write/);
  assert.match(workflow, /GEMINI_EMBEDDING_MODEL: gemini-embedding-2/);
  assert.match(workflow, /args=\(backfill --dir consciousness_payloads\)/);
  assert.match(workflow, /node \.github\/scripts\/gemini-embedding\.cjs "\$\{args\[@\]\}"/);
  assert.match(workflow, /concurrency:/);
});

test("README documents the Gemini Embedding 2 multimodal pipeline", () => {
  const readme = fs.readFileSync(path.join(repoRoot, "README.md"), "utf8");

  assert.match(readme, /gemini-embedding-2/);
  assert.match(readme, /text, image, audio, video, and PDF/i);
  assert.match(readme, /GEMINI_API_KEY/);
});
