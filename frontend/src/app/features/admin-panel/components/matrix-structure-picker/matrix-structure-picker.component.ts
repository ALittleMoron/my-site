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
import {
  AbstractControl,
  NonNullableFormBuilder,
  ReactiveFormsModule,
  Validators,
} from '@angular/forms';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { finalize, map, switchMap } from 'rxjs';
import { I18nService } from '../../../../core/i18n/i18n.service';
import { LanguageCode } from '../../../../core/i18n/i18n.model';
import { TranslatePipe } from '../../../../core/i18n/translate.pipe';
import {
  AdminMatrixStructure,
  AdminMatrixStructureSection,
  AdminMatrixStructureSheet,
  AdminMatrixStructureSubsection,
} from '../../models/matrix-question-workspace.model';
import { MatrixQuestionWorkspaceService } from '../../services/matrix-question-workspace.service';
import { AdminControlValidationStateDirective } from '../../directives/admin-control-validation-state.directive';
import {
  ADMIN_VALIDATION_LIMITS,
  slugValidator,
  trimRequired,
  validationMessage,
} from '../../utils/admin-validation';

interface MatrixStructureCreateFormValue {
  nameRu: string;
  nameEn: string;
}

@Component({
  selector: 'app-matrix-structure-picker',
  standalone: true,
  imports: [ReactiveFormsModule, TranslatePipe, AdminControlValidationStateDirective],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './matrix-structure-picker.component.html',
})
export class MatrixStructurePickerComponent implements OnInit, OnChanges {
  private readonly workspaceService = inject(MatrixQuestionWorkspaceService);
  private readonly formBuilder = inject(NonNullableFormBuilder);
  private readonly i18n = inject(I18nService);
  private readonly destroyRef = inject(DestroyRef);

  @Input({ required: true }) language!: LanguageCode;
  @Input({ required: true }) selectedSubsectionId!: string | null;
  @Input() disabled = false;
  @Input() invalid = false;

  @Output() readonly selectedSubsectionIdChange = new EventEmitter<string | null>();

  readonly structure = signal<AdminMatrixStructure>({ sheets: [] });
  readonly loading = signal(false);
  readonly creating = signal(false);
  readonly errorKey = signal<string | null>(null);
  readonly selectedSheetId = signal<string | null>(null);
  readonly selectedSectionId = signal<string | null>(null);
  readonly validationLimits = ADMIN_VALIDATION_LIMITS;

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
    key: [
      '',
      [trimRequired, Validators.maxLength(ADMIN_VALIDATION_LIMITS.shortText), slugValidator],
    ],
    nameRu: ['', [trimRequired, Validators.maxLength(ADMIN_VALIDATION_LIMITS.shortText)]],
    nameEn: ['', [trimRequired, Validators.maxLength(ADMIN_VALIDATION_LIMITS.shortText)]],
  });
  readonly sectionForm = this.formBuilder.group({
    nameRu: ['', [trimRequired, Validators.maxLength(ADMIN_VALIDATION_LIMITS.shortText)]],
    nameEn: ['', [trimRequired, Validators.maxLength(ADMIN_VALIDATION_LIMITS.shortText)]],
  });
  readonly subsectionForm = this.formBuilder.group({
    nameRu: ['', [trimRequired, Validators.maxLength(ADMIN_VALIDATION_LIMITS.shortText)]],
    nameEn: ['', [trimRequired, Validators.maxLength(ADMIN_VALIDATION_LIMITS.shortText)]],
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
    this.selectedSheetId.set(optionalString(value));
    this.selectedSectionId.set(null);
    this.selectedSubsectionIdChange.emit(null);
  }

  onSectionChange(value: string): void {
    this.selectedSectionId.set(optionalString(value));
    this.selectedSubsectionIdChange.emit(null);
  }

  onSubsectionChange(value: string): void {
    this.selectedSubsectionIdChange.emit(optionalString(value));
  }

  controlInvalid(control: AbstractControl<unknown>): boolean {
    return control.invalid && control.touched;
  }

  controlMessage(control: AbstractControl<unknown>): string | null {
    return validationMessage(control, this.i18n);
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
      .createSheet(
        {
          key: value.key.trim(),
          translations: translationsFromForm(value),
        },
        this.language,
      )
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
      .createSection(sheetId, { translations: translationsFromForm(value) }, this.language)
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
      .createSubsection(sectionId, { translations: translationsFromForm(value) }, this.language)
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

  private alignSelectionToSubsection(subsectionId: string | null): void {
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

function optionalString(value: string): string | null {
  return value === '' ? null : value;
}

function findSubsectionPath(
  structure: AdminMatrixStructure,
  subsectionId: string,
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
