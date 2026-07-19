declare module '@toast-ui/editor' {
  export interface ToastUiEditorOptions {
    el: HTMLElement;
    autofocus?: boolean;
    height?: string;
    initialEditType?: 'markdown' | 'wysiwyg';
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

    setMarkdown(markdown: string, cursorToEnd?: boolean): void;

    destroy(): void;
  }
}

declare module '@toast-ui/editor/dist/i18n/ru-ru' {
  const language: Record<string, string>;

  export default language;
}
