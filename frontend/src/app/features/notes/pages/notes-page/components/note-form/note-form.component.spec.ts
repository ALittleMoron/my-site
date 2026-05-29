import { Component, input, output } from '@angular/core';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { By } from '@angular/platform-browser';
import { of } from 'rxjs';
import { MarkdownEditorComponent } from '../../../../../../core/editor/markdown-editor.component';
import { NotesService } from '../../../../services/notes.service';
import { NoteFormComponent } from './note-form.component';

describe('NoteFormComponent', () => {
  let fixture: ComponentFixture<NoteFormComponent>;
  let notesService: {
    getTags: jest.Mock;
    createTag: jest.Mock;
    updateTag: jest.Mock;
    deleteTag: jest.Mock;
    restoreTag: jest.Mock;
  };

  beforeEach(async () => {
    notesService = {
      getTags: jest.fn().mockReturnValue(
        of([
          { id: 1, name: 'Python', slug: 'python', deletedAt: null },
          { id: 2, name: 'Old', slug: 'old', deletedAt: '2026-01-04T03:04:05+00:00' },
        ]),
      ),
      createTag: jest
        .fn()
        .mockReturnValue(of({ id: 3, name: 'Backend', slug: 'backend', deletedAt: null })),
      updateTag: jest.fn().mockReturnValue(of({ id: 1, name: 'Py', slug: 'py', deletedAt: null })),
      deleteTag: jest.fn().mockReturnValue(of(undefined)),
      restoreTag: jest.fn().mockReturnValue(of(undefined)),
    };

    await TestBed.configureTestingModule({
      imports: [NoteFormComponent],
      providers: [{ provide: NotesService, useValue: notesService }],
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
    const title = fixture.debugElement.query(By.css('#noteTitle'))
      .nativeElement as HTMLInputElement;
    const slug = fixture.debugElement.query(By.css('#noteSlug')).nativeElement as HTMLInputElement;

    title.value = 'Новая заметка про Angular';
    title.dispatchEvent(new Event('input'));
    fixture.detectChanges();

    expect(slug.value).toBe('novaya-zametka-pro-angular');

    slug.value = 'manual-slug';
    slug.dispatchEvent(new Event('input'));
    title.value = 'Другой заголовок';
    title.dispatchEvent(new Event('input'));
    fixture.detectChanges();

    expect(slug.value).toBe('manual-slug');
  });

  it('emits payload with selected active tags', () => {
    const title = fixture.debugElement.query(By.css('#noteTitle'))
      .nativeElement as HTMLInputElement;
    const contentEditor = fixture.debugElement.query(By.directive(MarkdownEditorStubComponent));
    const saveSpy = jest.fn();
    fixture.componentInstance.noteSave.subscribe(saveSpy);

    title.value = 'Typed note';
    title.dispatchEvent(new Event('input'));
    contentEditor.componentInstance.valueChange.emit('Content');
    const folder = fixture.debugElement.query(By.css('#noteFolder'))
      .nativeElement as HTMLInputElement;
    folder.value = 'Engineering';
    folder.dispatchEvent(new Event('input'));
    const tagCheckbox = fixture.debugElement.query(By.css('#noteTag-1'))
      .nativeElement as HTMLInputElement;
    tagCheckbox.click();
    fixture.detectChanges();

    const form = fixture.debugElement.query(By.css('form')).nativeElement as HTMLFormElement;
    form.dispatchEvent(new Event('submit'));

    expect(saveSpy).toHaveBeenCalledWith({
      title: 'Typed note',
      content: 'Content',
      slug: 'typed-note',
      folder: 'Engineering',
      publishStatus: 'Draft',
      tagIds: [1],
    });
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
