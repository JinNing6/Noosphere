/**
 * Recurso de traducción en español
 */
const es = {
  common: {
    loading: 'Cargando...',
    close: 'Cerrar',
    submit: 'Enviar',
    cancel: 'Cancelar',
    success: 'Éxito',
    error: 'Error',
    confirm: 'Confirmar',
  },

  layers: {
    matter: 'Memoria Material',
    life: 'Experiencia Vital',
    civilization: 'Sabiduría Civilizatoria',
  },

  disciplines: {
    math: 'Matemáticas',
    physics: 'Física',
    biology: 'Biología',
    philosophy: 'Filosofía',
    art: 'Arte',
    engineering: 'Ingeniería',
    history: 'Historia',
    ai: 'IA',
  },

  search: {
    placeholder: 'Explorar conocimiento universal...',
  },

  stats: {
    title: 'Atlas de Conciencia',
    layerLabel: 'Capas',
    totalNodes: 'Nodos Totales',
    totalLinks: 'Enlaces Emergentes',
    dynamicLabel: 'Conciencia en Vivo',
    clickHint: 'Haz clic en un nodo para explorar',
  },

  experience: {
    layer: 'Capa',
    discipline: 'Disciplina',
    importance: 'Importancia',
    tags: 'Etiquetas',
    externalLink: 'Explorar Más',
    media: 'Medios',
    noMedia: 'Sin medios disponibles',
    closePanel: 'Cerrar Panel',
    establishingUplink: 'ESTABLECIENDO ENLACE WIKI...',
    dataArchives: '// ARCHIVOS DE DATOS',
    uplinkPortal: 'PORTAL DE ENLACE',
    accessWikiCore: 'ACCEDER AL NÚCLEO WIKIPEDIA ↗',
    video: '▶ VIDEO',
  },

  contribution: {
    title: 'Red Térmica de Conciencia',
    heatmapTitle: 'Mapa Térmico de Actividad',
    leaderboard: 'Ranking Psi',
    totalPsi: 'Psi Total',
    commits: 'Commits',
    less: 'Menos',
    more: 'Más',
    loading: 'Conectando a la red de conciencia...',
    empty: 'Esperando al primer caminante de polvo estelar...',
    rank: {
      architect: 'Arquitecto Cósmico',
      navigator: 'Navegante Estelar',
      explorer: 'Explorador de la Verdad',
      weaver: 'Tejedor de Memorias',
      walker: 'Caminante de Polvo Estelar',
    },
  },

  uploader: {
    title: 'Carga de Conciencia',
    subtitle: 'Sube tu epifanía',
    typeLabel: 'Tipo de Conciencia',
    thought: 'Tu fragmento de conciencia',
    thoughtPlaceholder: 'Registra tu epifanía, decisión o advertencia...',
    context: 'Contexto',
    contextPlaceholder: 'Describe la situación que provocó este pensamiento...',
    tags: 'Etiquetas',
    tagsPlaceholder: 'Separa las etiquetas con espacios o comas',
    commaSeparated: 'separadas por comas',
    optional: 'opcional',
    creator: 'Creador',
    creatorPlaceholder: 'Tu nombre de usuario de GitHub',
    anonymous: 'Anónimo',
    type: {
      epiphany: 'Epifanía',
      warning: 'Advertencia',
      pattern: 'Patrón',
      decision: 'Decisión',
    },
    submit: 'Cargar al Globo de Conciencia',
    uploading: 'Cargando...',
    submitting: 'Colapso de conciencia...',
    success: 'Conciencia Cargada',
    successMessage: 'Tu fragmento de pensamiento se ha fusionado con la conciencia colectiva',
    error: 'Carga Fallida',
    minChars: 'Se requieren mínimo 20 caracteres',
    tokenTitle: 'Configurar GitHub Token',
    tokenConfigured: 'Token Configurado',
    tokenRequired: 'Por favor configura el GitHub Token primero',
    tokenPlaceholder: 'Pega tu GitHub Token',
    tokenHint: 'Requiere un Personal Access Token con permiso repo. El Token se almacena solo localmente.',
    tokenSave: 'Guardar',
    tokenRemove: 'Eliminar',
    tokenConnected: 'Conectado',
    uploadAnother: 'Seguir Cargando',
    collapse: 'Contraer',
    expand: 'Expandir',
    footer: 'Tu conciencia se preservará como un GitHub Issue — patrimonio digital eterno',
  },

  intro: {
    subtitle: 'THE COLLECTIVE CONSCIOUSNESS NETWORK',
    tagline: 'La pulsación de conciencia de toda existencia',
  },

  types: {
    failure: 'Registro de Tropiezo',
    success: 'Mejor Práctica',
    pattern: 'Patrón de Diseño',
    warning: 'Alerta de Riesgo',
    migration: 'Guía de Migración',
  },

  language: {
    label: 'Idioma',
    zh: '中文',
    en: 'English',
    ja: '日本語',
    ko: '한국어',
    fr: 'Français',
    es: 'Español',
  },
} as const;

export default es;
