import { Injectable, signal } from '@angular/core';

export interface AppNotification {
  id: number;
  type: 'success' | 'danger';
  message: string;
}

@Injectable({ providedIn: 'root' })
export class NotificationService {
  private nextId = 1;
  readonly notifications = signal<AppNotification[]>([]);

  success(message: string): void {
    this.add('success', message);
  }

  error(message: string): void {
    this.add('danger', message);
  }

  dismiss(id: number): void {
    this.notifications.update((items) => items.filter((item) => item.id !== id));
  }

  private add(type: AppNotification['type'], message: string): void {
    const notification: AppNotification = {
      id: this.nextId,
      type,
      message,
    };
    this.nextId += 1;
    this.notifications.update((items) => [...items, notification]);
  }
}
