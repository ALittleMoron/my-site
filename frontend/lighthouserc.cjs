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
      assertions: {
        'categories:performance': ['error', { minScore: 0.9 }],
        'categories:accessibility': ['warn', { minScore: 0.9 }],
        'categories:best-practices': ['warn', { minScore: 0.9 }],
        'categories:seo': ['warn', { minScore: 0.9 }],
        'first-contentful-paint': ['error', { maxNumericValue: 1800 }],
        'largest-contentful-paint': ['error', { maxNumericValue: 2500 }],
        'speed-index': ['error', { maxNumericValue: 3000 }],
        'total-blocking-time': ['error', { maxNumericValue: 200 }],
        'cumulative-layout-shift': ['error', { maxNumericValue: 0.1 }],
        'performance-budget': 'error',
      },
    },
    upload: {
      target: 'filesystem',
      outputDir: './performance/reports/lighthouse',
    },
  },
};
