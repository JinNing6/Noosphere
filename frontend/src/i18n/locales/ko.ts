/**
 * 한국어 번역 리소스
 */
const ko = {
  common: {
    loading: '로딩 중...',
    close: '닫기',
    submit: '제출',
    cancel: '취소',
    success: '성공',
    error: '오류',
    confirm: '확인',
  },

  layers: {
    matter: '물질 기억',
    life: '생명 경험',
    civilization: '문명 지혜',
  },

  disciplines: {
    math: '수학',
    physics: '물리학',
    biology: '생물학',
    philosophy: '철학',
    art: '예술',
    engineering: '공학',
    history: '역사',
    ai: '인공지능',
  },

  search: {
    placeholder: '만물의 지식 탐색...',
  },

  stats: {
    title: '의식 성도',
    layerLabel: '레이어',
    totalNodes: '의식 총량',
    totalLinks: '창발 연결',
    dynamicLabel: '실시간 의식체',
    clickHint: '노드를 클릭하여 상세 보기',
  },

  experience: {
    layer: '레이어',
    discipline: '학과',
    importance: '중요도',
    tags: '태그',
    externalLink: '깊이 탐색',
    media: '미디어',
    noMedia: '미디어 없음',
    closePanel: '패널 닫기',
  },

  contribution: {
    title: '의식 히트 네트워크',
    heatmapTitle: '의식 활동 히트맵',
    leaderboard: '영능 랭킹',
    totalPsi: '영능 총값',
    commits: '커밋 수',
    less: '적음',
    more: '많음',
    loading: '의식 네트워크 연결 중...',
    empty: '첫 번째 스타더스트 워커를 기다리는 중...',
    rank: {
      architect: '우주 건축가',
      navigator: '성해 항해사',
      explorer: '진리 탐험가',
      weaver: '기억 직조자',
      walker: '스타더스트 워커',
    },
  },

  uploader: {
    title: '의식 업로드',
    subtitle: '당신의 깨달음을 업로드',
    typeLabel: '의식 유형',
    thought: '당신의 의식 파편',
    thoughtPlaceholder: '지금의 깨달음, 결정 또는 경고를 기록...',
    context: '컨텍스트',
    contextPlaceholder: '이 생각이 떠오른 상황을 설명...',
    tags: '태그',
    tagsPlaceholder: '공백 또는 쉼표로 태그 구분',
    commaSeparated: '쉼표 구분',
    optional: '선택사항',
    creator: '크리에이터',
    creatorPlaceholder: 'GitHub 사용자명',
    anonymous: '익명',
    type: {
      epiphany: '깨달음',
      warning: '경고',
      pattern: '패턴',
      decision: '결정',
    },
    submit: '의식 행성에 업로드',
    uploading: '업로드 중...',
    submitting: '의식 붕괴 중...',
    success: '의식 업로드 완료',
    successMessage: '당신의 사고 파편이 집단 의식에 융합되었습니다',
    error: '업로드 실패',
    minChars: '최소 20자 이상 필요합니다',
    tokenTitle: 'GitHub Token 설정',
    tokenConfigured: 'Token 설정 완료',
    tokenRequired: '먼저 GitHub Token을 설정해주세요',
    tokenPlaceholder: 'GitHub Token 붙여넣기',
    tokenHint: 'repo 권한의 Personal Access Token이 필요합니다. Token은 로컬에만 저장됩니다.',
    tokenSave: '저장',
    tokenRemove: '제거',
    tokenConnected: '연결됨',
    uploadAnother: '계속 업로드',
    collapse: '접기',
    expand: '펼치기',
    footer: '당신의 의식은 GitHub Issue로 영구 보존됩니다 — 영원한 디지털 유산',
  },

  intro: {
    subtitle: 'THE COLLECTIVE CONSCIOUSNESS NETWORK',
    tagline: '만물 존재 자체의 의식 맥동',
  },

  types: {
    failure: '함정 기록',
    success: '모범 사례',
    pattern: '디자인 패턴',
    warning: '위험 경고',
    migration: '마이그레이션 가이드',
  },

  language: {
    label: '언어',
    zh: '中文',
    en: 'English',
    ja: '日本語',
    ko: '한국어',
    fr: 'Français',
    es: 'Español',
  },
} as const;

export default ko;
