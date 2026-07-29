import { history, undo } from '@codemirror/commands';
import { markdown, markdownLanguage } from '@codemirror/lang-markdown';
import { EditorSelection, EditorState, StateEffect, Transaction } from '@codemirror/state';
import { EditorView, lineNumbers } from '@codemirror/view';
import {
  markdownTableEditor,
  markdownTableSelectionState,
  markdownTableSelectionTsv,
  pasteMarkdownTableText,
  runMarkdownTableAction,
  type MarkdownTableEditorConfig,
} from './markdown-editor.tables';

const phrases: MarkdownTableEditorConfig['phrases'] = {
  table: 'Table',
  row: 'Row',
  column: 'Column',
  range: 'Selected cells',
  menu: 'Table menu',
  addRow: 'Add row',
  addColumn: 'Add column',
  moveRow: 'Move row',
  moveColumn: 'Move column',
  insertBefore: 'Insert before',
  insertAfter: 'Insert after',
  duplicate: 'Duplicate',
  clear: 'Clear',
  copy: 'Copy',
  cut: 'Cut',
  delete: 'Delete',
  moveBefore: 'Move before',
  moveAfter: 'Move after',
  sortAscending: 'Sort ascending',
  sortDescending: 'Sort descending',
  alignLeft: 'Align left',
  alignCenter: 'Align center',
  alignRight: 'Align right',
  format: 'Format table',
  deleteTable: 'Delete table',
  clipboardFailed: 'Clipboard unavailable',
};

const config: MarkdownTableEditorConfig = { locale: 'en', phrases };
const VALID_TABLE = '| Name | Value |\n| --- | ---: |\n| A | 2 |\n| B | 10 |';
const originalScrollIntoView = Reflect.get(HTMLElement.prototype, 'scrollIntoView') as
  HTMLElement['scrollIntoView'] | undefined;

describe('Markdown table editor extension', () => {
  const views: EditorView[] = [];

  afterEach(() => {
    views.splice(0).forEach((view) => view.destroy());
    document.body.replaceChildren();
    if (originalScrollIntoView === undefined) {
      Reflect.deleteProperty(HTMLElement.prototype, 'scrollIntoView');
    } else {
      Object.defineProperty(HTMLElement.prototype, 'scrollIntoView', {
        configurable: true,
        value: originalScrollIntoView,
      });
    }
  });

  it('renders only valid Lezer Table nodes as an accessible, normalized responsive grid', () => {
    const view = createView(
      '| A | B | C |\n| --- | --- | --- |\n| one |\n| two | three | extra |\n\n| malformed |\n| nope |',
      views,
    );

    const table = view.dom.querySelector<HTMLElement>('[role="table"]');
    expect(table?.getAttribute('aria-label')).toBe('Table');
    expect(table?.querySelectorAll('[role="row"]')).toHaveLength(3);
    expect(table?.querySelectorAll('[role="columnheader"]')).toHaveLength(3);
    const rows = table?.querySelectorAll<HTMLElement>('[role="row"]') ?? [];
    expect(
      [...rows].map((row) => row.querySelectorAll('[role="cell"], [role="columnheader"]').length),
    ).toEqual([3, 3, 3]);
    expect(getComputedStyle(table!).display).toBe('block');
    expect(getComputedStyle(rows[0]!).display).toBe('grid');
    expect(view.dom.querySelector('.cm-markdown-table-delimiter')).toBeNull();
    expect(getComputedStyle(cell(view, 1, 0)).display).toBe('block');
    expect(view.dom.querySelectorAll('.cm-markdown-table-editor')).toHaveLength(1);
    expect(view.state.doc.toString()).toContain('| malformed |\n| nope |');
  });

  it('keeps only semantic cells in each visible grid row', () => {
    const view = createView(VALID_TABLE, views);
    const rows = [
      ...view.dom.querySelectorAll<HTMLElement>(
        '.cm-markdown-table-row:not(.cm-markdown-table-delimiter)',
      ),
    ];

    for (const row of rows) {
      const flowChildren = [...row.childNodes].filter((node) => {
        if (node instanceof HTMLElement) {
          if (node.matches('[data-table-cell="true"]')) {
            return false;
          }
          const style = getComputedStyle(node);
          return style.display !== 'none' && style.position !== 'absolute';
        }
        return (node.textContent?.length ?? 0) > 0;
      });

      expect(flowChildren).toEqual([]);
      expect(row.querySelectorAll(':scope > [data-table-cell="true"]')).toHaveLength(2);
    }
  });

  it('uses a full-width editor-native grid with stable rows and quiet edge controls', () => {
    const view = createView('| H | V |\n| --- | --- |\n| filled |  |\n|  | value |', views);
    const table = view.dom.querySelector<HTMLElement>('.cm-markdown-table-editor')!;
    const populatedCell = cell(view, 1, 0);
    const emptyCell = cell(view, 1, 1);
    const addRow = button(view, 'Add row');

    expect(getComputedStyle(table).backgroundColor).toBe('rgba(0, 0, 0, 0)');
    expect(getComputedStyle(table).borderTopWidth).toBe('0px');
    expect(getComputedStyle(table).borderRadius).toBe('0px');
    expect(getComputedStyle(table).boxShadow).toBe('none');
    expect(getComputedStyle(table).width).toBe('100%');
    expect(getComputedStyle(table).maxWidth).toBe('100%');
    expect(getComputedStyle(table).minWidth).toBe('0');
    expect(
      getComputedStyle(table.querySelector<HTMLElement>('.cm-markdown-table-row')!).padding,
    ).toBe('0px');
    expect(getComputedStyle(populatedCell).minHeight).toBe('2.5rem');
    expect(getComputedStyle(emptyCell).minHeight).toBe('2.5rem');
    expect(getComputedStyle(populatedCell).minWidth).toBe('0');
    expect(getComputedStyle(addRow).backgroundColor).toBe('rgba(0, 0, 0, 0)');
    expect(getComputedStyle(addRow).borderTopWidth).toBe('0px');
  });

  it('enters and edits an authored empty cell without requesting a scroll', () => {
    const view = createView('| H | V |\n| --- | --- |\n|  | value |', views);
    const emptyCell = cell(view, 1, 0);
    const transactions: { readonly docChanged: boolean; readonly scrollIntoView: boolean }[] = [];
    const listener = EditorView.updateListener.of((update) => {
      transactions.push(
        ...update.transactions.map((transaction) => ({
          docChanged: transaction.docChanged,
          scrollIntoView: transaction.scrollIntoView,
        })),
      );
    });
    view.dispatch({ effects: StateEffect.appendConfig.of(listener) });

    pointer(emptyCell, 'pointerdown', { pointerType: 'mouse' });
    pointer(emptyCell, 'pointerup', { pointerType: 'mouse' });

    expect(cell(view, 1, 0).classList).toContain('cm-markdown-table-cell-active');
    expect(cell(view, 1, 0).dataset['activeCell']).toBe('true');

    view.dispatch(view.state.replaceSelection('typed'));

    expect(view.state.doc.toString()).toBe('| H | V |\n| --- | --- |\n| typed | value |');
    expect(transactions.some((transaction) => transaction.scrollIntoView)).toBe(false);
  });

  it('keeps browser typing in a populated cell visible without scrolling the owning page', () => {
    const view = createView('| H | V |\n| --- | --- |\n| value | other |', views);
    const position = view.state.doc.toString().indexOf('value') + 2;
    const transactions: { readonly scrollIntoView: boolean }[] = [];
    view.dispatch({
      effects: StateEffect.appendConfig.of(
        EditorView.updateListener.of((update) => {
          transactions.push(
            ...update.transactions.map((transaction) => ({
              scrollIntoView: transaction.scrollIntoView,
            })),
          );
        }),
      ),
    });
    setCursor(view, position);

    view.dispatch({
      changes: { from: position, insert: 'x' },
      selection: EditorSelection.cursor(position + 1),
      scrollIntoView: true,
      userEvent: 'input.type',
    });

    const activeCell = cell(view, 1, 0);
    expect(view.state.doc.toString()).toContain('| vaxlue | other |');
    expect(transactions.at(-1)?.scrollIntoView).toBe(false);
    expect(activeCell.classList).toContain('cm-markdown-table-cell-active');
    expect(view.contentDOM.querySelector('.cm-markdown-table-caret')).toBeNull();
  });

  it('keeps repeated browser-style input in the same header without an inline caret widget', () => {
    const source = '|  | V |\n| --- | --- |\n| value | other |';
    const view = createView(source, views);
    const emptyHeader = cell(view, 0, 0);
    pointer(emptyHeader, 'pointerdown', { pointerType: 'mouse' });
    pointer(emptyHeader, 'pointerup', { pointerType: 'mouse' });

    for (const character of ['A', 'B', 'C']) {
      view.dispatch(view.state.replaceSelection(character), {
        annotations: Transaction.userEvent.of('input.type'),
      });
    }

    const activeCell = cell(view, 0, 0);

    expect(view.state.doc.toString()).toBe('| ABC | V |\n| --- | --- |\n| value | other |');
    expect(activeCell.classList).toContain('cm-markdown-table-cell-active');
    expect(activeCell.textContent).toBe('ABC');
    expect(view.state.selection.main.assoc).toBe(-1);
    expect(view.dom.classList).toContain('cm-markdown-table-cursor-owned');
    expect(view.dom.querySelector('.cm-markdown-table-cursor-layer')).not.toBeNull();
    expect(view.contentDOM.querySelector('.cm-markdown-table-caret')).toBeNull();
  });

  it('keeps the empty-cell source cursor mapped to authored DOM after clearing the cell', () => {
    const source = '| H | V |\n| --- | --- |\n| value | other |';
    const view = createView(source, views);
    const from = source.indexOf('value');
    const to = from + 'value'.length;
    setCursor(view, to);

    view.dispatch({
      changes: { from, to, insert: '' },
      selection: EditorSelection.cursor(from),
      userEvent: 'delete.backward',
    });

    const activeCell = cell(view, 1, 0);
    const authoredWhitespace = activeCell.firstChild;

    expect(activeCell.dataset['emptyCell']).toBe('true');
    expect(activeCell.classList).toContain('cm-markdown-table-cell-active');
    expect(view.state.selection.main.head).toBe(Number(activeCell.dataset['cellFrom']));
    expect(authoredWhitespace).not.toBeNull();
    expect(view.posAtDOM(authoredWhitespace!, 0)).toBe(from);
    expect(view.contentDOM.querySelector('.cm-markdown-table-caret')).toBeNull();
  });

  it('preserves a protected blank terminator and moves following prose outside the table', () => {
    const source = `${VALID_TABLE}\n`;
    const view = createView(source, views);
    const terminator = view.state.doc.length;

    view.dispatch({
      changes: { from: terminator - 1, to: terminator, insert: '' },
      selection: EditorSelection.cursor(terminator - 1),
      userEvent: 'delete.backward',
    });
    expect(view.state.doc.toString()).toBe(source);

    view.dispatch({
      changes: { from: terminator, insert: 'after table' },
      selection: EditorSelection.cursor(terminator + 'after table'.length),
      scrollIntoView: true,
      userEvent: 'input.type',
    });

    expect(view.state.doc.toString()).toBe(`${VALID_TABLE}\n\nafter table`);
    expect(view.state.selection.main.head).toBe(view.state.doc.length);
    expect(view.dom.querySelectorAll('.cm-markdown-table-editor')).toHaveLength(1);
    expect(view.dom.querySelector('[role="table"]')?.textContent).not.toContain('after table');
    expect(undo(view)).toBe(true);
    expect(view.state.doc.toString()).toBe(source);
  });

  it('adds a final blank terminator when a table is inserted at document end', () => {
    const view = createView('', views);

    view.dispatch({
      changes: { from: 0, insert: VALID_TABLE },
      selection: EditorSelection.cursor(VALID_TABLE.length),
      userEvent: 'input',
    });

    expect(view.state.doc.toString()).toBe(`${VALID_TABLE}\n`);
    expect(view.state.selection.main.head).toBe(VALID_TABLE.length + 1);
    expect(undo(view)).toBe(true);
    expect(view.state.doc.toString()).toBe('');
  });

  it('does not allow following prose to consume the protected table separator', () => {
    const source = `${VALID_TABLE}\n\nfollowing prose`;
    const view = createView(source, views);
    const secondSeparatorBreak = VALID_TABLE.length + 1;

    view.dispatch({
      changes: {
        from: secondSeparatorBreak,
        to: secondSeparatorBreak + 1,
        insert: '',
      },
      selection: EditorSelection.cursor(secondSeparatorBreak),
      userEvent: 'delete.backward',
    });

    expect(view.state.doc.toString()).toBe(source);
  });

  it('keeps the following source line outside the table wrapper', () => {
    const view = createView(`${VALID_TABLE}\n\nafter table`, views);
    const table = view.dom.querySelector<HTMLElement>('.cm-markdown-table-editor')!;
    const blankLine = table.nextElementSibling;
    const followingLine = blankLine?.nextElementSibling;

    expect(table.querySelectorAll(':scope > .cm-markdown-table-row')).toHaveLength(3);
    expect(blankLine?.classList).toContain('cm-line');
    expect(blankLine?.textContent).toBe('');
    expect(followingLine?.classList).toContain('cm-line');
    expect(followingLine?.textContent).toBe('after table');
    expect(getComputedStyle(table).marginTop).toBe('0px');
    expect(getComputedStyle(table).marginBottom).toBe('0px');
  });

  it('maps cells from the Lezer node start inside Markdown containers', () => {
    const source = '> | H | V |\n> | --- | --- |\n> | A | B |';
    const view = createView(source, views);

    expect(cell(view, 0, 0).textContent).toBe('H');
    setCursor(view, source.indexOf('A') + 1);
    expect(pasteMarkdownTableText(view, '1')).toBe(true);
    expect(view.state.doc.toString()).toBe('> | H | V |\n> | --- | --- |\n> | A1 | B |');
  });

  it('keeps authored markup as editable text', () => {
    const view = createView('| Value |\n| --- |\n| <img src=x onerror="alert(1)"> |', views);
    const valueCell = cell(view, 1, 0);

    expect(valueCell.textContent).toContain('<img');
    expect(valueCell.querySelector('img:not(.cm-widgetBuffer)')).toBeNull();
  });

  it('starts a rectangular selection only after an LMB drag crosses into another cell', () => {
    const view = createView(VALID_TABLE, views);
    const start = cell(view, 1, 0);
    const end = cell(view, 2, 1);

    const down = pointer(start, 'pointerdown', { pointerType: 'mouse' });
    pointer(start, 'pointerup', { pointerType: 'mouse' });
    expect(down.defaultPrevented).toBe(false);
    expect(view.state.field(markdownTableSelectionState).anchor).toBeNull();

    pointer(start, 'pointerdown', { pointerType: 'mouse' });
    pointer(end, 'pointermove', { pointerType: 'mouse' });
    pointer(end, 'pointerup', { pointerType: 'mouse' });

    expect(view.state.field(markdownTableSelectionState)).toEqual({
      tableFrom: 0,
      anchor: { row: 1, column: 0 },
      head: { row: 2, column: 1 },
    });
    expect(view.dom.querySelectorAll('.cm-markdown-table-cell-selected')).toHaveLength(4);
    expect(view.dom.querySelectorAll('.cm-markdown-table-selection-top')).toHaveLength(2);
    expect(view.dom.querySelectorAll('.cm-markdown-table-selection-bottom')).toHaveLength(2);
  });

  it('does not change cell border geometry while drawing a rectangular selection', () => {
    const view = createView(VALID_TABLE, views);
    const start = cell(view, 1, 0);
    const end = cell(view, 2, 1);
    const before = {
      start: getComputedStyle(start).borderInlineStartWidth,
      end: getComputedStyle(end).borderInlineEndWidth,
      bottom: getComputedStyle(end).borderBottomWidth,
    };

    const up = selectCellsWithPointer(view, [1, 0], [2, 1]);

    expect(up.defaultPrevented).toBe(true);
    expect(getComputedStyle(start).borderInlineStartWidth).toBe(before.start);
    expect(getComputedStyle(end).borderInlineEndWidth).toBe(before.end);
    expect(getComputedStyle(end).borderBottomWidth).toBe(before.bottom);
  });

  it('selects right-to-left and clears the native browser selection after crossing cells', () => {
    const view = createView(VALID_TABLE, views);
    const start = cell(view, 2, 1);
    const end = cell(view, 1, 0);
    const startPosition = Number(start.dataset['cellFrom']);
    const selection = document.getSelection()!;
    const removeAllRanges = jest.spyOn(selection, 'removeAllRanges');

    pointer(start, 'pointerdown', { pointerType: 'mouse' });
    const move = pointer(end, 'pointermove', { pointerType: 'mouse' });
    view.dispatch({
      selection: EditorSelection.range(0, view.state.doc.length),
      userEvent: 'select.pointer',
    });
    pointer(cell(view, 1, 0), 'pointerup', { pointerType: 'mouse' });

    expect(move.defaultPrevented).toBe(true);
    expect(removeAllRanges).toHaveBeenCalled();
    expect(view.state.selection.main).toEqual(EditorSelection.cursor(startPosition));
    expect(view.state.field(markdownTableSelectionState)).toEqual({
      tableFrom: 0,
      anchor: { row: 2, column: 1 },
      head: { row: 1, column: 0 },
    });
  });

  it('resolves a crossed cell from pointer coordinates when the original cell keeps capture', () => {
    const view = createView(VALID_TABLE, views);
    const start = cell(view, 1, 0);
    const end = cell(view, 2, 1);
    const originalElementFromPoint = document.elementFromPoint;
    Object.defineProperty(document, 'elementFromPoint', {
      configurable: true,
      value: (): Element => end,
    });

    try {
      pointer(start, 'pointerdown', { pointerType: 'mouse' });
      pointer(start, 'pointermove', { pointerType: 'mouse', clientX: 50, clientY: 50 });
      pointer(start, 'pointerup', { pointerType: 'mouse', clientX: 50, clientY: 50 });
    } finally {
      Object.defineProperty(document, 'elementFromPoint', {
        configurable: true,
        value: originalElementFromPoint,
      });
    }

    expect(view.state.field(markdownTableSelectionState).head).toEqual({ row: 2, column: 1 });
  });

  it('extends a range with Shift and clears it with Escape or an outside click', () => {
    const view = createView(`${VALID_TABLE}\n\noutside`, views);
    selectCells(view, [1, 0], [1, 1]);

    pointer(cell(view, 2, 1), 'pointerdown', { pointerType: 'mouse', shiftKey: true });
    expect(view.state.field(markdownTableSelectionState).head).toEqual({ row: 2, column: 1 });

    key(view, 'Escape');
    expect(view.state.field(markdownTableSelectionState).anchor).toBeNull();

    selectCells(view, [1, 0], [2, 0]);
    pointer(document.body, 'pointerdown', { pointerType: 'mouse' });
    expect(view.state.field(markdownTableSelectionState).anchor).toBeNull();
  });

  it('adaptively handles Delete and Backspace in one undoable transaction', () => {
    const view = createView(VALID_TABLE, views);
    const original = view.state.doc.toString();

    selectCells(view, [1, 0], [2, 0]);
    key(view, 'Delete');
    expect(view.state.doc.toString()).toBe('| Name | Value |\n| --- | ---: |\n|  | 2 |\n|  | 10 |');
    expect(undo(view)).toBe(true);
    expect(view.state.doc.toString()).toBe(original);

    selectCells(view, [1, 0], [1, 1]);
    key(view, 'Backspace');
    expect(view.state.doc.toString()).toBe('| Name | Value |\n| --- | ---: |\n| B | 10 |');
    expect(undo(view)).toBe(true);

    selectCells(view, [0, 0], [2, 0]);
    key(view, 'Delete');
    expect(view.state.doc.toString()).toBe('| Value |\n| ---: |\n| 2 |\n| 10 |');
    expect(undo(view)).toBe(true);

    selectCells(view, [0, 0], [2, 1]);
    key(view, 'Delete');
    expect(view.state.doc.toString()).toBe('');
    expect(undo(view)).toBe(true);
    expect(view.state.doc.toString()).toBe(original);
  });

  it('promotes the following row when a fully selected header is deleted', () => {
    const view = createView(VALID_TABLE, views);

    selectCells(view, [0, 0], [0, 1]);
    key(view, 'Delete');

    expect(view.state.doc.toString()).toBe('| A | 2 |\n| --- | ---: |\n| B | 10 |');
  });

  it('opens an accessible tooltip menu by right click and keyboard', () => {
    const view = createView(VALID_TABLE, views);
    contextMenu(cell(view, 1, 0));

    const menu = requiredMenu(view);
    expect(menu.getAttribute('aria-label')).toBe('Table menu');
    expect(menu.querySelector<HTMLButtonElement>('[aria-label^="Insert before"]')).not.toBeNull();
    expect(menu.querySelector<HTMLButtonElement>('[aria-label="Delete table"]')).not.toBeNull();

    const first = menu.querySelector<HTMLButtonElement>('[role="menuitem"]')!;
    let bubbledEscape = false;
    view.dom.addEventListener('keydown', (event) => {
      if (event.key === 'Escape') {
        bubbledEscape = true;
      }
    });
    first.focus();
    key(first, 'ArrowDown');
    expect(document.activeElement).not.toBe(first);
    key(document.activeElement as HTMLElement, 'Escape');
    expect(view.dom.querySelector('[role="menu"]')).toBeNull();
    expect(bubbledEscape).toBe(false);

    setCursor(view, VALID_TABLE.indexOf('10'));
    key(view, 'F10', { shiftKey: true });
    expect(requiredMenu(view)).not.toBeNull();
  });

  it.each(['Enter', ' '] as const)('activates context-menu items with %s', (keyValue) => {
    const view = createView(VALID_TABLE, views);
    contextMenu(cell(view, 1, 0));
    const first = requiredMenu(view).querySelector<HTMLButtonElement>('[role="menuitem"]')!;

    first.focus();
    key(first, keyValue);

    expect(view.state.doc.toString().split('\n')).toHaveLength(5);
    expect(view.dom.querySelector('[role="menu"]')).toBeNull();
    expect(undo(view)).toBe(true);
    expect(view.state.doc.toString()).toBe(VALID_TABLE);
  });

  it('keeps the menu open and announces a clipboard failure', () => {
    const view = createView(VALID_TABLE, views);
    selectCells(view, [1, 0], [2, 1]);
    contextMenu(cell(view, 1, 0));
    const menu = requiredMenu(view);

    menu.querySelector<HTMLButtonElement>('[aria-label="Copy"]')?.click();

    expect(menu.querySelector('[role="status"]')?.textContent).toBe('Clipboard unavailable');
    expect(view.dom.querySelector('[role="menu"]')).toBe(menu);
  });

  it('shows edge add controls without adding them to table geometry', () => {
    const view = createView(VALID_TABLE, views);
    const table = view.dom.querySelector<HTMLElement>('.cm-markdown-table-editor')!;
    const addRow = button(view, 'Add row');
    const addColumn = button(view, 'Add column');
    const original = view.state.doc.toString();
    const transactions: { readonly docChanged: boolean; readonly scrollIntoView: boolean }[] = [];
    view.dispatch({
      effects: StateEffect.appendConfig.of(
        EditorView.updateListener.of((update) => {
          transactions.push(
            ...update.transactions.map((transaction) => ({
              docChanged: transaction.docChanged,
              scrollIntoView: transaction.scrollIntoView,
            })),
          );
        }),
      ),
    });

    expect(addRow.parentElement?.closest('[role="cell"], [role="columnheader"]')).toBeNull();
    expect(addColumn.parentElement?.closest('[role="cell"], [role="columnheader"]')).toBeNull();
    expect(table.querySelectorAll('[role="columnheader"]')).toHaveLength(2);
    expect(pointer(addRow, 'pointerdown', { pointerType: 'mouse' }).defaultPrevented).toBe(true);

    addRow.click();
    expect(view.state.doc.toString().split('\n')).toHaveLength(5);
    expect(
      transactions.filter((transaction) => transaction.docChanged).at(-1)?.scrollIntoView,
    ).toBe(false);
    expect(undo(view)).toBe(true);
    expect(view.state.doc.toString()).toBe(original);
    transactions.length = 0;

    button(view, 'Add column').click();
    expect(view.state.doc.toString()).toContain('| Name | Value |  |');
    expect(view.dom.querySelectorAll('[role="columnheader"]')).toHaveLength(3);
    expect(
      [...view.dom.querySelectorAll<HTMLElement>('[role="row"]')].map(
        (row) => row.querySelectorAll('[data-table-cell="true"]').length,
      ),
    ).toEqual([3, 3, 3]);
    expect(transactions.filter((transaction) => transaction.docChanged)).toEqual([
      { docChanged: true, scrollIntoView: false },
    ]);
  });

  it('positions every row handle against its own row without affecting cell geometry', () => {
    const view = createView(VALID_TABLE, views);
    const table = view.dom.querySelector<HTMLElement>('.cm-markdown-table-editor')!;
    const handles = [...table.querySelectorAll<HTMLElement>('.cm-markdown-table-row-handle')];

    expect(handles.map((handle) => getComputedStyle(handle).top)).toEqual(['50%', '50%', '50%']);
    expect(handles.map((handle) => getComputedStyle(handle).left)).toEqual([
      '-0.25rem',
      '-0.25rem',
      '-0.25rem',
    ]);
    expect(handles.every((handle) => handle.closest('[data-table-cell]') === null)).toBe(true);
    expect(
      handles.every((handle) => handle.parentElement?.classList.contains('cm-markdown-table-row')),
    ).toBe(true);

    const emptyView = createView('| H | V |\n| --- | --- |\n|  | value |', views);
    expect(button(emptyView, 'Move row 2').closest('[data-table-cell]')).toBeNull();
  });

  it('positions every column handle at its own grid boundary', () => {
    const view = createView('| A | B | C |\n| --- | --- | --- |\n| 1 | 2 | 3 |', views);
    const handles = [
      ...view.dom.querySelectorAll<HTMLButtonElement>('.cm-markdown-table-column-handle'),
    ];

    expect(handles.map((handle) => handle.style.insetInlineStart)).toEqual([
      '0%',
      '33.33333333333333%',
      '66.66666666666666%',
    ]);
    expect(new Set(handles.map((handle) => handle.style.insetInlineStart)).size).toBe(3);
  });

  it.each(['mouse', 'touch'] as const)(
    'moves rows with one Pointer Events transaction for %s',
    (pointerType) => {
      const view = createView(VALID_TABLE, views);
      const source = view.state.doc.toString();
      const first = button(view, 'Move row 2');
      const second = button(view, 'Move row 3');
      mockBounds(second, { left: 0, top: 100, width: 20, height: 20 });

      pointer(first, 'pointerdown', { pointerType, clientY: 5 });
      expect(first.classList).toContain('cm-markdown-table-drag-source');
      expect(first.getAttribute('aria-grabbed')).toBe('true');
      expect(cell(view, 1, 0).classList).toContain('cm-markdown-table-drag-source-cell');
      pointer(second, 'pointermove', { pointerType, clientY: 119 });
      expect(cell(view, 2, 0).closest<HTMLElement>('.cm-markdown-table-row')?.classList).toContain(
        'cm-markdown-table-drop-after-row',
      );
      pointer(second, 'pointerup', { pointerType, clientY: 119 });

      expect(view.state.doc.toString()).toContain('| B | 10 |\n| A | 2 |');
      expect(undo(view)).toBe(true);
      expect(view.state.doc.toString()).toBe(source);
    },
  );

  it('moves the header and columns with pointer drop indicators', () => {
    const view = createView('| A | B | C |\n| --- | --- | --- |\n| 1 | 2 | 3 |', views);
    const lastColumn = button(view, 'Move column 3');
    const firstColumn = button(view, 'Move column 1');
    mockBounds(firstColumn, { left: 100, top: 0, width: 20, height: 20 });

    pointer(lastColumn, 'pointerdown', { pointerType: 'mouse', clientX: 210 });
    pointer(firstColumn, 'pointermove', { pointerType: 'mouse', clientX: 101 });
    expect(firstColumn.classList).toContain('cm-markdown-table-drop-before');
    pointer(firstColumn, 'pointerup', { pointerType: 'mouse', clientX: 101 });
    expect(view.state.doc.toString()).toBe('| C | A | B |\n| --- | --- | --- |\n| 3 | 1 | 2 |');

    const header = button(view, 'Move row 1');
    const body = button(view, 'Move row 2');
    mockBounds(body, { left: 0, top: 50, width: 20, height: 20 });
    pointer(header, 'pointerdown', { pointerType: 'mouse', clientY: 5 });
    pointer(body, 'pointermove', { pointerType: 'mouse', clientY: 69 });
    pointer(body, 'pointerup', { pointerType: 'mouse', clientY: 69 });
    expect(view.state.doc.toString()).toBe('| 3 | 1 | 2 |\n| --- | --- | --- |\n| C | A | B |');
  });

  it('copies, cuts, and pastes from the top-left selected cell', () => {
    const view = createView(VALID_TABLE, views);
    selectCells(view, [0, 0], [2, 0]);

    expect(markdownTableSelectionTsv(view)).toBe('Name\nA\nB');

    const writes: Record<string, string> = {};
    const event = new Event('cut', { bubbles: true, cancelable: true });
    Object.defineProperty(event, 'clipboardData', {
      value: {
        setData: (format: string, value: string): void => {
          writes[format] = value;
        },
      },
    });
    view.contentDOM.dispatchEvent(event);
    expect(writes['text/plain']).toBe('Name\nA\nB');
    expect(view.state.doc.toString()).toBe('| Value |\n| ---: |\n| 2 |\n| 10 |');

    expect(undo(view)).toBe(true);
    selectCells(view, [1, 0], [2, 1]);
    expect(pasteMarkdownTableText(view, 'x\ty')).toBe(true);
    expect(view.state.doc.toString()).toContain('| x | y |');
  });

  it('keeps navigation, hard breaks, escaped pipes, and separator protection', () => {
    const view = createView('| H |\n| --- |\n| A |', views);
    setCursor(view, view.state.doc.toString().indexOf('A') + 1);

    key(view, 'Tab');
    expect(view.state.doc.toString().split('\n')).toHaveLength(4);
    key(view, 'Enter', { shiftKey: true });
    expect(view.state.doc.toString()).toContain('<br>');
    key(view, '|');
    expect(view.state.doc.toString()).toContain('\\|');

    const delimiterPosition = view.state.doc.toString().indexOf('| --- |');
    setCursor(view, delimiterPosition + 1);
    const before = view.state.doc.toString();
    key(view, 'Backspace');
    expect(view.state.doc.toString()).toBe(before);
  });

  it('rejects typing before the first header cell while keeping cell content editable', () => {
    const view = createView('| H | V |\n| --- | --- |\n| A | B |', views);
    const original = view.state.doc.toString();

    view.dispatch({ changes: { from: 0, insert: 'broken' } });
    expect(view.state.doc.toString()).toBe(original);

    const header = cell(view, 0, 0);
    const position = Number(header.dataset['cellFrom']);
    view.dispatch({ selection: EditorSelection.cursor(position) });
    view.dispatch(view.state.replaceSelection('safe'));
    expect(view.state.doc.toString()).toBe('| safeH | V |\n| --- | --- |\n| A | B |');
  });

  it('moves predictably across cell boundaries and vertically in the same column', () => {
    const source = '| ABC | D |\n| --- | --- |\n| xy | zzzz |';
    const view = createView(source, views);
    const headerStart = source.indexOf('ABC');
    const secondHeaderStart = source.indexOf('D');
    const bodyStart = source.indexOf('xy');

    setCursor(view, headerStart + 3);
    expect(key(view, 'ArrowRight').defaultPrevented).toBe(true);
    expect(view.state.selection.main.head).toBe(secondHeaderStart);

    expect(key(view, 'ArrowLeft').defaultPrevented).toBe(true);
    expect(view.state.selection.main.head).toBe(headerStart + 3);

    setCursor(view, headerStart + 1);
    expect(key(view, 'ArrowDown').defaultPrevented).toBe(true);
    expect(view.state.selection.main.head).toBe(bodyStart + 1);

    expect(key(view, 'ArrowUp').defaultPrevented).toBe(true);
    expect(view.state.selection.main.head).toBe(headerStart + 1);

    setCursor(view, headerStart + 1);
    expect(key(view, 'ArrowRight').defaultPrevented).toBe(false);
    expect(view.state.selection.main.head).toBe(headerStart + 1);
  });

  it('keeps horizontal arrows inside the outer table edges', () => {
    const source = 'before\n\n| ABC | D |\n| --- | --- |\n| xy | zzzz |\n\nafter';
    const view = createView(source, views);
    const firstCellStart = source.indexOf('ABC');
    const lastCellEnd = source.indexOf('zzzz') + 'zzzz'.length;
    const scrollRenderedCell = jest.fn();
    Object.defineProperty(HTMLElement.prototype, 'scrollIntoView', {
      configurable: true,
      value: scrollRenderedCell,
    });

    setCursor(view, firstCellStart);
    expect(key(view, 'ArrowLeft').defaultPrevented).toBe(true);
    expect(view.state.selection.main.head).toBe(firstCellStart);

    setCursor(view, lastCellEnd);
    expect(key(view, 'ArrowRight').defaultPrevented).toBe(true);
    expect(view.state.selection.main.head).toBe(lastCellEnd);
    expect(scrollRenderedCell).not.toHaveBeenCalled();
  });

  it('does not trap vertical arrows at the outer table edges', () => {
    const source = 'before\n\n| ABC | D |\n| --- | --- |\n| xy | zzzz |\n\nafter';
    const view = createView(source, views);
    const firstRowPosition = source.indexOf('ABC') + 1;
    const lastRowPosition = source.indexOf('xy') + 1;

    setCursor(view, firstRowPosition);
    expect(key(view, 'ArrowUp').defaultPrevented).toBe(false);
    expect(view.state.selection.main.head).toBe(firstRowPosition);

    setCursor(view, lastRowPosition);
    expect(key(view, 'ArrowDown').defaultPrevented).toBe(false);
    expect(view.state.selection.main.head).toBe(lastRowPosition);
  });

  it('scrolls rendered target cells instead of hidden source geometry in both directions', () => {
    const source = '| ABC | D |\n| --- | --- |\n| xy | zzzz |';
    const view = createView(source, views);
    const previousCellEnd = source.indexOf('ABC') + 'ABC'.length;
    const currentCellStart = source.indexOf('D');
    const scrollRenderedCell = jest.fn();
    Object.defineProperty(HTMLElement.prototype, 'scrollIntoView', {
      configurable: true,
      value: scrollRenderedCell,
    });
    const scrollRequests: boolean[] = [];
    view.dispatch({
      effects: StateEffect.appendConfig.of(
        EditorView.updateListener.of((update) => {
          scrollRequests.push(
            ...update.transactions.map((transaction) => transaction.scrollIntoView),
          );
        }),
      ),
    });
    setCursor(view, currentCellStart);
    scrollRequests.splice(0);

    expect(key(view, 'ArrowLeft').defaultPrevented).toBe(true);

    expect(view.state.selection.main.head).toBe(previousCellEnd);
    expect(view.state.selection.main.assoc).toBe(-1);
    expect(scrollRequests).toEqual([false]);
    expect(scrollRenderedCell).toHaveBeenCalledWith({
      block: 'nearest',
      inline: 'nearest',
    });
    expect(scrollRenderedCell.mock.instances[0]).toBe(cell(view, 0, 0));

    expect(key(view, 'ArrowRight').defaultPrevented).toBe(true);

    expect(view.state.selection.main.head).toBe(currentCellStart);
    expect(scrollRequests).toEqual([false, false]);
    expect(scrollRenderedCell).toHaveBeenCalledTimes(2);
    expect(scrollRenderedCell.mock.instances[1]).toBe(cell(view, 0, 1));
  });

  it('scrolls rendered target cells instead of hidden source geometry vertically', () => {
    const source = '| ABC | D |\n| --- | --- |\n| xy | zzzz |';
    const view = createView(source, views);
    const headerPosition = source.indexOf('ABC') + 1;
    const bodyPosition = source.indexOf('xy') + 1;
    const scrollRenderedCell = jest.fn();
    Object.defineProperty(HTMLElement.prototype, 'scrollIntoView', {
      configurable: true,
      value: scrollRenderedCell,
    });
    const scrollRequests: boolean[] = [];
    view.dispatch({
      effects: StateEffect.appendConfig.of(
        EditorView.updateListener.of((update) => {
          scrollRequests.push(
            ...update.transactions.map((transaction) => transaction.scrollIntoView),
          );
        }),
      ),
    });
    setCursor(view, headerPosition);
    scrollRequests.splice(0);

    expect(key(view, 'ArrowDown').defaultPrevented).toBe(true);

    expect(view.state.selection.main.head).toBe(bodyPosition);
    expect(scrollRequests).toEqual([false]);
    expect(scrollRenderedCell).toHaveBeenCalledWith({
      block: 'nearest',
      inline: 'nearest',
    });
    expect(scrollRenderedCell.mock.instances[0]).toBe(cell(view, 1, 0));

    expect(key(view, 'ArrowUp').defaultPrevented).toBe(true);

    expect(view.state.selection.main.head).toBe(headerPosition);
    expect(scrollRequests).toEqual([false, false]);
    expect(scrollRenderedCell).toHaveBeenCalledTimes(2);
    expect(scrollRenderedCell.mock.instances[1]).toBe(cell(view, 0, 0));
  });

  it('enters the rendered table from the ordinary line above without scrolling source geometry', () => {
    const source = 'above\n\n| ABC | D |\n| --- | --- |\n| xy | zzzz |';
    const view = createView(source, views);
    const lineAbove = view.state.doc.line(2);
    const headerPosition = source.indexOf('ABC') + 1;
    const scrollRenderedCell = jest.fn();
    Object.defineProperty(HTMLElement.prototype, 'scrollIntoView', {
      configurable: true,
      value: scrollRenderedCell,
    });
    const scrollRequests: boolean[] = [];
    view.dispatch({
      effects: StateEffect.appendConfig.of(
        EditorView.updateListener.of((update) => {
          scrollRequests.push(
            ...update.transactions.map((transaction) => transaction.scrollIntoView),
          );
        }),
      ),
    });
    setCursor(view, lineAbove.from);
    jest.spyOn(view, 'moveVertically').mockReturnValue(EditorSelection.cursor(headerPosition));
    scrollRequests.splice(0);

    expect(key(view, 'ArrowDown').defaultPrevented).toBe(true);

    expect(view.state.selection.main.head).toBe(headerPosition);
    expect(scrollRequests).toEqual([false]);
    expect(scrollRenderedCell).toHaveBeenCalledWith({
      block: 'nearest',
      inline: 'nearest',
    });
    expect(scrollRenderedCell.mock.instances[0]).toBe(cell(view, 0, 0));
  });

  it('enters the rendered table without source scrolling after a vertical geometry jump', () => {
    const source = 'above\n\n| ABC | D |\n| --- | --- |\n| xy | zzzz |';
    const view = createView(source, views);
    const lineAbove = view.state.doc.line(2);
    const headerStart = source.indexOf('ABC');
    const bodyStart = source.indexOf('xy');
    const scrollRenderedCell = jest.fn();
    Object.defineProperty(HTMLElement.prototype, 'scrollIntoView', {
      configurable: true,
      value: scrollRenderedCell,
    });
    const scrollRequests: boolean[] = [];
    view.dispatch({
      effects: StateEffect.appendConfig.of(
        EditorView.updateListener.of((update) => {
          scrollRequests.push(
            ...update.transactions.map((transaction) => transaction.scrollIntoView),
          );
        }),
      ),
    });
    setCursor(view, lineAbove.from);
    jest.spyOn(view, 'moveVertically').mockReturnValue(EditorSelection.cursor(bodyStart));
    scrollRequests.splice(0);

    expect(key(view, 'ArrowDown').defaultPrevented).toBe(true);

    expect(view.state.selection.main.head).toBe(headerStart);
    expect(scrollRequests).toEqual([false]);
    expect(scrollRenderedCell).toHaveBeenCalledWith({
      block: 'nearest',
      inline: 'nearest',
    });
    expect(scrollRenderedCell.mock.instances[0]).toBe(cell(view, 0, 0));
  });

  it('uses the rendered adjacent row when a horizontal arrow crosses a row boundary', () => {
    const source = '| ABC | D |\n| --- | --- |\n| xy | zzzz |';
    const view = createView(source, views);
    const secondHeaderEnd = source.indexOf('D') + 'D'.length;
    const firstBodyStart = source.indexOf('xy');
    const scrollRenderedCell = jest.fn();
    Object.defineProperty(HTMLElement.prototype, 'scrollIntoView', {
      configurable: true,
      value: scrollRenderedCell,
    });

    setCursor(view, secondHeaderEnd);
    expect(key(view, 'ArrowRight').defaultPrevented).toBe(true);

    expect(view.state.selection.main.head).toBe(firstBodyStart);
    expect(scrollRenderedCell.mock.instances[0]).toBe(cell(view, 1, 0));

    setCursor(view, firstBodyStart);
    scrollRenderedCell.mockClear();
    expect(key(view, 'ArrowLeft').defaultPrevented).toBe(true);

    expect(view.state.selection.main.head).toBe(secondHeaderEnd);
    expect(scrollRenderedCell.mock.instances[0]).toBe(cell(view, 0, 1));
  });

  it('repairs a vertical geometry jump from ordinary text below a table', () => {
    const source = `${VALID_TABLE}\n\nbelow one\nbelow two\nbelow three`;
    const view = createView(source, views);
    const lastLine = view.state.doc.line(view.state.doc.lines);
    const previousLine = view.state.doc.line(lastLine.number - 1);
    setCursor(view, lastLine.to);
    jest
      .spyOn(view, 'moveVertically')
      .mockReturnValue(EditorSelection.cursor(source.indexOf('| B | 10 |')));

    expect(key(view, 'ArrowUp').defaultPrevented).toBe(true);
    expect(view.state.doc.lineAt(view.state.selection.main.head).number).toBe(previousLine.number);
    expect(view.state.selection.main.head).toBe(previousLine.to);
  });

  it('hides delimiter and continuation line numbers while preserving the first table number', () => {
    const source = `before\n${VALID_TABLE}\n\nafter`;
    const view = createView(source, views, true);
    const continuationMarkers = [
      ...view.dom.querySelectorAll<HTMLElement>('.cm-markdown-table-continuation-gutter'),
    ];
    const gutterElements = [...view.dom.querySelectorAll<HTMLElement>('.cm-gutterElement')];
    const headerBlock = view.lineBlockAt(source.indexOf('| Name'));
    const firstBodyBlock = view.lineBlockAt(source.indexOf('| A |'));

    expect(continuationMarkers.map((marker) => marker.textContent)).toEqual(['3', '5']);
    expect(
      continuationMarkers.every((marker) => getComputedStyle(marker).visibility === 'hidden'),
    ).toBe(true);
    expect(gutterElements.some((marker) => marker.textContent === '4')).toBe(false);
    expect(gutterElements.find((marker) => marker.textContent === '2')?.classList).not.toContain(
      'cm-markdown-table-continuation-gutter',
    );
    expect(view.dom.querySelectorAll('.cm-markdown-table-delimiter')).toHaveLength(0);
    const delimiter = view.dom.querySelector<HTMLElement>('.cm-markdown-table-delimiter-block');
    const delimiterLine = view.dom.querySelector<HTMLElement>(
      '.cm-line.cm-markdown-table-delimiter-line',
    );
    expect(delimiter).not.toBeNull();
    expect(getComputedStyle(delimiter!).height).toBe('0px');
    expect(getComputedStyle(delimiter!).lineHeight).toBe('0');
    expect(delimiterLine).not.toBeNull();
    expect(getComputedStyle(delimiterLine!).height).toBe('0px');
    expect(getComputedStyle(delimiterLine!).lineHeight).toBe('0');
    expect(getComputedStyle(delimiterLine!).padding).toBe('0px');
    expect(
      view.dom.querySelectorAll('.cm-markdown-table-editor > .cm-markdown-table-row'),
    ).toHaveLength(3);
    expect(firstBodyBlock.top).toBe(headerBlock.top + headerBlock.height);
  });

  it('keeps structural actions available for range-aware context commands', () => {
    const view = createView(VALID_TABLE, views);
    selectCells(view, [1, 1], [2, 1]);

    expect(runMarkdownTableAction(view, 'sortDescending')).toBe(true);
    expect(view.state.doc.toString()).toContain('| B | 10 |\n| A | 2 |');
    expect(runMarkdownTableAction(view, 'alignCenter')).toBe(true);
    expect(view.state.doc.toString()).toContain(':---:');
    expect(runMarkdownTableAction(view, 'format')).toBe(true);
    expect(view.state.doc.toString()).toMatch(/^\| .+ \|$/m);
  });
});

function createView(doc: string, views: EditorView[], withLineNumbers = false): EditorView {
  const parent = document.createElement('div');
  document.body.append(parent);
  const view = new EditorView({
    parent,
    state: EditorState.create({
      doc,
      extensions: [
        markdown({ base: markdownLanguage }),
        history(),
        ...(withLineNumbers ? [lineNumbers()] : []),
        markdownTableEditor(config),
      ],
    }),
  });
  views.push(view);
  return view;
}

function cell(view: EditorView, row: number, column: number): HTMLElement {
  const result = view.dom.querySelector<HTMLElement>(
    `[data-table-cell="true"][data-row="${row}"][data-column="${column}"]`,
  );
  if (result === null) {
    throw new Error(`Missing cell ${row}:${column}`);
  }
  return result;
}

function button(view: EditorView, label: string): HTMLButtonElement {
  const result = view.dom.querySelector<HTMLButtonElement>(`button[aria-label="${label}"]`);
  if (result === null) {
    throw new Error(`Missing button ${label}`);
  }
  return result;
}

function selectCells(
  view: EditorView,
  anchor: readonly [number, number],
  head: readonly [number, number],
): void {
  selectCellsWithPointer(view, anchor, head);
}

function selectCellsWithPointer(
  view: EditorView,
  anchor: readonly [number, number],
  head: readonly [number, number],
): MouseEvent {
  const start = cell(view, anchor[0], anchor[1]);
  pointer(start, 'pointerdown', { pointerType: 'mouse' });
  pointer(cell(view, head[0], head[1]), 'pointermove', { pointerType: 'mouse' });
  return pointer(cell(view, head[0], head[1]), 'pointerup', { pointerType: 'mouse' });
}

function pointer(
  target: HTMLElement,
  type: 'pointerdown' | 'pointermove' | 'pointerup',
  options: {
    pointerType: 'mouse' | 'touch';
    shiftKey?: boolean;
    clientX?: number;
    clientY?: number;
  },
): MouseEvent {
  const event = new MouseEvent(type, {
    bubbles: true,
    cancelable: true,
    shiftKey: options.shiftKey,
    clientX: options.clientX,
    clientY: options.clientY,
  });
  Object.defineProperty(event, 'pointerType', { value: options.pointerType });
  Object.defineProperty(event, 'pointerId', { value: 1 });
  target.dispatchEvent(event);
  return event;
}

function contextMenu(target: HTMLElement): void {
  target.dispatchEvent(new MouseEvent('contextmenu', { bubbles: true, cancelable: true }));
}

function requiredMenu(view: EditorView): HTMLElement {
  const menu = view.dom.querySelector<HTMLElement>('[role="menu"]');
  if (menu === null) {
    throw new Error('Missing table menu');
  }
  return menu;
}

function setCursor(view: EditorView, position: number): void {
  view.dispatch({ selection: { anchor: position } });
  view.focus();
}

function key(
  target: EditorView | HTMLElement,
  keyValue: string,
  options: { shiftKey?: boolean } = {},
): KeyboardEvent {
  const event = new KeyboardEvent('keydown', {
    key: keyValue,
    bubbles: true,
    cancelable: true,
    shiftKey: options.shiftKey,
  });
  (target instanceof EditorView ? target.contentDOM : target).dispatchEvent(event);
  return event;
}

function mockBounds(
  target: HTMLElement,
  bounds: {
    readonly left: number;
    readonly top: number;
    readonly width: number;
    readonly height: number;
  },
): void {
  Object.defineProperty(target, 'getBoundingClientRect', {
    value: () => ({
      ...bounds,
      right: bounds.left + bounds.width,
      bottom: bounds.top + bounds.height,
      x: bounds.left,
      y: bounds.top,
      toJSON: (): string => '',
    }),
  });
}
