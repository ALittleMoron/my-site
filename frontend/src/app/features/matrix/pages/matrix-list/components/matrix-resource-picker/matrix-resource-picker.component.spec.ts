import { ComponentFixture, TestBed } from '@angular/core/testing';
import { MatrixResourcePickerComponent } from './matrix-resource-picker.component';
import { MatrixResource } from '../../../../models/matrix-question.model';

const existingResource: MatrixResource = {
  id: 1,
  name: 'Python docs',
  url: 'https://docs.python.org',
};

describe('MatrixResourcePickerComponent', () => {
  let fixture: ComponentFixture<MatrixResourcePickerComponent>;
  let component: MatrixResourcePickerComponent;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [MatrixResourcePickerComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(MatrixResourcePickerComponent);
    component = fixture.componentInstance;
    fixture.componentRef.setInput('resources', []);
    fixture.componentRef.setInput('searchResults', [existingResource]);
    fixture.detectChanges();
  });

  it('emits search text as it changes', () => {
    const emitted: string[] = [];
    component.searchChange.subscribe((value) => emitted.push(value));

    component.setSearch('python');

    expect(emitted).toEqual(['python']);
  });

  it('attaches an existing resource once', () => {
    const emitted: unknown[] = [];
    component.resourcesChange.subscribe((resources) => emitted.push(resources));

    component.attach(existingResource);
    fixture.componentRef.setInput('resources', [
      { ...existingResource, context: '', isNew: false },
    ]);
    component.attach(existingResource);

    expect(emitted).toEqual([[{ ...existingResource, context: '', isNew: false }]]);
  });

  it('adds a new resource when name and url are present', () => {
    const emitted: unknown[] = [];
    component.resourcesChange.subscribe((resources) => emitted.push(resources));

    component.newName.set('Docs');
    component.newUrl.set('https://example.com');
    component.addNew();

    expect(emitted).toEqual([
      [{ id: -1, name: 'Docs', url: 'https://example.com', context: '', isNew: true }],
    ]);
    expect(component.newName()).toBe('');
    expect(component.newUrl()).toBe('');
  });

  it('uses sequential negative ids for new resources', () => {
    const emitted: unknown[] = [];
    component.resourcesChange.subscribe((resources) => emitted.push(resources));

    component.newName.set('First');
    component.newUrl.set('https://first.example.com');
    component.addNew();

    fixture.componentRef.setInput('resources', [
      {
        id: -1,
        name: 'First',
        url: 'https://first.example.com',
        context: '',
        isNew: true,
      },
    ]);

    component.newName.set('Second');
    component.newUrl.set('https://second.example.com');
    component.addNew();

    expect(emitted.at(-1)).toEqual([
      { id: -1, name: 'First', url: 'https://first.example.com', context: '', isNew: true },
      { id: -2, name: 'Second', url: 'https://second.example.com', context: '', isNew: true },
    ]);
  });

  it('updates context and detaches resources', () => {
    const emitted: unknown[] = [];
    component.resourcesChange.subscribe((resources) => emitted.push(resources));
    fixture.componentRef.setInput('resources', [
      { ...existingResource, context: '', isNew: false },
    ]);

    component.updateContext(0, 'Read first');
    component.detach(0);

    expect(emitted).toEqual([
      [{ ...existingResource, context: 'Read first', isNew: false }],
      [],
    ]);
  });
});
