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
  sheet: 'Python',
  grade: 'Junior',
  section: 'Core',
  subsection: 'Style',
  publishStatus: 'Draft',
  resources: [{ id: 1, name: 'Python docs', url: 'https://docs.python.org', context: 'Read' }],
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
      question: 'What is PEP8?',
      answer: 'Answer',
      interviewExpectedAnswer: 'Expected',
      sheet: 'Python',
      grade: 'Junior',
      section: 'Core',
      subsection: 'Style',
      publishStatus: 'Draft',
    });
    expect(component.resources()).toEqual([
      { id: 1, name: 'Python docs', url: 'https://docs.python.org', context: 'Read', isNew: false },
    ]);
  });

  it('emits a typed payload with existing and new resources on submit', () => {
    const emitted: MatrixQuestionPayload[] = [];
    component.questionSave.subscribe((payload) => emitted.push(payload));
    fixture.detectChanges();

    component.form.setValue({
      question: 'Question',
      answer: 'Answer',
      interviewExpectedAnswer: 'Expected',
      sheet: 'Python',
      grade: 'Middle',
      section: 'Core',
      subsection: 'Syntax',
      publishStatus: 'Published',
    });
    component.resources.set([
      { id: 1, name: 'Python docs', url: 'https://docs.python.org', context: 'Read', isNew: false },
      { id: -1, name: 'New docs', url: 'https://example.com', context: '', isNew: true },
    ]);

    component.submit();

    expect(emitted).toEqual([
      {
        question: 'Question',
        answer: 'Answer',
        interviewExpectedAnswer: 'Expected',
        sheet: 'Python',
        grade: 'Middle',
        section: 'Core',
        subsection: 'Syntax',
        publishStatus: 'Published',
        resources: [
          { resourceId: 1, context: 'Read' },
          { resource: { name: 'New docs', url: 'https://example.com' }, context: '' },
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
