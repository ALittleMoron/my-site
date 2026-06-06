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
    fixture.componentRef.setInput('openCalendarLabel', 'Открыть календарь');
    fixture.componentRef.setInput('previousMonthLabel', 'Предыдущий месяц');
    fixture.componentRef.setInput('nextMonthLabel', 'Следующий месяц');
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
    expect(calendarButton.getAttribute('aria-label')).toBe('Открыть календарь');
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
});
