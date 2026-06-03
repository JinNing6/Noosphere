import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import {
  EMPTY_SHARE_PROOF_INDEX,
  SHARE_PROOF_FORM_URL,
  createShareProofWallPost,
  fetchShareProofIndex,
  type ShareProofIndex,
  type ShareProofRecord,
} from '../utils/shareProofs';

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

function proofTitle(proof: ShareProofRecord): string {
  const title = proof.share_context || proof.title || `Share proof #${proof.issue_number}`;
  return title.length > 76 ? `${title.slice(0, 73).trimEnd()}...` : title;
}

export default function ShareProofWall() {
  const [index, setIndex] = useState<ShareProofIndex>(EMPTY_SHARE_PROOF_INDEX);
  const [copyState, setCopyState] = useState<'idle' | 'copied' | 'failed'>('idle');
  const timerRef = useRef<number | null>(null);

  useEffect(() => {
    let cancelled = false;
    void fetchShareProofIndex().then(nextIndex => {
      if (!cancelled) setIndex(nextIndex);
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

  const reviewableProofs = useMemo(
    () => index.proofs.filter(proof => proof.reviewable && proof.share_url),
    [index.proofs],
  );
  const sharePost = useMemo(() => createShareProofWallPost(index), [index]);

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

  return (
    <aside className="share-proof-wall" aria-label="Noosphere public share proof wall">
      <div className="share-proof-header">
        <div>
          <span>Share proof wall</span>
          <strong>{index.summary.reviewable_public_urls} public URLs</strong>
        </div>
        <button
          type="button"
          className="share-proof-copy"
          onClick={handleCopyShare}
          aria-label="Copy Noosphere share proof wall report"
        >
          {copyState === 'idle' ? 'Copy' : copyState}
        </button>
      </div>

      <div className="share-proof-metrics" aria-label="Current Noosphere share proof stats">
        <div>
          <span>Proof issues</span>
          <strong>{index.summary.total_proof_issues}</strong>
        </div>
        <div>
          <span>Reviewable</span>
          <strong>{index.summary.reviewable_public_urls}</strong>
        </div>
        <div>
          <span>Needs URL</span>
          <strong>{index.summary.missing_or_invalid_urls}</strong>
        </div>
      </div>

      <div className="share-proof-list" aria-label="Latest reviewable public share proofs">
        {reviewableProofs.length > 0 ? (
          reviewableProofs.slice(0, 3).map(proof => (
            <article className="share-proof-card" key={proof.issue_number}>
              <a href={proof.share_url} target="_blank" rel="noopener noreferrer">
                {proofTitle(proof)}
              </a>
              <div>
                <span>{proof.submitted_by}</span>
                <a href={proof.issue_url} target="_blank" rel="noopener noreferrer">
                  Issue #{proof.issue_number}
                </a>
              </div>
            </article>
          ))
        ) : (
          <div className="share-proof-empty">
            <strong>No public share proof yet.</strong>
            <span>Record the first external post, thread, video, or repository comment.</span>
          </div>
        )}
      </div>

      <p className="share-proof-disclaimer">{index.summary.disclaimer}</p>

      <a className="share-proof-submit" href={index.next_action_url || SHARE_PROOF_FORM_URL} target="_blank" rel="noopener noreferrer">
        Open Share Proof Form
      </a>
    </aside>
  );
}
