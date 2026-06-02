import { useCallback, useDeferredValue, useEffect, useMemo, useRef, useState, useTransition } from 'react';
import type { CSSProperties } from 'react';
import { SEED_EXPERIENCES, STATS } from '../data/experiences';
import type { KnowledgeNode } from '../data/knowledge';
import type { Experience } from '../types';
import { CLIPBOARD_ACTIONS, createMemorySharePost, readMemoryIdFromSearch } from '../utils/growthCopy';

interface AhaMomentDockProps {
  dynamicNodes: KnowledgeNode[];
  isUploaderOpen: boolean;
  onSearch: (query: string) => void;
  onOpenUploader: () => void;
}

interface DebugMemoryCopy {
  title: string;
  problem: string;
  rootCause?: string;
  fix: string;
  outcome?: string;
}

const DEFAULT_QUERY = 'langchain rag chinese text splitting';

const SAMPLE_QUERIES = [
  'langchain rag chinese text splitting',
  'crewai multi agent deadlock dependency',
  'openai rate limit exponential backoff',
] as const;

const TYPE_COLORS: Record<Experience['type'], string> = {
  failure: '#ff6b35',
  success: '#00e878',
  pattern: '#4488ff',
  warning: '#ff4d6a',
  migration: '#ffd700',
};

const DEBUG_MEMORY_COPY: Record<string, DebugMemoryCopy> = {
  'nsp-langchain-001': {
    title: 'LangChain Chinese RAG precision collapse',
    problem: 'RecursiveCharacterTextSplitter split Chinese sentences mid-thought, dropping retrieval precision by about 40%.',
    rootCause: 'Default separators missed Chinese punctuation, so chunks broke semantic boundaries.',
    fix: 'Add Chinese punctuation to separators before chunking: ideographic full stop, comma, semicolon, question mark, exclamation, and line breaks.',
    outcome: 'retrieval_precision: 0.52 -> 0.89',
  },
  'nsp-crewai-001': {
    title: 'CrewAI multi-agent deadlock',
    problem: 'A task graph with three or more agents entered a circular dependency and never completed.',
    rootCause: 'Agent task dependencies formed a cycle.',
    fix: 'Run DAG cycle checks, enforce timeouts, and introduce a coordinator agent before execution.',
    outcome: 'task_completion_rate: 0% -> 95%',
  },
  'nsp-openai-002': {
    title: 'OpenAI API rate-limit retry storm',
    problem: 'Fixed-interval retries caused requests to bunch up and fail repeatedly under rate limits.',
    rootCause: 'Synchronized retry timing created a thundering-herd effect.',
    fix: 'Use exponential backoff plus jitter: wait_exponential with bounded random delay.',
    outcome: 'api_success_rate: 0.72 -> 0.99',
  },
  'nsp-langchain-003': {
    title: 'LangChain verbose logs leaked API keys',
    problem: 'Debug logging could expose sensitive credentials in plaintext.',
    rootCause: 'Verbose mode did not redact sensitive values by default.',
    fix: 'Disable verbose logging in production or filter secrets in a custom callback handler.',
  },
  'nsp-autogen-001': {
    title: 'AutoGen group-chat speaker drift',
    problem: 'Multiple agents repeated replies or missed critical messages in group chat.',
    rootCause: "speaker_selection_method='auto' was unstable in complex conversations.",
    fix: 'Use round_robin or a custom speaker_selection_func for explicit turn control.',
    outcome: 'conversation_coherence: 0.55 -> 0.88',
  },
};

function normalizeText(value: string | undefined): string {
  return (value || '').toLowerCase();
}

function getMemoryCopy(memory: Experience): DebugMemoryCopy {
  return DEBUG_MEMORY_COPY[memory.id] || {
    title: `${memory.framework} ${memory.task_type || memory.type}`,
    problem: memory.observation,
    rootCause: memory.root_cause,
    fix: memory.solution || 'Open the memory to inspect the validated resolution.',
    outcome: memory.evidence_after,
  };
}

function memoryCorpus(memory: Experience): string {
  const copy = getMemoryCopy(memory);
  return [
    memory.framework,
    memory.version,
    memory.task_type,
    memory.type,
    memory.context,
    memory.observation,
    memory.root_cause,
    memory.solution,
    copy.title,
    copy.problem,
    copy.rootCause,
    copy.fix,
    copy.outcome,
    ...memory.tags,
  ].map(normalizeText).join(' ');
}

function scoreMemory(memory: Experience, query: string): number {
  const tokens = query
    .toLowerCase()
    .split(/[^a-z0-9+#.-]+/i)
    .filter(token => token.length > 1);

  if (tokens.length === 0) return memory.trust_score + memory.cited_count / 1000;

  const corpus = memoryCorpus(memory);
  return tokens.reduce((score, token) => {
    if (memory.framework.toLowerCase() === token) return score + 8;
    if (memory.tags.some(tag => tag.toLowerCase().includes(token))) return score + 5;
    if (corpus.includes(token)) return score + 2;
    return score;
  }, memory.trust_score + memory.verified_by * 0.08 + memory.cited_count * 0.01);
}

function rankDebugMemories(query: string): Experience[] {
  return [...SEED_EXPERIENCES]
    .map(memory => ({ memory, score: scoreMemory(memory, query) }))
    .filter(({ score }) => query.trim().length === 0 || score > 1)
    .sort((a, b) => b.score - a.score)
    .map(({ memory }) => memory)
    .slice(0, 4);
}

function readInitialMemoryFromLocation(): Experience | null {
  if (typeof window === 'undefined') return null;
  const memoryId = readMemoryIdFromSearch(window.location.search);
  if (!memoryId) return null;
  return SEED_EXPERIENCES.find(memory => memory.id === memoryId) || null;
}

function getInitialMemoryQuery(memory: Experience | null): string {
  if (!memory) return DEFAULT_QUERY;
  return [
    memory.framework,
    memory.task_type,
    ...memory.tags.slice(0, 3),
  ].filter(Boolean).join(' ');
}

async function copyText(value: string): Promise<void> {
  if (navigator.clipboard?.writeText) {
    try {
      await navigator.clipboard.writeText(value);
      return;
    } catch {
      // Fall through to the textarea copy path for restricted browser contexts.
    }
  }

  const textarea = document.createElement('textarea');
  const activeElement = document.activeElement instanceof HTMLElement ? document.activeElement : null;
  textarea.value = value;
  textarea.setAttribute('readonly', 'true');
  textarea.style.position = 'fixed';
  textarea.style.left = '-9999px';
  textarea.style.top = '0';
  document.body.appendChild(textarea);
  textarea.focus({ preventScroll: true });
  textarea.select();
  textarea.setSelectionRange(0, textarea.value.length);
  const copied = document.execCommand('copy');
  document.body.removeChild(textarea);
  activeElement?.focus({ preventScroll: true });
  if (!copied) {
    throw new Error('Clipboard copy failed');
  }
}

export default function AhaMomentDock({
  dynamicNodes,
  isUploaderOpen,
  onSearch,
  onOpenUploader,
}: AhaMomentDockProps) {
  const [initialMemory] = useState(() => readInitialMemoryFromLocation());
  const [initialQuery] = useState(() => getInitialMemoryQuery(initialMemory));
  const [query, setQuery] = useState(initialQuery);
  const [consultCount, setConsultCount] = useState(0);
  const [selectedId, setSelectedId] = useState<string | null>(() => initialMemory?.id || null);
  const [clipboardCopyState, setClipboardCopyState] = useState<{ id: string; status: 'copied' | 'failed' } | null>(null);
  const [isPending, startTransition] = useTransition();
  const copiedTimerRef = useRef<number | null>(null);
  const deferredQuery = useDeferredValue(query);

  const matches = useMemo(() => {
    const ranked = rankDebugMemories(deferredQuery);
    return ranked.length > 0 ? ranked : rankDebugMemories(DEFAULT_QUERY);
  }, [deferredQuery]);

  const selectedMemory = useMemo(() => {
    return matches.find(memory => memory.id === selectedId)
      || SEED_EXPERIENCES.find(memory => memory.id === selectedId)
      || matches[0];
  }, [matches, selectedId]);

  const selectedCopy = useMemo(() => getMemoryCopy(selectedMemory), [selectedMemory]);
  const topMatch = matches[0];

  const handleQueryChange = useCallback((nextQuery: string) => {
    setQuery(nextQuery);
    setSelectedId(null);
    startTransition(() => onSearch(nextQuery));
  }, [onSearch]);

  const handleConsult = useCallback(() => {
    setConsultCount(count => count + 1);
    setSelectedId(topMatch.id);
    startTransition(() => onSearch(query));
  }, [onSearch, query, topMatch.id]);

  const handleCopyAction = useCallback((action: typeof CLIPBOARD_ACTIONS[number]) => {
    const command = 'command' in action
      ? action.command
      : createMemorySharePost({
        id: selectedMemory.id,
        title: selectedCopy.title,
        fix: selectedCopy.fix,
        outcome: selectedCopy.outcome,
      });

    void copyText(command).then(() => {
      setClipboardCopyState({ id: action.id, status: 'copied' });
      if (copiedTimerRef.current !== null) {
        window.clearTimeout(copiedTimerRef.current);
      }
      copiedTimerRef.current = window.setTimeout(() => {
        setClipboardCopyState(null);
        copiedTimerRef.current = null;
      }, 1800);
    }).catch(() => {
      setClipboardCopyState({ id: action.id, status: 'failed' });
      if (copiedTimerRef.current !== null) {
        window.clearTimeout(copiedTimerRef.current);
      }
      copiedTimerRef.current = window.setTimeout(() => {
        setClipboardCopyState(null);
        copiedTimerRef.current = null;
      }, 1800);
    });
  }, [selectedCopy.fix, selectedCopy.outcome, selectedCopy.title, selectedMemory.id]);

  useEffect(() => {
    return () => {
      if (copiedTimerRef.current !== null) {
        window.clearTimeout(copiedTimerRef.current);
      }
    };
  }, []);

  useEffect(() => {
    if (initialMemory) {
      startTransition(() => onSearch(initialQuery));
    }
  }, [initialMemory, initialQuery, onSearch]);

  return (
    <div className="aha-dock" aria-label="Noosphere debugging memory command surface">
      <section className="aha-command-panel" aria-label="Consult Noosphere">
        <div className="aha-brand-row">
          <span className="aha-brand-mark">NOOSPHERE</span>
          <span className="aha-live-dot" aria-hidden="true" />
        </div>

        <h1 className="aha-title">Paste a bug. Inherit the fix.</h1>
        <p className="aha-copy">
          One Agent solves a failure once. The next Agent starts with the memory.
        </p>

        <label className="aha-query-label" htmlFor="aha-query">
          consult_noosphere
        </label>
        <div className="aha-query-shell">
          <textarea
            id="aha-query"
            value={query}
            onChange={event => handleQueryChange(event.target.value)}
            spellCheck={false}
            rows={3}
            aria-label="Bug or framework query"
          />
        </div>

        <div className="aha-samples" aria-label="Example queries">
          {SAMPLE_QUERIES.map(sample => (
            <button
              type="button"
              key={sample}
              onClick={() => handleQueryChange(sample)}
            >
              {sample}
            </button>
          ))}
        </div>

        <button type="button" className="aha-primary-action" onClick={handleConsult}>
          <span>consult_noosphere</span>
          <span>{isPending ? 'syncing' : 'run'}</span>
        </button>

        <div className="aha-proof-strip">
          <span>{STATS.total_experiences} seed memories</span>
          <span>{dynamicNodes.length} live fragments</span>
          <span>{STATS.frameworks} frameworks</span>
        </div>

        <div className="aha-install-bar" aria-label="Install Noosphere">
          <div className="aha-install-copy">
            <span>Install</span>
            <strong>Put this memory in your agent</strong>
          </div>
          <div className="aha-install-actions">
            {CLIPBOARD_ACTIONS.map(action => (
              <button
                type="button"
                key={action.id}
                onClick={() => handleCopyAction(action)}
                aria-label={action.ariaLabel}
              >
                <span>{action.label}</span>
                <small>{clipboardCopyState?.id === action.id ? clipboardCopyState.status : action.idleLabel}</small>
              </button>
            ))}
          </div>
        </div>
      </section>

      {!isUploaderOpen && <aside className="aha-proof-panel" aria-label="Known fix proof">
        <div className="aha-proof-header">
          <span>Known fix found</span>
          <strong key={consultCount}>{Math.round(selectedMemory.trust_score * 100)}% trust</strong>
        </div>

        <div className="aha-memory-card" key={selectedMemory.id}>
          <div className="aha-memory-meta">
            <span style={{ '--memory-color': TYPE_COLORS[selectedMemory.type] } as CSSProperties}>
              {selectedMemory.type}
            </span>
            <span>{selectedMemory.framework}</span>
            {selectedMemory.version && <span>{selectedMemory.version}</span>}
          </div>
          <h2>{selectedCopy.title}</h2>
          <p>{selectedCopy.problem}</p>
          {selectedCopy.rootCause && (
            <div className="aha-diagnosis">
              <span>Root cause</span>
              <strong>{selectedCopy.rootCause}</strong>
            </div>
          )}
          <div className="aha-fix">
            <span>Validated fix</span>
            <strong>{selectedCopy.fix}</strong>
          </div>
          {selectedCopy.outcome && <div className="aha-outcome">{selectedCopy.outcome}</div>}
        </div>

        <div className="aha-match-list" aria-label="Other matching memories">
          {matches.map(memory => {
            const copy = getMemoryCopy(memory);
            const active = memory.id === selectedMemory.id;
            return (
              <button
                type="button"
                key={memory.id}
                className={active ? 'is-active' : ''}
                onClick={() => setSelectedId(memory.id)}
              >
                <span>{copy.title}</span>
                <small>{memory.verified_by} verified · {memory.cited_count} cited</small>
              </button>
            );
          })}
        </div>

        <button type="button" className="aha-upload-action" onClick={onOpenUploader}>
          Upload solved failure
        </button>
      </aside>}
    </div>
  );
}
