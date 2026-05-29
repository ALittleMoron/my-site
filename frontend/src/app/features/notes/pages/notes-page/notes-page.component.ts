import {
  ChangeDetectionStrategy,
  Component,
  DestroyRef,
  OnInit,
  computed,
  inject,
  signal,
} from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { ActivatedRoute, Router } from '@angular/router';
import { combineLatest } from 'rxjs';
import { AuthService } from '../../../../core/auth/auth.service';
import { ApiError } from '../../../../core/models/api-error.model';
import { NotificationService } from '../../../../core/notifications/notification.service';
import { SeoService } from '../../../../core/seo/seo.service';
import { EmptyStateComponent } from '../../../../shared/ui/empty-state/empty-state.component';
import { ErrorMessageComponent } from '../../../../shared/ui/error-message/error-message.component';
import { LoadingSpinnerComponent } from '../../../../shared/ui/loading-spinner/loading-spinner.component';
import { NoteDetail, NoteList, NotePayload, NoteTag, NoteTree } from '../../models/notes.model';
import { NotesService } from '../../services/notes.service';
import { NoteDetailComponent } from './components/note-detail/note-detail.component';
import { NoteFormComponent } from './components/note-form/note-form.component';
import { NoteListComponent } from './components/note-list/note-list.component';
import { NotesSidePanelComponent } from './components/notes-side-panel/notes-side-panel.component';

const PAGE_SIZE = 10;
const SIDE_PANEL_STORAGE_KEY = 'notesSidePanelOpen';

@Component({
  selector: 'app-notes-page',
  standalone: true,
  imports: [
    EmptyStateComponent,
    ErrorMessageComponent,
    LoadingSpinnerComponent,
    NoteDetailComponent,
    NoteFormComponent,
    NoteListComponent,
    NotesSidePanelComponent,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './notes-page.component.html',
  styleUrl: './notes-page.component.scss',
})
export class NotesPageComponent implements OnInit {
  private readonly notesService = inject(NotesService);
  private readonly authService = inject(AuthService);
  private readonly seoService = inject(SeoService);
  private readonly notifications = inject(NotificationService);
  private readonly route = inject(ActivatedRoute);
  private readonly router = inject(Router);
  private readonly destroyRef = inject(DestroyRef);

  readonly isAdmin = this.authService.isAdmin;
  readonly sidePanelOpen = signal(localStorage.getItem(SIDE_PANEL_STORAGE_KEY) === 'true');
  readonly onlyPublished = signal(true);
  readonly currentSlug = signal<string | null>(null);
  readonly activeTagSlug = signal<string | null>(null);
  readonly page = signal(1);

  readonly notes = signal<NoteList | null>(null);
  readonly tree = signal<NoteTree>({ folders: [] });
  readonly tags = signal<NoteTag[]>([]);
  readonly selectedNote = signal<NoteDetail | null>(null);

  readonly listLoading = signal(false);
  readonly listError = signal<ApiError | null>(null);
  readonly detailLoading = signal(false);
  readonly detailError = signal<ApiError | null>(null);

  readonly formVisible = signal(false);
  readonly formNote = signal<NoteDetail | null>(null);
  readonly formError = signal<ApiError | null>(null);

  readonly activeTags = computed(() =>
    [...this.tags()].filter((tag) => tag.deletedAt === null).sort(compareTags),
  );
  readonly activeTag = computed(() => {
    const slug = this.activeTagSlug();
    return slug ? (this.activeTags().find((tag) => tag.slug === slug) ?? null) : null;
  });
  readonly isDetailRoute = computed(() => this.currentSlug() !== null);
  readonly isEmpty = computed(
    () => !this.listLoading() && !this.listError() && (this.notes()?.notes.length ?? 0) === 0,
  );

  ngOnInit(): void {
    this.seoService.setMeta({
      title: 'Заметки',
      description: 'Заметки и короткие материалы.',
      canonicalPath: '/notes',
    });
    this.loadTags();
    this.loadTree();
    combineLatest([this.route.paramMap, this.route.queryParamMap])
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe(([params, query]) => {
        const slug = params.get('slug');
        this.currentSlug.set(slug);
        this.activeTagSlug.set(query.get('tag'));
        this.page.set(readPage(query.get('page')));
        if (slug) {
          this.loadDetail(slug);
        } else {
          this.selectedNote.set(null);
          this.loadNotes();
        }
      });
  }

  toggleSidePanel(): void {
    this.sidePanelOpen.update((value) => {
      const next = !value;
      localStorage.setItem(SIDE_PANEL_STORAGE_KEY, String(next));
      return next;
    });
  }

  closeSidePanel(): void {
    this.sidePanelOpen.set(false);
    localStorage.setItem(SIDE_PANEL_STORAGE_KEY, 'false');
  }

  setOnlyPublished(value: boolean): void {
    this.onlyPublished.set(value);
    const slug = this.currentSlug();
    if (slug) {
      this.loadDetail(slug);
    } else {
      this.loadNotes();
    }
  }

  openNote(slug: string): void {
    this.router.navigate(['/notes', slug]);
  }

  backToList(): void {
    this.router.navigate(['/notes']);
  }

  selectTag(slug: string): void {
    this.router.navigate(['/notes'], { queryParams: { tag: slug, page: 1 } });
  }

  clearTag(): void {
    this.router.navigate(['/notes'], { queryParams: { page: 1 } });
  }

  changePage(page: number): void {
    const queryParams: Record<string, string | number> = { page };
    const tag = this.activeTagSlug();
    if (tag) {
      queryParams['tag'] = tag;
    }
    this.router.navigate(['/notes'], { queryParams });
  }

  openCreate(): void {
    this.formNote.set(null);
    this.formError.set(null);
    this.formVisible.set(true);
  }

  openEdit(): void {
    this.formNote.set(this.selectedNote());
    this.formError.set(null);
    this.formVisible.set(true);
  }

  closeForm(): void {
    this.formVisible.set(false);
    this.formNote.set(null);
    this.formError.set(null);
  }

  saveNote(payload: NotePayload): void {
    const editing = this.formNote();
    const request = editing
      ? this.notesService.updateNote(editing.slug, payload)
      : this.notesService.createNote(payload);
    request.pipe(takeUntilDestroyed(this.destroyRef)).subscribe({
      next: (note) => {
        this.notifications.success('Заметка сохранена.');
        this.closeForm();
        this.loadTags();
        this.loadTree();
        this.router.navigate(['/notes', note.slug]);
      },
      error: (err: ApiError) => {
        this.formError.set(err);
        this.notifications.error('Не удалось сохранить заметку.');
      },
    });
  }

  publishNote(): void {
    const note = this.selectedNote();
    if (!note) return;
    this.notesService
      .publishNote(note.slug)
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: () => {
          this.notifications.success('Заметка опубликована.');
          this.loadTree();
          this.loadDetail(note.slug);
        },
        error: (err: ApiError) => {
          this.detailError.set(err);
          this.notifications.error('Не удалось опубликовать заметку.');
        },
      });
  }

  unpublishNote(): void {
    const note = this.selectedNote();
    if (!note) return;
    this.notesService
      .unpublishNote(note.slug)
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: () => {
          this.notifications.success('Заметка снята с публикации.');
          this.loadTree();
          this.loadDetail(note.slug);
        },
        error: (err: ApiError) => {
          this.detailError.set(err);
          this.notifications.error('Не удалось снять заметку с публикации.');
        },
      });
  }

  deleteNote(): void {
    const note = this.selectedNote();
    if (!note) return;
    this.notesService
      .deleteNote(note.slug)
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: () => {
          this.notifications.success('Заметка удалена.');
          this.loadTree();
          this.router.navigate(['/notes']);
        },
        error: (err: ApiError) => {
          this.detailError.set(err);
          this.notifications.error('Не удалось удалить заметку.');
        },
      });
  }

  loadNotes(): void {
    this.listLoading.set(true);
    this.listError.set(null);
    this.notesService
      .getNotes({
        page: this.page(),
        pageSize: PAGE_SIZE,
        onlyPublished: this.onlyPublished(),
        tagSlug: this.activeTagSlug(),
      })
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (notes) => {
          this.notes.set(notes);
          this.listLoading.set(false);
        },
        error: (err: ApiError) => {
          this.listError.set(err);
          this.listLoading.set(false);
        },
      });
  }

  loadDetail(slug: string): void {
    this.detailLoading.set(true);
    this.detailError.set(null);
    this.notesService
      .getNote(slug, !this.isAdmin())
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (note) => {
          this.selectedNote.set(note);
          this.detailLoading.set(false);
        },
        error: (err: ApiError) => {
          this.detailError.set(err);
          this.detailLoading.set(false);
        },
      });
  }

  loadTags(): void {
    this.notesService
      .getTags(false)
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (tags) => this.tags.set(tags),
        error: () => this.tags.set([]),
      });
  }

  loadTree(): void {
    this.notesService
      .getTree()
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (tree) => this.tree.set(tree),
        error: () => this.tree.set({ folders: [] }),
      });
  }
}

function readPage(value: string | null): number {
  const page = Number(value ?? '1');
  return Number.isFinite(page) && page > 0 ? page : 1;
}

function compareTags(a: NoteTag, b: NoteTag): number {
  return a.name.localeCompare(b.name, 'ru');
}
