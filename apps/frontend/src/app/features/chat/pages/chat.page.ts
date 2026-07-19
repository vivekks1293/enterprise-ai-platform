import { ChangeDetectionStrategy, Component, OnInit, effect, inject, input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ChatFacade } from '@features/chat/services/chat.facade';
import { ChatStateService } from '@features/chat/state/chat-state.service';
import { ConversationWorkspaceComponent } from '@features/chat/components/conversation-workspace/conversation-workspace.component';

/**
 * The only component in the Chat feature that injects ChatFacade.
 * Every component below ConversationWorkspace receives its data as
 * plain inputs bound from `facade.*` signals here, and every user
 * action bubbles back up as a plain output bound to a `facade.*`
 * method here — see this feature's Phase 4 architecture note for why.
 *
 * `conversationId` is bound directly from the `:conversationId` route
 * param via Angular's `withComponentInputBinding()` (enabled in
 * app.config.ts) — no ActivatedRoute injection needed. The route is
 * the source of truth for which conversation is open: an `effect()`
 * reacts to it changing (including to `undefined` on bare `/chat`)
 * and tells the Facade to load or deselect accordingly. This
 * component is reused by the Router across `/chat/:id1` → `/chat/:id2`
 * navigations, which is exactly why this has to be an `effect()` and
 * not just `ngOnInit` logic.
 */
@Component({
  selector: 'eap-chat-page',
  standalone: true,
  imports: [CommonModule, ConversationWorkspaceComponent],
  changeDetection: ChangeDetectionStrategy.OnPush,
  providers: [ChatStateService, ChatFacade],
  templateUrl: './chat.page.html',
  styleUrl: './chat.page.scss'
})
export class ChatPageComponent implements OnInit {
  public readonly conversationId = input<string | undefined>(undefined);

  protected readonly facade = inject(ChatFacade);

  constructor() {
    // allowSignalWrites is required here: loadConversation()/
    // deselectConversation() write to ChatStateService's signals
    // (setSelectedConversationId, etc.) as a side effect of this
    // input changing. This is Angular's documented, sanctioned pattern
    // for "input changed → trigger a side effect that updates other
    // state" — without the flag, Angular throws NG0600 to guard
    // against accidental infinite reactive loops, which doesn't apply
    // here since the write targets different signals than the ones
    // this effect reads.
    effect(
      () => {
        const id = this.conversationId();
        if (id) {
          this.facade.loadConversation(id);
        } else {
          this.facade.deselectConversation();
        }
      },
      { allowSignalWrites: true }
    );
  }

  public ngOnInit(): void {
    // Sidebar list load is independent of which conversation is open
    // and only needs to happen once per component instantiation.
    this.facade.loadConversations();
  }
}
