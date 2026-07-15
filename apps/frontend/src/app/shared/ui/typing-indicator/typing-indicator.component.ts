import { ChangeDetectionStrategy, Component } from '@angular/core';
import { CommonModule } from '@angular/common';

/**
 * Generic "something is being generated" indicator — not chat-specific.
 * Reusable anywhere a background/async response is pending (agent
 * progress, background job status), which is why it lives in
 * shared/ui rather than features/chat/components.
 */
@Component({
  selector: 'eap-typing-indicator',
  standalone: true,
  imports: [CommonModule],
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <span class="eap-typing-indicator" role="status" aria-label="Generating response">
      <span></span><span></span><span></span>
    </span>
  `,
  styles: `
    .eap-typing-indicator {
      display: inline-flex;
      align-items: center;
      gap: 0.25rem;
      padding: 0.25rem 0;

      span {
        width: 6px;
        height: 6px;
        border-radius: 50%;
        background-color: var(--eap-text-muted, #8a8fa3);
        animation: eap-typing-bounce 1.2s infinite ease-in-out;

        &:nth-child(2) {
          animation-delay: 0.15s;
        }
        &:nth-child(3) {
          animation-delay: 0.3s;
        }
      }
    }

    @keyframes eap-typing-bounce {
      0%,
      60%,
      100% {
        transform: translateY(0);
        opacity: 0.5;
      }
      30% {
        transform: translateY(-3px);
        opacity: 1;
      }
    }
  `
})
export class TypingIndicatorComponent {}
