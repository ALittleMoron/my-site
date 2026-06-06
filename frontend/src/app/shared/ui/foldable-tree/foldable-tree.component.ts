import { ChangeDetectionStrategy, Component, input, output, signal } from '@angular/core';

export interface FoldableTreeItem {
  key: string;
  label: string;
  badgeText: string | null;
}

export interface FoldableTreeSection {
  key: string;
  label: string;
  trailingText: string | null;
  items: readonly FoldableTreeItem[];
}

@Component({
  selector: 'app-foldable-tree',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './foldable-tree.component.html',
  styleUrl: './foldable-tree.component.scss',
})
export class FoldableTreeComponent {
  readonly sections = input.required<readonly FoldableTreeSection[]>();
  readonly emptyMessage = input.required<string>();
  readonly selectedItemKey = input.required<string | null>();
  readonly sectionTestId = input.required<string>();
  readonly itemTestId = input.required<string>();
  readonly itemSelected = output<string>();

  readonly expandedSections = signal<ReadonlySet<string>>(new Set<string>());

  isExpanded(sectionKey: string): boolean {
    return this.expandedSections().has(sectionKey);
  }

  toggleSection(sectionKey: string): void {
    this.expandedSections.update((current) => {
      const next = new Set(current);
      if (next.has(sectionKey)) {
        next.delete(sectionKey);
      } else {
        next.add(sectionKey);
      }
      return next;
    });
  }
}
