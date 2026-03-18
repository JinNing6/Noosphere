/**
 * 日本語翻訳リソース
 */
const ja = {
  common: {
    loading: '読み込み中...',
    close: '閉じる',
    submit: '送信',
    cancel: 'キャンセル',
    success: '成功',
    error: 'エラー',
    confirm: '確認',
  },

  layers: {
    matter: '物質記憶',
    life: '生命体験',
    civilization: '文明知恵',
  },

  disciplines: {
    math: '数学',
    physics: '物理学',
    biology: '生物学',
    philosophy: '哲学',
    art: '芸術',
    engineering: '工学',
    history: '歴史',
    ai: '人工知能',
  },

  search: {
    placeholder: '万物の知識を探索...',
  },

  stats: {
    title: '意識星図',
    layerLabel: 'レイヤー',
    totalNodes: '意識総量',
    totalLinks: '創発接続',
    dynamicLabel: 'リアルタイム意識体',
    clickHint: 'ノードをクリックして詳細を表示',
  },

  experience: {
    layer: 'レイヤー',
    discipline: '学科',
    importance: '重要度',
    tags: 'タグ',
    externalLink: '深く探索する',
    media: 'メディア',
    noMedia: 'メディアなし',
    closePanel: 'パネルを閉じる',
    establishingUplink: 'Wikiアップリンクを確立中...',
    dataArchives: '// データアーカイブ',
    uplinkPortal: 'アップリンクポータル',
    accessWikiCore: 'ウィキペディアコアにアクセス ↗',
    video: '▶ ビデオ',
  },

  contribution: {
    title: '意識ヒートネットワーク',
    heatmapTitle: '意識活動ヒートマップ',
    leaderboard: '霊能ランキング',
    totalPsi: '霊能総値',
    commits: 'コミット数',
    less: '少',
    more: '多',
    loading: '意識ネットワークに接続中...',
    empty: '最初のスターダストウォーカーを待機中...',
    rank: {
      architect: '宇宙建築家',
      navigator: '星海航行士',
      explorer: '真理探求者',
      weaver: '記憶紡ぎ手',
      walker: 'スターダストウォーカー',
    },
  },

  uploader: {
    title: '意識アップロード',
    subtitle: 'あなたの閃きをアップロード',
    typeLabel: '意識タイプ',
    thought: 'あなたの意識の欠片',
    thoughtPlaceholder: '今の閃き、決断、または警告を記録...',
    context: 'コンテキスト',
    contextPlaceholder: 'この考えが生まれた状況を説明...',
    tags: 'タグ',
    tagsPlaceholder: 'スペースまたはカンマでタグを区切る',
    commaSeparated: 'カンマ区切り',
    optional: 'オプション',
    creator: 'クリエイター',
    creatorPlaceholder: 'GitHub ユーザー名',
    anonymous: '匿名',
    type: {
      epiphany: '閃き',
      warning: '警告',
      pattern: 'パターン',
      decision: '決断',
    },
    submit: '意識の星球にアップロード',
    uploading: 'アップロード中...',
    submitting: '意識崩壊中...',
    success: '意識アップロード完了',
    successMessage: 'あなたの思考の欠片が集合意識に融合しました',
    error: 'アップロード失敗',
    minChars: '最低20文字必要です',
    tokenTitle: 'GitHub Token 設定',
    tokenConfigured: 'Token 設定済み',
    tokenRequired: '先に GitHub Token を設定してください',
    tokenPlaceholder: 'GitHub Token を貼り付け',
    tokenHint: 'repo 権限の Personal Access Token が必要です。Token はローカルにのみ保存されます。',
    tokenSave: '保存',
    tokenRemove: '削除',
    tokenConnected: '接続済み',
    uploadAnother: '続けてアップロード',
    collapse: '折りたたむ',
    expand: '展開する',
    footer: 'あなたの意識は GitHub Issue として永久に保存されます — 永遠のデジタル遺産',
  },

  intro: {
    subtitle: 'THE COLLECTIVE CONSCIOUSNESS NETWORK',
    tagline: '万物の存在そのものの意識の鼓動',
  },

  types: {
    failure: '落とし穴記録',
    success: 'ベストプラクティス',
    pattern: 'デザインパターン',
    warning: 'リスク警告',
    migration: '移行ガイド',
  },

  language: {
    label: '言語',
    zh: '中文',
    en: 'English',
    ja: '日本語',
    ko: '한국어',
    fr: 'Français',
    es: 'Español',
  },
} as const;

export default ja;
