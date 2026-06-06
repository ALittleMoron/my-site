import { ComponentFixture, TestBed } from '@angular/core/testing';
import { FoldableTreeComponent, FoldableTreeSection } from './foldable-tree.component';

describe('FoldableTreeComponent', () => {
  let fixture: ComponentFixture<FoldableTreeComponent>;

  const sections: readonly FoldableTreeSection[] = [
    {
      key: 'matrix',
      label: 'Матрица компетенций',
      trailingText: '2',
      items: [
        { key: 'all-questions', label: 'Все вопросы', badgeText: null },
        { key: 'typos', label: 'Опечатки от пользователей', badgeText: '4' },
      ],
    },
  ];

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [FoldableTreeComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(FoldableTreeComponent);
    fixture.componentRef.setInput('sections', sections);
    fixture.componentRef.setInput('emptyMessage', 'Разделы появятся позже.');
    fixture.componentRef.setInput('selectedItemKey', 'typos');
    fixture.componentRef.setInput('sectionTestId', 'admin-tree-section');
    fixture.componentRef.setInput('itemTestId', 'admin-tree-item');
    fixture.detectChanges();
  });

  it('renders foldable sections and selected nested items as an accessible tree', () => {
    const section = fixture.nativeElement.querySelector(
      '[data-testid="admin-tree-section"]',
    ) as HTMLButtonElement;

    expect(fixture.nativeElement.querySelector('[role="tree"]')).not.toBeNull();
    expect(section.textContent).toContain('Матрица компетенций');
    expect(section.textContent).toContain('2');
    expect(section.getAttribute('aria-expanded')).toBe('false');

    section.click();
    fixture.detectChanges();

    const items = Array.from(
      fixture.nativeElement.querySelectorAll('[data-testid="admin-tree-item"]'),
    ) as HTMLButtonElement[];
    expect(section.getAttribute('aria-expanded')).toBe('true');
    expect(items.map((item) => item.textContent?.trim())).toEqual([
      '+--Все вопросы',
      '+--Опечатки от пользователей4',
    ]);
    expect(items[1].classList).toContain('active');
    expect(items[1].getAttribute('aria-selected')).toBe('true');
  });

  it('emits selected item keys', () => {
    const selected: string[] = [];
    fixture.componentInstance.itemSelected.subscribe((key) => selected.push(key));

    (
      fixture.nativeElement.querySelector('[data-testid="admin-tree-section"]') as HTMLButtonElement
    ).click();
    fixture.detectChanges();
    (
      fixture.nativeElement.querySelector('[data-testid="admin-tree-item"]') as HTMLButtonElement
    ).click();

    expect(selected).toEqual(['all-questions']);
  });

  it('renders the explicit empty message when there are no sections', () => {
    fixture.componentRef.setInput('sections', []);
    fixture.detectChanges();

    expect(fixture.nativeElement.querySelector('[role="tree"]')).toBeNull();
    expect(fixture.nativeElement.textContent).toContain('Разделы появятся позже.');
  });
});
