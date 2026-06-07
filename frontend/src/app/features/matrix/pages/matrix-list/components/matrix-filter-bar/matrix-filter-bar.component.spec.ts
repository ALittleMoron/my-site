import { ComponentFixture, TestBed } from '@angular/core/testing';
import { MatrixLayoutMode } from '../../../../../../core/layout/layout-preferences.service';
import { provideI18nTesting } from '../../../../../../testing/i18n-testing';
import { MatrixFilterBarComponent } from './matrix-filter-bar.component';

describe('MatrixFilterBarComponent', () => {
  let fixture: ComponentFixture<MatrixFilterBarComponent>;
  let el: HTMLElement;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [MatrixFilterBarComponent],
      providers: [
        provideI18nTesting({
          'matrix.filter.clearSearch': 'Очистить поиск',
          'matrix.addQuestion': 'Добавить вопрос',
          'matrix.suggestQuestion': 'Предложить вопрос',
        }),
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(MatrixFilterBarComponent);
    fixture.componentRef.setInput('search', '');
    fixture.componentRef.setInput('onlyPublished', true);
    fixture.componentRef.setInput('layoutMode', 'list' as MatrixLayoutMode);
    fixture.componentRef.setInput('canManageContent', false);
    fixture.detectChanges();
    el = fixture.nativeElement as HTMLElement;
  });

  it('should render search input', () => {
    const input = el.querySelector<HTMLInputElement>('input[type="text"]');
    expect(input).toBeTruthy();
    expect(input?.value).toBe('');
    expect(input?.placeholder).toBe('Поиск навыков и вопросов');
  });

  it('should emit searchChange when user types', () => {
    const emitted: string[] = [];
    fixture.componentInstance.searchChange.subscribe((v: string) => emitted.push(v));
    const input = el.querySelector<HTMLInputElement>('input[type="text"]')!;
    input.value = 'closure';
    input.dispatchEvent(new Event('input'));
    expect(emitted).toEqual(['closure']);
  });

  it('should not show clear button when search is empty', () => {
    expect(el.querySelector('button[aria-label="Очистить поиск"]')).toBeFalsy();
  });

  it('should show clear button when search is not empty', () => {
    fixture.componentRef.setInput('search', 'closure');
    fixture.detectChanges();
    const button = el.querySelector('button[aria-label="Очистить поиск"]');
    expect(button).toBeTruthy();
    expect(button?.textContent?.trim()).toBe('Очистить');
  });

  it('should emit searchChange with empty string on clear', () => {
    fixture.componentRef.setInput('search', 'closure');
    fixture.detectChanges();
    const emitted: string[] = [];
    fixture.componentInstance.searchChange.subscribe((v: string) => emitted.push(v));
    el.querySelector<HTMLButtonElement>('button[aria-label="Очистить поиск"]')!.click();
    expect(emitted).toEqual(['']);
  });

  it('should hide published/all switch for users without content access users', () => {
    expect(el.querySelector('#onlyPublishedToggle')).toBeNull();
  });

  it('should show published/all switch for content managers', () => {
    fixture.componentRef.setInput('canManageContent', true);
    fixture.detectChanges();
    expect(el.querySelector('#onlyPublishedToggle')).not.toBeNull();
  });

  it('should show a green add question button immediately after search for content managers', () => {
    fixture.componentRef.setInput('canManageContent', true);
    fixture.detectChanges();

    const searchArea = el.querySelector('[data-testid="matrix-filter-search"]');
    const addButton = el.querySelector<HTMLButtonElement>(
      '[data-testid="matrix-filter-add-question"]',
    );

    expect(addButton).toBeTruthy();
    expect(addButton?.classList).toContain('btn-success');
    expect(addButton?.classList).not.toContain('mt-2');
    expect(addButton?.textContent?.trim()).toBe('Добавить вопрос');
    expect(searchArea?.parentElement?.classList).toContain('flex-md-row');
    expect(searchArea?.nextElementSibling).toBe(addButton);
  });

  it('should emit addQuestion when the add question button is clicked', () => {
    fixture.componentRef.setInput('canManageContent', true);
    fixture.detectChanges();
    const emitted: void[] = [];
    fixture.componentInstance.addQuestion.subscribe(() => emitted.push(undefined));

    el.querySelector<HTMLButtonElement>('[data-testid="matrix-filter-add-question"]')!.click();

    expect(emitted.length).toBe(1);
  });

  it('should emit suggestQuestion when the suggestion button is clicked', () => {
    const emitted: void[] = [];
    fixture.componentInstance.suggestQuestion.subscribe(() => emitted.push(undefined));

    el.querySelector<HTMLButtonElement>('[data-testid="matrix-filter-suggest-question"]')!.click();

    expect(emitted.length).toBe(1);
  });

  it('should render suggestion button with note-tag gray styling instead of accent styling', () => {
    const button = el.querySelector<HTMLButtonElement>(
      '[data-testid="matrix-filter-suggest-question"]',
    );

    expect(button).toBeTruthy();
    expect(button?.classList).toContain('btn-outline-secondary');
    expect(button?.classList).not.toContain('btn-success');
    expect(button?.classList).not.toContain('btn-primary');
    expect(button?.classList).not.toContain('btn-outline-primary');
  });

  it('should make the published only switch green when enabled', () => {
    fixture.componentRef.setInput('canManageContent', true);
    fixture.componentRef.setInput('onlyPublished', true);
    fixture.detectChanges();

    expect(el.querySelector('#onlyPublishedToggle')?.classList).toContain('text-bg-success');
  });

  it('should mark list layout button as primary when layoutMode is list', () => {
    const buttons = el.querySelectorAll<HTMLButtonElement>('.btn-group button');
    expect(buttons[0].classList.contains('button-active')).toBe(true);
    expect(buttons[1].classList.contains('button-active')).toBe(false);
  });

  it('should emit layoutModeChange when grid button clicked', () => {
    const emitted: MatrixLayoutMode[] = [];
    fixture.componentInstance.layoutModeChange.subscribe((v: MatrixLayoutMode) => emitted.push(v));
    const buttons = el.querySelectorAll<HTMLButtonElement>('.btn-group button');
    buttons[1].click();
    expect(emitted).toEqual(['grid']);
  });
});
