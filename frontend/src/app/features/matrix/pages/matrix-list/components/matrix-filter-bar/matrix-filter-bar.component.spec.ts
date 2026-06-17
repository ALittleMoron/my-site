import { ComponentFixture, TestBed } from '@angular/core/testing';
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

  it('does not render the admin published/all switch', () => {
    expect(el.querySelector('#onlyPublishedToggle')).toBeNull();
  });

  it('does not render the admin add-question button', () => {
    expect(el.querySelector('[data-testid="matrix-filter-add-question"]')).toBeNull();
  });

  it('should emit suggestQuestion when the suggestion button is clicked', () => {
    const emitted: void[] = [];
    fixture.componentInstance.suggestQuestion.subscribe(() => emitted.push(undefined));

    el.querySelector<HTMLButtonElement>('[data-testid="matrix-filter-suggest-question"]')!.click();

    expect(emitted.length).toBe(1);
  });

  it('should render suggestion button with article-tag gray styling instead of accent styling', () => {
    const button = el.querySelector<HTMLButtonElement>(
      '[data-testid="matrix-filter-suggest-question"]',
    );

    expect(button).toBeTruthy();
    expect(button?.classList).toContain('btn-outline-secondary');
    expect(button?.classList).not.toContain('btn-success');
    expect(button?.classList).not.toContain('btn-primary');
    expect(button?.classList).not.toContain('btn-outline-primary');
  });

  it('should not render matrix layout switcher controls', () => {
    expect(el.querySelector('[aria-label="Переключение вида"]')).toBeNull();
    expect(el.querySelector('button[aria-label="Список"]')).toBeNull();
    expect(el.querySelector('button[aria-label="Таблица"]')).toBeNull();
  });
});
