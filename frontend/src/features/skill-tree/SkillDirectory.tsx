import { CheckCircle2, PackageCheck, Sprout } from 'lucide-react';
import { useTranslation } from 'react-i18next';
import { domainById, SKILL_DOMAINS } from './taxonomy';
import type { SkillRecord } from './types';

interface SkillDirectoryProps {
  records: SkillRecord[];
  selectedDomainId: string | null;
  hideEmpty?: boolean;
  onSelectSkill: (record: SkillRecord) => void;
}

const KIND_ICONS = {
  published: CheckCircle2,
  bundled: PackageCheck,
  seed: Sprout,
};

export default function SkillDirectory({ records, selectedDomainId, hideEmpty = false, onSelectSkill }: SkillDirectoryProps) {
  const { t } = useTranslation();
  const visibleDomains = SKILL_DOMAINS.filter((domain) => (
    (!selectedDomainId || domain.id === selectedDomainId)
    && (!hideEmpty || records.some((record) => record.domainId === domain.id))
  ));

  return (
    <main className="skill-directory" data-testid="skill-directory">
      {visibleDomains.map((domain) => {
        const domainRecords = records.filter((record) => record.domainId === domain.id);
        return (
          <section className="skill-directory-section" key={domain.id}>
            <header className="skill-directory-heading">
              <span className="skill-domain-swatch" style={{ background: domain.color }} />
              <div>
                <h2>{t(`skills.domains.${domain.translationKey}`)}</h2>
                <p>{t(`skills.domainDescriptions.${domain.translationKey}`)}</p>
              </div>
              <strong>{domainRecords.length}</strong>
            </header>

            {domainRecords.length === 0 ? (
              <div className="skill-directory-empty">{t('skills.emptyDomain')}</div>
            ) : (
              <div className="skill-directory-rows">
                {domainRecords.map((record) => {
                  const Icon = KIND_ICONS[record.kind];
                  const recordDomain = domainById(record.domainId);
                  return (
                    <button
                      className="skill-directory-row"
                      key={record.id}
                      onClick={() => onSelectSkill(record)}
                    >
                      <Icon size={18} strokeWidth={1.8} color={recordDomain.color} aria-hidden="true" />
                      <span className="skill-directory-main">
                        <strong>{record.name}</strong>
                        <small>{record.description}</small>
                      </span>
                      <span className={`skill-kind-label skill-kind-${record.kind}`}>
                        {t(`skills.kinds.${record.kind}`)}
                      </span>
                      <span className="skill-directory-version">
                        {record.version || (record.sourceIssue ? `#${record.sourceIssue}` : 'repo')}
                      </span>
                    </button>
                  );
                })}
              </div>
            )}
          </section>
        );
      })}
    </main>
  );
}
