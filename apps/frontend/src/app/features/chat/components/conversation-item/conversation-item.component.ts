import { ChangeDetectionStrategy, Component, input, output } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ChatConversationSummary } from '@features/chat/models/chat-conversation-summary.model';
import { RelativeTimePipe } from '@shared/pipes/relative-time.pipe';
import { TruncatePipe } from '@shared/pipes/truncate.pipe';

@Component({
  selector: 'eap-conversation-item',
  standalone: true,
  imports: [CommonModule, RelativeTimePipe, TruncatePipe],
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <button
      type="button"
      class="eap-conv-item"
      [class.eap-conv-item--active]="active()"
      (click)="select.emit(conversation().id)"
    >
      <div class="eap-conv-item__title">{{ conversation().title }}</div>
      <div class="eap-conv-item__preview">{{ (conversation().preview ?? 'No messages yet') | eapTruncate: 56 }}</div>
      <div class="eap-conv-item__time">{{ conversation().updatedAt | eapRelativeTime }}</div>
    </button>
  `,
  styles: `
    .eap-conv-item {
      display: block;
      width: 100%;
      text-align: left;
      border: none;
      background: transparent;
      border-radius: 0.5rem;
      padding: 0.625rem 0.75rem;
      cursor: pointer;

      &:hover {
        background-color: #eef0f5;
      }

      &.eap-conv-item--active {
        background-color: #e8eefc;
      }
    }
    .eap-conv-item__title {
      font-size: 0.8125rem;
      font-weight: 600;
      color: #1a1d29;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }
    .eap-conv-item__preview {
      font-size: 0.75rem;
      color: #5b6072;
      margin-top: 0.125rem;
    }
    .eap-conv-item__time {
      font-size: 0.6875rem;
      color: #8a8fa3;
      margin-top: 0.25rem;
    }
  `
})
export class ConversationItemComponent {
  public readonly conversation = input.required<ChatConversationSummary>();
  public readonly active = input<boolean>(false);
  public readonly select = output<string>();
}
