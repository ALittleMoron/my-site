import { marked } from 'marked';
import { LanguageCode } from '../i18n/i18n.model';

export const WIKI_LINK_TARGET_TYPES = ['articles', 'matrix'] as const;

export type WikiLinkTargetType = (typeof WIKI_LINK_TARGET_TYPES)[number];

export interface WikiLink {
  type: WikiLinkTargetType;
  slug: string;
  label: string;
  raw: string;
}

export interface WikiLinkTargetGroup {
  type: WikiLinkTargetType;
  slugs: string[];
}

export type WikiLinkTargetLookup = ReadonlyMap<WikiLinkTargetType, ReadonlySet<string>>;

const WIKI_LINK_PATTERN = /\[\[(articles|matrix):([a-z0-9]+(?:-[a-z0-9]+)*)(?:\|([^\]\n]+))?\]\]/g;

export function parseWikiLinks(markdown: string): WikiLink[] {
  return Array.from(markdown.matchAll(WIKI_LINK_PATTERN), (match) => ({
    type: match[1] as WikiLinkTargetType,
    slug: match[2],
    label: match[3]?.trim() || match[2],
    raw: match[0],
  }));
}

export function createWikiLinkTargetLookup(
  targets: readonly WikiLinkTargetGroup[],
): WikiLinkTargetLookup {
  return new Map(targets.map((target) => [target.type, new Set(target.slugs)] as const));
}

export function findMissingWikiLinkTargets(params: {
  markdown: string;
  availableTargets: WikiLinkTargetLookup;
}): string[] {
  const missing = new Set<string>();
  for (const link of parseWikiLinks(params.markdown)) {
    if (!params.availableTargets.get(link.type)?.has(link.slug)) {
      missing.add(`${link.type}:${link.slug}`);
    }
  }
  return Array.from(missing);
}

export function renderMarkdownWithWikiLinks(
  markdown: string,
  language: LanguageCode,
  sanitizeHtml: (html: string) => string,
): string {
  const markdownWithLinks = replaceWikiLinks(markdown, language);
  const html = marked.parse(markdownWithLinks, { async: false });
  const enhanced = html.replaceAll('<pre><code', '<pre class="markdown-code"><code');
  return sanitizeHtml(enhanced);
}

export function replaceWikiLinksWithPlainText(markdown: string): string {
  return markdown.replace(
    WIKI_LINK_PATTERN,
    (_raw, _type: WikiLinkTargetType, slug: string, label?: string) => label?.trim() || slug,
  );
}

function replaceWikiLinks(markdown: string, language: LanguageCode): string {
  return markdown.replace(
    WIKI_LINK_PATTERN,
    (_raw, type: WikiLinkTargetType, slug: string, label?: string) => {
      const linkLabel = escapeMarkdownLinkLabel(label?.trim() || slug);
      return `[${linkLabel}](${wikiLinkPath(type, slug, language)})`;
    },
  );
}

function wikiLinkPath(type: WikiLinkTargetType, slug: string, language: LanguageCode): string {
  if (type === 'articles') {
    return `/${language}/articles/${slug}`;
  }
  return `/${language}/competency-matrix/questions/${slug}`;
}

function escapeMarkdownLinkLabel(value: string): string {
  return value.replace(/([\\[\]])/g, '\\$1');
}
