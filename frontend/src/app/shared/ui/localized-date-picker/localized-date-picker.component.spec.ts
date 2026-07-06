import { ComponentFixture, TestBed } from '@angular/core/testing';
import { By } from '@angular/platform-browser';
import { LocalizedDatePickerComponent } from './localized-date-picker.component';

describe('LocalizedDatePickerComponent', () => {
  let fixture: ComponentFixture<LocalizedDatePickerComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [LocalizedDatePickerComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(LocalizedDatePickerComponent);
    fixture.componentRef.setInput('inputId', 'publishedFrom');
    fixture.componentRef.setInput('value', '2026-02-05');
    fixture.componentRef.setInput('dateLocale', 'ru-RU');
    fixture.componentRef.setInput('placeholder', 'дд/мм/гггг');
    fixture.componentRef.setInput('required', false);
    fixture.componentRef.setInput('invalid', false);
    fixture.componentRef.setInput('openCalendarLabel', 'Открыть календарь');
    fixture.componentRef.setInput('previousMonthLabel', 'Предыдущий месяц');
    fixture.componentRef.setInput('nextMonthLabel', 'Следующий месяц');
    fixture.componentRef.setInput('openMonthYearPickerLabel', 'Выбрать месяц и год');
    fixture.componentRef.setInput('previousYearLabel', 'Предыдущий год');
    fixture.componentRef.setInput('nextYearLabel', 'Следующий год');
  });

  it('renders a localized text field with a calendar button', () => {
    fixture.detectChanges();

    const input = fixture.debugElement.query(By.css('#publishedFrom'))
      .nativeElement as HTMLInputElement;
    const calendarButton = fixture.debugElement.query(By.css('[data-testid="date-picker-toggle"]'))
      .nativeElement as HTMLButtonElement;

    expect(input.type).toBe('text');
    expect(input.value).toBe('05/02/2026');
    expect(input.placeholder).toBe('дд/мм/гггг');
    expect(input.getAttribute('aria-controls')).toBeNull();
    expect(input.getAttribute('aria-expanded')).toBeNull();
    expect(calendarButton.getAttribute('aria-label')).toBe('Открыть календарь');
  });

  it('marks the text field as required and invalid when requested', () => {
    fixture.componentRef.setInput('required', true);
    fixture.componentRef.setInput('invalid', true);
    fixture.detectChanges();

    const input = fixture.debugElement.query(By.css('#publishedFrom'))
      .nativeElement as HTMLInputElement;

    expect(input.required).toBe(true);
    expect(input.getAttribute('aria-required')).toBe('true');
    expect(input.classList).toContain('is-invalid');
  });

  it('emits ISO dates selected from the calendar', () => {
    const valueChange = jest.fn();
    fixture.componentInstance.valueChange.subscribe(valueChange);
    fixture.detectChanges();

    fixture.debugElement.query(By.css('[data-testid="date-picker-toggle"]')).nativeElement.click();
    fixture.detectChanges();
    fixture.debugElement.query(By.css('[data-date="2026-02-15"]')).nativeElement.click();
    fixture.detectChanges();

    expect(valueChange).toHaveBeenCalledWith('2026-02-15');
    expect(fixture.debugElement.query(By.css('[data-testid="date-picker-calendar"]'))).toBe(null);
  });

  it('positions the open calendar under the field as a viewport overlay', () => {
    Object.defineProperty(window, 'innerWidth', { configurable: true, value: 1024 });
    Object.defineProperty(window, 'innerHeight', { configurable: true, value: 768 });
    fixture.detectChanges();
    mockFieldRect({
      bottom: 132,
      height: 32,
      left: 80,
      right: 320,
      top: 100,
      width: 240,
      x: 80,
      y: 100,
      toJSON: () => ({}),
    });

    fixture.debugElement.query(By.css('[data-testid="date-picker-toggle"]')).nativeElement.click();
    fixture.detectChanges();

    const calendar = openCalendar();
    expect(calendar.style.position).toBe('fixed');
    expect(calendar.style.top).toBe('136px');
    expect(calendar.style.left).toBe('80px');
    expect(calendar.style.width).toBe('288px');
    expect(calendar.style.maxHeight).toBe('624px');
  });

  it('opens the calendar above the field when the viewport has more room above than below', () => {
    Object.defineProperty(window, 'innerWidth', { configurable: true, value: 1024 });
    Object.defineProperty(window, 'innerHeight', { configurable: true, value: 260 });
    fixture.detectChanges();
    mockFieldRect({
      bottom: 242,
      height: 32,
      left: 40,
      right: 280,
      top: 210,
      width: 240,
      x: 40,
      y: 210,
      toJSON: () => ({}),
    });

    fixture.debugElement.query(By.css('[data-testid="date-picker-toggle"]')).nativeElement.click();
    fixture.detectChanges();

    const calendar = openCalendar();
    expect(calendar.style.top).toBe('');
    expect(calendar.style.bottom).toBe('54px');
    expect(calendar.style.maxHeight).toBe('198px');
  });

  it('clamps the calendar horizontally inside narrow viewports', () => {
    Object.defineProperty(window, 'innerWidth', { configurable: true, value: 300 });
    Object.defineProperty(window, 'innerHeight', { configurable: true, value: 500 });
    fixture.detectChanges();
    mockFieldRect({
      bottom: 100,
      height: 32,
      left: 260,
      right: 300,
      top: 68,
      width: 40,
      x: 260,
      y: 68,
      toJSON: () => ({}),
    });

    fixture.debugElement.query(By.css('[data-testid="date-picker-toggle"]')).nativeElement.click();
    fixture.detectChanges();

    const calendar = openCalendar();
    expect(calendar.style.left).toBe('8px');
    expect(calendar.style.width).toBe('284px');
  });

  it('changes visible month and year inside the calendar before selecting a day', () => {
    const valueChange = jest.fn();
    fixture.componentInstance.valueChange.subscribe(valueChange);
    fixture.detectChanges();

    fixture.debugElement.query(By.css('[data-testid="date-picker-toggle"]')).nativeElement.click();
    fixture.detectChanges();

    const monthYearToggle = fixture.debugElement.query(
      By.css('[data-testid="date-picker-month-year-toggle"]'),
    );
    expect(monthYearToggle).not.toBeNull();

    monthYearToggle.nativeElement.click();
    fixture.detectChanges();

    const monthYearPanel = fixture.debugElement.query(
      By.css('[data-testid="date-picker-month-year-panel"]'),
    );
    expect(monthYearPanel).not.toBeNull();

    fixture.debugElement
      .query(By.css('[data-testid="date-picker-next-year"]'))
      .nativeElement.click();
    fixture.detectChanges();
    fixture.debugElement.query(By.css('[data-month-index="11"]')).nativeElement.click();
    fixture.detectChanges();

    expect(valueChange).not.toHaveBeenCalled();
    expect(fixture.debugElement.query(By.css('[data-testid="date-picker-month-year-panel"]'))).toBe(
      null,
    );

    fixture.debugElement.query(By.css('[data-date="2027-12-15"]')).nativeElement.click();
    fixture.detectChanges();

    expect(valueChange).toHaveBeenCalledWith('2027-12-15');
  });

  it('parses English month-first typed dates as ISO', () => {
    fixture.componentRef.setInput('value', '2026-03-04');
    fixture.componentRef.setInput('dateLocale', 'en-US');
    fixture.componentRef.setInput('placeholder', 'mm/dd/yyyy');
    const valueChange = jest.fn();
    fixture.componentInstance.valueChange.subscribe(valueChange);
    fixture.detectChanges();

    const input = fixture.debugElement.query(By.css('#publishedFrom'))
      .nativeElement as HTMLInputElement;

    expect(input.value).toBe('03/04/2026');
    expect(input.placeholder).toBe('mm/dd/yyyy');

    input.value = '03/31/2026';
    input.dispatchEvent(new Event('input'));

    expect(valueChange).toHaveBeenCalledWith('2026-03-31');
  });

  function mockFieldRect(rect: DOMRect): void {
    const field = fixture.nativeElement.querySelector('.input-group') as HTMLElement | null;
    expect(field).not.toBeNull();
    jest.spyOn(field as HTMLElement, 'getBoundingClientRect').mockReturnValue(rect);
  }

  function openCalendar(): HTMLElement {
    const calendar = fixture.debugElement.query(By.css('[data-testid="date-picker-calendar"]'))
      ?.nativeElement as HTMLElement | undefined;
    expect(calendar).toBeDefined();
    return calendar as HTMLElement;
  }
});
