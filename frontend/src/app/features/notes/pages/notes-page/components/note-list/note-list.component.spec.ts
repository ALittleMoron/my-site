import { ComponentFixture, TestBed } from '@angular/core/testing';
import { By } from '@angular/platform-browser';
import { provideI18nTesting } from '../../../../../../testing/i18n-testing';
import { NoteListComponent } from './note-list.component';

describe('NoteListComponent', () => {
  let fixture: ComponentFixture<NoteListComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [NoteListComponent],
      providers: [provideI18nTesting()],
    }).compileComponents();
    fixture = TestBed.createComponent(NoteListComponent);
    fixture.componentRef.setInput('notes', [
      {
        id: '00000000-0000-0000-0000-000000000001',
        title: 'Typed notes',
        slug: 'typed-notes',
        folder: 'Engineering',
        authorUsername: 'admin',
        publishedAt: '2026-01-02T03:04:05+00:00',
        publishStatus: 'Published',
        updatedAt: '2026-01-03T03:04:05+00:00',
        excerpt: 'Excerpt',
        viewCount: 42,
        tags: [{ id: 1, name: 'Python', slug: 'python', deletedAt: null }],
      },
    ]);
    fixture.componentRef.setInput('page', 1);
    fixture.componentRef.setInput('totalPages', 1);
    fixture.componentRef.setInput('dateLocale', 'ru-RU');
    fixture.detectChanges();
  });

  it('renders public view count', () => {
    expect(fixture.nativeElement.textContent).toContain('42 просмотров');
  });

  it('emits note and tag selections', () => {
    const noteSelected = jest.fn();
    const tagSelected = jest.fn();
    fixture.componentInstance.noteSelected.subscribe(noteSelected);
    fixture.componentInstance.tagSelected.subscribe(tagSelected);

    fixture.debugElement.query(By.css('.notes-title-button')).nativeElement.click();
    fixture.debugElement.query(By.css('.btn-outline-secondary')).nativeElement.click();

    expect(noteSelected).toHaveBeenCalledWith('typed-notes');
    expect(tagSelected).toHaveBeenCalledWith('python');
  });
});
