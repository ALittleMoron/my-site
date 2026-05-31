import { Component, input, output } from '@angular/core';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import {
  MatrixQuestionDetail,
  MatrixQuestionPayload,
} from '../../../../models/matrix-question.model';
import { MarkdownEditorComponent } from '../../../../../../core/editor/markdown-editor.component';
import { MatrixQuestionFormComponent } from './matrix-question-form.component';

@Component({
  selector: 'app-markdown-editor',
  standalone: true,
  template: '',
})
class MarkdownEditorStubComponent {
  readonly value = input<string>('');
  readonly valueChange = output<string>();
}

const question: MatrixQuestionDetail = {
  id: 7,
  question: 'What is PEP8?',
  answer: 'Answer',
  interviewExpectedAnswer: 'Expected',
  sheetKey: 'python',
  sheet: 'Python',
  grade: 'Junior',
  section: 'Core',
  subsection: 'Style',
  publishStatus: 'Draft',
  translations: {
    ru: {
      question: 'Что такое PEP8?',
      answer: 'Ответ',
      interviewExpectedAnswer: 'Ожидаемый ответ',
      sheet: 'Python',
      section: 'Core',
      subsection: 'Style',
    },
    en: {
      question: 'What is PEP8?',
      answer: 'Answer',
      interviewExpectedAnswer: 'Expected',
      sheet: 'Python',
      section: 'Core',
      subsection: 'Style',
    },
  },
  resources: [
    {
      id: 1,
      name: 'Python docs',
      url: 'https://docs.python.org',
      context: 'Read',
      translations: {
        ru: { name: 'Документация Python', context: 'Читать' },
        en: { name: 'Python docs', context: 'Read' },
      },
    },
  ],
};

describe('MatrixQuestionFormComponent', () => {
  let fixture: ComponentFixture<MatrixQuestionFormComponent>;
  let component: MatrixQuestionFormComponent;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [MatrixQuestionFormComponent],
    })
      .overrideComponent(MatrixQuestionFormComponent, {
        remove: { imports: [MarkdownEditorComponent] },
        add: { imports: [MarkdownEditorStubComponent] },
      })
      .compileComponents();

    fixture = TestBed.createComponent(MatrixQuestionFormComponent);
    component = fixture.componentInstance;
    fixture.componentRef.setInput('searchResults', []);
  });

  it('populates controls and resources when editing a question', () => {
    fixture.componentRef.setInput('question', question);
    fixture.detectChanges();

    expect(component.form.getRawValue()).toEqual({
      questionRu: 'Что такое PEP8?',
      questionEn: 'What is PEP8?',
      answerRu: 'Ответ',
      answerEn: 'Answer',
      interviewExpectedAnswerRu: 'Ожидаемый ответ',
      interviewExpectedAnswerEn: 'Expected',
      sheetKey: 'python',
      sheetRu: 'Python',
      sheetEn: 'Python',
      grade: 'Junior',
      sectionRu: 'Core',
      sectionEn: 'Core',
      subsectionRu: 'Style',
      subsectionEn: 'Style',
      publishStatus: 'Draft',
    });
    expect(component.resources()).toEqual([
      {
        id: 1,
        name: 'Python docs',
        url: 'https://docs.python.org',
        context: 'Read',
        translations: {
          ru: { name: 'Документация Python', context: 'Читать' },
          en: { name: 'Python docs', context: 'Read' },
        },
        isNew: false,
      },
    ]);
  });

  it('emits a typed payload with existing and new resources on submit', () => {
    const emitted: MatrixQuestionPayload[] = [];
    component.questionSave.subscribe((payload) => emitted.push(payload));
    fixture.detectChanges();

    component.form.setValue({
      questionRu: 'Вопрос',
      questionEn: 'Question',
      answerRu: 'Ответ',
      answerEn: 'Answer',
      interviewExpectedAnswerRu: 'Ожидаемый ответ',
      interviewExpectedAnswerEn: 'Expected',
      sheetKey: 'python',
      sheetRu: 'Python',
      sheetEn: 'Python',
      grade: 'Middle',
      sectionRu: 'Core',
      sectionEn: 'Core',
      subsectionRu: 'Syntax',
      subsectionEn: 'Syntax',
      publishStatus: 'Published',
    });
    component.resources.set([
      {
        id: 1,
        name: 'Python docs',
        url: 'https://docs.python.org',
        context: 'Read',
        translations: {
          ru: { name: 'Документация Python', context: 'Читать' },
          en: { name: 'Python docs', context: 'Read' },
        },
        isNew: false,
      },
      {
        id: -1,
        name: 'New docs',
        url: 'https://example.com',
        context: '',
        translations: {
          ru: { name: 'Новая документация', context: '' },
          en: { name: 'New docs', context: '' },
        },
        isNew: true,
      },
    ]);

    component.submit();

    expect(emitted).toEqual([
      {
        sheetKey: 'python',
        grade: 'Middle',
        publishStatus: 'Published',
        translations: {
          ru: {
            question: 'Вопрос',
            answer: 'Ответ',
            interviewExpectedAnswer: 'Ожидаемый ответ',
            sheet: 'Python',
            section: 'Core',
            subsection: 'Syntax',
          },
          en: {
            question: 'Question',
            answer: 'Answer',
            interviewExpectedAnswer: 'Expected',
            sheet: 'Python',
            section: 'Core',
            subsection: 'Syntax',
          },
        },
        resources: [
          {
            resourceId: 1,
            translations: { ru: { context: 'Читать' }, en: { context: 'Read' } },
          },
          {
            resource: {
              url: 'https://example.com',
              translations: {
                ru: { name: 'Новая документация' },
                en: { name: 'New docs' },
              },
            },
            translations: { ru: { context: '' }, en: { context: '' } },
          },
        ],
      },
    ]);
  });

  it('does not emit when required fields are invalid', () => {
    const emitted: MatrixQuestionPayload[] = [];
    component.questionSave.subscribe((payload) => emitted.push(payload));
    fixture.detectChanges();

    component.submit();

    expect(emitted).toEqual([]);
    expect(component.form.touched).toBe(true);
  });
});
