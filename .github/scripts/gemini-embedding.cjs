const fs = require("node:fs");
const path = require("node:path");

const DEFAULT_EMBEDDING_MODEL = "gemini-embedding-2";
const GEMINI_API_BASE = "https://generativelanguage.googleapis.com/v1beta";
const MAX_EMBEDDING_TEXT_CHARS = 30000;
const DEFAULT_REQUEST_TIMEOUT_MS = 15000;
const DEFAULT_MAX_MEDIA_BYTES = 20 * 1024 * 1024;
const DEFAULT_CHECK_IMAGE_URL =
  "https://github.com/JinNing6/Noosphere/releases/download/image-consciousness/image_JinNing6_20260320093215_a34f9fb8.png";
const DEFAULT_CHECK_IMAGE_SIZE_BYTES = 1119;

const MULTIMODAL_EMBEDDING_MODELS = new Set(["gemini-embedding-2"]);

const SUPPORTED_MEDIA_MIME_TYPES = new Map([
  ["image/png", "image"],
  ["image/jpeg", "image"],
  ["audio/mpeg", "audio"],
  ["audio/mp3", "audio"],
  ["audio/wav", "audio"],
  ["audio/x-wav", "audio"],
  ["video/mp4", "video"],
  ["video/quicktime", "video"],
  ["application/pdf", "document"],
]);

const EXTENSION_MIME_TYPES = new Map([
  [".png", "image/png"],
  [".jpg", "image/jpeg"],
  [".jpeg", "image/jpeg"],
  [".mp3", "audio/mpeg"],
  [".wav", "audio/wav"],
  [".mp4", "video/mp4"],
  [".mov", "video/quicktime"],
  [".pdf", "application/pdf"],
]);

const MEDIA_URL_FIELDS_BY_TYPE = {
  image: ["image_url", "media_url", "source_url"],
  video: ["video_url", "media_url", "source_url"],
  voice: ["audio_url", "voice_url", "media_url", "source_url"],
  audio: ["audio_url", "voice_url", "media_url", "source_url"],
  document: ["document_url", "pdf_url", "media_url", "source_url"],
  pdf: ["pdf_url", "document_url", "media_url", "source_url"],
};

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

function supportsInlineMedia(model) {
  return MULTIMODAL_EMBEDDING_MODELS.has(normalizeEmbeddingModel(model).id);
}

function normalizeMimeType(value) {
  const mimeType = String(value || "").split(";")[0].trim().toLowerCase();
  if (mimeType === "image/jpg") return "image/jpeg";
  if (mimeType === "audio/mp3") return "audio/mpeg";
  return mimeType;
}

function inferMimeTypeFromUrl(mediaUrl) {
  try {
    const url = new URL(mediaUrl);
    return EXTENSION_MIME_TYPES.get(path.extname(url.pathname).toLowerCase()) || "";
  } catch {
    return "";
  }
}

function inferMimeTypeFromPayload(payload, mediaUrl) {
  const explicit = normalizeMimeType(payload?.mime_type);
  if (SUPPORTED_MEDIA_MIME_TYPES.has(explicit)) return explicit;

  const type = String(payload?.consciousness_type || "").toLowerCase();
  const formatCandidates = [
    payload?.image_format,
    payload?.video_format,
    payload?.audio_format,
    payload?.voice_format,
    payload?.media_format,
    type,
  ];

  for (const candidate of formatCandidates) {
    const normalized = String(candidate || "").trim().toLowerCase().replace(/^\./, "");
    if (!normalized) continue;
    const mimeType = EXTENSION_MIME_TYPES.get(`.${normalized}`);
    if (mimeType) return mimeType;
  }

  return inferMimeTypeFromUrl(mediaUrl);
}

function getHeader(headers, name) {
  if (!headers) return "";
  if (typeof headers.get === "function") return headers.get(name) || "";
  const lowerName = name.toLowerCase();
  for (const [key, value] of Object.entries(headers)) {
    if (key.toLowerCase() === lowerName) return value;
  }
  return "";
}

function parseContentLength(headers) {
  const raw = getHeader(headers, "content-length");
  const parsed = Number.parseInt(raw, 10);
  return Number.isFinite(parsed) && parsed >= 0 ? parsed : null;
}

function normalizeMediaUrl(value) {
  const mediaUrl = String(value || "").trim();
  if (!mediaUrl) return null;

  try {
    const url = new URL(mediaUrl);
    if (!["https:", "http:"].includes(url.protocol)) return null;
    return url.toString();
  } catch {
    return null;
  }
}

function getMediaUrlFields(payload) {
  const type = String(payload?.consciousness_type || "").toLowerCase();
  const fields = MEDIA_URL_FIELDS_BY_TYPE[type] || [];
  return [...fields, "image_url", "video_url", "audio_url", "voice_url", "media_url", "source_url"];
}

function selectMediaSource(payload) {
  const seen = new Set();
  for (const field of getMediaUrlFields(payload)) {
    if (seen.has(field)) continue;
    seen.add(field);

    const mediaUrl = normalizeMediaUrl(payload?.[field]);
    if (!mediaUrl) continue;

    const mimeType = inferMimeTypeFromPayload(payload, mediaUrl);
    const modality = SUPPORTED_MEDIA_MIME_TYPES.get(mimeType);
    if (!modality) {
      return {
        status: "skipped",
        reason: "unsupported-media-type",
        field,
        url: mediaUrl,
        mimeType: mimeType || "",
      };
    }

    return {
      status: "selected",
      field,
      url: mediaUrl,
      mimeType,
      modality,
    };
  }

  return null;
}

async function fetchInlineMediaPart(source, options = {}) {
  if (!source) return null;
  if (source.status !== "selected") return source;

  const fetchImpl = options.fetchImpl || globalThis.fetch;
  if (typeof fetchImpl !== "function") {
    return { ...source, status: "skipped", reason: "missing-fetch" };
  }

  const maxBytes = Number.parseInt(options.maxMediaBytes || DEFAULT_MAX_MEDIA_BYTES, 10);
  const timeoutMs = Number.parseInt(options.timeoutMs || DEFAULT_REQUEST_TIMEOUT_MS, 10);
  const timeout = createTimeoutSignal(timeoutMs);
  let response;

  try {
    response = await fetchImpl(source.url, {
      method: "GET",
      headers: {
        Accept: Array.from(SUPPORTED_MEDIA_MIME_TYPES.keys()).join(", "),
      },
      signal: timeout.signal,
    });
  } catch (error) {
    if (isTimeoutLikeError(error)) {
      return { ...source, status: "skipped", reason: "media-fetch-timeout" };
    }
    return {
      ...source,
      status: "skipped",
      reason: "media-fetch-network-error",
      error: error?.message || String(error),
    };
  } finally {
    timeout.cancel();
  }

  if (!response.ok) {
    return {
      ...source,
      status: "skipped",
      reason: "media-fetch-failed",
      statusCode: response.status,
    };
  }

  const responseMimeType = normalizeMimeType(getHeader(response.headers, "content-type"));
  const mimeType = SUPPORTED_MEDIA_MIME_TYPES.has(responseMimeType) ? responseMimeType : source.mimeType;
  const modality = SUPPORTED_MEDIA_MIME_TYPES.get(mimeType);
  if (!modality) {
    return {
      ...source,
      status: "skipped",
      reason: "unsupported-media-type",
      mimeType: responseMimeType || source.mimeType || "",
    };
  }

  const contentLength = parseContentLength(response.headers);
  if (contentLength !== null && contentLength > maxBytes) {
    return {
      ...source,
      status: "skipped",
      reason: "media-too-large",
      mimeType,
      bytes: contentLength,
    };
  }

  if (typeof response.arrayBuffer !== "function") {
    return { ...source, status: "skipped", reason: "media-body-unavailable", mimeType };
  }

  const bytes = Buffer.from(await response.arrayBuffer());
  if (bytes.length > maxBytes) {
    return {
      ...source,
      status: "skipped",
      reason: "media-too-large",
      mimeType,
      bytes: bytes.length,
    };
  }

  return {
    ...source,
    status: "included",
    mimeType,
    modality,
    bytes: bytes.length,
    part: {
      inline_data: {
        mime_type: mimeType,
        data: bytes.toString("base64"),
      },
    },
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
  const media = options.media?.status === "included" ? options.media : null;
  const parts = [];
  const inputModalities = [];

  if (text) {
    parts.push({ text });
    inputModalities.push("text");
  }
  if (media?.part) {
    parts.push(media.part);
    inputModalities.push(media.modality);
  }

  return {
    model: model.id,
    url: `${apiBase}/models/${model.id}:embedContent`,
    inputModalities,
    body: {
      model: model.resource,
      content: {
        parts,
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

function createTimeoutSignal(timeoutMs) {
  if (!timeoutMs || timeoutMs <= 0 || typeof AbortSignal === "undefined") {
    return { signal: undefined, cancel: () => {} };
  }

  if (typeof AbortSignal.timeout === "function") {
    return { signal: AbortSignal.timeout(timeoutMs), cancel: () => {} };
  }

  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeoutMs);
  return {
    signal: controller.signal,
    cancel: () => clearTimeout(timeoutId),
  };
}

function isTimeoutLikeError(error) {
  return ["AbortError", "TimeoutError"].includes(error?.name);
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

  const model = normalizeEmbeddingModel(options.model);
  const mediaSource = supportsInlineMedia(model.id) ? selectMediaSource(payload) : null;
  const media = await fetchInlineMediaPart(mediaSource, {
    fetchImpl,
    maxMediaBytes: options.maxMediaBytes,
    timeoutMs: options.timeoutMs,
  });
  const request = buildEmbedContentRequest(payload, { ...options, model: model.id, media });
  if (request.body.content.parts.length === 0) {
    return { status: "empty-content", error: "Payload has no embeddable text" };
  }

  const timeoutMs = Number.parseInt(options.timeoutMs || DEFAULT_REQUEST_TIMEOUT_MS, 10);
  const timeout = createTimeoutSignal(timeoutMs);
  let response;
  try {
    response = await fetchImpl(request.url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "x-goog-api-key": apiKey,
      },
      body: JSON.stringify(request.body),
      signal: timeout.signal,
    });
  } catch (error) {
    if (isTimeoutLikeError(error)) {
      return {
        status: "timeout",
        model: request.model,
        error: `Gemini embedding request timed out after ${timeoutMs} ms`,
      };
    }
    return {
      status: "network-error",
      model: request.model,
      error: error?.message || String(error),
    };
  } finally {
    timeout.cancel();
  }

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
    inputModalities: request.inputModalities,
    media,
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
  payload.embedding_input_modalities = result.inputModalities;
  if (result.media?.status === "included") {
    payload.embedding_media_mime_type = result.media.mimeType;
    payload.embedding_media_bytes = result.media.bytes;
  }
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

function buildCheckPayload(modelId, args = {}) {
  const basePayload = {
    creator_signature: "noosphere-ci",
    is_anonymous: true,
    context_environment: "GitHub Actions secret health check for Gemini embeddings.",
    tags: ["noosphere", "gemini", "embedding-check"],
  };

  const textOnly = Boolean(args.textOnly) || parseBoolean(args["text-only"]);

  if (!textOnly && supportsInlineMedia(modelId)) {
    return {
      ...basePayload,
      consciousness_type: "image",
      thought_vector_text: "Noosphere Gemini Embedding 2 health check image probe.",
      image_url: args["media-url"] || DEFAULT_CHECK_IMAGE_URL,
      image_format: "png",
      image_size_bytes: DEFAULT_CHECK_IMAGE_SIZE_BYTES,
      mime_type: args["media-mime-type"] || "image/png",
      category: "health-check",
    };
  }

  return {
    ...basePayload,
    consciousness_type: "epiphany",
    thought_vector_text: "Noosphere Gemini API key validation probe.",
  };
}

function formatModalities(modalities = []) {
  return modalities.length > 0 ? modalities.join("+") : "unknown";
}

function getCheckMode(args = {}, env = {}) {
  if (Boolean(args.textOnly) || parseBoolean(args["text-only"])) return "text-only";
  const rawMode = String(env.GEMINI_CHECK_MODE || "").trim().toLowerCase();
  if (rawMode === "text-only" || rawMode === "text") return "text-only";
  if (parseBoolean(env.GEMINI_CHECK_TEXT_ONLY)) return "text-only";
  return "multimodal";
}

async function runCheck(argv = [], options = {}) {
  const args = parseArgs(argv);
  const env = options.env || process.env;
  const log = options.log || console.log;
  const error = options.error || console.error;
  const model = normalizeEmbeddingModel(args.model || env.GEMINI_EMBEDDING_MODEL);
  const mode = getCheckMode(args, env);
  const result = await generateEmbedding(buildCheckPayload(model.id, { ...args, textOnly: mode === "text-only" }), {
    apiKey: env.GEMINI_API_KEY,
    model: model.id,
    fetchImpl: options.fetchImpl,
    maxMediaBytes: options.maxMediaBytes,
    timeoutMs: options.timeoutMs || args.timeout,
  });

  if (result.status === "ok") {
    if (mode !== "text-only" && supportsInlineMedia(result.model) && !result.inputModalities?.includes("image")) {
      error("Gemini embedding key check failed: image media was not included in the multimodal request.");
      if (result.media?.reason) {
        error(`Media status: ${result.media.status} ${result.media.reason}`);
      }
      return 1;
    }

    const mediaSummary =
      result.media?.status === "included" ? `, media ${result.media.mimeType} ${result.media.bytes} bytes` : "";
    log(
      `Gemini embedding key is valid: ${result.model}, ${result.embedding.length} dimensions, modalities ${formatModalities(result.inputModalities)}${mediaSummary}.`
    );
    return 0;
  }

  error(
    `Gemini embedding key check failed: ${result.status}${result.statusCode ? ` ${result.statusCode}` : ""}`
  );
  if (result.error) {
    error(result.error);
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
    return runCheck(argv);
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
  DEFAULT_CHECK_IMAGE_URL,
  DEFAULT_MAX_MEDIA_BYTES,
  DEFAULT_REQUEST_TIMEOUT_MS,
  applyEmbeddingToPayload,
  backfillEmbeddings,
  buildCheckPayload,
  buildEmbeddingText,
  buildEmbedContentRequest,
  extractEmbeddingValues,
  fetchInlineMediaPart,
  generateEmbedding,
  normalizeEmbeddingModel,
  runCheck,
  selectMediaSource,
  supportsInlineMedia,
};
