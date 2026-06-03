import { ComponentFixture, TestBed } from '@angular/core/testing';
import { By } from '@angular/platform-browser';
import { provideI18nTesting } from '../../../../../../testing/i18n-testing';
import { NoteAuthoringPreviewComponent } from './note-authoring-preview.component';

describe('NoteAuthoringPreviewComponent', () => {
  let fixture: ComponentFixture<NoteAuthoringPreviewComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [NoteAuthoringPreviewComponent],
      providers: [provideI18nTesting()],
    }).compileComponents();

    fixture = TestBed.createComponent(NoteAuthoringPreviewComponent);
    fixture.componentRef.setInput('title', 'Typed notes');
    fixture.componentRef.setInput('content', 'Read [[typed-note|typed note]].');
    fixture.componentRef.setInput('tags', [
      {
        id: 1,
        name: 'Angular',
        slug: 'angular',
        deletedAt: null,
        translations: { ru: { name: 'Angular' }, en: { name: 'Angular' } },
      },
    ]);
    fixture.componentRef.setInput('coverImageUrl', 'https://example.com/cover.jpg');
    fixture.componentRef.setInput('coverImageAlt', 'Cover alt');
    fixture.componentRef.setInput('seoTitle', 'SEO Typed notes');
    fixture.componentRef.setInput(
      'seoDescription',
      'SEO description for social cards and search snippets.',
    );
    fixture.componentRef.setInput('language', 'ru');
    fixture.detectChanges();
  });

  it('renders article content, tags, cover, and wiki links', () => {
    const text = fixture.nativeElement.textContent as string;
    const link = fixture.debugElement.query(By.css('.notes-preview-article a'))
      .nativeElement as HTMLAnchorElement;
    const cover = fixture.debugElement.query(By.css('.notes-preview-cover'))
      .nativeElement as HTMLImageElement;

    expect(text).toContain('Typed notes');
    expect(text).toContain('Angular');
    expect(link.getAttribute('href')).toBe('/ru/notes/typed-note');
    expect(cover.getAttribute('src')).toBe('https://example.com/cover.jpg');
    expect(cover.getAttribute('alt')).toBe('Cover alt');
  });

  it('renders social preview from SEO metadata', () => {
    const social = fixture.debugElement.query(By.css('.notes-social-preview'))
      .nativeElement as HTMLElement;

    expect(social.textContent).toContain('SEO Typed notes');
    expect(social.textContent).toContain('SEO description for social cards');
  });
});
