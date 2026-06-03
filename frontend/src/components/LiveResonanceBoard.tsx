import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import type { KnowledgeNode } from '../data/knowledge';
import { createNoosphereIssueUrl } from '../utils/issueDeepLink';
import { createResonanceBoardSharePost, summarizeResonanceBoard } from '../utils/resonanceBoard';

interface LiveResonanceBoardProps {
  dynamicNodes: KnowledgeNode[];
  onOpenUploader: () => void;
}

async function copyText(value: string): Promise<void> {
  if (navigator.clipboard?.writeText) {
    try {
      await navigator.clipboard.writeText(value);
      return;
    } catch {
      // Fallback below handles restricted clipboard contexts.
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
  if (!copied) throw new Error('Clipboard copy failed');
}

function latestLabel(node: KnowledgeNode | null): string {
  if (!node) return 'Awaiting first public memory';
  const title = node.title_zh || node.title_en || node.id;
  return title.length > 42 ? `${title.slice(0, 39).trimEnd()}...` : title;
}

function resonanceLabel(node: KnowledgeNode): string {
  const title = node.title_zh || node.title_en || node.id;
  return title.length > 28 ? `${title.slice(0, 25).trimEnd()}...` : title;
}

export default function LiveResonanceBoard({
  dynamicNodes,
  onOpenUploader,
}: LiveResonanceBoardProps) {
  const [copyState, setCopyState] = useState<'idle' | 'copied' | 'failed'>('idle');
  const timerRef = useRef<number | null>(null);
  const summary = useMemo(() => summarizeResonanceBoard(dynamicNodes), [dynamicNodes]);
  const sharePost = useMemo(() => createResonanceBoardSharePost(summary), [summary]);
  const latestUrl = summary.latestMemory?.issueNumber
    ? createNoosphereIssueUrl(summary.latestMemory.issueNumber)
    : null;

  const handleCopyShare = useCallback(() => {
    void copyText(sharePost).then(() => {
      setCopyState('copied');
      if (timerRef.current !== null) window.clearTimeout(timerRef.current);
      timerRef.current = window.setTimeout(() => {
        setCopyState('idle');
        timerRef.current = null;
      }, 1800);
    }).catch(() => {
      setCopyState('failed');
      if (timerRef.current !== null) window.clearTimeout(timerRef.current);
      timerRef.current = window.setTimeout(() => {
        setCopyState('idle');
        timerRef.current = null;
      }, 1800);
    });
  }, [sharePost]);

  useEffect(() => {
    return () => {
      if (timerRef.current !== null) {
        window.clearTimeout(timerRef.current);
      }
    };
  }, []);

  return (
    <aside className="resonance-board" aria-label="Live Noosphere resonance board">
      <div className="resonance-board-header">
        <div>
          <span>Live network</span>
          <strong>{summary.totalMemories} memories</strong>
        </div>
        <button
          type="button"
          className="resonance-share-button"
          onClick={handleCopyShare}
          aria-label="Copy live Noosphere memory network report"
        >
          {copyState === 'idle' ? 'Share' : copyState}
        </button>
      </div>

      <div className="resonance-metric-grid" aria-label="Current Noosphere memory stats">
        <div>
          <span>Media</span>
          <strong>{summary.mediaMemories}</strong>
        </div>
        <div>
          <span>Resonance</span>
          <strong>{summary.totalResonance}</strong>
        </div>
        <div>
          <span>Creators</span>
          <strong>{summary.topCreators.length}</strong>
        </div>
      </div>

      <div className="resonance-latest">
        <span>Latest memory</span>
        {latestUrl ? (
          <a href={latestUrl} target="_blank" rel="noopener noreferrer">
            {latestLabel(summary.latestMemory)}
          </a>
        ) : (
          <strong>{latestLabel(summary.latestMemory)}</strong>
        )}
      </div>

      {summary.strongestResonance && (
        <div className="resonance-strongest">
          <span>Strongest resonance</span>
          <strong>
            {resonanceLabel(summary.strongestResonance.source)}
            <small>{Math.round(summary.strongestResonance.score * 100)}%</small>
            {resonanceLabel(summary.strongestResonance.target)}
          </strong>
        </div>
      )}

      <div className="resonance-board-columns">
        <div aria-label="Memory type distribution">
          <span className="resonance-section-label">Types</span>
          {summary.typeRows.slice(0, 4).map(row => (
            <div className="resonance-row" key={row.type}>
              <span>{row.type}</span>
              <strong>{row.count}</strong>
            </div>
          ))}
        </div>
        <div aria-label="Top public memory contributors">
          <span className="resonance-section-label">Contributors</span>
          {summary.topCreators.slice(0, 4).map(row => (
            <div className="resonance-row" key={row.creator}>
              <span>{row.creator}</span>
              <strong>{row.count}</strong>
            </div>
          ))}
        </div>
      </div>

      <button type="button" className="resonance-upload-button" onClick={onOpenUploader}>
        Upload a solved failure
      </button>
    </aside>
  );
}
