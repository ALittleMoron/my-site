import DOMPurify from 'dompurify';
import { marked } from 'marked';
import { LanguageCode } from '../../../core/i18n/i18n.model';

export interface NoteWikiLink {
  slug: string;
  label: string;
  raw: string;
}

const NOTE_WIKI_LINK_PATTERN = /\[\[([a-z0-9]+(?:-[a-z0-9]+)*)(?:\|([^\]\n]+))?\]\]/g;

export function parseNoteWikiLinks(markdown: string): NoteWikiLink[] {
  return Array.from(markdown.matchAll(NOTE_WIKI_LINK_PATTERN), (match) => ({
    slug: match[1],
    label: match[2]?.trim() || match[1],
    raw: match[0],
  }));
}

export function findMissingNoteWikiLinkSlugs(params: {
  markdown: string;
  availableSlugs: ReadonlySet<string>;
}): string[] {
  const missing = new Set<string>();
  for (const link of parseNoteWikiLinks(params.markdown)) {
    if (!params.availableSlugs.has(link.slug)) {
      missing.add(link.slug);
    }
  }
  return Array.from(missing);
}

export function renderNoteMarkdown(markdown: string, language: LanguageCode): string {
  const markdownWithLinks = replaceNoteWikiLinks(markdown, language);
  const html = marked.parse(markdownWithLinks, { async: false });
  const enhanced = html.replaceAll('<pre><code', '<pre class="markdown-code"><code');
  return sanitizeHtml(enhanced);
}

function sanitizeHtml(html: string): string {
  const domPurify = DOMPurify as Partial<{ sanitize: (dirty: string) => string }>;
  return typeof domPurify.sanitize === 'function' ? domPurify.sanitize(html) : html;
}

function replaceNoteWikiLinks(markdown: string, language: LanguageCode): string {
  return markdown.replace(NOTE_WIKI_LINK_PATTERN, (_raw, slug: string, label?: string) => {
    const linkLabel = escapeMarkdownLinkLabel(label?.trim() || slug);
    return `[${linkLabel}](/${language}/notes/${slug})`;
  });
}

function escapeMarkdownLinkLabel(value: string): string {
  return value.replace(/([\\[\]])/g, '\\$1');
}
