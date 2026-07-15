import { Check, Clipboard, ExternalLink, GitFork, ShieldCheck, Sprout, X } from 'lucide-react';
import { useState, type CSSProperties } from 'react';
import { useTranslation } from 'react-i18next';
import { domainById } from './taxonomy';
import type { SkillRecord } from './types';

interface SkillDetailPanelProps {
  record: SkillRecord;
  onClose: () => void;
  onContributeVersion: (record: SkillRecord) => void;
}

export default function SkillDetailPanel({ record, onClose, onContributeVersion }: SkillDetailPanelProps) {
  const { t } = useTranslation();
  const [copied, setCopied] = useState(false);
  const domain = domainById(record.domainId);
  const command = `npx skills add JinNing6/Noosphere --skill ${record.name}`;
  const isInstallable = record.kind === 'published' || record.kind === 'bundled';

  const copyCommand = async () => {
    await navigator.clipboard.writeText(command);
    setCopied(true);
    window.setTimeout(() => setCopied(false), 1600);
  };

  return (
    <aside
      className="skill-detail-panel"
      aria-label={t('skills.detailTitle')}
      data-testid="skill-detail-panel"
      style={{ '--skill-detail-accent': domain.color } as CSSProperties}
    >
      <header className="skill-detail-header">
        <div className="skill-detail-status">
          <span className="skill-domain-swatch" style={{ background: domain.color }} />
          <span>{t(`skills.domains.${domain.translationKey}`)}</span>
          <span className={`skill-kind-label skill-kind-${record.kind}`}>{t(`skills.kinds.${record.kind}`)}</span>
        </div>
        <button className="skill-icon-button" onClick={onClose} aria-label={t('common.close')} title={t('common.close')}>
          <X size={18} aria-hidden="true" />
        </button>
      </header>

      <div className="skill-detail-scroll">
        <h1>{record.name}</h1>
        <p className="skill-detail-description">{record.description}</p>

        <dl className="skill-detail-facts">
          <div>
            <dt>{t('skills.lifecycle')}</dt>
            <dd><ShieldCheck size={15} aria-hidden="true" /> {t(`skills.lifecycleStates.${record.lifecycle}`)}</dd>
          </div>
          <div>
            <dt>{record.version ? t('skills.version') : t('skills.source')}</dt>
            <dd>{record.version || (record.sourceIssue ? `GitHub Issue #${record.sourceIssue}` : 'Repository Skill')}</dd>
          </div>
          {record.creator && (
            <div>
              <dt>{t('skills.creator')}</dt>
              <dd>{record.creator}</dd>
            </div>
          )}
          {record.digest && (
            <div>
              <dt>SHA-256</dt>
              <dd className="skill-detail-digest">{record.digest}</dd>
            </div>
          )}
        </dl>

        {record.evidence && (
          <div className="skill-evidence">
            <section>
              <h2>{t('skills.evidence.symptom')}</h2>
              <p>{record.evidence.symptom}</p>
            </section>
            <section>
              <h2>{t('skills.evidence.rootCause')}</h2>
              <p>{record.evidence.root_cause}</p>
            </section>
            <section>
              <h2>{t('skills.evidence.fix')}</h2>
              <p>{record.evidence.fix}</p>
            </section>
            <section>
              <h2>{t('skills.evidence.verification')}</h2>
              <p>{record.evidence.verification}</p>
            </section>
            {record.evidence.test_commands.length > 0 && (
              <section>
                <h2>{t('skills.evidence.commands')}</h2>
                {record.evidence.test_commands.map((testCommand) => <code key={testCommand}>{testCommand}</code>)}
              </section>
            )}
          </div>
        )}

        {isInstallable && (
          <div className="skill-install-block">
            <span>{t('skills.install')}</span>
            <code>{command}</code>
            <button className="skill-icon-button" onClick={copyCommand} aria-label={t('skills.copyCommand')} title={t('skills.copyCommand')}>
              {copied ? <Check size={17} aria-hidden="true" /> : <Clipboard size={17} aria-hidden="true" />}
            </button>
          </div>
        )}

        {record.kind === 'seed' && (
          <p className="skill-honesty-note"><Sprout size={16} aria-hidden="true" />{t('skills.seedNotice')}</p>
        )}
      </div>

      <footer className="skill-detail-actions">
        <a className="skill-button skill-button-secondary" href={record.sourceUrl} target="_blank" rel="noreferrer">
          <ExternalLink size={16} aria-hidden="true" />
          {t('skills.openSource')}
        </a>
        <button className="skill-button skill-button-primary" onClick={() => onContributeVersion(record)}>
          <GitFork size={16} aria-hidden="true" />
          {t('skills.contributeVersion')}
        </button>
      </footer>
    </aside>
  );
}
