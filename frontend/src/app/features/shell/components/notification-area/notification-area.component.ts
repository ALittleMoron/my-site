import { ChangeDetectionStrategy, Component, inject } from '@angular/core';
import { NotificationService } from '../../../../core/notifications/notification.service';

@Component({
  selector: 'app-notification-area',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    @if (notificationService.notifications().length > 0) {
      <section class="alerts-section position-fixed top-0 end-0" aria-live="polite">
        @for (notification of notificationService.notifications(); track notification.id) {
          <div class="alert alert-{{ notification.type }} alert-dismissible shadow-sm" role="alert">
            {{ notification.message }}
            <button
              type="button"
              class="btn-close"
              aria-label="Закрыть"
              (click)="notificationService.dismiss(notification.id)"
            ></button>
          </div>
        }
      </section>
    }
  `,
})
export class NotificationAreaComponent {
  readonly notificationService = inject(NotificationService);
}
