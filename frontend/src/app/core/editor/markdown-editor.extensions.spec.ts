import { EditorState } from '@codemirror/state';
import { syntaxTree } from '@codemirror/language';
import { markdownEditorLanguage } from './markdown-editor.extensions';

describe('Markdown editor extensions', () => {
  it('parses the extended Markdown structures used by the editor', () => {
    const state = EditorState.create({
      doc: [
        '| Name | Value |',
        '| --- | --- |',
        '| answer | 42 |',
        '',
        '- [ ] task',
        '',
        '~~removed~~',
      ].join('\n'),
      extensions: [markdownEditorLanguage],
    });
    const tree = syntaxTree(state).toString();

    expect(tree).toContain('Table');
    expect(tree).toContain('Task');
    expect(tree).toContain('Strikethrough');
  });
});
