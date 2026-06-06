import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideI18nTesting } from '../../../../../../testing/i18n-testing';
import { NoteTree } from '../../../../models/notes.model';
import { NotesSidePanelComponent } from './notes-side-panel.component';

describe('NotesSidePanelComponent', () => {
  let fixture: ComponentFixture<NotesSidePanelComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [NotesSidePanelComponent],
      providers: [provideI18nTesting()],
    }).compileComponents();

    fixture = TestBed.createComponent(NotesSidePanelComponent);
  });

  it('renders expanded folders and notes as a tree with note indentation', () => {
    const tree: NoteTree = {
      folders: [
        {
          folder: 'Engineering',
          notes: [
            {
              title: 'Typed notes',
              slug: 'typed-notes',
              publishStatus: 'Published',
              publishedAt: '2026-01-02T03:04:05+00:00',
              updatedAt: '2026-01-03T03:04:05+00:00',
            },
          ],
        },
      ],
    };
    fixture.componentRef.setInput('tree', tree);
    fixture.componentRef.setInput('currentSlug', 'typed-notes');
    fixture.detectChanges();

    const folder = fixture.nativeElement.querySelector(
      '[data-testid="notes-tree-folder"]',
    ) as HTMLButtonElement;
    folder.click();
    fixture.detectChanges();

    const note = fixture.nativeElement.querySelector(
      '[data-testid="notes-tree-note"]',
    ) as HTMLButtonElement;

    expect(fixture.nativeElement.querySelector('[role="tree"]')).toBeTruthy();
    expect(fixture.nativeElement.querySelector('app-foldable-tree')).not.toBeNull();
    expect(folder.getAttribute('role')).toBe('treeitem');
    expect(note.getAttribute('role')).toBe('treeitem');
    expect(note.classList).toContain('active');
  });
});
