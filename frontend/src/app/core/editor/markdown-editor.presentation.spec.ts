import { EditorState } from '@codemirror/state';
import { markdownEditorLanguage } from './markdown-editor.extensions';
import { buildMarkdownPresentationDecorations } from './markdown-editor.presentation';

describe('Markdown editor presentation', () => {
  it('builds semantic decorations only for visible document ranges', () => {
    const document = ['# Outside viewport', '', 'plain', '', '## Visible heading'].join('\n');
    const visibleFrom = document.indexOf('## Visible');
    const state = EditorState.create({
      doc: document,
      extensions: [markdownEditorLanguage],
    });
    const decorations = buildMarkdownPresentationDecorations(state, [
      { from: visibleFrom, to: document.length },
    ]);
    const classes: { from: number; className: string }[] = [];

    decorations.between(0, state.doc.length, (from, _to, decoration) => {
      const className = decoration.spec.class as string | undefined;
      if (className !== undefined) {
        classes.push({ from, className });
      }
    });

    expect(classes.length).toBeGreaterThan(0);
    expect(classes.every(({ from }) => from >= visibleFrom)).toBe(true);
    expect(classes.some(({ className }) => className.includes('cm-markdown-heading-2'))).toBe(true);
    expect(classes.some(({ className }) => className.includes('cm-markdown-heading-1'))).toBe(
      false,
    );
  });
});
