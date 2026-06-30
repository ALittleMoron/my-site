import { Component, input, output } from '@angular/core';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { By } from '@angular/platform-browser';
import { of } from 'rxjs';
import { MarkdownEditorComponent } from '../../../../../../core/editor/markdown-editor.component';
import { WikiLinkTargetsService } from '../../../../../../core/wiki-links/wiki-link-targets.service';
import { MediaUploadService } from '../../../../../../core/uploads/media-upload.service';
import { provideI18nTesting } from '../../../../../../testing/i18n-testing';
import { ArticleWorkspaceService } from '../../../../services/article-workspace.service';
import { ArticleDetail } from '../../../../models/article-workspace.model';
import { ArticleFormComponent } from './article-form.component';

const INVALID_SHORT_TEXT = 'x'.repeat(256);
const INVALID_SEO_DESCRIPTION = 'x'.repeat(321);
const INVALID_ARTICLE_CONTENT = 'x'.repeat(100_001);

interface ArticleValidationCase {
  description: string;
  selector: string;
  expectedMessage: string;
  setInvalidValue: () => void;
  invalidClass?: string;
}

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

  it('refreshes form values when a different article input is loaded', () => {
    fixture.componentRef.setInput('article', articleDetail('first-article', 'First article'));
    fixture.detectChanges();

    expect(elementValue('#articleSlug')).toBe('first-article');
    expect(elementValue('#articleTitleEn')).toBe('First article');

    fixture.componentRef.setInput('article', articleDetail('second-article', 'Second article'));
    fixture.detectChanges();

    expect(elementValue('#articleSlug')).toBe('second-article');
    expect(elementValue('#articleTitleEn')).toBe('Second article');
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

  it('marks required article fields and blocks empty submit', () => {
    const saveSpy = jest.fn();
    fixture.componentInstance.articleSave.subscribe(saveSpy);

    const form = fixture.debugElement.query(By.css('form')).nativeElement as HTMLFormElement;
    const slug = fixture.debugElement.query(By.css('#articleSlug'))
      .nativeElement as HTMLInputElement;
    const titleRu = fixture.debugElement.query(By.css('#articleTitleRu'))
      .nativeElement as HTMLInputElement;
    const contentRuEditor = fixture.nativeElement.querySelector(
      '[data-testid="article-content-ru-editor"]',
    ) as HTMLElement | null;

    expect(fixture.nativeElement.textContent).toContain('Slug *');
    expect(fixture.nativeElement.textContent).toContain('Заголовок RU *');
    expect(fixture.nativeElement.textContent).toContain('Папка RU *');
    expect(fixture.nativeElement.textContent).toContain('Содержимое RU *');
    expect(contentRuEditor).not.toBeNull();

    form.dispatchEvent(new Event('submit'));
    fixture.detectChanges();

    expect(saveSpy).not.toHaveBeenCalled();
    expect(slug.classList).toContain('is-invalid');
    expect(titleRu.classList).toContain('is-invalid');
    expect(contentRuEditor?.classList).toContain('article-markdown-editor-invalid');

    slug.value = 'typed-article';
    slug.dispatchEvent(new Event('input'));
    fixture.detectChanges();

    expect(slug.classList).not.toContain('is-invalid');
  });

  it.each<ArticleValidationCase>([
    {
      description: 'article slug pattern',
      selector: '#articleSlug',
      expectedMessage: 'Используйте строчные латинские буквы, цифры и одинарные дефисы.',
      setInvalidValue: () => setInput('#articleSlug', 'Invalid Slug'),
    },
    {
      description: 'RU title required text',
      selector: '#articleTitleRu',
      expectedMessage: 'Заполните поле.',
      setInvalidValue: () => setInput('#articleTitleRu', '   '),
    },
    {
      description: 'RU folder max length',
      selector: '#articleFolderRu',
      expectedMessage: 'Максимум 255 символов.',
      setInvalidValue: () => setInput('#articleFolderRu', INVALID_SHORT_TEXT),
    },
    {
      description: 'RU content required text',
      selector: '[data-testid="article-content-ru-editor"]',
      expectedMessage: 'Заполните поле.',
      invalidClass: 'is-invalid',
      setInvalidValue: () => setArticleContent('ru', '   '),
    },
    {
      description: 'EN title required text',
      selector: '#articleTitleEn',
      expectedMessage: 'Заполните поле.',
      setInvalidValue: () => setInput('#articleTitleEn', '   '),
    },
    {
      description: 'EN folder max length',
      selector: '#articleFolderEn',
      expectedMessage: 'Максимум 255 символов.',
      setInvalidValue: () => setInput('#articleFolderEn', INVALID_SHORT_TEXT),
    },
    {
      description: 'EN content max length',
      selector: '[data-testid="article-content-en-editor"]',
      expectedMessage: 'Максимум 100000 символов.',
      invalidClass: 'is-invalid',
      setInvalidValue: () => setArticleContent('en', INVALID_ARTICLE_CONTENT),
    },
    {
      description: 'RU SEO title max length',
      selector: '#articleSeoTitleRu',
      expectedMessage: 'Максимум 255 символов.',
      setInvalidValue: () => setInput('#articleSeoTitleRu', INVALID_SHORT_TEXT),
    },
    {
      description: 'EN SEO title max length',
      selector: '#articleSeoTitleEn',
      expectedMessage: 'Максимум 255 символов.',
      setInvalidValue: () => setInput('#articleSeoTitleEn', INVALID_SHORT_TEXT),
    },
    {
      description: 'RU SEO description max length',
      selector: '#articleSeoDescriptionRu',
      expectedMessage: 'Максимум 320 символов.',
      setInvalidValue: () => setInput('#articleSeoDescriptionRu', INVALID_SEO_DESCRIPTION),
    },
    {
      description: 'EN SEO description max length',
      selector: '#articleSeoDescriptionEn',
      expectedMessage: 'Максимум 320 символов.',
      setInvalidValue: () => setInput('#articleSeoDescriptionEn', INVALID_SEO_DESCRIPTION),
    },
    {
      description: 'cover image URL scheme',
      selector: '#articleCoverImageUrl',
      expectedMessage: 'Укажите ссылку с http или https.',
      setInvalidValue: () => setInput('#articleCoverImageUrl', 'ftp://example.com/cover.jpg'),
    },
    {
      description: 'RU cover alt max length',
      selector: '#articleCoverImageAltRu',
      expectedMessage: 'Максимум 255 символов.',
      setInvalidValue: () => setInput('#articleCoverImageAltRu', INVALID_SHORT_TEXT),
    },
    {
      description: 'EN cover alt max length',
      selector: '#articleCoverImageAltEn',
      expectedMessage: 'Максимум 255 символов.',
      setInvalidValue: () => setInput('#articleCoverImageAltEn', INVALID_SHORT_TEXT),
    },
  ])('shows invalid styling and localized feedback for $description', (validationCase) => {
    const saveSpy = jest.fn();
    fixture.componentInstance.articleSave.subscribe(saveSpy);
    fillValidArticleMinimum();
    validationCase.setInvalidValue();

    submitArticleForm();

    expect(saveSpy).not.toHaveBeenCalled();
    expectInvalidControl(
      validationCase.selector,
      validationCase.expectedMessage,
      validationCase.invalidClass,
    );
  });

  it('marks the hidden language tab that contains an invalid article field', () => {
    fillValidArticleMinimum();
    setInput('#articleTitleEn', '   ');
    fixture.componentInstance.setActiveLanguageTab('ru');
    fixture.detectChanges();

    submitArticleForm();

    const englishTab = buttonByText('Английский');
    expect(englishTab.classList).toContain('text-danger');
    expect(englishTab.getAttribute('aria-invalid')).toBe('true');
    expect(englishTab.textContent).toContain('!');
    expectInvalidControl('#articleTitleEn', 'Заполните поле.');
  });

  it('keeps whitespace-only required article fields invalid', () => {
    const saveSpy = jest.fn();
    fixture.componentInstance.articleSave.subscribe(saveSpy);
    const slug = fixture.debugElement.query(By.css('#articleSlug'))
      .nativeElement as HTMLInputElement;

    slug.value = '   ';
    slug.dispatchEvent(new Event('input'));
    fixture.debugElement.query(By.css('form')).nativeElement.dispatchEvent(new Event('submit'));
    fixture.detectChanges();

    expect(saveSpy).not.toHaveBeenCalled();
    expect(slug.classList).toContain('is-invalid');
  });

  it('blocks invalid article slug, cover URL, and content length violations', () => {
    const saveSpy = jest.fn();
    fixture.componentInstance.articleSave.subscribe(saveSpy);
    fillValidArticleMinimum();
    setInput('#articleSlug', 'Invalid Slug');

    submitArticleForm();

    expect(saveSpy).not.toHaveBeenCalled();

    setInput('#articleSlug', 'typed-article');
    setInput('#articleCoverImageUrl', 'ftp://example.com/cover.jpg');

    submitArticleForm();

    expect(saveSpy).not.toHaveBeenCalled();

    setInput('#articleCoverImageUrl', 'https://example.com/cover.jpg');
    const contentEditors = fixture.debugElement.queryAll(By.directive(MarkdownEditorStubComponent));
    contentEditors[1].componentInstance.valueChange.emit('x'.repeat(100_001));
    fixture.detectChanges();

    submitArticleForm();

    expect(saveSpy).not.toHaveBeenCalled();
  });

  it('marks required new-tag fields and blocks empty tag creation', () => {
    const nameRu = fixture.debugElement.query(By.css('#newTagNameRu'))
      .nativeElement as HTMLInputElement;
    const addButton = fixture.debugElement.query(By.css('[data-testid="article-new-tag-add"]'));

    expect(fixture.nativeElement.textContent).toContain('Название RU *');
    expect(fixture.nativeElement.textContent).toContain('Название EN *');
    expect(fixture.nativeElement.textContent).toContain('Slug *');
    expect(addButton).not.toBeNull();
    if (addButton === null) return;

    (addButton.nativeElement as HTMLButtonElement).click();
    fixture.detectChanges();

    expect(articlesService.createTag).not.toHaveBeenCalled();
    expect(nameRu.classList).toContain('is-invalid');

    nameRu.value = 'Backend';
    nameRu.dispatchEvent(new Event('input'));
    fixture.detectChanges();

    expect(nameRu.classList).not.toContain('is-invalid');
  });

  it.each<ArticleValidationCase>([
    {
      description: 'new tag RU name required text',
      selector: '#newTagNameRu',
      expectedMessage: 'Заполните поле.',
      setInvalidValue: () => {
        setInput('#newTagNameEn', 'Backend');
        setInput('#newTagSlug', 'backend');
      },
    },
    {
      description: 'new tag EN name max length',
      selector: '#newTagNameEn',
      expectedMessage: 'Максимум 255 символов.',
      setInvalidValue: () => {
        setInput('#newTagNameRu', 'Бэкенд');
        setInput('#newTagNameEn', INVALID_SHORT_TEXT);
        setInput('#newTagSlug', 'backend');
      },
    },
    {
      description: 'new tag slug pattern',
      selector: '#newTagSlug',
      expectedMessage: 'Используйте строчные латинские буквы, цифры и одинарные дефисы.',
      setInvalidValue: () => {
        setInput('#newTagNameRu', 'Бэкенд');
        setInput('#newTagNameEn', 'Backend');
        setInput('#newTagSlug', 'Backend Tag');
      },
    },
  ])('shows invalid styling and localized feedback for $description', (validationCase) => {
    validationCase.setInvalidValue();

    fixture.debugElement.query(By.css('[data-testid="article-new-tag-add"]')).nativeElement.click();
    fixture.detectChanges();

    expect(articlesService.createTag).not.toHaveBeenCalled();
    expectInvalidControl(validationCase.selector, validationCase.expectedMessage);
  });

  it.each<ArticleValidationCase>([
    {
      description: 'inline tag RU name required text',
      selector: '[data-testid="article-tag-1-name-ru"]',
      expectedMessage: 'Заполните поле.',
      setInvalidValue: () => setInput('[data-testid="article-tag-1-name-ru"]', '   '),
    },
    {
      description: 'inline tag EN name max length',
      selector: '[data-testid="article-tag-1-name-en"]',
      expectedMessage: 'Максимум 255 символов.',
      setInvalidValue: () => setInput('[data-testid="article-tag-1-name-en"]', INVALID_SHORT_TEXT),
    },
    {
      description: 'inline tag slug pattern',
      selector: '[data-testid="article-tag-1-slug"]',
      expectedMessage: 'Используйте строчные латинские буквы, цифры и одинарные дефисы.',
      setInvalidValue: () => setInput('[data-testid="article-tag-1-slug"]', 'Python Tag'),
    },
  ])('shows invalid styling and localized feedback for $description', (validationCase) => {
    validationCase.setInvalidValue();

    fixture.nativeElement
      .querySelector<HTMLButtonElement>('[data-testid="article-tag-1-save"]')
      ?.click();
    fixture.detectChanges();

    expect(articlesService.updateTag).not.toHaveBeenCalled();
    expectInvalidControl(validationCase.selector, validationCase.expectedMessage);
  });

  it('blocks invalid new and inline tag edits', () => {
    setInput('#newTagNameRu', 'Бэкенд');
    setInput('#newTagNameEn', 'Backend');
    setInput('#newTagSlug', 'Backend Tag');

    fixture.debugElement.query(By.css('[data-testid="article-new-tag-add"]')).nativeElement.click();
    fixture.detectChanges();

    expect(articlesService.createTag).not.toHaveBeenCalled();

    const inlineSlug = fixture.nativeElement.querySelector(
      '[data-testid="article-tag-1-slug"]',
    ) as HTMLInputElement | null;
    expect(inlineSlug).not.toBeNull();
    inlineSlug!.value = 'Python Tag';
    inlineSlug!.dispatchEvent(new Event('input'));
    fixture.detectChanges();
    fixture.nativeElement
      .querySelector<HTMLButtonElement>('[data-testid="article-tag-1-save"]')
      ?.click();

    expect(articlesService.updateTag).not.toHaveBeenCalled();
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

  function elementValue(selector: string): string {
    const input = fixture.nativeElement.querySelector(selector) as HTMLInputElement | null;
    expect(input).not.toBeNull();
    return (input as HTMLInputElement).value;
  }

  function setInput(selector: string, value: string): void {
    const input = fixture.nativeElement.querySelector(selector) as
      HTMLInputElement | HTMLTextAreaElement;
    input.value = value;
    input.dispatchEvent(new Event('input'));
    fixture.detectChanges();
  }

  function fillValidArticleMinimum(): void {
    setInput('#articleSlug', 'typed-article');
    setInput('#articleTitleRu', 'Типизированная статья');
    setInput('#articleTitleEn', 'Typed article');
    setInput('#articleFolderRu', 'Инженерия');
    setInput('#articleFolderEn', 'Engineering');
    const contentEditors = fixture.debugElement.queryAll(By.directive(MarkdownEditorStubComponent));
    contentEditors[0].componentInstance.valueChange.emit('Содержимое');
    contentEditors[1].componentInstance.valueChange.emit('Content');
    fixture.detectChanges();
  }

  function setArticleContent(language: 'ru' | 'en', value: string): void {
    const contentEditors = fixture.debugElement.queryAll(By.directive(MarkdownEditorStubComponent));
    const index = language === 'ru' ? 0 : 1;
    contentEditors[index].componentInstance.valueChange.emit(value);
    fixture.detectChanges();
  }

  function expectInvalidControl(
    selector: string,
    expectedMessage: string,
    invalidClass = 'is-invalid',
  ): void {
    const element = fixture.nativeElement.querySelector(selector) as HTMLElement | null;
    expect(element).not.toBeNull();
    expect(element?.classList).toContain(invalidClass);
    expect(element?.getAttribute('aria-invalid')).toBe('true');
    expect(fixture.nativeElement.textContent).toContain(expectedMessage);
  }

  function buttonByText(text: string): HTMLButtonElement {
    const button = Array.from(
      fixture.nativeElement.querySelectorAll<HTMLButtonElement>('button'),
    ).find((candidate) => candidate.textContent?.includes(text));
    if (button === undefined) {
      throw new Error(`Button not found: ${text}`);
    }
    return button;
  }

  function submitArticleForm(): void {
    fixture.debugElement.query(By.css('form')).nativeElement.dispatchEvent(new Event('submit'));
    fixture.detectChanges();
  }
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

function articleDetail(slug: string, title: string): ArticleDetail {
  return {
    id: `00000000-0000-0000-0000-00000000000${slug === 'first-article' ? '1' : '2'}`,
    title,
    slug,
    folder: 'Engineering',
    authorUsername: 'admin',
    publishedAt: null,
    publishStatus: 'Draft',
    updatedAt: '2026-01-03T03:04:05+00:00',
    excerpt: '',
    metadata: {
      seoTitleRu: null,
      seoTitleEn: null,
      seoDescriptionRu: null,
      seoDescriptionEn: null,
      coverImageUrl: null,
      coverImageAltRu: null,
      coverImageAltEn: null,
    },
    viewCount: 0,
    tags: [],
    content: '# Content',
    createdAt: '2026-01-01T03:04:05+00:00',
    reactionCounts: { heart: 0, fire: 0, thinking: 0, neutral: 0, poop: 0 },
    translations: {
      ru: { title: `${title} RU`, content: '# RU', folder: 'Инженерия' },
      en: { title, content: '# EN', folder: 'Engineering' },
    },
  };
}
