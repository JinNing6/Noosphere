import {
  AlertTriangle,
  GitBranch,
  GitFork,
  Languages,
  List,
  Network,
  Plus,
  RotateCcw,
  Search,
  Sparkles,
  SquareTerminal,
} from 'lucide-react';
import { lazy, Suspense, useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { SUPPORTED_LANGUAGES } from '../../i18n';
import { loadSkillTreeData, matchesSkillQuery } from './data';
import SkillContributionPanel from './SkillContributionPanel';
import SkillDetailPanel from './SkillDetailPanel';
import SkillDirectory from './SkillDirectory';
import { SKILL_DOMAINS } from './taxonomy';
import type { SkillRecord, SkillTreeData } from './types';
import './skill-tree.css';

type ViewMode = 'tree' | 'directory';
type ContributionState = { mode: 'skill' | 'domain'; parentSkill?: SkillRecord | null } | null;

const SkillTreeScene = lazy(() => import('./SkillTreeScene'));

function navigateToUniverse() {
  const url = new URL(window.location.href);
  url.search = '';
  url.searchParams.set('view', 'universe');
  window.location.assign(url);
}

function SkillLanguageMenu() {
  const { i18n, t } = useTranslation();
  const [open, setOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);
  const current = SUPPORTED_LANGUAGES.find((language) => i18n.language.startsWith(language.code)) || SUPPORTED_LANGUAGES[1];

  useEffect(() => {
    if (!open) return undefined;
    const close = (event: PointerEvent) => {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) setOpen(false);
    };
    document.addEventListener('pointerdown', close);
    return () => document.removeEventListener('pointerdown', close);
  }, [open]);

  return (
    <div className="skill-language-menu" ref={menuRef}>
      <button
        className="skill-icon-button skill-topbar-icon"
        onClick={() => setOpen((value) => !value)}
        aria-label={t('language.label')}
        title={t('language.label')}
        aria-expanded={open}
      >
        <Languages size={18} aria-hidden="true" />
        <span>{current.code.toUpperCase()}</span>
      </button>
      {open && (
        <div className="skill-language-options">
          {SUPPORTED_LANGUAGES.map((language) => (
            <button
              key={language.code}
              className={language.code === current.code ? 'active' : ''}
              onClick={() => {
                void i18n.changeLanguage(language.code);
                setOpen(false);
              }}
            >
              <span>{language.flag}</span>
              {language.label}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

export default function SkillTreeApp() {
  const { t } = useTranslation();
  const [data, setData] = useState<SkillTreeData | null>(null);
  const [loadError, setLoadError] = useState('');
  const [reloadKey, setReloadKey] = useState(0);
  const [viewMode, setViewMode] = useState<ViewMode>('tree');
  const [query, setQuery] = useState('');
  const [selectedDomainId, setSelectedDomainId] = useState<string | null>(null);
  const [selectedSkill, setSelectedSkill] = useState<SkillRecord | null>(null);
  const [contribution, setContribution] = useState<ContributionState>(null);
  const [reducedMotion, setReducedMotion] = useState(false);

  useEffect(() => {
    const media = window.matchMedia('(prefers-reduced-motion: reduce)');
    const update = () => setReducedMotion(media.matches);
    update();
    media.addEventListener('change', update);
    return () => media.removeEventListener('change', update);
  }, []);

  useEffect(() => {
    const controller = new AbortController();
    loadSkillTreeData(controller.signal)
      .then(setData)
      .catch((error: unknown) => {
        if (controller.signal.aborted) return;
        setLoadError(error instanceof Error ? error.message : String(error));
      });
    return () => controller.abort();
  }, [reloadKey]);

  const matchingRecords = useMemo(() => {
    if (!data) return [];
    return data.records.filter((record) => matchesSkillQuery(record, query));
  }, [data, query]);
  const matchingSkillIds = useMemo(() => new Set(matchingRecords.map((record) => record.id)), [matchingRecords]);
  const directoryRecords = useMemo(() => {
    if (!selectedDomainId) return matchingRecords;
    return matchingRecords.filter((record) => record.domainId === selectedDomainId);
  }, [matchingRecords, selectedDomainId]);
  const domainCounts = useMemo(() => new Map(SKILL_DOMAINS.map((domain) => [
    domain.id,
    data?.records.filter((record) => record.domainId === domain.id).length || 0,
  ])), [data]);

  const selectDomain = useCallback((domainId: string) => {
    setSelectedDomainId((current) => current === domainId ? null : domainId);
    setSelectedSkill(null);
    setContribution(null);
  }, []);

  const selectSkill = useCallback((record: SkillRecord) => {
    setSelectedDomainId(record.domainId);
    setSelectedSkill(record);
    setContribution(null);
  }, []);

  const clearSelection = useCallback(() => {
    setSelectedSkill(null);
    setContribution(null);
  }, []);

  const retryLoad = useCallback(() => {
    setLoadError('');
    setReloadKey((value) => value + 1);
  }, []);

  if (!data && !loadError) {
    return (
      <div className="skill-app skill-loading" data-testid="skill-loading">
        <Network size={30} aria-hidden="true" />
        <span>{t('skills.loading')}</span>
      </div>
    );
  }

  if (!data && loadError) {
    return (
      <div className="skill-app skill-load-error" role="alert">
        <AlertTriangle size={30} aria-hidden="true" />
        <h1>{t('skills.loadError')}</h1>
        <p>{loadError}</p>
        <button className="skill-button skill-button-primary" onClick={retryLoad}>
          <RotateCcw size={16} aria-hidden="true" />{t('skills.retry')}
        </button>
      </div>
    );
  }

  if (!data) return null;

  return (
    <div className="skill-app" data-testid="skill-app">
      <header className="skill-topbar">
        <div className="skill-brand" aria-label="Noosphere Skills">
          <span className="skill-brand-mark">N</span>
          <span>
            <strong>Noosphere</strong>
            <small>{t('skills.productName')}</small>
          </span>
        </div>

        <label className="skill-search">
          <Search size={18} aria-hidden="true" />
          <input
            value={query}
            onChange={(event) => {
              const nextQuery = event.target.value;
              setQuery(nextQuery);
              if (nextQuery.trim()) setSelectedDomainId(null);
            }}
            placeholder={t('skills.searchPlaceholder')}
            aria-label={t('skills.searchPlaceholder')}
          />
          {query && <span>{matchingRecords.length}</span>}
        </label>

        <div className="skill-topbar-actions">
          <div className="skill-view-switch" aria-label={t('skills.viewMode')}>
            <button className={viewMode === 'tree' ? 'active' : ''} onClick={() => setViewMode('tree')} aria-pressed={viewMode === 'tree'}>
              <GitBranch size={17} aria-hidden="true" /><span>{t('skills.tree')}</span>
            </button>
            <button className={viewMode === 'directory' ? 'active' : ''} onClick={() => setViewMode('directory')} aria-pressed={viewMode === 'directory'}>
              <List size={17} aria-hidden="true" /><span>{t('skills.directory')}</span>
            </button>
          </div>
          <SkillLanguageMenu />
          <a className="skill-icon-button skill-topbar-icon" href="https://github.com/JinNing6/Noosphere" target="_blank" rel="noreferrer" aria-label="GitHub" title="GitHub">
            <GitFork size={18} aria-hidden="true" />
          </a>
          <a className="skill-button skill-button-secondary skill-connect-button" href="https://github.com/JinNing6/Noosphere#install-for-your-agent" target="_blank" rel="noreferrer">
            <SquareTerminal size={16} aria-hidden="true" /><span>{t('skills.connectAgent')}</span>
          </a>
          <button className="skill-button skill-button-secondary skill-universe-button" onClick={navigateToUniverse}>
            <Sparkles size={16} aria-hidden="true" /><span>{t('skills.universe')}</span>
          </button>
          <button className="skill-button skill-button-primary" onClick={() => setContribution({ mode: 'skill' })}>
            <Plus size={17} aria-hidden="true" /><span>{t('skills.createSkill')}</span>
          </button>
        </div>
      </header>

      <div className="skill-workspace">
        <nav className="skill-domain-rail" aria-label={t('skills.domainsTitle')}>
          <div className="skill-domain-heading">
            <span>{t('skills.domainsTitle')}</span>
            <strong>{SKILL_DOMAINS.length}</strong>
          </div>
          <button
            className={`skill-domain-item ${selectedDomainId === null ? 'active' : ''}`}
            onClick={() => setSelectedDomainId(null)}
            aria-label={`${t('skills.allDomains')}: ${data.records.length}`}
          >
            <span className="skill-domain-all-icon"><Network size={15} aria-hidden="true" /></span>
            <span><strong>{t('skills.allDomains')}</strong><small>{t('skills.allDomainsHint')}</small></span>
            <b>{data.records.length}</b>
          </button>
          {SKILL_DOMAINS.map((domain) => (
            <button
              className={`skill-domain-item ${selectedDomainId === domain.id ? 'active' : ''}`}
              key={domain.id}
              onClick={() => selectDomain(domain.id)}
              aria-label={`${t(`skills.domains.${domain.translationKey}`)}: ${domainCounts.get(domain.id) || 0}`}
            >
              <span className="skill-domain-swatch" style={{ background: domain.color }} />
              <span>
                <strong>{t(`skills.domains.${domain.translationKey}`)}</strong>
                <small>{t(`skills.domainDescriptions.${domain.translationKey}`)}</small>
              </span>
              <b>{domainCounts.get(domain.id) || 0}</b>
            </button>
          ))}
          <button className="skill-propose-domain" onClick={() => setContribution({ mode: 'domain' })} aria-label={t('skills.proposeDomain')} title={t('skills.proposeDomain')}>
            <GitBranch size={15} aria-hidden="true" />
            <span>{t('skills.proposeDomain')}</span>
          </button>
        </nav>

        <section className="skill-main-surface">
          <div className="skill-network-summary" aria-label={t('skills.networkStatus')}>
            <span><strong>{data.index.counts.published}</strong>{t('skills.metrics.published')}</span>
            <span><strong>{data.index.counts.static}</strong>{t('skills.metrics.bundled')}</span>
            <span><strong>{data.index.counts.seeds}</strong>{t('skills.metrics.seeds')}</span>
            <span><strong>r{data.index.source.registry_revision}</strong>{t('skills.metrics.registry')}</span>
          </div>

          <div className="skill-mobile-view-switch" aria-label={t('skills.viewMode')}>
            <button className={viewMode === 'tree' ? 'active' : ''} onClick={() => setViewMode('tree')} aria-label={t('skills.tree')} aria-pressed={viewMode === 'tree'}>
              <GitBranch size={17} aria-hidden="true" />
            </button>
            <button className={viewMode === 'directory' ? 'active' : ''} onClick={() => setViewMode('directory')} aria-label={t('skills.directory')} aria-pressed={viewMode === 'directory'}>
              <List size={17} aria-hidden="true" />
            </button>
          </div>

          {viewMode === 'tree' ? (
            <>
              <Suspense fallback={<div className="skill-scene-loading"><Network size={22} aria-hidden="true" />{t('skills.loadingTree')}</div>}>
                <SkillTreeScene
                  records={data.records}
                  selectedDomainId={selectedDomainId}
                  selectedSkillId={selectedSkill?.id || null}
                  matchingSkillIds={matchingSkillIds}
                  onSelectDomain={selectDomain}
                  onSelectSkill={selectSkill}
                  onClearSelection={clearSelection}
                  reducedMotion={reducedMotion}
                />
              </Suspense>
              <div className="skill-tree-legend" aria-label={t('skills.legend')}>
                <span><i className="legend-seed" />{t('skills.kinds.seed')}</span>
                <span><i className="legend-bundled" />{t('skills.kinds.bundled')}</span>
                <span><i className="legend-published" />{t('skills.kinds.published')}</span>
              </div>
              <p className="skill-tree-hint">{t('skills.treeHint')}</p>
            </>
          ) : (
            <SkillDirectory
              records={directoryRecords}
              selectedDomainId={selectedDomainId}
              hideEmpty={Boolean(query.trim())}
              onSelectSkill={selectSkill}
            />
          )}

          {query && matchingRecords.length === 0 && (
            <div className="skill-no-results" role="status">
              <Search size={22} aria-hidden="true" />
              <strong>{t('skills.noResults')}</strong>
              <span>{t('skills.noResultsHint')}</span>
            </div>
          )}
        </section>
      </div>

      {selectedSkill && !contribution && (
        <SkillDetailPanel
          record={selectedSkill}
          onClose={() => setSelectedSkill(null)}
          onContributeVersion={(record) => setContribution({ mode: 'skill', parentSkill: record })}
        />
      )}

      {contribution && (
        <SkillContributionPanel
          mode={contribution.mode}
          initialDomainId={selectedDomainId}
          parentSkill={contribution.parentSkill}
          onClose={() => setContribution(null)}
        />
      )}
    </div>
  );
}
