import {
  ChangeDetectionStrategy,
  Component,
  DestroyRef,
  EventEmitter,
  Input,
  OnChanges,
  OnInit,
  Output,
  SimpleChanges,
  computed,
  inject,
  signal,
} from '@angular/core';
import { NonNullableFormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { finalize, map, switchMap } from 'rxjs';
import { LanguageCode } from '../../../../core/i18n/i18n.model';
import { TranslatePipe } from '../../../../core/i18n/translate.pipe';
import {
  AdminMatrixStructure,
  AdminMatrixStructureSection,
  AdminMatrixStructureSheet,
  AdminMatrixStructureSubsection,
} from '../../models/matrix-question-workspace.model';
import { MatrixQuestionWorkspaceService } from '../../services/matrix-question-workspace.service';

interface MatrixStructureCreateFormValue {
  nameRu: string;
  nameEn: string;
}

@Component({
  selector: 'app-matrix-structure-picker',
  standalone: true,
  imports: [ReactiveFormsModule, TranslatePipe],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './matrix-structure-picker.component.html',
})
export class MatrixStructurePickerComponent implements OnInit, OnChanges {
  private readonly workspaceService = inject(MatrixQuestionWorkspaceService);
  private readonly formBuilder = inject(NonNullableFormBuilder);
  private readonly destroyRef = inject(DestroyRef);

  @Input({ required: true }) language!: LanguageCode;
  @Input({ required: true }) selectedSubsectionId!: number | null;
  @Input() disabled = false;

  @Output() readonly selectedSubsectionIdChange = new EventEmitter<number | null>();

  readonly structure = signal<AdminMatrixStructure>({ sheets: [] });
  readonly loading = signal(false);
  readonly creating = signal(false);
  readonly errorKey = signal<string | null>(null);
  readonly selectedSheetId = signal<number | null>(null);
  readonly selectedSectionId = signal<number | null>(null);

  readonly selectedSections = computed(() => {
    const sheetId = this.selectedSheetId();
    if (sheetId === null) return [];
    return this.structure().sheets.find((sheet) => sheet.id === sheetId)?.sections ?? [];
  });
  readonly selectedSubsections = computed(() => {
    const sectionId = this.selectedSectionId();
    if (sectionId === null) return [];
    return this.selectedSections().find((section) => section.id === sectionId)?.subsections ?? [];
  });

  readonly sheetForm = this.formBuilder.group({
    key: ['', [Validators.required, Validators.maxLength(255)]],
    nameRu: ['', [Validators.required, Validators.maxLength(255)]],
    nameEn: ['', [Validators.required, Validators.maxLength(255)]],
  });
  readonly sectionForm = this.formBuilder.group({
    nameRu: ['', [Validators.required, Validators.maxLength(255)]],
    nameEn: ['', [Validators.required, Validators.maxLength(255)]],
  });
  readonly subsectionForm = this.formBuilder.group({
    nameRu: ['', [Validators.required, Validators.maxLength(255)]],
    nameEn: ['', [Validators.required, Validators.maxLength(255)]],
  });

  ngOnInit(): void {
    this.loadStructure();
  }

  ngOnChanges(changes: SimpleChanges): void {
    if (changes['language'] && !changes['language'].firstChange) {
      this.loadStructure();
      return;
    }
    if (changes['selectedSubsectionId'] && !changes['selectedSubsectionId'].firstChange) {
      this.alignSelectionToSubsection(this.selectedSubsectionId);
    }
  }

  onSheetChange(value: string): void {
    this.selectedSheetId.set(optionalNumber(value));
    this.selectedSectionId.set(null);
    this.selectedSubsectionIdChange.emit(null);
  }

  onSectionChange(value: string): void {
    this.selectedSectionId.set(optionalNumber(value));
    this.selectedSubsectionIdChange.emit(null);
  }

  onSubsectionChange(value: string): void {
    this.selectedSubsectionIdChange.emit(optionalNumber(value));
  }

  createSheet(): void {
    if (this.sheetForm.invalid) {
      this.sheetForm.markAllAsTouched();
      return;
    }
    const value = this.sheetForm.getRawValue();
    this.creating.set(true);
    this.errorKey.set(null);
    this.workspaceService
      .createSheet({
        key: value.key.trim(),
        translations: translationsFromForm(value),
      })
      .pipe(
        switchMap((sheet) =>
          this.workspaceService
            .getStructure(this.language)
            .pipe(map((structure) => ({ structure, sheet }))),
        ),
        finalize(() => this.creating.set(false)),
        takeUntilDestroyed(this.destroyRef),
      )
      .subscribe({
        next: ({ structure, sheet }) => {
          this.structure.set(structure);
          this.selectedSheetId.set(sheet.id);
          this.selectedSectionId.set(null);
          this.selectedSubsectionIdChange.emit(null);
          this.sheetForm.reset();
        },
        error: () => this.errorKey.set('adminMatrixStructure.createError'),
      });
  }

  createSection(): void {
    const sheetId = this.selectedSheetId();
    if (sheetId === null) return;
    if (this.sectionForm.invalid) {
      this.sectionForm.markAllAsTouched();
      return;
    }
    const value = this.sectionForm.getRawValue();
    this.creating.set(true);
    this.errorKey.set(null);
    this.workspaceService
      .createSection(sheetId, { translations: translationsFromForm(value) })
      .pipe(
        switchMap((section) =>
          this.workspaceService
            .getStructure(this.language)
            .pipe(map((structure) => ({ structure, section }))),
        ),
        finalize(() => this.creating.set(false)),
        takeUntilDestroyed(this.destroyRef),
      )
      .subscribe({
        next: ({ structure, section }) => {
          this.structure.set(structure);
          this.selectedSectionId.set(section.id);
          this.selectedSubsectionIdChange.emit(null);
          this.sectionForm.reset();
        },
        error: () => this.errorKey.set('adminMatrixStructure.createError'),
      });
  }

  createSubsection(): void {
    const sectionId = this.selectedSectionId();
    if (sectionId === null) return;
    if (this.subsectionForm.invalid) {
      this.subsectionForm.markAllAsTouched();
      return;
    }
    const value = this.subsectionForm.getRawValue();
    this.creating.set(true);
    this.errorKey.set(null);
    this.workspaceService
      .createSubsection(sectionId, { translations: translationsFromForm(value) })
      .pipe(
        switchMap((subsection) =>
          this.workspaceService
            .getStructure(this.language)
            .pipe(map((structure) => ({ structure, subsection }))),
        ),
        finalize(() => this.creating.set(false)),
        takeUntilDestroyed(this.destroyRef),
      )
      .subscribe({
        next: ({ structure, subsection }) => {
          this.structure.set(structure);
          this.selectedSubsectionIdChange.emit(subsection.id);
          this.alignSelectionToSubsection(subsection.id);
          this.subsectionForm.reset();
        },
        error: () => this.errorKey.set('adminMatrixStructure.createError'),
      });
  }

  private loadStructure(): void {
    this.loading.set(true);
    this.errorKey.set(null);
    this.workspaceService
      .getStructure(this.language)
      .pipe(
        finalize(() => this.loading.set(false)),
        takeUntilDestroyed(this.destroyRef),
      )
      .subscribe({
        next: (structure) => {
          this.structure.set(structure);
          this.alignSelectionToSubsection(this.selectedSubsectionId);
        },
        error: () => this.errorKey.set('adminMatrixStructure.loadError'),
      });
  }

  private alignSelectionToSubsection(subsectionId: number | null): void {
    const path = subsectionId === null ? null : findSubsectionPath(this.structure(), subsectionId);
    this.selectedSheetId.set(path?.sheet.id ?? null);
    this.selectedSectionId.set(path?.section.id ?? null);
  }
}

function translationsFromForm(value: MatrixStructureCreateFormValue): {
  ru: { name: string };
  en: { name: string };
} {
  return {
    ru: { name: value.nameRu.trim() },
    en: { name: value.nameEn.trim() },
  };
}

function optionalNumber(value: string): number | null {
  return value === '' ? null : Number(value);
}

function findSubsectionPath(
  structure: AdminMatrixStructure,
  subsectionId: number,
): {
  sheet: AdminMatrixStructureSheet;
  section: AdminMatrixStructureSection;
  subsection: AdminMatrixStructureSubsection;
} | null {
  for (const sheet of structure.sheets) {
    for (const section of sheet.sections) {
      const subsection = section.subsections.find((item) => item.id === subsectionId);
      if (subsection !== undefined) {
        return { sheet, section, subsection };
      }
    }
  }
  return null;
}
