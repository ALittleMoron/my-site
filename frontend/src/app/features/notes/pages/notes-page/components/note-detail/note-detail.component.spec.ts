import { ComponentFixture, TestBed } from '@angular/core/testing';
import { By } from '@angular/platform-browser';
import { provideI18nTesting } from '../../../../../../testing/i18n-testing';
import { NoteDetailComponent } from './note-detail.component';

describe('NoteDetailComponent', () => {
  let fixture: ComponentFixture<NoteDetailComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [NoteDetailComponent],
      providers: [provideI18nTesting()],
    }).compileComponents();
    fixture = TestBed.createComponent(NoteDetailComponent);
    fixture.componentRef.setInput('note', {
      id: '00000000-0000-0000-0000-000000000001',
      title: 'Typed notes',
      slug: 'typed-notes',
      folder: 'Engineering',
      authorUsername: 'admin',
      publishedAt: '2026-01-02T03:04:05+00:00',
      publishStatus: 'Published',
      createdAt: '2026-01-01T03:04:05+00:00',
      updatedAt: '2026-01-03T03:04:05+00:00',
      excerpt: 'Excerpt',
      content: '# Content',
      viewCount: 42,
      reactionCounts: { heart: 1, fire: 2, thinking: 3, neutral: 4, poop: 5 },
      tags: [{ id: 1, name: 'Python', slug: 'python', deletedAt: null }],
    });
    fixture.componentRef.setInput('selectedReaction', 'poop');
    fixture.componentRef.setInput('dateLocale', 'ru-RU');
    fixture.detectChanges();
  });

  it('renders public view count and reaction counts', () => {
    const text = fixture.nativeElement.textContent as string;

    expect(text).toContain('42 просмотров');
    expect(text).toContain('5');
  });

  it('emits selected reaction', () => {
    const reactionSelected = jest.fn();
    fixture.componentInstance.reactionSelected.subscribe(reactionSelected);

    const heartButton = fixture.debugElement.query(By.css('[aria-label="Понравилось"]'));
    heartButton.nativeElement.click();

    expect(reactionSelected).toHaveBeenCalledWith('heart');
  });
});
