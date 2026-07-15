import { ChangeDetectionStrategy, Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ChatFacade } from '@features/chat/services/chat.facade';
import { ChatStateService } from '@features/chat/state/chat-state.service';
import { ConversationWorkspaceComponent } from '@features/chat/components/conversation-workspace/conversation-workspace.component';
import { LoadingStateComponent } from '@shared/ui/loading-state/loading-state.component';

/**
 * The only component in the Chat feature that injects ChatFacade.
 * Every component below ConversationWorkspace receives its data as
 * plain inputs bound from `facade.*` signals here, and every user
 * action bubbles back up as a plain output bound to a `facade.*`
 * method here — see this phase's architecture note for why.
 */
@Component({
  selector: 'eap-chat-page',
  standalone: true,
  imports: [CommonModule, ConversationWorkspaceComponent, LoadingStateComponent],
  changeDetection: ChangeDetectionStrategy.OnPush,
  providers: [ChatStateService, ChatFacade],
  templateUrl: './chat.page.html',
  styleUrl: './chat.page.scss'
})
export class ChatPageComponent implements OnInit {
  protected readonly facade = inject(ChatFacade);

  public ngOnInit(): void {
    this.facade.initWorkspace();
  }
}
