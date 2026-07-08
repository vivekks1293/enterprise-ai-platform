import { Injectable, signal } from '@angular/core';

export type NotificationSeverity = 'info' | 'success' | 'warning' | 'error';

export interface AppNotification {
  readonly id: string;
  readonly severity: NotificationSeverity;
  readonly message: string;
  readonly createdAt: Date;
}

/**
 * In-memory notification/toast store. This backs both transient
 * toasts and the future Notification Panel placeholder in the Shell
 * header — both read from the same signal so there is one source of
 * truth for "what has the user been told."
 */
@Injectable({ providedIn: 'root' })
export class NotificationService {
  private readonly _notifications = signal<readonly AppNotification[]>([]);
  public readonly notifications = this._notifications.asReadonly();

  public notify(message: string, severity: NotificationSeverity = 'info'): void {
    const notification: AppNotification = {
      id: crypto.randomUUID(),
      severity,
      message,
      createdAt: new Date()
    };
    this._notifications.update((list) => [notification, ...list]);
  }

  public dismiss(id: string): void {
    this._notifications.update((list) => list.filter((n) => n.id !== id));
  }

  public clearAll(): void {
    this._notifications.set([]);
  }
}
