import { ChangeDetectionStrategy, Component, computed, inject, input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ChatMessage } from '@features/chat/models/chat-message.model';
import { AvatarComponent } from '@shared/ui/avatar/avatar.component';
import { TypingIndicatorComponent } from '@shared/ui/typing-indicator/typing-indicator.component';
import { RelativeTimePipe } from '@shared/pipes/relative-time.pipe';
import { AuthSessionService } from '@core/services/auth-session.service';
import { NotificationService } from '@core/services/notification.service';

/**
 * Renders from `message.status` so this same component serves both
 * today's simulated replies and future token streaming without any
 * change: 'streaming' + empty content shows the typing indicator;
 * 'streaming' + non-empty content (a partially streamed-in response)
 * would render exactly like 'complete' does today, just still growing.
 *
 * Copy/Regenerate are UI-only placeholders — inject NotificationService
 * directly rather than emitting outputs the parent would just forward
 * to the same toast anyway.
 */
@Component({
  selector: 'eap-message-bubble',
  standalone: true,
  imports: [CommonModule, AvatarComponent, TypingIndicatorComponent, RelativeTimePipe],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './message-bubble.component.html',
  styleUrl: './message-bubble.component.scss'
})
export class MessageBubbleComponent {
  public readonly message = input.required<ChatMessage>();

  private readonly session = inject(AuthSessionService);
  private readonly notifications = inject(NotificationService);

  protected readonly isUser = computed(() => this.message().role === 'user');

  protected readonly authorName = computed(() =>
    this.isUser() ? (this.session.currentUser()?.displayName ?? 'You') : 'Assistant'
  );

  protected readonly isEmptyStreaming = computed(
    () => this.message().status === 'streaming' && this.message().content.length === 0
  );

  protected onCopy(): void {
    this.notifications.notify('Copy is coming soon.', 'info');
  }

  protected onRegenerate(): void {
    this.notifications.notify('Regenerate is coming soon.', 'info');
  }
}
