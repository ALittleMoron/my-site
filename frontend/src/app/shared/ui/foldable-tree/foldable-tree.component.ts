import { ChangeDetectionStrategy, Component, computed, input, output, signal } from '@angular/core';

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
  readonly defaultExpandedSectionKeys = input.required<readonly string[]>();
  readonly sectionTestId = input.required<string>();
  readonly itemTestId = input.required<string>();
  readonly itemSelected = output<string>();

  private readonly defaultExpandedSectionKeySet = computed(
    () => new Set(this.defaultExpandedSectionKeys()),
  );
  readonly sectionExpansionOverrides = signal<ReadonlyMap<string, boolean>>(
    new Map<string, boolean>(),
  );

  isExpanded(sectionKey: string): boolean {
    return (
      this.sectionExpansionOverrides().get(sectionKey) ??
      this.defaultExpandedSectionKeySet().has(sectionKey)
    );
  }

  toggleSection(sectionKey: string): void {
    const expanded = !this.isExpanded(sectionKey);
    this.sectionExpansionOverrides.update((current) => {
      const next = new Map(current);
      next.set(sectionKey, expanded);
      return next;
    });
  }
}
