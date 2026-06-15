const LHCI_ORIGIN = 'http://127.0.0.1:4210';

module.exports = {
  ci: {
    collect: {
      startServerCommand: 'node scripts/lhci_server.mjs',
      startServerReadyPattern: 'LHCI server ready',
      startServerReadyTimeout: 60000,
      numberOfRuns: 1,
      url: [
        `${LHCI_ORIGIN}/ru/how-this-site-is-built`,
        `${LHCI_ORIGIN}/ru/notes`,
        `${LHCI_ORIGIN}/ru/notes/typed-notes`,
        `${LHCI_ORIGIN}/ru/competency-matrix`,
        `${LHCI_ORIGIN}/ru/competency-matrix/questions/how-to-write-function`,
      ],
      settings: {
        preset: 'desktop',
        budgetPath: './lighthouse/budgets.json',
      },
    },
    assert: {
      preset: 'lighthouse:recommended',
      assertions: {
        'categories:performance': ['error', { minScore: 0.9 }],
        'categories:accessibility': ['error', { minScore: 0.9 }],
        'categories:best-practices': ['error', { minScore: 0.9 }],
        'categories:seo': ['error', { minScore: 0.9 }],
        'first-contentful-paint': ['error', { maxNumericValue: 1800 }],
        'largest-contentful-paint': ['error', { maxNumericValue: 2500 }],
        'speed-index': ['error', { maxNumericValue: 3000 }],
        'total-blocking-time': ['error', { maxNumericValue: 200 }],
        'cumulative-layout-shift': ['error', { maxNumericValue: 0.1 }],
        'performance-budget': 'error',
        'document-latency-insight': ['warn', {}],
        'forced-reflow-insight': ['warn', {}],
        'image-delivery-insight': ['warn', {}],
        'lcp-discovery-insight': ['warn', {}],
        'network-dependency-tree-insight': ['warn', {}],
        'unused-css-rules': ['warn', { maxLength: 0 }],
        'unused-javascript': ['warn', { maxLength: 0 }],
      },
    },
    upload: {
      target: 'filesystem',
      outputDir: './performance/reports/lighthouse',
    },
  },
};
