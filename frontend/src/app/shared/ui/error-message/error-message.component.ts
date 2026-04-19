import { Component, ChangeDetectionStrategy, input, output } from '@angular/core';

export interface ErrorDisplay {
  message: string;
}

@Component({
  selector: 'app-error-message',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <div class="alert alert-danger d-flex align-items-center justify-content-between" role="alert">
      <span>{{ error().message }}</span>
      <button type="button" class="btn btn-sm btn-outline-danger ms-3" (click)="retry.emit()">
        Retry
      </button>
    </div>
  `,
})
export class ErrorMessageComponent {
  readonly error = input.required<ErrorDisplay>();
  readonly retry = output<void>();
}
