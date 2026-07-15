import { ExternalLink, GitBranchPlus, Send, X } from 'lucide-react';
import { useMemo, useState, type FormEvent } from 'react';
import { useTranslation } from 'react-i18next';
import { SKILL_DOMAINS } from './taxonomy';
import type { SkillRecord } from './types';

type ContributionMode = 'skill' | 'domain';

interface SkillContributionPanelProps {
  mode: ContributionMode;
  initialDomainId?: string | null;
  parentSkill?: SkillRecord | null;
  onClose: () => void;
}

function createIssueUrl(title: string, body: string, labels: string[]) {
  const url = new URL('https://github.com/JinNing6/Noosphere/issues/new');
  url.searchParams.set('title', title);
  url.searchParams.set('body', body);
  url.searchParams.set('labels', labels.join(','));
  return url.toString();
}

export default function SkillContributionPanel({
  mode,
  initialDomainId,
  parentSkill,
  onClose,
}: SkillContributionPanelProps) {
  const { t } = useTranslation();
  const [name, setName] = useState(parentSkill?.name || '');
  const [domainId, setDomainId] = useState(initialDomainId || parentSkill?.domainId || SKILL_DOMAINS[0].id);
  const [summary, setSummary] = useState('');
  const [symptom, setSymptom] = useState('');
  const [rootCause, setRootCause] = useState('');
  const [fix, setFix] = useState('');
  const [verification, setVerification] = useState('');
  const [appliesWhen, setAppliesWhen] = useState('');
  const [avoidWhen, setAvoidWhen] = useState('');
  const [testCommands, setTestCommands] = useState('');
  const [sourceUrls, setSourceUrls] = useState('');

  const valid = useMemo(() => {
    if (mode === 'domain') return name.trim().length >= 3 && summary.trim().length >= 20;
    return name.trim().length >= 3
      && summary.trim().length >= 20
      && symptom.trim().length >= 20
      && rootCause.trim().length >= 20
      && fix.trim().length >= 20
      && verification.trim().length >= 20
      && appliesWhen.trim().length >= 20
      && testCommands.split(/\r?\n/).some((value) => value.trim())
      && sourceUrls.split(/\r?\n/).some((value) => /^https:\/\//i.test(value.trim()));
  }, [appliesWhen, fix, mode, name, rootCause, sourceUrls, summary, symptom, testCommands, verification]);

  const submit = (event: FormEvent) => {
    event.preventDefault();
    if (!valid) return;

    if (mode === 'domain') {
      const body = [
        '## Domain branch proposal',
        '',
        `**Proposed domain:** ${name.trim()}`,
        '',
        `**Why existing branches do not fit:** ${summary.trim()}`,
        '',
        'This proposal requests taxonomy review. It does not mutate the public Skill Tree directly.',
      ].join('\n');
      window.open(createIssueUrl(`Domain proposal: ${name.trim()}`, body, ['skill-candidate']), '_blank', 'noopener,noreferrer');
      return;
    }

    const payload = {
      schema_version: '1.0',
      skill_name: name.trim(),
      domain: domainId,
      parent_skill: parentSkill?.name || null,
      summary: summary.trim(),
      evidence: {
        symptom: symptom.trim(),
        root_cause: rootCause.trim(),
        fix: fix.trim(),
        verification: verification.trim(),
        applies_when: appliesWhen.trim(),
        avoid_when: avoidWhen.trim(),
        test_commands: testCommands.split(/\r?\n/).map((value) => value.trim()).filter(Boolean),
        source_urls: sourceUrls.split(/\r?\n/).map((value) => value.trim()).filter(Boolean),
      },
    };
    const body = [
      '## Agent Skill proposal',
      '',
      '<!-- SKILL_PROPOSAL_START -->',
      '```json',
      JSON.stringify(payload, null, 2),
      '```',
      '<!-- SKILL_PROPOSAL_END -->',
      '',
      'This proposal is review input. It cannot publish or replace a Skill without independent evidence and maintainer approval.',
    ].join('\n');
    const titlePrefix = parentSkill ? `Skill version proposal: ${parentSkill.name}` : `Skill proposal: ${name.trim()}`;
    window.open(createIssueUrl(titlePrefix, body, ['skill-candidate']), '_blank', 'noopener,noreferrer');
  };

  return (
    <aside className="skill-contribution-panel" aria-label={t(mode === 'domain' ? 'skills.proposeDomain' : 'skills.createSkill')}>
      <header className="skill-contribution-header">
        <div>
          <span>{mode === 'domain' ? t('skills.taxonomyReview') : t('skills.reviewGated')}</span>
          <h1>{mode === 'domain' ? t('skills.proposeDomain') : parentSkill ? t('skills.uploadVersion') : t('skills.createSkill')}</h1>
        </div>
        <button className="skill-icon-button" onClick={onClose} aria-label={t('common.close')} title={t('common.close')}>
          <X size={18} aria-hidden="true" />
        </button>
      </header>

      <form className="skill-contribution-form" onSubmit={submit}>
        <label>
          <span>{mode === 'domain' ? t('skills.fields.domainName') : t('skills.fields.skillName')}</span>
          <input value={name} onChange={(event) => setName(event.target.value)} disabled={Boolean(parentSkill)} required />
        </label>

        {mode === 'skill' && (
          <label>
            <span>{t('skills.fields.domain')}</span>
            <select value={domainId} onChange={(event) => setDomainId(event.target.value)}>
              {SKILL_DOMAINS.map((domain) => (
                <option key={domain.id} value={domain.id}>{t(`skills.domains.${domain.translationKey}`)}</option>
              ))}
            </select>
          </label>
        )}

        <label>
          <span>{mode === 'domain' ? t('skills.fields.domainReason') : t('skills.fields.summary')}</span>
          <textarea value={summary} onChange={(event) => setSummary(event.target.value)} rows={3} required />
        </label>

        {mode === 'skill' && (
          <>
            <label><span>{t('skills.fields.symptom')}</span><textarea value={symptom} onChange={(event) => setSymptom(event.target.value)} rows={3} required /></label>
            <label><span>{t('skills.fields.rootCause')}</span><textarea value={rootCause} onChange={(event) => setRootCause(event.target.value)} rows={3} required /></label>
            <label><span>{t('skills.fields.fix')}</span><textarea value={fix} onChange={(event) => setFix(event.target.value)} rows={3} required /></label>
            <label><span>{t('skills.fields.verification')}</span><textarea value={verification} onChange={(event) => setVerification(event.target.value)} rows={3} required /></label>
            <label><span>{t('skills.fields.appliesWhen')}</span><textarea value={appliesWhen} onChange={(event) => setAppliesWhen(event.target.value)} rows={2} required /></label>
            <label><span>{t('skills.fields.avoidWhen')}</span><textarea value={avoidWhen} onChange={(event) => setAvoidWhen(event.target.value)} rows={2} /></label>
            <label><span>{t('skills.fields.testCommands')}</span><textarea className="skill-mono-input" value={testCommands} onChange={(event) => setTestCommands(event.target.value)} rows={3} required /></label>
            <label><span>{t('skills.fields.sourceUrls')}</span><textarea className="skill-mono-input" value={sourceUrls} onChange={(event) => setSourceUrls(event.target.value)} rows={3} required /></label>
          </>
        )}

        <p className="skill-contribution-note">
          <GitBranchPlus size={16} aria-hidden="true" />
          {mode === 'domain' ? t('skills.domainReviewNotice') : t('skills.skillReviewNotice')}
        </p>

        <button className="skill-button skill-button-primary skill-contribution-submit" type="submit" disabled={!valid}>
          <Send size={16} aria-hidden="true" />
          {t('skills.continueOnGitHub')}
          <ExternalLink size={14} aria-hidden="true" />
        </button>
      </form>
    </aside>
  );
}
