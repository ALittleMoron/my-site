import {
  ChangeDetectionStrategy,
  Component,
  HostListener,
  computed,
  effect,
  input,
  output,
  signal,
} from '@angular/core';

interface CalendarCell {
  iso: string;
  label: string;
  ariaLabel: string;
  selected: boolean;
  today: boolean;
}

const DATE_SEPARATOR_PATTERN = /[./-]/;
let nextCalendarId = 0;

@Component({
  selector: 'app-localized-date-picker',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './localized-date-picker.component.html',
  styleUrl: './localized-date-picker.component.scss',
})
export class LocalizedDatePickerComponent {
  readonly inputId = input.required<string>();
  readonly value = input.required<string>();
  readonly dateLocale = input.required<string>();
  readonly placeholder = input.required<string>();
  readonly openCalendarLabel = input.required<string>();
  readonly previousMonthLabel = input.required<string>();
  readonly nextMonthLabel = input.required<string>();

  readonly valueChange = output<string>();

  readonly calendarOpen = signal(false);
  readonly displayValue = signal('');
  readonly visibleMonth = signal(startOfMonth(new Date()));
  readonly calendarId = `localizedDatePicker${nextCalendarId++}`;
  readonly monthLabel = computed(() =>
    new Intl.DateTimeFormat(this.dateLocale(), { month: 'long', year: 'numeric' }).format(
      this.visibleMonth(),
    ),
  );
  readonly weekdayLabels = computed(() => weekdayLabels(this.dateLocale()));
  readonly calendarCells = computed(() =>
    calendarCells({
      month: this.visibleMonth(),
      selectedIso: this.value(),
      dateLocale: this.dateLocale(),
    }),
  );

  private readonly valueSyncEffect = effect(() => {
    const value = this.value();
    this.displayValue.set(formatDateForLocale(value, this.dateLocale()));
    const parsed = parseIsoDate(value);
    if (parsed !== null) {
      this.visibleMonth.set(startOfMonth(parsed));
    }
  });

  toggleCalendar(): void {
    this.calendarOpen.update((open) => !open);
  }

  showPreviousMonth(): void {
    this.visibleMonth.update((month) => new Date(month.getFullYear(), month.getMonth() - 1, 1));
  }

  showNextMonth(): void {
    this.visibleMonth.update((month) => new Date(month.getFullYear(), month.getMonth() + 1, 1));
  }

  selectDate(iso: string): void {
    this.valueChange.emit(iso);
    this.displayValue.set(formatDateForLocale(iso, this.dateLocale()));
    this.calendarOpen.set(false);
  }

  onTextInput(event: Event): void {
    const value = readInputValue(event);
    this.displayValue.set(value);
    const parsed = parseDateForLocale(value, this.dateLocale());
    if (parsed !== null) {
      this.valueChange.emit(parsed);
    }
  }

  onTextBlur(): void {
    const parsed = parseDateForLocale(this.displayValue(), this.dateLocale());
    if (parsed === null) {
      this.displayValue.set(formatDateForLocale(this.value(), this.dateLocale()));
    }
  }

  @HostListener('keydown.escape')
  closeCalendar(): void {
    this.calendarOpen.set(false);
  }
}

function readInputValue(event: Event): string {
  return (event.target as HTMLInputElement).value;
}

function weekdayLabels(dateLocale: string): string[] {
  const sunday = new Date(2026, 1, 1);
  const labels = Array.from({ length: 7 }, (_, index) =>
    new Intl.DateTimeFormat(dateLocale, { weekday: 'short' }).format(
      new Date(sunday.getFullYear(), sunday.getMonth(), sunday.getDate() + index),
    ),
  );
  return isEnglishLocale(dateLocale) ? labels : [...labels.slice(1), labels[0]];
}

function calendarCells(params: {
  month: Date;
  selectedIso: string;
  dateLocale: string;
}): (CalendarCell | null)[] {
  const year = params.month.getFullYear();
  const month = params.month.getMonth();
  const firstDay = new Date(year, month, 1);
  const startOffset = weekStartOffset(firstDay.getDay(), params.dateLocale);
  const daysInMonth = new Date(year, month + 1, 0).getDate();
  const cells: (CalendarCell | null)[] = Array.from({ length: startOffset }, () => null);
  const todayIso = datePartsToIso(
    new Date().getFullYear(),
    new Date().getMonth(),
    new Date().getDate(),
  );

  for (let day = 1; day <= daysInMonth; day += 1) {
    const iso = datePartsToIso(year, month, day);
    const date = new Date(year, month, day);
    cells.push({
      iso,
      label: String(day),
      ariaLabel: new Intl.DateTimeFormat(params.dateLocale, { dateStyle: 'long' }).format(date),
      selected: iso === params.selectedIso,
      today: iso === todayIso,
    });
  }

  return cells;
}

function weekStartOffset(day: number, dateLocale: string): number {
  if (isEnglishLocale(dateLocale)) return day;
  return day === 0 ? 6 : day - 1;
}

function formatDateForLocale(value: string, dateLocale: string): string {
  if (value === '') return '';
  const date = parseIsoDate(value);
  if (date === null) return value;
  const day = padDatePart(date.getDate());
  const month = padDatePart(date.getMonth() + 1);
  const year = String(date.getFullYear());
  return isEnglishLocale(dateLocale) ? `${month}/${day}/${year}` : `${day}/${month}/${year}`;
}

function parseDateForLocale(value: string, dateLocale: string): string | null {
  const normalized = value.trim();
  if (normalized === '') return '';
  const parts = normalized.split(DATE_SEPARATOR_PATTERN);
  if (parts.length !== 3) return null;
  const first = Number(parts[0]);
  const second = Number(parts[1]);
  const year = Number(parts[2]);
  if (!Number.isInteger(first) || !Number.isInteger(second) || !Number.isInteger(year)) return null;
  const month = isEnglishLocale(dateLocale) ? first : second;
  const day = isEnglishLocale(dateLocale) ? second : first;
  if (!isValidDateParts(year, month, day)) return null;
  return `${year}-${padDatePart(month)}-${padDatePart(day)}`;
}

function parseIsoDate(value: string): Date | null {
  const parts = value.split('-');
  if (parts.length !== 3) return null;
  const year = Number(parts[0]);
  const month = Number(parts[1]);
  const day = Number(parts[2]);
  if (!isValidDateParts(year, month, day)) return null;
  return new Date(year, month - 1, day);
}

function isValidDateParts(year: number, month: number, day: number): boolean {
  const date = new Date(year, month - 1, day);
  return (
    Number.isInteger(year) &&
    Number.isInteger(month) &&
    Number.isInteger(day) &&
    date.getFullYear() === year &&
    date.getMonth() === month - 1 &&
    date.getDate() === day
  );
}

function startOfMonth(date: Date): Date {
  return new Date(date.getFullYear(), date.getMonth(), 1);
}

function datePartsToIso(year: number, monthIndex: number, day: number): string {
  return `${year}-${padDatePart(monthIndex + 1)}-${padDatePart(day)}`;
}

function isEnglishLocale(dateLocale: string): boolean {
  return dateLocale.toLowerCase().startsWith('en');
}

function padDatePart(value: number): string {
  return String(value).padStart(2, '0');
}
