import { ChangeDetectionStrategy, Component, computed, inject, input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ChatMessage } from '@features/chat/models/chat-message.model';
import { Citation } from '@features/chat/models/citation.model';
import { AvatarComponent } from '@shared/ui/avatar/avatar.component';
import { TypingIndicatorComponent } from '@shared/ui/typing-indicator/typing-indicator.component';
import { ChipComponent } from '@shared/ui/chips/chip.component';
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
  imports: [CommonModule, AvatarComponent, TypingIndicatorComponent, ChipComponent, RelativeTimePipe],
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

  protected readonly isError = computed(() => this.message().status === 'error');

  /**
   * The backend can return multiple citations pointing at the same
   * (filename, page) — different retrieved chunks from the same page —
   * which is meaningful for retrieval quality but reads as visibly
   * duplicated/broken to a user looking at a source list. De-duplicated
   * for DISPLAY only here; `message().citations` itself is untouched,
   * so nothing upstream loses data over this presentation choice.
   */
  protected readonly displayCitations = computed<readonly Citation[]>(() => {
    const citations = this.message().citations;
    if (!citations || citations.length === 0) {
      return [];
    }
    const seen = new Set<string>();
    const deduped: Citation[] = [];
    for (const citation of citations) {
      const key = `${citation.filename}|${citation.pageNumber ?? ''}`;
      if (!seen.has(key)) {
        seen.add(key);
        deduped.push(citation);
      }
    }
    return deduped;
  });

  protected onCopy(): void {
    this.notifications.notify('Copy is coming soon.', 'info');
  }

  protected onRegenerate(): void {
    this.notifications.notify('Regenerate is coming soon.', 'info');
  }
}
