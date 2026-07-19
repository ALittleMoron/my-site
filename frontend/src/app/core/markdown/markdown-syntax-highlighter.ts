import Prism from 'prismjs';
import 'prismjs/components/prism-bash.js';
import 'prismjs/components/prism-docker.js';
import 'prismjs/components/prism-ini.js';
import 'prismjs/components/prism-json.js';
import 'prismjs/components/prism-markdown.js';
import 'prismjs/components/prism-nginx.js';
import 'prismjs/components/prism-python.js';
import 'prismjs/components/prism-scss.js';
import 'prismjs/components/prism-sql.js';
import 'prismjs/components/prism-toml.js';
import 'prismjs/components/prism-typescript.js';
import 'prismjs/components/prism-yaml.js';

export interface HighlightedMarkdownCode {
  html: string;
  language: string;
}

export type MarkdownPrism = typeof Prism & { manual: boolean };

Prism.manual = true;

export const MARKDOWN_PRISM = Prism as MarkdownPrism;

export function highlightMarkdownCode(
  code: string,
  languageInfo: string | undefined,
): HighlightedMarkdownCode | null {
  const language = normalizedLanguage(languageInfo);
  if (language === null) return null;

  const grammar = MARKDOWN_PRISM.languages[language];
  if (!grammar) return null;

  return {
    html: MARKDOWN_PRISM.highlight(code, grammar, language),
    language,
  };
}

function normalizedLanguage(languageInfo: string | undefined): string | null {
  const language = languageInfo?.trim().split(/\s+/, 1)[0].toLowerCase() ?? '';
  if (!/^[a-z][a-z0-9-]*$/.test(language)) return null;
  return language;
}
