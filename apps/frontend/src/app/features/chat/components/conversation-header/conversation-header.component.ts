import { ChangeDetectionStrategy, Component, inject, input, output } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ChatConversationSummary } from '@features/chat/models/chat-conversation-summary.model';
import { RelativeTimePipe } from '@shared/pipes/relative-time.pipe';
import { NotificationService } from '@core/services/notification.service';

/**
 * Rename/delete/menu are UI-only placeholders — they inject
 * NotificationService (Core) directly for a "coming soon" toast
 * rather than round-tripping through ChatFacade, matching the same
 * pattern HeaderComponent and LoginPage already use for non-state-
 * changing actions.
 */
@Component({
  selector: 'eap-conversation-header',
  standalone: true,
  imports: [CommonModule, RelativeTimePipe],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './conversation-header.component.html',
  styleUrl: './conversation-header.component.scss'
})
export class ConversationHeaderComponent {
  public readonly conversation = input<ChatConversationSummary | null>(null);
  public readonly rightPanelCollapsed = input<boolean>(false);

  public readonly toggleRightPanel = output<void>();

  private readonly notifications = inject(NotificationService);

  protected onRename(): void {
    this.notifications.notify('Renaming conversations is coming soon.', 'info');
  }

  protected onDelete(): void {
    this.notifications.notify('Deleting conversations is coming soon.', 'info');
  }

  protected onMenu(): void {
    this.notifications.notify('More conversation actions are coming soon.', 'info');
  }
}
