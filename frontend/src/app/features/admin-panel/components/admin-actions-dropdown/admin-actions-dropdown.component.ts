import {
  ChangeDetectionStrategy,
  Component,
  ElementRef,
  HostListener,
  computed,
  inject,
  input,
  output,
  signal,
} from '@angular/core';

export interface AdminAction {
  id: string;
  label: string;
  destructive: boolean;
  disabled: boolean;
}

@Component({
  selector: 'app-admin-actions-dropdown',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  styles: `
    .dropdown-menu {
      z-index: 1055;
    }
  `,
  template: `
    @if (availableActions().length > 0) {
      <div class="dropdown">
        <button
          type="button"
          class="btn btn-outline-secondary btn-sm dropdown-toggle"
          [attr.aria-expanded]="open()"
          [attr.aria-label]="ariaLabel()"
          [attr.data-testid]="testId() + '-toggle'"
          (click)="toggle()"
        >
          {{ buttonLabel() }}
        </button>
        <ul
          class="dropdown-menu dropdown-menu-end"
          [class.show]="open()"
          data-bs-popper="static"
          [attr.data-testid]="testId() + '-menu'"
        >
          @for (action of availableActions(); track action.id) {
            <li>
              <button
                type="button"
                class="dropdown-item"
                [class.text-danger]="action.destructive"
                [attr.aria-label]="
                  action.destructive ? action.label + ', ' + destructiveActionLabel() : action.label
                "
                [attr.data-testid]="testId() + '-' + action.id"
                (click)="select(action)"
              >
                {{ action.label }}
              </button>
            </li>
          }
        </ul>
      </div>
    }
  `,
})
export class AdminActionsDropdownComponent {
  private readonly elementRef = inject<ElementRef<HTMLElement>>(ElementRef);

  readonly actions = input.required<readonly AdminAction[]>();
  readonly buttonLabel = input.required<string>();
  readonly ariaLabel = input.required<string>();
  readonly destructiveActionLabel = input.required<string>();
  readonly testId = input.required<string>();
  readonly actionSelected = output<string>();
  readonly availableActions = computed(() => this.actions().filter((action) => !action.disabled));
  readonly open = signal(false);

  @HostListener('document:click', ['$event'])
  onDocumentClick(event: MouseEvent): void {
    const target = event.target;
    if (target instanceof Node && !this.elementRef.nativeElement.contains(target)) {
      this.close();
    }
  }

  @HostListener('document:keydown.escape')
  onDocumentEscape(): void {
    this.close();
  }

  @HostListener('window:resize')
  @HostListener('window:scroll')
  onViewportChange(): void {
    this.close();
  }

  toggle(): void {
    if (this.open()) {
      this.close();
      return;
    }
    this.open.set(true);
  }

  close(): void {
    this.open.set(false);
  }

  select(action: AdminAction): void {
    if (action.disabled) return;
    this.close();
    this.actionSelected.emit(action.id);
  }
}
