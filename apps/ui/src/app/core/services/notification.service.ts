import { Injectable, signal } from '@angular/core';

export interface ToastMessage {
  readonly id: string;
  readonly type: 'info' | 'success' | 'warning' | 'error';
  readonly message: string;
}

@Injectable({ providedIn: 'root' })
export class NotificationService {
  private readonly _toasts = signal<readonly ToastMessage[]>([]);
  public readonly toasts = this._toasts.asReadonly();

  public show(message: string, type: ToastMessage['type'] = 'info', durationMs = 4000): void {
    const id = Math.random().toString(36).substring(2, 9);
    const toast: ToastMessage = { id, type, message };

    this._toasts.update((current) => [...current, toast]);

    setTimeout(() => {
      this.dismiss(id);
    }, durationMs);
  }

  public info(message: string): void {
    this.show(message, 'info');
  }

  public success(message: string): void {
    this.show(message, 'success');
  }

  public error(message: string): void {
    this.show(message, 'error', 6000);
  }

  public warning(message: string): void {
    this.show(message, 'warning');
  }

  public dismiss(id: string): void {
    this._toasts.update((current) => current.filter((t) => t.id !== id));
  }
}

