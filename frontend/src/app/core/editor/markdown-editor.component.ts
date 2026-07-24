import { DOCUMENT, isPlatformBrowser } from '@angular/common';
import {
  AfterViewInit,
  ChangeDetectionStrategy,
  Component,
  CSP_NONCE,
  DestroyRef,
  ElementRef,
  OnDestroy,
  PLATFORM_ID,
  ViewChild,
  computed,
  effect,
  inject,
  input,
  output,
  signal,
} from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import {
  closeBracketsKeymap,
  nextSnippetField,
  prevSnippetField,
  snippet,
} from '@codemirror/autocomplete';
import { defaultKeymap, historyKeymap, indentLess, indentMore } from '@codemirror/commands';
import { openSearchPanel, searchKeymap } from '@codemirror/search';
import {
  Compartment,
  EditorSelection,
  EditorState,
  Transaction,
  type Extension,
} from '@codemirror/state';
import { EditorView, keymap, type ViewUpdate } from '@codemirror/view';
import { LanguageCode } from '../i18n/i18n.model';
import { I18nService } from '../i18n/i18n.service';
import { TranslatePipe } from '../i18n/translate.pipe';
import { WikiLinkRendererService } from '../wiki-links/wiki-link-renderer.service';
import {
  MARKDOWN_EDITOR_COMMANDS,
  MARKDOWN_EDITOR_SHORTCUT_GROUPS,
  MarkdownEditorCommandDefinition,
  MarkdownEditorCommandId,
  MarkdownKeyboardEvent,
  MarkdownSelection,
  MarkdownTransactionResult,
  applyMarkdownCommandTransaction,
  autoCloseMarkdownFenceTransaction,
  continueMarkdownBlockTransaction,
  findMarkdownEditorCommand,
  formatMarkdownShortcut,
  indentMarkdownLinesTransaction,
} from './markdown-editor.commands';
import { EditorImageUploadService } from './editor-image-upload.service';
import {
  markdownEditorCspExtension,
  markdownEditorFoundationExtensions,
} from './markdown-editor.extensions';

type EditorMode = 'edit' | 'preview';
type UploadStatus = 'queued' | 'uploading' | 'error';

interface ImageUpload {
  id: number;
  file: File;
  anchor: number;
  status: UploadStatus;
}

interface ResolvedShortcutGroup {
  id: string;
  labelKey: string;
  commands: readonly MarkdownEditorCommandDefinition[];
}

let editorInstanceId = 0;

@Component({
  selector: 'app-markdown-editor',
  standalone: true,
  imports: [TranslatePipe],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './markdown-editor.component.html',
  styleUrl: './markdown-editor.component.scss',
})
export class MarkdownEditorComponent implements AfterViewInit, OnDestroy {
  private readonly imageUpload = inject(EditorImageUploadService);
  private readonly i18n = inject(I18nService);
  private readonly wikiLinkRenderer = inject(WikiLinkRendererService);
  private readonly destroyRef = inject(DestroyRef);
  private readonly document = inject(DOCUMENT);
  private readonly platformId = inject(PLATFORM_ID);
  private readonly cspNonce = inject(CSP_NONCE);
  private readonly contentAttributesCompartment = new Compartment();
  private readonly phrasesCompartment = new Compartment();
  private readonly instanceId = ++editorInstanceId;
  readonly sourcePanelId = `markdown-editor-source-${this.instanceId}`;
  readonly previewPanelId = `markdown-editor-preview-${this.instanceId}`;
  private editorView: EditorView | null = null;
  private syncingInput = false;
  private focusPending = false;
  private restoreEditorFocus = false;
  private savedScrollTop = 0;
  private nextUploadId = 0;

  @ViewChild('editorHost', { static: true }) private readonly editorHost!: ElementRef<HTMLElement>;
  @ViewChild('imageInput', { static: true })
  private readonly imageInput!: ElementRef<HTMLInputElement>;
  @ViewChild('previewTab', { static: true })
  private readonly previewTab!: ElementRef<HTMLButtonElement>;

  readonly value = input.required<string>();
  readonly language = input.required<LanguageCode>();
  readonly accessibleLabel = input.required<string>();
  readonly valueChange = output<string>();

  readonly mode = signal<EditorMode>('edit');
  readonly internalValue = signal('');
  readonly uploads = signal<readonly ImageUpload[]>([]);
  readonly uploading = computed(() =>
    this.uploads().some((upload) => upload.status === 'uploading'),
  );
  readonly uploadErrors = computed(() =>
    this.uploads().filter((upload) => upload.status === 'error'),
  );
  readonly previewHtml = computed(() =>
    this.wikiLinkRenderer.render(this.internalValue(), this.language()),
  );
  readonly previewEmpty = computed(() => this.internalValue().trim() === '');
  readonly shortcutGroups = resolveShortcutGroups();
  readonly shortcutModifierHintKey =
    this.editorPlatform() === 'mac'
      ? 'markdownEditor.shortcuts.modifierHintMac'
      : 'markdownEditor.shortcuts.modifierHintOther';
  readonly editTabId = `markdown-editor-edit-tab-${this.instanceId}`;
  readonly previewTabId = `markdown-editor-preview-tab-${this.instanceId}`;

  constructor() {
    effect(() => {
      const value = this.value();
      const view = this.editorView;
      if (view === null) {
        this.internalValue.set(value);
        return;
      }
      if (view.state.doc.toString() === value) {
        return;
      }

      this.syncingInput = true;
      view.dispatch({
        changes: { from: 0, to: view.state.doc.length, insert: value },
        annotations: Transaction.addToHistory.of(false),
      });
      this.internalValue.set(value);
      this.syncingInput = false;
    });
    effect(() => {
      const contentAttributes = this.editorContentAttributes();
      const phrases = this.searchPhrases();
      const view = this.editorView;
      if (view === null) {
        return;
      }
      view.dispatch({
        effects: [
          this.contentAttributesCompartment.reconfigure(
            EditorView.contentAttributes.of(contentAttributes),
          ),
          this.phrasesCompartment.reconfigure(EditorState.phrases.of(phrases)),
        ],
      });
    });
  }

  ngAfterViewInit(): void {
    if (!isPlatformBrowser(this.platformId)) {
      return;
    }

    this.editorView = new EditorView({
      parent: this.editorHost.nativeElement,
      state: EditorState.create({
        doc: this.value(),
        extensions: this.editorExtensions(),
      }),
    });
    this.internalValue.set(this.value());
    if (this.focusPending) {
      this.focusPending = false;
      this.editorView.focus();
    }
  }

  ngOnDestroy(): void {
    this.editorView?.destroy();
  }

  focus(): void {
    this.mode.set('edit');
    const view = this.editorView;
    if (view === null) {
      this.focusPending = true;
      return;
    }
    this.restoreScrollAndFocus(true);
  }

  selectMode(mode: EditorMode): void {
    if (mode === this.mode()) {
      return;
    }
    if (mode === 'preview') {
      this.savedScrollTop = this.editorView?.scrollDOM.scrollTop ?? 0;
      this.restoreEditorFocus = this.editorView?.hasFocus ?? false;
      this.mode.set('preview');
      if (this.restoreEditorFocus) {
        this.previewTab.nativeElement.focus();
      }
      return;
    }

    this.mode.set('edit');
    this.restoreScrollAndFocus(this.restoreEditorFocus);
    this.restoreEditorFocus = false;
  }

  onModeTabKeydown(event: KeyboardEvent): void {
    const target = event.currentTarget;
    if (!(target instanceof HTMLButtonElement)) {
      return;
    }
    const tablist = target.parentElement;
    if (tablist === null) {
      return;
    }
    const tabs = Array.from(tablist.querySelectorAll<HTMLButtonElement>('[role="tab"]'));
    const currentIndex = tabs.indexOf(target);
    const nextIndex = modeTabIndex(event.key, currentIndex, tabs.length);
    if (nextIndex === null) {
      return;
    }
    event.preventDefault();
    event.stopPropagation();
    tabs[nextIndex]?.focus();
  }

  onContainerKeydown(event: KeyboardEvent): void {
    if (this.consumeComposingEditorShortcut(event)) {
      return;
    }
    const command = findMarkdownEditorCommand(event, this.editorPlatform());
    if (command !== 'togglePreview') {
      return;
    }
    this.consumeKeyboardEvent(event);
    this.selectMode(this.mode() === 'edit' ? 'preview' : 'edit');
  }

  onImageInput(event: Event): void {
    const input = event.currentTarget;
    if (!(input instanceof HTMLInputElement)) {
      return;
    }
    this.queueImageUploads(Array.from(input.files ?? []), this.currentCursor());
    input.value = '';
  }

  retryUpload(id: number): void {
    this.uploads.update((uploads) =>
      uploads.map((upload) => (upload.id === id ? { ...upload, status: 'queued' } : upload)),
    );
    this.processNextUpload();
  }

  dismissUpload(id: number): void {
    this.uploads.update((uploads) => uploads.filter((upload) => upload.id !== id));
    this.processNextUpload();
  }

  shortcutParts(command: MarkdownEditorCommandDefinition): readonly string[] {
    return formatMarkdownShortcut(command, this.editorPlatform());
  }

  shortcutLabel(command: MarkdownEditorCommandDefinition): string {
    return this.shortcutParts(command)
      .map((part) => (part === '⌘' ? 'Command' : part))
      .join(' + ');
  }

  private editorExtensions(): readonly Extension[] {
    return [
      ...markdownEditorFoundationExtensions,
      markdownEditorCspExtension(this.cspNonce),
      this.phrasesCompartment.of(EditorState.phrases.of(this.searchPhrases())),
      this.contentAttributesCompartment.of(
        EditorView.contentAttributes.of(this.editorContentAttributes()),
      ),
      keymap.of([
        {
          key: 'Enter',
          run: (view) => this.applySmartEnter(view),
        },
        {
          key: 'Tab',
          run: (view) => nextSnippetField(view) || this.indentSelection(view, 'more'),
        },
        {
          key: 'Shift-Tab',
          run: (view) => prevSnippetField(view) || this.indentSelection(view, 'less'),
        },
        ...closeBracketsKeymap,
        ...defaultKeymap,
        ...historyKeymap,
        ...searchKeymap,
      ]),
      EditorView.domEventHandlers({
        keydown: (event, view) => this.handleEditorKeydown(event, view),
        keyup: (event, view) => this.handleEditorKeyup(event, view),
        paste: (event, view) => this.handlePaste(event, view),
        drop: (event, view) => this.handleDrop(event, view),
        dragover: (event) => this.handleDragOver(event),
      }),
      EditorView.updateListener.of((update) => this.handleEditorUpdate(update)),
    ];
  }

  private handleEditorUpdate(update: ViewUpdate): void {
    if (!update.changes.empty && this.uploads().length > 0) {
      this.uploads.update((uploads) =>
        uploads.map((upload) => ({
          ...upload,
          anchor: update.changes.mapPos(upload.anchor, 1),
        })),
      );
    }
    if (!update.docChanged || this.syncingInput) {
      return;
    }
    const value = update.state.doc.toString();
    this.internalValue.set(value);
    this.valueChange.emit(value);
  }

  private handleEditorKeydown(event: KeyboardEvent, view: EditorView): boolean {
    if (this.consumeComposingEditorShortcut(event)) {
      return true;
    }
    const command = findMarkdownEditorCommand(event, this.editorPlatform());
    if (command === null) {
      return false;
    }

    const handled = this.executeCommand(command, view);
    if (handled) {
      this.consumeKeyboardEvent(event);
    }
    return handled;
  }

  private handleEditorKeyup(event: KeyboardEvent, view: EditorView): boolean {
    if (event.isComposing || (event.key !== '`' && event.key !== '~')) {
      return false;
    }
    const result = autoCloseMarkdownFenceTransaction(
      view.state.doc.toString(),
      editorSelections(view),
      event.key,
    );
    if (result === null) {
      return false;
    }
    this.dispatchTransaction(view, result);
    return true;
  }

  private executeCommand(command: MarkdownEditorCommandId, view: EditorView): boolean {
    if (command === 'togglePreview') {
      this.selectMode('preview');
      return true;
    }
    if (command === 'search') {
      openSearchPanel(view);
      return true;
    }
    if (command === 'image') {
      this.imageInput.nativeElement.click();
      return true;
    }
    if (command === 'link' || command === 'table') {
      return this.applySnippet(command, view);
    }

    const result = applyMarkdownCommandTransaction(
      command,
      view.state.doc.toString(),
      editorSelections(view),
    );
    if (result === null) {
      return false;
    }
    this.dispatchTransaction(view, result);
    return true;
  }

  private applySnippet(command: 'link' | 'table', view: EditorView): boolean {
    if (view.state.selection.ranges.length !== 1) {
      const result = applyMarkdownCommandTransaction(
        command,
        view.state.doc.toString(),
        editorSelections(view),
      );
      if (result === null) {
        return false;
      }
      this.dispatchTransaction(view, result);
      return true;
    }

    const selection = view.state.selection.main;
    const selectedText = view.state.sliceDoc(selection.from, selection.to);
    const template =
      command === 'link'
        ? linkSnippet(selectedText)
        : '| ${1} | ${2} |\n| --- | --- |\n| ${3} | ${4} |\n${0}';
    snippet(template)(view, null, selection.from, selection.to);
    return true;
  }

  private applySmartEnter(view: EditorView): boolean {
    const result = continueMarkdownBlockTransaction(
      view.state.doc.toString(),
      editorSelections(view),
    );
    if (result === null) {
      return false;
    }
    this.dispatchTransaction(view, result);
    return true;
  }

  private indentSelection(view: EditorView, direction: 'more' | 'less'): boolean {
    const result = indentMarkdownLinesTransaction(
      view.state.doc.toString(),
      editorSelections(view),
      direction,
    );
    if (result !== null) {
      this.dispatchTransaction(view, result);
      return true;
    }
    return direction === 'more' ? indentMore(view) : indentLess(view);
  }

  private dispatchTransaction(view: EditorView, transaction: MarkdownTransactionResult): void {
    view.dispatch({
      changes: transaction.changes,
      selection: EditorSelection.create(
        transaction.selections.map((selection) =>
          EditorSelection.range(selection.anchor, selection.head),
        ),
      ),
      userEvent: 'input',
    });
  }

  private handlePaste(event: ClipboardEvent, view: EditorView): boolean {
    const files = Array.from(event.clipboardData?.items ?? [])
      .filter((item) => item.kind === 'file' && item.type.startsWith('image/'))
      .map((item) => item.getAsFile())
      .filter((file): file is File => file !== null);
    if (files.length === 0) {
      return false;
    }
    event.preventDefault();
    event.stopPropagation();
    this.queueImageUploads(files, view.state.selection.main.head);
    return true;
  }

  private handleDrop(event: DragEvent, view: EditorView): boolean {
    const files = Array.from(event.dataTransfer?.files ?? []).filter((file) =>
      file.type.startsWith('image/'),
    );
    if (files.length === 0) {
      return false;
    }
    event.preventDefault();
    event.stopPropagation();
    const position = view.posAtCoords({ x: event.clientX, y: event.clientY });
    this.queueImageUploads(files, position ?? view.state.selection.main.head);
    return true;
  }

  private handleDragOver(event: DragEvent): boolean {
    const hasImage = Array.from(event.dataTransfer?.items ?? []).some(
      (item) => item.kind === 'file' && item.type.startsWith('image/'),
    );
    if (!hasImage) {
      return false;
    }
    event.preventDefault();
    if (event.dataTransfer !== null) {
      event.dataTransfer.dropEffect = 'copy';
    }
    return true;
  }

  private queueImageUploads(files: readonly File[], anchor: number): void {
    const images = files.filter((file) => file.type.startsWith('image/'));
    if (images.length === 0) {
      return;
    }
    const queued = images.map((file) => ({
      id: ++this.nextUploadId,
      file,
      anchor,
      status: 'queued' as const,
    }));
    this.uploads.update((uploads) => [...uploads, ...queued]);
    this.processNextUpload();
  }

  private processNextUpload(): void {
    if (this.uploads().some((upload) => upload.status === 'uploading')) {
      return;
    }
    if (this.uploads().some((upload) => upload.status === 'error')) {
      return;
    }
    const next = this.uploads().find((upload) => upload.status === 'queued');
    if (next === undefined) {
      return;
    }
    this.updateUploadStatus(next.id, 'uploading');
    this.imageUpload
      .uploadEditorImage(next.file)
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (markdownUrl) => {
          const current = this.uploads().find((upload) => upload.id === next.id);
          const view = this.editorView;
          if (current === undefined || view === null) {
            return;
          }
          view.dispatch({
            changes: {
              from: current.anchor,
              to: current.anchor,
              insert: markdownImage(next.file.name, markdownUrl),
            },
            userEvent: 'input',
          });
          this.uploads.update((uploads) => uploads.filter((upload) => upload.id !== next.id));
          this.processNextUpload();
        },
        error: () => this.updateUploadStatus(next.id, 'error'),
      });
  }

  private updateUploadStatus(id: number, status: UploadStatus): void {
    this.uploads.update((uploads) =>
      uploads.map((upload) => (upload.id === id ? { ...upload, status } : upload)),
    );
  }

  private currentCursor(): number {
    return this.editorView?.state.selection.main.head ?? 0;
  }

  private restoreScrollAndFocus(shouldFocus: boolean): void {
    const view = this.editorView;
    if (view === null) {
      return;
    }
    view.scrollDOM.scrollTop = this.savedScrollTop;
    if (shouldFocus) {
      view.focus();
      this.document.defaultView?.requestAnimationFrame(() => {
        if (
          !this.destroyRef.destroyed &&
          this.editorView === view &&
          this.mode() === 'edit' &&
          !view.hasFocus
        ) {
          view.focus();
        }
      });
    }
  }

  private consumeKeyboardEvent(event: KeyboardEvent): void {
    event.preventDefault();
    event.stopPropagation();
  }

  private consumeComposingEditorShortcut(event: KeyboardEvent): boolean {
    if (
      !event.isComposing ||
      findMarkdownEditorCommand(keyboardEventWithoutComposition(event), this.editorPlatform()) ===
        null
    ) {
      return false;
    }
    this.consumeKeyboardEvent(event);
    return true;
  }

  private editorPlatform(): 'mac' | 'other' {
    const navigator = this.document.defaultView?.navigator;
    return navigator !== undefined && /Mac|iPhone|iPad/.test(navigator.platform) ? 'mac' : 'other';
  }

  private searchPhrases(): Record<string, string> {
    return {
      Find: this.i18n.translate('markdownEditor.search.find'),
      Replace: this.i18n.translate('markdownEditor.search.replace'),
      next: this.i18n.translate('markdownEditor.search.next'),
      previous: this.i18n.translate('markdownEditor.search.previous'),
      all: this.i18n.translate('markdownEditor.search.all'),
      'match case': this.i18n.translate('markdownEditor.search.matchCase'),
      'by word': this.i18n.translate('markdownEditor.search.byWord'),
      regexp: this.i18n.translate('markdownEditor.search.regexp'),
      replace: this.i18n.translate('markdownEditor.search.replace'),
      'replace all': this.i18n.translate('markdownEditor.search.replaceAll'),
      close: this.i18n.translate('markdownEditor.search.close'),
      'Go to line': this.i18n.translate('markdownEditor.search.goToLine'),
      go: this.i18n.translate('markdownEditor.search.go'),
      'current match': this.i18n.translate('markdownEditor.search.currentMatch'),
      'on line': this.i18n.translate('markdownEditor.search.onLine'),
      'replaced $ matches': this.i18n.translate('markdownEditor.search.replacedMatches'),
      'replaced match on line $': this.i18n.translate('markdownEditor.search.replacedMatchOnLine'),
    };
  }

  private editorContentAttributes(): Record<string, string> {
    return {
      'aria-label': this.accessibleLabel(),
      lang: this.language(),
      spellcheck: 'true',
    };
  }
}

function resolveShortcutGroups(): readonly ResolvedShortcutGroup[] {
  const commandsById = new Map(
    MARKDOWN_EDITOR_COMMANDS.map((command) => [command.id, command] as const),
  );
  return MARKDOWN_EDITOR_SHORTCUT_GROUPS.map((group) => ({
    id: group.id,
    labelKey: group.labelKey,
    commands: group.commandIds.map((commandId) => {
      const command = commandsById.get(commandId);
      if (command === undefined) {
        throw new Error(`Unknown Markdown editor command: ${commandId}`);
      }
      return command;
    }),
  }));
}

function editorSelections(view: EditorView): readonly MarkdownSelection[] {
  return view.state.selection.ranges.map((selection) => ({
    anchor: selection.anchor,
    head: selection.head,
  }));
}

function modeTabIndex(key: string, currentIndex: number, tabCount: number): number | null {
  if (key === 'Home') return 0;
  if (key === 'End') return tabCount - 1;
  if (key === 'ArrowRight' || key === 'ArrowDown') return (currentIndex + 1) % tabCount;
  if (key === 'ArrowLeft' || key === 'ArrowUp') return (currentIndex - 1 + tabCount) % tabCount;
  return null;
}

function linkSnippet(selectedText: string): string {
  if (selectedText === '') {
    return '[${1}](${2})${0}';
  }
  return `[${escapeSnippetText(selectedText)}](${'${1}'})${'${0}'}`;
}

function escapeSnippetText(value: string): string {
  return value
    .replaceAll('\\', '\\\\')
    .replaceAll('[', '\\[')
    .replaceAll(']', '\\]')
    .replaceAll('$', '\\$')
    .replaceAll('{', '\\{')
    .replaceAll('}', '\\}');
}

function markdownImage(fileName: string, markdownUrl: string): string {
  const alt = fileName
    .replaceAll('\\', '\\\\')
    .replaceAll('[', '\\[')
    .replaceAll(']', '\\]')
    .replaceAll(/\r?\n/g, ' ');
  const url = markdownUrl.replaceAll('\\', '\\\\').replaceAll('(', '\\(').replaceAll(')', '\\)');
  return `![${alt}](${url})`;
}

function keyboardEventWithoutComposition(event: KeyboardEvent): MarkdownKeyboardEvent {
  return {
    code: event.code,
    key: event.key,
    altKey: event.altKey,
    ctrlKey: event.ctrlKey,
    metaKey: event.metaKey,
    shiftKey: event.shiftKey,
    isComposing: false,
  };
}
