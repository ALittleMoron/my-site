declare module '@toast-ui/editor' {
  export type EditorType = 'markdown' | 'wysiwyg';
  export type MarkdownPosition = [number, number];
  export type SelectionPosition = [MarkdownPosition, MarkdownPosition] | [number, number];

  export interface ToastUiEditorOptions {
    el: HTMLElement;
    autofocus?: boolean;
    height?: string;
    initialEditType?: EditorType;
    hideModeSwitch?: boolean;
    language?: string;
    previewStyle?: 'tab' | 'vertical';
    theme?: string;
    usageStatistics?: boolean;
    initialValue?: string;
    plugins?: unknown[];
    toolbarItems?: string[][];
    events?: {
      change?: () => void;
      keyup?: (editorType: EditorType, event: KeyboardEvent) => void;
    };
    hooks?: {
      addImageBlobHook?: (
        blob: Blob | File,
        callback: (url: string, altText?: string) => void,
      ) => void;
    };
  }

  export default class Editor {
    static setLanguage(code: string, data: Record<string, string>): void;

    constructor(options: ToastUiEditorOptions);

    getMarkdown(): string;

    getSelection(): SelectionPosition;

    insertText(text: string): void;

    setSelection(start: MarkdownPosition | number, end?: MarkdownPosition | number): void;

    setMarkdown(markdown: string, cursorToEnd?: boolean): void;

    destroy(): void;
  }
}

declare module '@toast-ui/editor/dist/i18n/ru-ru' {
  const language: Record<string, string>;

  export default language;
}
