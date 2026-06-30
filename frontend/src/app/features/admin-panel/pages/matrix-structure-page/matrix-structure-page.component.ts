import { CdkDrag, CdkDragDrop, CdkDropList, moveItemInArray } from '@angular/cdk/drag-drop';
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
import { Observable } from 'rxjs';
import { ApiError } from '../../../../core/models/api-error.model';
import { I18nService } from '../../../../core/i18n/i18n.service';
import { TranslatePipe } from '../../../../core/i18n/translate.pipe';
import { NotificationService } from '../../../../core/notifications/notification.service';
import { EmptyStateComponent } from '../../../../shared/ui/empty-state/empty-state.component';
import { ErrorMessageComponent } from '../../../../shared/ui/error-message/error-message.component';
import { LoadingSpinnerComponent } from '../../../../shared/ui/loading-spinner/loading-spinner.component';
import {
  AdminMatrixStructure,
  AdminMatrixStructureSection,
  AdminMatrixStructureSheet,
} from '../../models/matrix-question-workspace.model';
import { MatrixQuestionWorkspaceService } from '../../services/matrix-question-workspace.service';

@Component({
  selector: 'app-matrix-structure-page',
  standalone: true,
  imports: [
    CdkDrag,
    CdkDropList,
    TranslatePipe,
    LoadingSpinnerComponent,
    ErrorMessageComponent,
    EmptyStateComponent,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './matrix-structure-page.component.html',
  styleUrl: './matrix-structure-page.component.scss',
})
export class MatrixStructurePageComponent implements OnInit {
  private readonly workspaceService = inject(MatrixQuestionWorkspaceService);
  private readonly notifications = inject(NotificationService);
  private readonly i18n = inject(I18nService);
  private readonly destroyRef = inject(DestroyRef);

  readonly structure = signal<AdminMatrixStructure>({ sheets: [] });
  readonly selectedSheetId = signal<number | null>(null);
  readonly loading = signal(false);
  readonly saving = signal(false);
  readonly error = signal<ApiError | null>(null);

  readonly selectedSheet = computed(() => {
    const selectedId = this.selectedSheetId();
    return this.structure().sheets.find((sheet) => sheet.id === selectedId) ?? null;
  });
  readonly isEmpty = computed(() => !this.loading() && this.structure().sheets.length === 0);

  ngOnInit(): void {
    this.loadStructure();
  }

  loadStructure(): void {
    this.loading.set(true);
    this.error.set(null);
    this.workspaceService
      .getStructure(this.currentLanguage())
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (structure) => {
          this.structure.set(structure);
          this.selectedSheetId.set(this.nextSelectedSheetId(structure));
          this.loading.set(false);
        },
        error: (err: ApiError) => {
          this.error.set(err);
          this.loading.set(false);
          this.notifications.error(this.i18n.translate('adminMatrixStructure.loadError'));
        },
      });
  }

  selectSheet(sheetId: number): void {
    this.selectedSheetId.set(sheetId);
  }

  dropSheets(event: CdkDragDrop<AdminMatrixStructureSheet[]>): void {
    this.reorderSheets(event.previousIndex, event.currentIndex);
  }

  dropSections(
    event: CdkDragDrop<AdminMatrixStructureSection[]>,
    sheet: AdminMatrixStructureSheet,
  ): void {
    this.reorderSections(sheet.id, event.previousIndex, event.currentIndex);
  }

  dropSubsections(
    event: CdkDragDrop<AdminMatrixStructureSection['subsections']>,
    section: AdminMatrixStructureSection,
  ): void {
    this.reorderSubsections(section.id, event.previousIndex, event.currentIndex);
  }

  private reorderSheets(previousIndex: number, currentIndex: number): void {
    const current = this.structure();
    if (this.shouldSkipReorder(previousIndex, currentIndex, current.sheets.length)) return;
    const snapshot = cloneStructure(current);
    const next = cloneStructure(current);
    moveItemInArray(next.sheets, previousIndex, currentIndex);
    renumberPriorities(next.sheets);
    this.structure.set(next);
    this.selectedSheetId.set(next.sheets[currentIndex]?.id ?? this.selectedSheetId());
    this.saveReorder(
      snapshot,
      this.workspaceService.updateSheetPriorities(next.sheets.map((sheet) => sheet.id)),
    );
  }

  private reorderSections(sheetId: number, previousIndex: number, currentIndex: number): void {
    const current = this.structure();
    const sheet = current.sheets.find((item) => item.id === sheetId);
    if (!sheet || this.shouldSkipReorder(previousIndex, currentIndex, sheet.sections.length))
      return;
    const snapshot = cloneStructure(current);
    const next = cloneStructure(current);
    const nextSheet = next.sheets.find((item) => item.id === sheetId);
    if (!nextSheet) return;
    moveItemInArray(nextSheet.sections, previousIndex, currentIndex);
    renumberPriorities(nextSheet.sections);
    this.structure.set(next);
    this.saveReorder(
      snapshot,
      this.workspaceService.updateSectionPriorities(
        sheetId,
        nextSheet.sections.map((section) => section.id),
      ),
    );
  }

  private reorderSubsections(sectionId: number, previousIndex: number, currentIndex: number): void {
    const current = this.structure();
    const section = findSection(current, sectionId);
    if (
      !section ||
      this.shouldSkipReorder(previousIndex, currentIndex, section.subsections.length)
    ) {
      return;
    }
    const snapshot = cloneStructure(current);
    const next = cloneStructure(current);
    const nextSection = findSection(next, sectionId);
    if (!nextSection) return;
    moveItemInArray(nextSection.subsections, previousIndex, currentIndex);
    renumberPriorities(nextSection.subsections);
    this.structure.set(next);
    this.saveReorder(
      snapshot,
      this.workspaceService.updateSubsectionPriorities(
        sectionId,
        nextSection.subsections.map((subsection) => subsection.id),
      ),
    );
  }

  private saveReorder(snapshot: AdminMatrixStructure, request: Observable<void>): void {
    this.saving.set(true);
    request.pipe(takeUntilDestroyed(this.destroyRef)).subscribe({
      next: () => {
        this.saving.set(false);
        this.notifications.success(this.i18n.translate('adminMatrixStructure.saved'));
      },
      error: () => {
        this.structure.set(snapshot);
        this.selectedSheetId.set(this.nextSelectedSheetId(snapshot));
        this.saving.set(false);
        this.notifications.error(this.i18n.translate('adminMatrixStructure.saveError'));
        this.loadStructure();
      },
    });
  }

  private shouldSkipReorder(previousIndex: number, currentIndex: number, length: number): boolean {
    return (
      this.saving() ||
      previousIndex === currentIndex ||
      previousIndex < 0 ||
      currentIndex < 0 ||
      previousIndex >= length ||
      currentIndex >= length
    );
  }

  private nextSelectedSheetId(structure: AdminMatrixStructure): number | null {
    const selectedId = this.selectedSheetId();
    const existing = structure.sheets.find((sheet) => sheet.id === selectedId);
    return existing?.id ?? structure.sheets[0]?.id ?? null;
  }

  private currentLanguage(): 'ru' | 'en' {
    const language = this.i18n.language();
    if (language === null) {
      throw new Error('I18n language is not initialized');
    }
    return language;
  }
}

function findSection(
  structure: AdminMatrixStructure,
  sectionId: number,
): AdminMatrixStructureSection | null {
  for (const sheet of structure.sheets) {
    const section = sheet.sections.find((item) => item.id === sectionId);
    if (section) return section;
  }
  return null;
}

function cloneStructure(structure: AdminMatrixStructure): AdminMatrixStructure {
  return {
    sheets: structure.sheets.map((sheet) => ({
      ...sheet,
      sections: sheet.sections.map((section) => ({
        ...section,
        subsections: section.subsections.map((subsection) => ({ ...subsection })),
      })),
    })),
  };
}

function renumberPriorities<T extends { priority: number }>(items: T[]): void {
  items.forEach((item, index) => {
    item.priority = index + 1;
  });
}
