import { ChangeDetectionStrategy, Component, input, output } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ChatConversationSummary } from '@features/chat/models/chat-conversation-summary.model';
import { ChatMessage } from '@features/chat/models/chat-message.model';
import { ConversationSidebarComponent } from '@features/chat/components/conversation-sidebar/conversation-sidebar.component';
import { ConversationHeaderComponent } from '@features/chat/components/conversation-header/conversation-header.component';
import { MessageListComponent } from '@features/chat/components/message-list/message-list.component';
import { RightPanelComponent } from '@features/chat/components/right-panel/right-panel.component';
import { PromptComposerComponent } from '@shared/ui/prompt-composer/prompt-composer.component';
import { LoadingStateComponent } from '@shared/ui/loading-state/loading-state.component';

/**
 * Arranges the three columns (sidebar, main, right panel) and forwards
 * bindings between ChatPage and the leaf components below it. Knows
 * nothing about ChatFacade — every value it renders arrived as a
 * plain input, every action it triggers leaves as a plain output.
 * This is the Chat feature's equivalent of AppLayout: structural only.
 */
@Component({
  selector: 'eap-conversation-workspace',
  standalone: true,
  imports: [
    CommonModule,
    ConversationSidebarComponent,
    ConversationHeaderComponent,
    MessageListComponent,
    RightPanelComponent,
    PromptComposerComponent,
    LoadingStateComponent
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './conversation-workspace.component.html',
  styleUrl: './conversation-workspace.component.scss'
})
export class ConversationWorkspaceComponent {
  public readonly pinnedConversations = input<readonly ChatConversationSummary[]>([]);
  public readonly recentConversations = input<readonly ChatConversationSummary[]>([]);
  public readonly selectedConversationId = input<string | null>(null);
  public readonly selectedConversation = input<ChatConversationSummary | null>(null);
  public readonly messages = input<readonly ChatMessage[]>([]);
  public readonly isSending = input<boolean>(false);
  public readonly sidebarCollapsed = input<boolean>(false);
  public readonly rightPanelCollapsed = input<boolean>(false);
  /** Sidebar's own "conversation list loading" state. */
  public readonly conversationsLoading = input<boolean>(false);
  /** Main pane's "this specific conversation's messages are loading" state. */
  public readonly mainLoading = input<boolean>(false);

  public readonly newConversation = output<void>();
  public readonly selectConversation = output<string>();
  public readonly searchTermChange = output<string>();
  public readonly toggleSidebar = output<void>();
  public readonly toggleRightPanel = output<void>();
  public readonly sendMessage = output<string>();
  public readonly stopGeneration = output<void>();
}
