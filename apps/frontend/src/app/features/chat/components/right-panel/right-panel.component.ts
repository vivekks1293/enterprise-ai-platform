import { ChangeDetectionStrategy, Component, input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ChatConversationSummary } from '@features/chat/models/chat-conversation-summary.model';
import { CardComponent } from '@shared/ui/card/card.component';
import { RelativeTimePipe } from '@shared/pipes/relative-time.pipe';

/**
 * Every section here is a static placeholder card today. Wiring a
 * real one up later (e.g. Citations bound to a signal of citation
 * objects) is additive — this panel's shell, collapse behavior, and
 * responsive width don't change when that happens.
 */
@Component({
  selector: 'eap-right-panel',
  standalone: true,
  imports: [CommonModule, CardComponent, RelativeTimePipe],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './right-panel.component.html',
  styleUrl: './right-panel.component.scss'
})
export class RightPanelComponent {
  public readonly conversation = input<ChatConversationSummary | null>(null);
  public readonly collapsed = input<boolean>(false);
}
