import type { Config } from 'jest';

const config: Config = {
  preset: 'jest-preset-angular',
  setupFilesAfterEnv: ['<rootDir>/src/setup-jest.ts'],
  testMatch: ['<rootDir>/src/**/*.spec.ts'],
  collectCoverageFrom: ['src/app/**/*.ts', '!src/app/**/*.routes.ts'],
  coverageReporters: ['text', 'lcov', 'cobertura'],
  // Allow Jest to transform ESM-only packages while preserving the Angular preset's mjs handling
  transformIgnorePatterns: [
    'node_modules/(?!(.*\\.mjs$|@angular/common/locales/.*\\.js$|marked|dompurify))',
  ],
};

export default config;
