import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ApiError } from '../../../../../../core/models/api-error.model';
import { provideI18nTesting } from '../../../../../../testing/i18n-testing';
import { MatrixQuestionDetail } from '../../../../models/matrix-question.model';
import { MatrixQuestionDetailComponent } from './matrix-question-detail.component';

const mockDetail: MatrixQuestionDetail = {
  id: 1,
  question: 'What is a closure?',
  answer: 'A **closure** is a function with access to its outer scope.',
  interviewExpectedAnswer: 'Demonstrate understanding of lexical scoping.',
  sheet: 'JavaScript',
  grade: 'Junior',
  section: 'Core',
  subsection: 'Syntax',
  publishStatus: 'Published',
  resources: [{ id: 10, name: 'MDN', url: 'https://mdn.io', context: 'See MDN docs' }],
};

const mockError: ApiError = {
  code: 'server_error',
  type: 'server_error',
  message: 'Internal server error',
  location: null,
  attr: null,
};

describe('MatrixQuestionDetailComponent', () => {
  let fixture: ComponentFixture<MatrixQuestionDetailComponent>;
  let el: HTMLElement;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [MatrixQuestionDetailComponent],
      providers: [provideI18nTesting()],
    }).compileComponents();

    fixture = TestBed.createComponent(MatrixQuestionDetailComponent);
    el = fixture.nativeElement as HTMLElement;
  });

  it('should show loading spinner when loading', () => {
    fixture.componentRef.setInput('loading', true);
    fixture.componentRef.setInput('question', null);
    fixture.componentRef.setInput('error', null);
    fixture.componentRef.setInput('isAdmin', false);
    fixture.detectChanges();
    expect(el.querySelector('app-loading-spinner')).toBeTruthy();
  });

  it('should show error when error is set', () => {
    fixture.componentRef.setInput('loading', false);
    fixture.componentRef.setInput('question', null);
    fixture.componentRef.setInput('error', mockError);
    fixture.componentRef.setInput('isAdmin', false);
    fixture.detectChanges();
    expect(el.querySelector('app-error-message')).toBeTruthy();
  });

  it('should show nothing when question is null and no loading/error', () => {
    fixture.componentRef.setInput('loading', false);
    fixture.componentRef.setInput('question', null);
    fixture.componentRef.setInput('error', null);
    fixture.componentRef.setInput('isAdmin', false);
    fixture.detectChanges();
    expect(el.querySelector('.question-detail')).toBeFalsy();
  });

  it('should render question text when question is set', () => {
    fixture.componentRef.setInput('loading', false);
    fixture.componentRef.setInput('question', mockDetail);
    fixture.componentRef.setInput('error', null);
    fixture.componentRef.setInput('isAdmin', false);
    fixture.detectChanges();
    expect(el.textContent).toContain('What is a closure?');
  });

  it('should render detail headings in Russian', () => {
    fixture.componentRef.setInput('loading', false);
    fixture.componentRef.setInput('question', mockDetail);
    fixture.componentRef.setInput('error', null);
    fixture.componentRef.setInput('isAdmin', false);
    fixture.detectChanges();
    const headings = Array.from(el.querySelectorAll('h2')).map((heading) =>
      heading.textContent?.trim(),
    );
    expect(headings).toContain('Вопрос:');
    expect(headings).toContain('Ответ:');
    expect(headings).toContain('Ответ, который ожидается на собеседовании:');
  });

  it('should render answer as HTML (markdown converted)', () => {
    fixture.componentRef.setInput('loading', false);
    fixture.componentRef.setInput('question', mockDetail);
    fixture.componentRef.setInput('error', null);
    fixture.componentRef.setInput('isAdmin', false);
    fixture.detectChanges();
    const answerDiv = el.querySelector('.question-detail div');
    expect(answerDiv?.innerHTML).toContain('<strong>');
  });

  it('should render fenced code blocks with language and highlight classes', () => {
    fixture.componentRef.setInput('loading', false);
    fixture.componentRef.setInput('question', {
      ...mockDetail,
      answer: '```ts\nconst answer = 42;\n```',
    });
    fixture.componentRef.setInput('error', null);
    fixture.componentRef.setInput('isAdmin', false);
    fixture.detectChanges();

    const pre = el.querySelector('pre.markdown-code');
    const code = el.querySelector('code.language-ts');
    expect(pre).toBeTruthy();
    expect(code?.textContent).toContain('const answer = 42;');
  });

  it('should render resources', () => {
    fixture.componentRef.setInput('loading', false);
    fixture.componentRef.setInput('question', mockDetail);
    fixture.componentRef.setInput('error', null);
    fixture.componentRef.setInput('isAdmin', false);
    fixture.detectChanges();
    expect(el.textContent).toContain('MDN');
    expect(el.querySelector('a[href="https://mdn.io"]')).toBeTruthy();
  });

  it('should hide admin buttons when isAdmin is false', () => {
    fixture.componentRef.setInput('loading', false);
    fixture.componentRef.setInput('question', mockDetail);
    fixture.componentRef.setInput('error', null);
    fixture.componentRef.setInput('isAdmin', false);
    fixture.detectChanges();
    expect(el.querySelector('button')).toBeFalsy();
  });

  it('should show Удалить button when isAdmin is true', () => {
    fixture.componentRef.setInput('loading', false);
    fixture.componentRef.setInput('question', mockDetail);
    fixture.componentRef.setInput('error', null);
    fixture.componentRef.setInput('isAdmin', true);
    fixture.detectChanges();
    const buttons = Array.from(el.querySelectorAll('button'));
    expect(buttons.some((b) => b.textContent?.includes('Удалить'))).toBe(true);
  });

  it('should show Снять с публикации button when isAdmin is true and question is Published', () => {
    fixture.componentRef.setInput('loading', false);
    fixture.componentRef.setInput('question', { ...mockDetail, publishStatus: 'Published' });
    fixture.componentRef.setInput('error', null);
    fixture.componentRef.setInput('isAdmin', true);
    fixture.detectChanges();
    const buttons = Array.from(el.querySelectorAll('button'));
    expect(buttons.some((b) => b.textContent?.includes('Снять с публикации'))).toBe(true);
    expect(buttons.some((b) => b.textContent?.includes('Опубликовать'))).toBe(false);
  });

  it('should show Опубликовать button when isAdmin is true and question is Draft', () => {
    fixture.componentRef.setInput('loading', false);
    fixture.componentRef.setInput('question', { ...mockDetail, publishStatus: 'Draft' });
    fixture.componentRef.setInput('error', null);
    fixture.componentRef.setInput('isAdmin', true);
    fixture.detectChanges();
    const buttons = Array.from(el.querySelectorAll('button'));
    expect(buttons.some((b) => b.textContent?.trim() === 'Опубликовать')).toBe(true);
    expect(buttons.some((b) => b.textContent?.includes('Снять с публикации'))).toBe(false);
  });

  it('should emit publish output when Опубликовать is clicked', () => {
    fixture.componentRef.setInput('loading', false);
    fixture.componentRef.setInput('question', { ...mockDetail, publishStatus: 'Draft' });
    fixture.componentRef.setInput('error', null);
    fixture.componentRef.setInput('isAdmin', true);
    fixture.detectChanges();

    let emitted = false;
    fixture.componentInstance.publish.subscribe(() => {
      emitted = true;
    });

    const buttons = Array.from(el.querySelectorAll('button'));
    const publishBtn = buttons.find(
      (b) => b.textContent?.trim() === 'Опубликовать',
    ) as HTMLButtonElement;
    publishBtn.click();

    expect(emitted).toBe(true);
  });

  it('should emit unpublish output when Снять с публикации is clicked', () => {
    fixture.componentRef.setInput('loading', false);
    fixture.componentRef.setInput('question', { ...mockDetail, publishStatus: 'Published' });
    fixture.componentRef.setInput('error', null);
    fixture.componentRef.setInput('isAdmin', true);
    fixture.detectChanges();

    let emitted = false;
    fixture.componentInstance.unpublish.subscribe(() => {
      emitted = true;
    });

    const buttons = Array.from(el.querySelectorAll('button'));
    const unpublishBtn = buttons.find((b) =>
      b.textContent?.includes('Снять с публикации'),
    ) as HTMLButtonElement;
    unpublishBtn.click();

    expect(emitted).toBe(true);
  });

  it('should emit delete output when Удалить is clicked', () => {
    fixture.componentRef.setInput('loading', false);
    fixture.componentRef.setInput('question', mockDetail);
    fixture.componentRef.setInput('error', null);
    fixture.componentRef.setInput('isAdmin', true);
    fixture.detectChanges();

    let emitted = false;
    fixture.componentInstance.delete.subscribe(() => {
      emitted = true;
    });

    const buttons = Array.from(el.querySelectorAll('button'));
    const deleteBtn = buttons.find((b) => b.textContent?.trim() === 'Удалить') as HTMLButtonElement;
    deleteBtn.click();

    expect(emitted).toBe(true);
  });
});
