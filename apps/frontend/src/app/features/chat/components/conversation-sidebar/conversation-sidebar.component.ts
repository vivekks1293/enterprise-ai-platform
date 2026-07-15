import { ChangeDetectionStrategy, Component, input, output } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ChatConversationSummary } from '@features/chat/models/chat-conversation-summary.model';
import { ButtonComponent } from '@shared/ui/button/button.component';
import { SearchBoxComponent } from '@shared/ui/search-box/search-box.component';
import { EmptyStateComponent } from '@shared/ui/empty-state/empty-state.component';
import { ConversationItemComponent } from '@features/chat/components/conversation-item/conversation-item.component';

@Component({
  selector: 'eap-conversation-sidebar',
  standalone: true,
  imports: [CommonModule, ButtonComponent, SearchBoxComponent, EmptyStateComponent, ConversationItemComponent],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './conversation-sidebar.component.html',
  styleUrl: './conversation-sidebar.component.scss'
})
export class ConversationSidebarComponent {
  public readonly pinnedConversations = input<readonly ChatConversationSummary[]>([]);
  public readonly recentConversations = input<readonly ChatConversationSummary[]>([]);
  public readonly selectedConversationId = input<string | null>(null);
  public readonly collapsed = input<boolean>(false);

  public readonly newConversation = output<void>();
  public readonly selectConversation = output<string>();
  public readonly searchTermChange = output<string>();
  public readonly toggleCollapse = output<void>();
}
