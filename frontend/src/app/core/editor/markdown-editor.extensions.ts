import { autocompletion, closeBrackets } from '@codemirror/autocomplete';
import { history } from '@codemirror/commands';
import { markdown, markdownLanguage } from '@codemirror/lang-markdown';
import { bracketMatching, indentUnit, syntaxHighlighting } from '@codemirror/language';
import { highlightSelectionMatches, search } from '@codemirror/search';
import { EditorState, type Extension } from '@codemirror/state';
import {
  EditorView,
  drawSelection,
  dropCursor,
  highlightActiveLine,
  highlightActiveLineGutter,
  lineNumbers,
} from '@codemirror/view';
import { classHighlighter } from '@lezer/highlight';
import { markdownPresentation } from './markdown-editor.presentation';

export const markdownEditorLanguage = markdown({ base: markdownLanguage });

export const markdownEditorFoundationExtensions: readonly Extension[] = [
  EditorState.allowMultipleSelections.of(true),
  EditorView.editorAttributes.of({ class: 'markdown-editor-static-theme' }),
  indentUnit.of('  '),
  markdownEditorLanguage,
  markdownPresentation,
  history(),
  lineNumbers(),
  drawSelection(),
  dropCursor(),
  highlightActiveLine(),
  highlightActiveLineGutter(),
  bracketMatching(),
  closeBrackets(),
  autocompletion({ activateOnTyping: false }),
  search({ top: true }),
  highlightSelectionMatches(),
  syntaxHighlighting(classHighlighter),
  EditorView.lineWrapping,
];

export function markdownEditorCspExtension(nonce: string | null): Extension {
  return nonce === null ? [] : EditorView.cspNonce.of(nonce);
}
