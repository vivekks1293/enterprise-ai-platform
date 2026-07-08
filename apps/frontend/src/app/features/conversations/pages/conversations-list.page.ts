import { ChangeDetectionStrategy, Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ConversationsFacade } from '@features/conversations/services/conversations.facade';
import { ConversationsStateService } from '@features/conversations/state/conversations-state.service';
import { CardComponent } from '@shared/ui/card/card.component';
import { EmptyStateComponent } from '@shared/ui/empty-state/empty-state.component';
import { LoadingStateComponent } from '@shared/ui/loading-state/loading-state.component';
import { ErrorStateComponent } from '@shared/ui/error-state/error-state.component';
import { BadgeComponent } from '@shared/ui/badge/badge.component';
import { RelativeTimePipe } from '@shared/pipes/relative-time.pipe';

@Component({
  selector: 'eap-conversations-list-page',
  standalone: true,
  imports: [
    CommonModule,
    CardComponent,
    EmptyStateComponent,
    LoadingStateComponent,
    ErrorStateComponent,
    BadgeComponent,
    RelativeTimePipe
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
  providers: [ConversationsStateService, ConversationsFacade],
  templateUrl: './conversations-list.page.html'
})
export class ConversationsListPageComponent implements OnInit {
  protected readonly facade = inject(ConversationsFacade);

  public ngOnInit(): void {
    this.facade.loadConversations();
  }
}
