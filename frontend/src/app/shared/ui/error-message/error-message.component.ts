import { Component, ChangeDetectionStrategy, computed, input, output } from '@angular/core';

export interface ErrorDisplay {
  message: string;
  nested_errors?: readonly ErrorDisplay[];
}

export function flattenNestedErrorMessages(error: ErrorDisplay): readonly string[] {
  const messages: string[] = [];
  appendNestedErrorMessages(error.nested_errors ?? [], messages);
  return messages;
}

function appendNestedErrorMessages(errors: readonly ErrorDisplay[], messages: string[]): void {
  for (const error of errors) {
    messages.push(error.message);
    appendNestedErrorMessages(error.nested_errors ?? [], messages);
  }
}

@Component({
  selector: 'app-error-message',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <div class="alert alert-danger d-flex align-items-center justify-content-between" role="alert">
      <div class="flex-grow-1">
        @if (nestedMessages().length > 0) {
          <ul class="mb-0 ps-3">
            @for (message of nestedMessages(); track $index) {
              <li>{{ message }}</li>
            }
          </ul>
        } @else {
          <span>{{ error().message }}</span>
        }
      </div>
      <button type="button" class="btn btn-sm btn-outline-danger ms-3" (click)="retry.emit()">
        {{ retryLabel() }}
      </button>
    </div>
  `,
})
export class ErrorMessageComponent {
  readonly error = input.required<ErrorDisplay>();
  readonly retryLabel = input.required<string>();
  readonly retry = output<void>();
  readonly nestedMessages = computed(() => flattenNestedErrorMessages(this.error()));
}
