import { lazy, Suspense, useMemo } from 'react';
import SkillTreeApp from './features/skill-tree/SkillTreeApp';

const UniverseApp = lazy(() => import('./UniverseApp'));
const ProfilePage = lazy(() => import('./components/ProfilePage'));

function RouteLoading() {
  return (
    <div style={{
      display: 'grid', placeItems: 'center', width: '100vw', height: '100dvh',
      color: '#9299a1', background: '#090b0d', fontFamily: 'Inter, sans-serif', fontSize: 13,
    }}>
      Loading Noosphere...
    </div>
  );
}

export default function App() {
  const route = useMemo(() => {
    const params = new URLSearchParams(window.location.search);
    return {
      profileUser: params.get('profile'),
      isPlayground: params.get('playground') === 'true',
      hasIssueDeepLink: Boolean(params.get('issue')),
      view: params.get('view'),
    };
  }, []);

  if (route.profileUser) {
    return (
      <Suspense fallback={<RouteLoading />}>
        <ProfilePage username={route.profileUser} />
      </Suspense>
    );
  }

  const usesLegacyUniverseRoute = route.isPlayground || route.hasIssueDeepLink;
  if (route.view === 'universe' || usesLegacyUniverseRoute) {
    return (
      <Suspense fallback={<RouteLoading />}>
        <UniverseApp isPlayground={route.isPlayground} />
      </Suspense>
    );
  }

  return <SkillTreeApp />;
}
