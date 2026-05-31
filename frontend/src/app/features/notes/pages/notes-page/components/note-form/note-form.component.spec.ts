import { Component, input, output } from '@angular/core';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { By } from '@angular/platform-browser';
import { of } from 'rxjs';
import { MarkdownEditorComponent } from '../../../../../../core/editor/markdown-editor.component';
import { provideI18nTesting } from '../../../../../../testing/i18n-testing';
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
      providers: [{ provide: NotesService, useValue: notesService }, provideI18nTesting()],
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
      translations: {
        ru: { title: 'Типизированная заметка', content: 'Содержимое', folder: 'Инженерия' },
        en: { title: 'Typed note', content: 'Content', folder: 'Engineering' },
      },
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
