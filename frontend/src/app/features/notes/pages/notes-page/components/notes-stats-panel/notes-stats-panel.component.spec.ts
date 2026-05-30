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

    const dateInput = fixture.debugElement.query(By.css('input[type="date"]'))
      .nativeElement as HTMLInputElement;
    dateInput.value = '2026-01-02';
    dateInput.dispatchEvent(new Event('input'));
    fixture.debugElement.query(By.css('button')).nativeElement.click();

    expect(dateFromChange).toHaveBeenCalledWith('2026-01-02');
    expect(refresh).toHaveBeenCalled();
  });
});
