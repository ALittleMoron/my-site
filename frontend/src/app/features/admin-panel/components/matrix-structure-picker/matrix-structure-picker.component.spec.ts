import { ComponentFixture, TestBed } from '@angular/core/testing';
import { of } from 'rxjs';
import { provideI18nTesting } from '../../../../testing/i18n-testing';
import { AdminMatrixStructure } from '../../models/matrix-question-workspace.model';
import { MatrixQuestionWorkspaceService } from '../../services/matrix-question-workspace.service';
import { MatrixStructurePickerComponent } from './matrix-structure-picker.component';

const initialStructure: AdminMatrixStructure = {
  sheets: [
    {
      id: 1,
      key: 'python',
      name: 'Питон',
      priority: 1,
      translations: { ru: { name: 'Питон' }, en: { name: 'Python' } },
      sections: [
        {
          id: 2,
          name: 'Основы',
          priority: 1,
          translations: { ru: { name: 'Основы' }, en: { name: 'Core' } },
          subsections: [
            {
              id: 3,
              name: 'Стиль',
              priority: 1,
              translations: { ru: { name: 'Стиль' }, en: { name: 'Style' } },
            },
          ],
        },
      ],
    },
  ],
};

const INVALID_SHORT_TEXT = 'x'.repeat(256);

interface MatrixStructureValidationCase {
  description: string;
  selector: string;
  addButtonSelector: string;
  expectedMessage: string;
  prepare: () => void;
}

describe('MatrixStructurePickerComponent', () => {
  let fixture: ComponentFixture<MatrixStructurePickerComponent>;
  let service: jest.Mocked<MatrixQuestionWorkspaceService>;

  beforeEach(async () => {
    service = {
      getStructure: jest.fn().mockReturnValue(of(initialStructure)),
      createSheet: jest.fn(),
      createSection: jest.fn(),
      createSubsection: jest.fn(),
    } as unknown as jest.Mocked<MatrixQuestionWorkspaceService>;

    await TestBed.configureTestingModule({
      imports: [MatrixStructurePickerComponent],
      providers: [
        provideI18nTesting(),
        { provide: MatrixQuestionWorkspaceService, useValue: service },
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(MatrixStructurePickerComponent);
    fixture.componentRef.setInput('language', 'ru');
    fixture.componentRef.setInput('selectedSubsectionId', null);
    fixture.detectChanges();
  });

  it('loads localized structure and enables dependent selects step by step', () => {
    const sheet = select('[data-testid="matrix-structure-sheet"]');
    const section = select('[data-testid="matrix-structure-section"]');
    const subsection = select('[data-testid="matrix-structure-subsection"]');

    expect(service.getStructure).toHaveBeenCalledWith('ru');
    expect(sheet.textContent).toContain('Питон');
    expect(section.disabled).toBe(true);
    expect(subsection.disabled).toBe(true);

    choose(sheet, '1');
    fixture.detectChanges();

    expect(section.disabled).toBe(false);
    expect(section.textContent).toContain('Основы');

    choose(section, '2');
    fixture.detectChanges();

    expect(subsection.disabled).toBe(false);
    expect(subsection.textContent).toContain('Стиль');
  });

  it('emits selected subsection id', () => {
    const emit = jest.spyOn(fixture.componentInstance.selectedSubsectionIdChange, 'emit');

    choose(select('[data-testid="matrix-structure-sheet"]'), '1');
    fixture.detectChanges();
    choose(select('[data-testid="matrix-structure-section"]'), '2');
    fixture.detectChanges();
    choose(select('[data-testid="matrix-structure-subsection"]'), '3');

    expect(emit).toHaveBeenLastCalledWith(3);
  });

  it('reloads structure and selects newly created sheet', () => {
    const updatedStructure: AdminMatrixStructure = {
      sheets: [
        ...initialStructure.sheets,
        {
          id: 4,
          key: 'sql',
          name: 'SQL',
          priority: 2,
          translations: { ru: { name: 'SQL' }, en: { name: 'SQL' } },
          sections: [],
        },
      ],
    };
    service.getStructure
      .mockReturnValueOnce(of(initialStructure))
      .mockReturnValueOnce(of(updatedStructure));
    service.createSheet.mockReturnValue(
      of({
        id: 4,
        key: 'sql',
        name: 'SQL',
        priority: 2,
        translations: { ru: { name: 'SQL' }, en: { name: 'SQL' } },
        sections: [],
      }),
    );
    fixture = TestBed.createComponent(MatrixStructurePickerComponent);
    fixture.componentRef.setInput('language', 'ru');
    fixture.componentRef.setInput('selectedSubsectionId', null);
    fixture.detectChanges();

    setInput('[data-testid="matrix-structure-sheet-key"]', 'sql');
    setInput('[data-testid="matrix-structure-sheet-ru"]', 'SQL');
    setInput('[data-testid="matrix-structure-sheet-en"]', 'SQL');
    fixture.detectChanges();
    fixture.nativeElement
      .querySelector<HTMLButtonElement>('[data-testid="matrix-structure-add-sheet"]')
      ?.click();
    fixture.detectChanges();

    expect(service.createSheet).toHaveBeenCalledWith({
      key: 'sql',
      translations: { ru: { name: 'SQL' }, en: { name: 'SQL' } },
    });
    expect(select('[data-testid="matrix-structure-sheet"]').value).toBe('4');
  });

  it('blocks invalid sheet key and whitespace-only structure names', () => {
    setInput('[data-testid="matrix-structure-sheet-key"]', 'Python Core');
    setInput('[data-testid="matrix-structure-sheet-ru"]', 'Питон');
    setInput('[data-testid="matrix-structure-sheet-en"]', 'Python');
    fixture.nativeElement
      .querySelector<HTMLButtonElement>('[data-testid="matrix-structure-add-sheet"]')
      ?.click();

    expect(service.createSheet).not.toHaveBeenCalled();

    setInput('[data-testid="matrix-structure-sheet-key"]', 'python-core');
    setInput('[data-testid="matrix-structure-sheet-ru"]', '   ');
    setInput('[data-testid="matrix-structure-sheet-en"]', 'Python');
    fixture.nativeElement
      .querySelector<HTMLButtonElement>('[data-testid="matrix-structure-add-sheet"]')
      ?.click();

    expect(service.createSheet).not.toHaveBeenCalled();
  });

  it.each<MatrixStructureValidationCase>([
    {
      description: 'sheet key pattern',
      selector: '[data-testid="matrix-structure-sheet-key"]',
      addButtonSelector: '[data-testid="matrix-structure-add-sheet"]',
      expectedMessage: 'Используйте строчные латинские буквы, цифры и одинарные дефисы.',
      prepare: () => {
        setInput('[data-testid="matrix-structure-sheet-key"]', 'Python Core');
        setInput('[data-testid="matrix-structure-sheet-ru"]', 'Питон');
        setInput('[data-testid="matrix-structure-sheet-en"]', 'Python');
      },
    },
    {
      description: 'sheet RU name required',
      selector: '[data-testid="matrix-structure-sheet-ru"]',
      addButtonSelector: '[data-testid="matrix-structure-add-sheet"]',
      expectedMessage: 'Заполните поле.',
      prepare: () => {
        setInput('[data-testid="matrix-structure-sheet-key"]', 'python-core');
        setInput('[data-testid="matrix-structure-sheet-ru"]', '   ');
        setInput('[data-testid="matrix-structure-sheet-en"]', 'Python');
      },
    },
    {
      description: 'sheet EN name max length',
      selector: '[data-testid="matrix-structure-sheet-en"]',
      addButtonSelector: '[data-testid="matrix-structure-add-sheet"]',
      expectedMessage: 'Максимум 255 символов.',
      prepare: () => {
        setInput('[data-testid="matrix-structure-sheet-key"]', 'python-core');
        setInput('[data-testid="matrix-structure-sheet-ru"]', 'Питон');
        setInput('[data-testid="matrix-structure-sheet-en"]', INVALID_SHORT_TEXT);
      },
    },
    {
      description: 'section RU name required',
      selector: '[data-testid="matrix-structure-section-ru"]',
      addButtonSelector: '[data-testid="matrix-structure-add-section"]',
      expectedMessage: 'Заполните поле.',
      prepare: () => {
        choose(select('[data-testid="matrix-structure-sheet"]'), '1');
        fixture.detectChanges();
        setInput('[data-testid="matrix-structure-section-ru"]', '   ');
        setInput('[data-testid="matrix-structure-section-en"]', 'Core');
      },
    },
    {
      description: 'section EN name max length',
      selector: '[data-testid="matrix-structure-section-en"]',
      addButtonSelector: '[data-testid="matrix-structure-add-section"]',
      expectedMessage: 'Максимум 255 символов.',
      prepare: () => {
        choose(select('[data-testid="matrix-structure-sheet"]'), '1');
        fixture.detectChanges();
        setInput('[data-testid="matrix-structure-section-ru"]', 'Основы');
        setInput('[data-testid="matrix-structure-section-en"]', INVALID_SHORT_TEXT);
      },
    },
    {
      description: 'subsection RU name required',
      selector: '[data-testid="matrix-structure-subsection-ru"]',
      addButtonSelector: '[data-testid="matrix-structure-add-subsection"]',
      expectedMessage: 'Заполните поле.',
      prepare: () => {
        selectExistingSection();
        setInput('[data-testid="matrix-structure-subsection-ru"]', '   ');
        setInput('[data-testid="matrix-structure-subsection-en"]', 'Typing');
      },
    },
    {
      description: 'subsection EN name max length',
      selector: '[data-testid="matrix-structure-subsection-en"]',
      addButtonSelector: '[data-testid="matrix-structure-add-subsection"]',
      expectedMessage: 'Максимум 255 символов.',
      prepare: () => {
        selectExistingSection();
        setInput('[data-testid="matrix-structure-subsection-ru"]', 'Типизация');
        setInput('[data-testid="matrix-structure-subsection-en"]', INVALID_SHORT_TEXT);
      },
    },
  ])('shows invalid styling and localized feedback for $description', (validationCase) => {
    validationCase.prepare();
    const addButton = fixture.nativeElement.querySelector<HTMLButtonElement>(
      validationCase.addButtonSelector,
    );

    expect(addButton?.disabled).toBe(false);
    addButton?.click();
    fixture.detectChanges();

    expect(service.createSheet).not.toHaveBeenCalled();
    expect(service.createSection).not.toHaveBeenCalled();
    expect(service.createSubsection).not.toHaveBeenCalled();
    expectInvalidControl(validationCase.selector, validationCase.expectedMessage);
  });

  it('reloads structure and emits newly created subsection', () => {
    const updatedStructure: AdminMatrixStructure = {
      sheets: [
        {
          ...initialStructure.sheets[0],
          sections: [
            {
              ...initialStructure.sheets[0].sections[0],
              subsections: [
                ...initialStructure.sheets[0].sections[0].subsections,
                {
                  id: 5,
                  name: 'Типизация',
                  priority: 2,
                  translations: { ru: { name: 'Типизация' }, en: { name: 'Typing' } },
                },
              ],
            },
          ],
        },
      ],
    };
    service.getStructure
      .mockReturnValueOnce(of(initialStructure))
      .mockReturnValueOnce(of(updatedStructure));
    service.createSubsection.mockReturnValue(
      of({
        id: 5,
        name: 'Типизация',
        priority: 2,
        translations: { ru: { name: 'Типизация' }, en: { name: 'Typing' } },
      }),
    );
    fixture = TestBed.createComponent(MatrixStructurePickerComponent);
    fixture.componentRef.setInput('language', 'ru');
    fixture.componentRef.setInput('selectedSubsectionId', null);
    fixture.detectChanges();
    const emit = jest.spyOn(fixture.componentInstance.selectedSubsectionIdChange, 'emit');
    choose(select('[data-testid="matrix-structure-sheet"]'), '1');
    fixture.detectChanges();
    choose(select('[data-testid="matrix-structure-section"]'), '2');
    fixture.detectChanges();
    setInput('[data-testid="matrix-structure-subsection-ru"]', 'Типизация');
    setInput('[data-testid="matrix-structure-subsection-en"]', 'Typing');
    fixture.detectChanges();

    fixture.nativeElement
      .querySelector<HTMLButtonElement>('[data-testid="matrix-structure-add-subsection"]')
      ?.click();
    fixture.detectChanges();

    expect(service.createSubsection).toHaveBeenCalledWith(2, {
      translations: { ru: { name: 'Типизация' }, en: { name: 'Typing' } },
    });
    expect(emit).toHaveBeenLastCalledWith(5);
    expect(select('[data-testid="matrix-structure-subsection"]').textContent).toContain(
      'Типизация',
    );
  });

  function select(selector: string): HTMLSelectElement {
    return fixture.nativeElement.querySelector(selector) as HTMLSelectElement;
  }

  function choose(element: HTMLSelectElement, value: string): void {
    element.value = value;
    element.dispatchEvent(new Event('change'));
  }

  function setInput(selector: string, value: string): void {
    const input = fixture.nativeElement.querySelector(selector) as HTMLInputElement;
    input.value = value;
    input.dispatchEvent(new Event('input'));
    fixture.detectChanges();
  }

  function selectExistingSection(): void {
    choose(select('[data-testid="matrix-structure-sheet"]'), '1');
    fixture.detectChanges();
    choose(select('[data-testid="matrix-structure-section"]'), '2');
    fixture.detectChanges();
  }

  function expectInvalidControl(selector: string, expectedMessage: string): void {
    const element = fixture.nativeElement.querySelector(selector) as HTMLElement | null;
    expect(element).not.toBeNull();
    expect(element?.classList).toContain('is-invalid');
    expect(element?.getAttribute('aria-invalid')).toBe('true');
    expect(fixture.nativeElement.textContent).toContain(expectedMessage);
  }
});
