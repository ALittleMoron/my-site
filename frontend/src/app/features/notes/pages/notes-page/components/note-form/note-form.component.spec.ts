import { Component, input, output } from '@angular/core';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { By } from '@angular/platform-browser';
import { of } from 'rxjs';
import { MarkdownEditorComponent } from '../../../../../../core/editor/markdown-editor.component';
import { MediaUploadService } from '../../../../../../core/uploads/media-upload.service';
import { provideI18nTesting } from '../../../../../../testing/i18n-testing';
import { NotesService } from '../../../../services/notes.service';
import { NoteFormComponent } from './note-form.component';

describe('NoteFormComponent', () => {
  let fixture: ComponentFixture<NoteFormComponent>;
  let notesService: {
    getTree: jest.Mock;
    getTags: jest.Mock;
    createTag: jest.Mock;
    updateTag: jest.Mock;
    deleteTag: jest.Mock;
    restoreTag: jest.Mock;
  };
  let mediaUpload: { uploadMediaFile: jest.Mock };

  beforeEach(async () => {
    mediaUpload = {
      uploadMediaFile: jest.fn().mockReturnValue(of('https://cdn.example.com/cover.jpg')),
    };
    notesService = {
      getTree: jest.fn().mockReturnValue(
        of({
          folders: [
            {
              folder: 'Engineering',
              notes: [
                {
                  title: 'Typed note',
                  slug: 'typed-note',
                  publishStatus: 'Published',
                  publishedAt: '2026-01-02T03:04:05+00:00',
                  updatedAt: '2026-01-03T03:04:05+00:00',
                },
              ],
            },
          ],
        }),
      ),
      getTags: jest.fn().mockReturnValue(
        of([
          tag({ id: 1, name: 'Python', slug: 'python', deletedAt: null }),
          tag({
            id: 2,
            name: 'Old',
            slug: 'old',
            deletedAt: '2026-01-04T03:04:05+00:00',
          }),
        ]),
      ),
      createTag: jest
        .fn()
        .mockReturnValue(of(tag({ id: 3, name: 'Backend', slug: 'backend', deletedAt: null }))),
      updateTag: jest
        .fn()
        .mockReturnValue(of(tag({ id: 1, name: 'Py', slug: 'py', deletedAt: null }))),
      deleteTag: jest.fn().mockReturnValue(of(undefined)),
      restoreTag: jest.fn().mockReturnValue(of(undefined)),
    };

    await TestBed.configureTestingModule({
      imports: [NoteFormComponent],
      providers: [
        { provide: NotesService, useValue: notesService },
        { provide: MediaUploadService, useValue: mediaUpload },
        provideI18nTesting(),
      ],
    })
      .overrideComponent(NoteFormComponent, {
        remove: { imports: [MarkdownEditorComponent] },
        add: { imports: [MarkdownEditorStubComponent] },
      })
      .compileComponents();

    fixture = TestBed.createComponent(NoteFormComponent);
    fixture.componentRef.setInput('note', null);
    fixture.detectChanges();
  });

  it('suggests slug from title until slug is edited manually', () => {
    const title = fixture.debugElement.query(By.css('#noteTitleEn'))
      .nativeElement as HTMLInputElement;
    const slug = fixture.debugElement.query(By.css('#noteSlug')).nativeElement as HTMLInputElement;

    title.value = 'New Angular note';
    title.dispatchEvent(new Event('input'));
    fixture.detectChanges();

    expect(slug.value).toBe('new-angular-note');

    slug.value = 'manual-slug';
    slug.dispatchEvent(new Event('input'));
    title.value = 'Another title';
    title.dispatchEvent(new Event('input'));
    fixture.detectChanges();

    expect(slug.value).toBe('manual-slug');
  });

  it('emits payload with selected active tags', () => {
    const titleRu = fixture.debugElement.query(By.css('#noteTitleRu'))
      .nativeElement as HTMLInputElement;
    const titleEn = fixture.debugElement.query(By.css('#noteTitleEn'))
      .nativeElement as HTMLInputElement;
    const contentEditors = fixture.debugElement.queryAll(By.directive(MarkdownEditorStubComponent));
    const saveSpy = jest.fn();
    fixture.componentInstance.noteSave.subscribe(saveSpy);

    titleRu.value = 'Типизированная заметка';
    titleRu.dispatchEvent(new Event('input'));
    titleEn.value = 'Typed note';
    titleEn.dispatchEvent(new Event('input'));
    contentEditors[0].componentInstance.valueChange.emit('Содержимое');
    contentEditors[1].componentInstance.valueChange.emit('Content');
    const folderRu = fixture.debugElement.query(By.css('#noteFolderRu'))
      .nativeElement as HTMLInputElement;
    folderRu.value = 'Инженерия';
    folderRu.dispatchEvent(new Event('input'));
    const folderEn = fixture.debugElement.query(By.css('#noteFolderEn'))
      .nativeElement as HTMLInputElement;
    folderEn.value = 'Engineering';
    folderEn.dispatchEvent(new Event('input'));
    const seoTitleRu = fixture.debugElement.query(By.css('#noteSeoTitleRu'))
      .nativeElement as HTMLInputElement;
    seoTitleRu.value = 'SEO типизированная заметка';
    seoTitleRu.dispatchEvent(new Event('input'));
    const seoTitleEn = fixture.debugElement.query(By.css('#noteSeoTitleEn'))
      .nativeElement as HTMLInputElement;
    seoTitleEn.value = 'SEO typed note';
    seoTitleEn.dispatchEvent(new Event('input'));
    const seoDescriptionRu = fixture.debugElement.query(By.css('#noteSeoDescriptionRu'))
      .nativeElement as HTMLTextAreaElement;
    seoDescriptionRu.value = 'Описание для поисковой выдачи';
    seoDescriptionRu.dispatchEvent(new Event('input'));
    const seoDescriptionEn = fixture.debugElement.query(By.css('#noteSeoDescriptionEn'))
      .nativeElement as HTMLTextAreaElement;
    seoDescriptionEn.value = 'Description for search results';
    seoDescriptionEn.dispatchEvent(new Event('input'));
    const coverImageUrl = fixture.debugElement.query(By.css('#noteCoverImageUrl'))
      .nativeElement as HTMLInputElement;
    coverImageUrl.value = 'https://example.com/cover.jpg';
    coverImageUrl.dispatchEvent(new Event('input'));
    const coverImageAltRu = fixture.debugElement.query(By.css('#noteCoverImageAltRu'))
      .nativeElement as HTMLInputElement;
    coverImageAltRu.value = 'Обложка';
    coverImageAltRu.dispatchEvent(new Event('input'));
    const coverImageAltEn = fixture.debugElement.query(By.css('#noteCoverImageAltEn'))
      .nativeElement as HTMLInputElement;
    coverImageAltEn.value = 'Cover';
    coverImageAltEn.dispatchEvent(new Event('input'));
    const tagCheckbox = fixture.debugElement.query(By.css('#noteTag-1'))
      .nativeElement as HTMLInputElement;
    tagCheckbox.click();
    fixture.detectChanges();

    const form = fixture.debugElement.query(By.css('form')).nativeElement as HTMLFormElement;
    form.dispatchEvent(new Event('submit'));

    expect(saveSpy).toHaveBeenCalledWith({
      slug: 'typed-note',
      publishStatus: 'Draft',
      tagIds: [1],
      metadata: {
        seoTitleRu: 'SEO типизированная заметка',
        seoTitleEn: 'SEO typed note',
        seoDescriptionRu: 'Описание для поисковой выдачи',
        seoDescriptionEn: 'Description for search results',
        coverImageUrl: 'https://example.com/cover.jpg',
        coverImageAltRu: 'Обложка',
        coverImageAltEn: 'Cover',
      },
      translations: {
        ru: { title: 'Типизированная заметка', content: 'Содержимое', folder: 'Инженерия' },
        en: { title: 'Typed note', content: 'Content', folder: 'Engineering' },
      },
    });
  });

  it('uploads cover image and writes access URL into the metadata field', () => {
    const fileInput = fixture.debugElement.query(By.css('#noteCoverImageFile'))
      .nativeElement as HTMLInputElement;
    const file = new File(['cover'], 'cover.png', { type: 'image/png' });
    Object.defineProperty(fileInput, 'files', { value: [file] });

    fileInput.dispatchEvent(new Event('change'));
    fixture.detectChanges();

    const coverImageUrl = fixture.debugElement.query(By.css('#noteCoverImageUrl'))
      .nativeElement as HTMLInputElement;
    expect(mediaUpload.uploadMediaFile).toHaveBeenCalledWith(file);
    expect(coverImageUrl.value).toBe('https://cdn.example.com/cover.jpg');
  });

  it('updates SEO analysis while editing localized fields', () => {
    const slug = fixture.debugElement.query(By.css('#noteSlug')).nativeElement as HTMLInputElement;
    const titleRu = fixture.debugElement.query(By.css('#noteTitleRu'))
      .nativeElement as HTMLInputElement;
    const folderRu = fixture.debugElement.query(By.css('#noteFolderRu'))
      .nativeElement as HTMLInputElement;
    const contentEditors = fixture.debugElement.queryAll(By.directive(MarkdownEditorStubComponent));

    slug.value = 'typed-note';
    slug.dispatchEvent(new Event('input'));
    titleRu.value = 'Типизированная заметка для поиска';
    titleRu.dispatchEvent(new Event('input'));
    folderRu.value = 'Инженерия';
    folderRu.dispatchEvent(new Event('input'));
    contentEditors[0].componentInstance.valueChange.emit(
      'Эта заметка объясняет работу типизированных Angular форм, сигналов и локализованных полей в редакторе заметок.',
    );
    fixture.detectChanges();

    const text = fixture.nativeElement.textContent as string;

    expect(text).toContain('SEO-анализ');
    expect(text).toContain('/notes/typed-note');
  });

  it('warns when wiki links point to missing note slugs', () => {
    const contentEditors = fixture.debugElement.queryAll(By.directive(MarkdownEditorStubComponent));

    contentEditors[0].componentInstance.valueChange.emit(
      'См. [[typed-note]] и [[missing-note|отсутствующую заметку]].',
    );
    fixture.detectChanges();

    const text = fixture.nativeElement.textContent as string;
    expect(text).toContain('missing-note');
  });

  it('renders active-language preview content with wiki links', () => {
    const titleRu = fixture.debugElement.query(By.css('#noteTitleRu'))
      .nativeElement as HTMLInputElement;
    const contentEditors = fixture.debugElement.queryAll(By.directive(MarkdownEditorStubComponent));

    titleRu.value = 'Предпросмотр заметки';
    titleRu.dispatchEvent(new Event('input'));
    contentEditors[0].componentInstance.valueChange.emit(
      'Откройте [[typed-note|типизированную заметку]].',
    );
    fixture.detectChanges();

    const preview = fixture.debugElement.query(By.css('.notes-preview-article'))
      .nativeElement as HTMLElement;
    const link = fixture.debugElement.query(By.css('.notes-preview-article a'))
      .nativeElement as HTMLAnchorElement;

    expect(preview.textContent).toContain('Предпросмотр заметки');
    expect(preview.textContent).toContain('типизированную заметку');
    expect(link.getAttribute('href')).toBe('/notes/typed-note');
  });
});

@Component({
  selector: 'app-markdown-editor',
  standalone: true,
  template: '',
})
class MarkdownEditorStubComponent {
  readonly value = input<string>('');
  readonly valueChange = output<string>();
}

function tag(params: {
  id: number;
  name: string;
  slug: string;
  deletedAt: string | null;
}): unknown {
  return {
    ...params,
    translations: {
      ru: { name: params.name },
      en: { name: params.name },
    },
  };
}
