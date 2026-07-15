import {
  AfterViewInit,
  ChangeDetectionStrategy,
  Component,
  ElementRef,
  ViewChild,
  effect,
  input
} from '@angular/core';
import { CommonModule } from '@angular/common';
import { ChatMessage } from '@features/chat/models/chat-message.model';
import { MessageBubbleComponent } from '@features/chat/components/message-bubble/message-bubble.component';
import { EmptyStateComponent } from '@shared/ui/empty-state/empty-state.component';

/**
 * Purely a rendering surface — it has no idea how `messages` arrives
 * (mock timer today, streamed tokens later). Auto-scroll runs off an
 * `effect()` watching the message array's length/last-content, which
 * is exactly as valid whether a message is added once (mock reply) or
 * grows token-by-token (real streaming) — the scroll-to-bottom
 * behavior doesn't change either way.
 */
@Component({
  selector: 'eap-message-list',
  standalone: true,
  imports: [CommonModule, MessageBubbleComponent, EmptyStateComponent],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './message-list.component.html',
  styleUrl: './message-list.component.scss'
})
export class MessageListComponent implements AfterViewInit {
  public readonly messages = input<readonly ChatMessage[]>([]);

  @ViewChild('scrollRegion') private readonly scrollRegion?: ElementRef<HTMLDivElement>;

  constructor() {
    effect(() => {
      // Re-run whenever the messages array reference changes (new
      // message appended, or an existing one's content mutated in
      // place by the Facade) and scroll to the newest content.
      const messages = this.messages();
      if (messages.length > 0) {
        this.scrollToBottom();
      }
    });
  }

  public ngAfterViewInit(): void {
    this.scrollToBottom();
  }

  private scrollToBottom(): void {
    queueMicrotask(() => {
      const el = this.scrollRegion?.nativeElement;
      if (el) {
        el.scrollTop = el.scrollHeight;
      }
    });
  }
}
