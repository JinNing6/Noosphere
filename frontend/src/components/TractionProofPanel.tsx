import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import {
  EMPTY_TRACTION_PROOF,
  createTractionProofPost,
  fetchTractionProof,
  type TractionProofSnapshot,
} from '../utils/tractionProof';

interface TractionProofPanelProps {
  onOpenUploader: () => void;
}

async function copyText(value: string): Promise<void> {
  if (navigator.clipboard?.writeText) {
    try {
      await navigator.clipboard.writeText(value);
      return;
    } catch {
      // Restricted clipboard contexts fall through to the textarea path.
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

function stageLabel(value: string): string {
  return value.replace(/[-_]+/g, ' ').replace(/\s+/g, ' ').trim() || 'public share proof';
}

function firstAccessIssue(snapshot: TractionProofSnapshot): string {
  return snapshot.access_issues[0] || '';
}

export default function TractionProofPanel({ onOpenUploader }: TractionProofPanelProps) {
  const [snapshot, setSnapshot] = useState<TractionProofSnapshot>(EMPTY_TRACTION_PROOF);
  const [copyState, setCopyState] = useState<'idle' | 'copied' | 'failed'>('idle');
  const timerRef = useRef<number | null>(null);

  useEffect(() => {
    let cancelled = false;
    void fetchTractionProof().then(nextSnapshot => {
      if (!cancelled) setSnapshot(nextSnapshot);
    });
    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    return () => {
      if (timerRef.current !== null) {
        window.clearTimeout(timerRef.current);
      }
    };
  }, []);

  const sharePost = useMemo(() => createTractionProofPost(snapshot), [snapshot]);
  const accessIssue = firstAccessIssue(snapshot);

  const handleCopy = useCallback(() => {
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

  return (
    <aside className="traction-proof-panel" aria-label="Noosphere public traction proof">
      <div className="traction-proof-header">
        <div>
          <span>Traction proof</span>
          <strong>{snapshot.target_progress.real_contributor_identities} real contributors</strong>
        </div>
        <button type="button" onClick={handleCopy} aria-label="Copy Noosphere traction proof report">
          {copyState === 'idle' ? 'Copy' : copyState}
        </button>
      </div>

      <div className="traction-proof-metrics" aria-label="Current Noosphere public traction metrics">
        <div>
          <span>Stars</span>
          <strong>{snapshot.repo.stars}</strong>
        </div>
        <div>
          <span>Memories</span>
          <strong>{snapshot.memory.public_memories}</strong>
        </div>
        <div>
          <span>Proof URLs</span>
          <strong>{snapshot.share_proof.reviewable_public_urls}</strong>
        </div>
      </div>

      <div className="traction-proof-bottleneck">
        <span>Weakest bridge</span>
        <strong>{stageLabel(snapshot.bottleneck.stage)}</strong>
        <p>{accessIssue || snapshot.bottleneck.reason}</p>
      </div>

      <div className="traction-proof-actions">
        <a href={snapshot.bottleneck.next_action_url} target="_blank" rel="noopener noreferrer">
          Next proof
        </a>
        <button type="button" onClick={onOpenUploader}>
          Upload
        </button>
      </div>

      <p className="traction-proof-disclosure">{snapshot.disclaimer}</p>
    </aside>
  );
}
