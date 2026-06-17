import { Component, input, output } from '@angular/core';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { By } from '@angular/platform-browser';
import { of } from 'rxjs';
import { MarkdownEditorComponent } from '../../../../../../core/editor/markdown-editor.component';
import { WikiLinkTargetsService } from '../../../../../../core/wiki-links/wiki-link-targets.service';
import { MediaUploadService } from '../../../../../../core/uploads/media-upload.service';
import { provideI18nTesting } from '../../../../../../testing/i18n-testing';
import { ArticleWorkspaceService } from '../../../../services/article-workspace.service';
import { ArticleFormComponent } from './article-form.component';

describe('ArticleFormComponent', () => {
  let fixture: ComponentFixture<ArticleFormComponent>;
  let articlesService: {
    getTags: jest.Mock;
    createTag: jest.Mock;
    updateTag: jest.Mock;
    deleteTag: jest.Mock;
    restoreTag: jest.Mock;
  };
  let mediaUpload: { uploadMediaFile: jest.Mock };
  let wikiLinkTargetsService: { getTargets: jest.Mock };

  beforeEach(async () => {
    mediaUpload = {
      uploadMediaFile: jest.fn().mockReturnValue(of('https://cdn.example.com/cover.jpg')),
    };
    wikiLinkTargetsService = {
      getTargets: jest.fn().mockReturnValue(
        of(
          new Map([
            ['articles', new Set(['typed-article'])],
            ['matrix', new Set(['known-question'])],
          ]),
        ),
      ),
    };
    articlesService = {
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
      imports: [ArticleFormComponent],
      providers: [
        { provide: ArticleWorkspaceService, useValue: articlesService },
        { provide: MediaUploadService, useValue: mediaUpload },
        { provide: WikiLinkTargetsService, useValue: wikiLinkTargetsService },
        provideI18nTesting(),
      ],
    })
      .overrideComponent(ArticleFormComponent, {
        remove: { imports: [MarkdownEditorComponent] },
        add: { imports: [MarkdownEditorStubComponent] },
      })
      .compileComponents();

    fixture = TestBed.createComponent(ArticleFormComponent);
    fixture.componentRef.setInput('article', null);
    fixture.detectChanges();
  });

  it('suggests slug from title until slug is edited manually', () => {
    const title = fixture.debugElement.query(By.css('#articleTitleEn'))
      .nativeElement as HTMLInputElement;
    const slug = fixture.debugElement.query(By.css('#articleSlug'))
      .nativeElement as HTMLInputElement;

    title.value = 'New Angular article';
    title.dispatchEvent(new Event('input'));
    fixture.detectChanges();

    expect(slug.value).toBe('new-angular-article');

    slug.value = 'manual-slug';
    slug.dispatchEvent(new Event('input'));
    title.value = 'Another title';
    title.dispatchEvent(new Event('input'));
    fixture.detectChanges();

    expect(slug.value).toBe('manual-slug');
  });

  it('emits payload with selected active tags', () => {
    const titleRu = fixture.debugElement.query(By.css('#articleTitleRu'))
      .nativeElement as HTMLInputElement;
    const titleEn = fixture.debugElement.query(By.css('#articleTitleEn'))
      .nativeElement as HTMLInputElement;
    const contentEditors = fixture.debugElement.queryAll(By.directive(MarkdownEditorStubComponent));
    const saveSpy = jest.fn();
    fixture.componentInstance.articleSave.subscribe(saveSpy);

    titleRu.value = 'Типизированная статья';
    titleRu.dispatchEvent(new Event('input'));
    titleEn.value = 'Typed article';
    titleEn.dispatchEvent(new Event('input'));
    contentEditors[0].componentInstance.valueChange.emit('Содержимое');
    contentEditors[1].componentInstance.valueChange.emit('Content');
    const folderRu = fixture.debugElement.query(By.css('#articleFolderRu'))
      .nativeElement as HTMLInputElement;
    folderRu.value = 'Инженерия';
    folderRu.dispatchEvent(new Event('input'));
    const folderEn = fixture.debugElement.query(By.css('#articleFolderEn'))
      .nativeElement as HTMLInputElement;
    folderEn.value = 'Engineering';
    folderEn.dispatchEvent(new Event('input'));
    const seoTitleRu = fixture.debugElement.query(By.css('#articleSeoTitleRu'))
      .nativeElement as HTMLInputElement;
    seoTitleRu.value = 'SEO типизированная статья';
    seoTitleRu.dispatchEvent(new Event('input'));
    const seoTitleEn = fixture.debugElement.query(By.css('#articleSeoTitleEn'))
      .nativeElement as HTMLInputElement;
    seoTitleEn.value = 'SEO typed article';
    seoTitleEn.dispatchEvent(new Event('input'));
    const seoDescriptionRu = fixture.debugElement.query(By.css('#articleSeoDescriptionRu'))
      .nativeElement as HTMLTextAreaElement;
    seoDescriptionRu.value = 'Описание для поисковой выдачи';
    seoDescriptionRu.dispatchEvent(new Event('input'));
    const seoDescriptionEn = fixture.debugElement.query(By.css('#articleSeoDescriptionEn'))
      .nativeElement as HTMLTextAreaElement;
    seoDescriptionEn.value = 'Description for search results';
    seoDescriptionEn.dispatchEvent(new Event('input'));
    const coverImageUrl = fixture.debugElement.query(By.css('#articleCoverImageUrl'))
      .nativeElement as HTMLInputElement;
    coverImageUrl.value = 'https://example.com/cover.jpg';
    coverImageUrl.dispatchEvent(new Event('input'));
    const coverImageAltRu = fixture.debugElement.query(By.css('#articleCoverImageAltRu'))
      .nativeElement as HTMLInputElement;
    coverImageAltRu.value = 'Обложка';
    coverImageAltRu.dispatchEvent(new Event('input'));
    const coverImageAltEn = fixture.debugElement.query(By.css('#articleCoverImageAltEn'))
      .nativeElement as HTMLInputElement;
    coverImageAltEn.value = 'Cover';
    coverImageAltEn.dispatchEvent(new Event('input'));
    const tagCheckbox = fixture.debugElement.query(By.css('#articleTag-1'))
      .nativeElement as HTMLInputElement;
    tagCheckbox.click();
    fixture.detectChanges();

    const form = fixture.debugElement.query(By.css('form')).nativeElement as HTMLFormElement;
    form.dispatchEvent(new Event('submit'));

    expect(saveSpy).toHaveBeenCalledWith({
      slug: 'typed-article',
      publishStatus: 'Draft',
      tagIds: [1],
      metadata: {
        seoTitleRu: 'SEO типизированная статья',
        seoTitleEn: 'SEO typed article',
        seoDescriptionRu: 'Описание для поисковой выдачи',
        seoDescriptionEn: 'Description for search results',
        coverImageUrl: 'https://example.com/cover.jpg',
        coverImageAltRu: 'Обложка',
        coverImageAltEn: 'Cover',
      },
      translations: {
        ru: { title: 'Типизированная статья', content: 'Содержимое', folder: 'Инженерия' },
        en: { title: 'Typed article', content: 'Content', folder: 'Engineering' },
      },
    });
  });

  it('uploads cover image and writes access URL into the metadata field', () => {
    const fileInput = fixture.debugElement.query(By.css('#articleCoverImageFile'))
      .nativeElement as HTMLInputElement;
    const file = new File(['cover'], 'cover.png', { type: 'image/png' });
    Object.defineProperty(fileInput, 'files', { value: [file] });

    fileInput.dispatchEvent(new Event('change'));
    fixture.detectChanges();

    const coverImageUrl = fixture.debugElement.query(By.css('#articleCoverImageUrl'))
      .nativeElement as HTMLInputElement;
    expect(mediaUpload.uploadMediaFile).toHaveBeenCalledWith(file);
    expect(coverImageUrl.value).toBe('https://cdn.example.com/cover.jpg');
  });

  it('updates SEO analysis while editing localized fields', () => {
    const slug = fixture.debugElement.query(By.css('#articleSlug'))
      .nativeElement as HTMLInputElement;
    const titleRu = fixture.debugElement.query(By.css('#articleTitleRu'))
      .nativeElement as HTMLInputElement;
    const folderRu = fixture.debugElement.query(By.css('#articleFolderRu'))
      .nativeElement as HTMLInputElement;
    const contentEditors = fixture.debugElement.queryAll(By.directive(MarkdownEditorStubComponent));

    slug.value = 'typed-article';
    slug.dispatchEvent(new Event('input'));
    titleRu.value = 'Типизированная статья для поиска';
    titleRu.dispatchEvent(new Event('input'));
    folderRu.value = 'Инженерия';
    folderRu.dispatchEvent(new Event('input'));
    contentEditors[0].componentInstance.valueChange.emit(
      'Эта статья объясняет работу типизированных Angular форм, сигналов и локализованных полей в редакторе статей.',
    );
    fixture.detectChanges();

    const text = fixture.nativeElement.textContent as string;

    expect(text).toContain('SEO-анализ');
    expect(text).toContain('/articles/typed-article');
  });

  it('warns when typed wiki links point to missing targets', () => {
    const contentEditors = fixture.debugElement.queryAll(By.directive(MarkdownEditorStubComponent));

    contentEditors[0].componentInstance.valueChange.emit(
      'См. [[articles:typed-article]] и [[matrix:missing-question|отсутствующий вопрос]].',
    );
    fixture.detectChanges();

    const text = fixture.nativeElement.textContent as string;
    expect(text).toContain('matrix:missing-question');
  });

  it('renders active-language preview content with wiki links', () => {
    const titleRu = fixture.debugElement.query(By.css('#articleTitleRu'))
      .nativeElement as HTMLInputElement;
    const contentEditors = fixture.debugElement.queryAll(By.directive(MarkdownEditorStubComponent));

    titleRu.value = 'Предпросмотр статьи';
    titleRu.dispatchEvent(new Event('input'));
    contentEditors[0].componentInstance.valueChange.emit(
      'Откройте [[articles:typed-article|типизированную статью]].',
    );
    fixture.detectChanges();

    const preview = fixture.debugElement.query(By.css('.articles-preview-article'))
      .nativeElement as HTMLElement;
    const link = fixture.debugElement.query(By.css('.articles-preview-article a'))
      .nativeElement as HTMLAnchorElement;

    expect(preview.textContent).toContain('Предпросмотр статьи');
    expect(preview.textContent).toContain('типизированную статью');
    expect(link.getAttribute('href')).toBe('/ru/articles/typed-article');
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
