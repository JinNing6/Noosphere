import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import type { KnowledgeNode } from '../data/knowledge';
import type { LaunchKitPost } from '../utils/launchKit';
import { createLaunchKitPosts } from '../utils/launchKit';

interface LaunchKitProps {
  dynamicNodes: KnowledgeNode[];
  onOpenUploader: () => void;
}

async function copyLaunchPost(post: LaunchKitPost): Promise<void> {
  if (navigator.clipboard?.writeText) {
    try {
      await navigator.clipboard.writeText(post.body);
      return;
    } catch {
      // Restricted clipboard contexts fall through to the textarea path.
    }
  }

  const textarea = document.createElement('textarea');
  const activeElement = document.activeElement instanceof HTMLElement ? document.activeElement : null;
  textarea.value = post.body;
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

export default function LaunchKit({
  dynamicNodes,
  onOpenUploader,
}: LaunchKitProps) {
  const posts = useMemo(() => createLaunchKitPosts(dynamicNodes), [dynamicNodes]);
  const [copiedChannel, setCopiedChannel] = useState<string | null>(null);
  const [failedChannel, setFailedChannel] = useState<string | null>(null);
  const timerRef = useRef<number | null>(null);

  const handleCopy = useCallback((post: LaunchKitPost) => {
    void copyLaunchPost(post).then(() => {
      setCopiedChannel(post.channel);
      setFailedChannel(null);
      if (timerRef.current !== null) window.clearTimeout(timerRef.current);
      timerRef.current = window.setTimeout(() => {
        setCopiedChannel(null);
        timerRef.current = null;
      }, 1800);
    }).catch(() => {
      setFailedChannel(post.channel);
      setCopiedChannel(null);
      if (timerRef.current !== null) window.clearTimeout(timerRef.current);
      timerRef.current = window.setTimeout(() => {
        setFailedChannel(null);
        timerRef.current = null;
      }, 1800);
    });
  }, []);

  useEffect(() => {
    return () => {
      if (timerRef.current !== null) {
        window.clearTimeout(timerRef.current);
      }
    };
  }, []);

  return (
    <aside className="launch-kit" aria-label="Noosphere public launch kit">
      <div className="launch-kit-header">
        <div>
          <span>Launch kit</span>
          <strong>Copy posts</strong>
        </div>
        <button type="button" onClick={onOpenUploader}>
          Upload
        </button>
      </div>

      <div className="launch-kit-posts">
        {posts.map(post => (
          <article className="launch-kit-post" key={post.channel}>
            <div>
              <span>{post.channel}</span>
              <strong>{post.title}</strong>
            </div>
            <button type="button" onClick={() => handleCopy(post)} aria-label={`Copy ${post.channel} launch post`}>
              {copiedChannel === post.channel ? 'Copied' : failedChannel === post.channel ? 'Failed' : 'Copy'}
            </button>
            <a href={post.proofUrl} target="_blank" rel="noopener noreferrer">
              Record proof
            </a>
          </article>
        ))}
      </div>
    </aside>
  );
}
