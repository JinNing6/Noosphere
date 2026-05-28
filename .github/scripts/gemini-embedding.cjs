const fs = require("node:fs");
const path = require("node:path");

const DEFAULT_EMBEDDING_MODEL = "gemini-embedding-001";
const GEMINI_API_BASE = "https://generativelanguage.googleapis.com/v1beta";
const MAX_EMBEDDING_TEXT_CHARS = 30000;

const MEDIA_METADATA_FIELDS = [
  "image_url",
  "video_url",
  "audio_url",
  "voice_url",
  "media_url",
  "image_format",
  "video_format",
  "audio_format",
  "voice_format",
  "mime_type",
  "image_size_bytes",
  "video_size_bytes",
  "audio_size_bytes",
  "voice_size_bytes",
  "duration_seconds",
  "category",
  "species",
  "genre",
  "transcript",
  "caption",
  "alt_text",
  "description",
  "media_description",
  "source_url",
];

function normalizeEmbeddingModel(model = DEFAULT_EMBEDDING_MODEL) {
  const raw = String(model || DEFAULT_EMBEDDING_MODEL).trim() || DEFAULT_EMBEDDING_MODEL;
  const id = raw.startsWith("models/") ? raw.slice("models/".length) : raw;
  return {
    id,
    resource: `models/${id}`,
  };
}

function stringifyField(value) {
  if (value === undefined || value === null) return "";
  if (Array.isArray(value)) {
    return value
      .map((item) => stringifyField(item))
      .filter(Boolean)
      .join(", ");
  }
  if (typeof value === "object") {
    return JSON.stringify(value);
  }
  return String(value).trim();
}

function addLine(lines, label, value) {
  const rendered = stringifyField(value);
  if (!rendered) return;
  lines.push(`${label}: ${rendered}`);
}

function buildEmbeddingText(payload, options = {}) {
  const maxChars = options.maxChars || MAX_EMBEDDING_TEXT_CHARS;
  const lines = [];

  addLine(lines, "type", payload?.consciousness_type);
  addLine(lines, "thought", payload?.thought_vector_text);
  addLine(lines, "context", payload?.context_environment);
  addLine(lines, "tags", payload?.tags);

  for (const field of MEDIA_METADATA_FIELDS) {
    addLine(lines, field, payload?.[field]);
  }

  const text = lines.join("\n").trim();
  return text.length > maxChars ? text.slice(0, maxChars) : text;
}

function buildEmbedContentRequest(payload, options = {}) {
  const model = normalizeEmbeddingModel(options.model);
  const apiBase = String(options.apiBase || GEMINI_API_BASE).replace(/\/+$/, "");
  const text = buildEmbeddingText(payload, options);

  return {
    model: model.id,
    url: `${apiBase}/models/${model.id}:embedContent`,
    body: {
      model: model.resource,
      content: {
        parts: [{ text }],
      },
    },
  };
}

function extractEmbeddingValues(data) {
  const candidates = [
    data?.embedding?.values,
    data?.embeddings?.[0]?.values,
    data?.embeddings?.[0]?.embedding?.values,
  ];

  for (const candidate of candidates) {
    if (
      Array.isArray(candidate) &&
      candidate.length > 0 &&
      candidate.every((value) => typeof value === "number" && Number.isFinite(value))
    ) {
      return candidate;
    }
  }

  return null;
}

async function readResponseText(response) {
  try {
    return await response.text();
  } catch {
    return "";
  }
}

async function generateEmbedding(payload, options = {}) {
  const apiKey = String(options.apiKey || "").trim();
  if (!apiKey) {
    return { status: "missing-key", error: "GEMINI_API_KEY is not configured" };
  }

  const fetchImpl = options.fetchImpl || globalThis.fetch;
  if (typeof fetchImpl !== "function") {
    return { status: "missing-fetch", error: "A fetch implementation is required" };
  }

  const request = buildEmbedContentRequest(payload, options);
  const text = request.body.content.parts[0].text;
  if (!text) {
    return { status: "empty-content", error: "Payload has no embeddable text" };
  }

  const response = await fetchImpl(request.url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "x-goog-api-key": apiKey,
    },
    body: JSON.stringify(request.body),
  });

  if (!response.ok) {
    const body = await readResponseText(response);
    return {
      status: "api-error",
      statusCode: response.status,
      model: request.model,
      error: body.slice(0, 500),
    };
  }

  const data = await response.json();
  const embedding = extractEmbeddingValues(data);
  if (!embedding) {
    return {
      status: "unexpected-response",
      model: request.model,
      error: JSON.stringify(data).slice(0, 500),
    };
  }

  return {
    status: "ok",
    model: request.model,
    embedding,
  };
}

async function applyEmbeddingToPayload(payload, options = {}) {
  const result = await generateEmbedding(payload, options);
  if (result.status !== "ok") {
    payload.embedding = null;
    return result;
  }

  const now = options.now || (() => new Date());
  payload.embedding = result.embedding;
  payload.embedding_model = result.model;
  payload.embedding_generated_at = now().toISOString();
  return result;
}

function parseBoolean(value) {
  return ["1", "true", "yes", "on"].includes(String(value || "").toLowerCase());
}

function parseArgs(argv) {
  const args = {};
  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i];
    if (!arg.startsWith("--")) continue;

    const [rawKey, inlineValue] = arg.slice(2).split("=", 2);
    if (inlineValue !== undefined) {
      args[rawKey] = inlineValue;
    } else if (i + 1 < argv.length && !argv[i + 1].startsWith("--")) {
      args[rawKey] = argv[i + 1];
      i += 1;
    } else {
      args[rawKey] = true;
    }
  }
  return args;
}

function shouldBackfillPayload(payload, force) {
  return force || !Array.isArray(payload?.embedding) || payload.embedding.length === 0;
}

function readJsonFile(filePath) {
  return JSON.parse(fs.readFileSync(filePath, "utf8"));
}

function writeJsonFile(filePath, payload) {
  fs.writeFileSync(filePath, `${JSON.stringify(payload, null, 2)}\n`, "utf8");
}

async function backfillEmbeddings(options = {}) {
  const apiKey = String(options.apiKey || "").trim();
  if (!apiKey) {
    throw new Error("GEMINI_API_KEY is required for embedding backfill");
  }

  const dir = path.resolve(options.dir || "consciousness_payloads");
  const limit = Number.parseInt(options.limit || "0", 10);
  const dryRun = Boolean(options.dryRun);
  const force = Boolean(options.force);

  const files = fs
    .readdirSync(dir)
    .filter((name) => name.endsWith(".json"))
    .sort()
    .map((name) => path.join(dir, name));

  const summary = {
    scanned: 0,
    attempted: 0,
    updated: 0,
    skipped: 0,
    dryRun,
    errors: [],
  };

  for (const file of files) {
    summary.scanned += 1;
    const payload = readJsonFile(file);

    if (!shouldBackfillPayload(payload, force)) {
      summary.skipped += 1;
      continue;
    }

    if (limit > 0 && summary.attempted >= limit) {
      break;
    }

    summary.attempted += 1;
    const result = await applyEmbeddingToPayload(payload, {
      apiKey,
      model: options.model,
      fetchImpl: options.fetchImpl,
    });

    if (result.status === "ok") {
      summary.updated += 1;
      if (!dryRun) {
        writeJsonFile(file, payload);
      }
      console.log(
        `${dryRun ? "DRY-RUN" : "UPDATED"} ${path.relative(process.cwd(), file)} (${result.embedding.length} dimensions)`
      );
    } else if (result.status === "empty-content") {
      summary.skipped += 1;
      console.log(`SKIP ${path.relative(process.cwd(), file)} (${result.status})`);
    } else {
      summary.errors.push({
        file: path.relative(process.cwd(), file),
        status: result.status,
        statusCode: result.statusCode,
        error: result.error,
      });
      console.error(`ERROR ${path.relative(process.cwd(), file)} (${result.status})`);
    }
  }

  if (summary.errors.length > 0) {
    const first = summary.errors[0];
    throw new Error(
      `Embedding backfill failed for ${summary.errors.length} file(s); first failure: ${first.file} ${first.status} ${first.statusCode || ""} ${first.error || ""}`.trim()
    );
  }

  return summary;
}

async function runCheck() {
  const result = await generateEmbedding(
    {
      consciousness_type: "epiphany",
      thought_vector_text: "Noosphere Gemini API key validation probe.",
      context_environment: "GitHub Actions secret health check for Gemini embeddings.",
      tags: ["noosphere", "gemini", "embedding-check"],
    },
    {
      apiKey: process.env.GEMINI_API_KEY,
      model: process.env.GEMINI_EMBEDDING_MODEL,
    }
  );

  if (result.status === "ok") {
    console.log(`Gemini embedding key is valid: ${result.model}, ${result.embedding.length} dimensions.`);
    return 0;
  }

  console.error(
    `Gemini embedding key check failed: ${result.status}${result.statusCode ? ` ${result.statusCode}` : ""}`
  );
  if (result.error) {
    console.error(result.error);
  }
  return result.status === "missing-key" ? 2 : 1;
}

async function runBackfill(argv) {
  const args = parseArgs(argv);
  const summary = await backfillEmbeddings({
    apiKey: process.env.GEMINI_API_KEY,
    model: process.env.GEMINI_EMBEDDING_MODEL,
    dir: args.dir || "consciousness_payloads",
    limit: args.limit,
    dryRun: parseBoolean(args["dry-run"]),
    force: parseBoolean(args.force),
  });
  console.log(`Backfill summary: ${JSON.stringify(summary)}`);
  return 0;
}

async function main() {
  const [command, ...argv] = process.argv.slice(2);
  if (command === "check") {
    return runCheck();
  }
  if (command === "backfill") {
    return runBackfill(argv);
  }

  console.error("Usage: node .github/scripts/gemini-embedding.cjs <check|backfill>");
  return 64;
}

if (require.main === module) {
  main()
    .then((code) => {
      process.exitCode = code;
    })
    .catch((error) => {
      console.error(error.message);
      process.exitCode = 1;
    });
}

module.exports = {
  DEFAULT_EMBEDDING_MODEL,
  applyEmbeddingToPayload,
  backfillEmbeddings,
  buildEmbeddingText,
  buildEmbedContentRequest,
  extractEmbeddingValues,
  generateEmbedding,
  normalizeEmbeddingModel,
};
