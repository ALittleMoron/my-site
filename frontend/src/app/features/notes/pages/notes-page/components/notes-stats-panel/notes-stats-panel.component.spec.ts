import { ComponentFixture, TestBed } from '@angular/core/testing';
import { By } from '@angular/platform-browser';
import { provideI18nTesting } from '../../../../../../testing/i18n-testing';
import { NotesStatsPanelComponent } from './notes-stats-panel.component';

describe('NotesStatsPanelComponent', () => {
  let fixture: ComponentFixture<NotesStatsPanelComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [NotesStatsPanelComponent],
      providers: [provideI18nTesting()],
    }).compileComponents();
    fixture = TestBed.createComponent(NotesStatsPanelComponent);
    fixture.componentRef.setInput('dateFrom', '2026-01-01');
    fixture.componentRef.setInput('dateTo', '2026-01-31');
    fixture.componentRef.setInput('dateLocale', 'ru-RU');
    fixture.componentRef.setInput('datePlaceholder', 'дд/мм/гггг');
    fixture.componentRef.setInput('openCalendarLabel', 'Открыть календарь');
    fixture.componentRef.setInput('previousMonthLabel', 'Предыдущий месяц');
    fixture.componentRef.setInput('nextMonthLabel', 'Следующий месяц');
    fixture.componentRef.setInput('openMonthYearPickerLabel', 'Выбрать месяц и год');
    fixture.componentRef.setInput('previousYearLabel', 'Предыдущий год');
    fixture.componentRef.setInput('nextYearLabel', 'Следующий год');
  });

  it('renders totals and note rows', () => {
    fixture.componentRef.setInput('stats', {
      dateFrom: '2026-01-01',
      dateTo: '2026-01-31',
      totals: { viewCount: 7, engagedViewCount: 3, reactionCount: 2 },
      notes: [
        {
          noteId: '00000000-0000-0000-0000-000000000001',
          title: 'Typed notes',
          slug: 'typed-notes',
          viewCount: 7,
          engagedViewCount: 3,
          reactionCounts: { heart: 1, fire: 0, thinking: 1, neutral: 0, poop: 0 },
        },
      ],
      daily: [],
    });
    fixture.detectChanges();

    const text = fixture.nativeElement.textContent as string;

    expect(text).toContain('Просмотры: 7');
    expect(text).toContain('Typed notes');
  });

  it('emits date changes and refresh command', () => {
    const dateFromChange = jest.fn();
    const refresh = jest.fn();
    fixture.componentInstance.dateFromChange.subscribe(dateFromChange);
    fixture.componentInstance.refresh.subscribe(refresh);
    fixture.detectChanges();

    const dateInput = fixture.debugElement.query(By.css('input[type="text"]'))
      .nativeElement as HTMLInputElement;
    dateInput.value = '02/01/2026';
    dateInput.dispatchEvent(new Event('input'));
    fixture.debugElement.query(By.css('[data-testid="notes-stats-refresh"]')).nativeElement.click();

    expect(dateFromChange).toHaveBeenCalledWith('2026-01-02');
    expect(refresh).toHaveBeenCalled();
  });

  it('renders localized date pickers with calendar buttons', () => {
    fixture.detectChanges();

    const inputs = fixture.debugElement
      .queryAll(By.css('input[type="text"]'))
      .map((input) => input.nativeElement as HTMLInputElement);

    expect(inputs).toHaveLength(2);
    expect(inputs[0].value).toBe('01/01/2026');
    expect(inputs[1].value).toBe('31/01/2026');
    expect(
      fixture.debugElement.queryAll(By.css('[data-testid="date-picker-toggle"]')),
    ).toHaveLength(2);

    fixture.debugElement.query(By.css('[data-testid="date-picker-toggle"]')).nativeElement.click();
    fixture.detectChanges();

    const monthYearToggle = fixture.debugElement.query(
      By.css('[data-testid="date-picker-month-year-toggle"]'),
    ).nativeElement as HTMLButtonElement;
    expect(monthYearToggle.getAttribute('aria-label')).toBe('Выбрать месяц и год');
  });
});
