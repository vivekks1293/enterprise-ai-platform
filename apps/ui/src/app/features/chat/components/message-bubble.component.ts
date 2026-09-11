import { Component, ChangeDetectionStrategy, input, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ChatMessage } from '@data/models/chat.dto';
import { MarkdownPipe } from '@shared/pipes/markdown.pipe';
import { IconComponent } from '@shared/components/icon.component';
import { CitationChipsComponent } from './citation-chips.component';

@Component({
  selector: 'app-message-bubble',
  standalone: true,
  imports: [CommonModule, MarkdownPipe, IconComponent, CitationChipsComponent],
  template: `
    <div class="message-row" [class.user-row]="message().role === 'user'" [class.assistant-row]="message().role === 'assistant'">
      <!-- Avatar (Assistant) -->
      @if (message().role === 'assistant') {
        <div class="avatar assistant-avatar" title="AI Assistant">
          <app-icon name="sparkles" [size]="16"></app-icon>
        </div>
      }

      <div class="message-content-wrapper">
        <!-- Message Bubble -->
        <div class="bubble" [class.user-bubble]="message().role === 'user'" [class.assistant-bubble]="message().role === 'assistant'">
          @if (message().role === 'user') {
            <p class="user-text">{{ message().content }}</p>
          } @else {
            <div class="assistant-markdown" [innerHTML]="message().content | markdown"></div>
            @if (message().isStreaming) {
              <span class="streaming-cursor"></span>
            }

            <!-- Bottom Inline Citations -->
            <app-citation-chips [citations]="message().citations"></app-citation-chips>
          }
        </div>

        <!-- Meta info (Timestamp & Copy Action) -->
        <div class="message-meta">
          <span class="timestamp">{{ formatTime(message().createdAt) }}</span>
          @if (message().role === 'assistant' && message().content && !message().isStreaming) {
            <button type="button" class="copy-btn" (click)="copyContent()" [title]="copied() ? 'Copied!' : 'Copy response'">
              <app-icon [name]="copied() ? 'check' : 'copy'" [size]="12"></app-icon>
              <span>{{ copied() ? 'Copied' : 'Copy' }}</span>
            </button>
          }
        </div>
      </div>

      <!-- Avatar (User) -->
      @if (message().role === 'user') {
        <div class="avatar user-avatar" title="You">
          <app-icon name="user" [size]="15"></app-icon>
        </div>
      }
    </div>
  `,
  styles: [
    `
      :host {
        display: block;
        width: 100%;
        margin-bottom: 1.5rem;
      }

      .message-row {
        display: flex;
        gap: 0.75rem;
        max-width: 860px;
        margin: 0 auto;
        padding: 0 1rem;
      }

      .user-row {
        justify-content: flex-end;
      }

      .assistant-row {
        justify-content: flex-start;
      }

      .avatar {
        width: 32px;
        height: 32px;
        border-radius: var(--radius-md);
        display: flex;
        align-items: center;
        justify-content: center;
        flex-shrink: 0;
        margin-top: 2px;
      }

      .assistant-avatar {
        background: linear-gradient(135deg, var(--primary), #8b5cf6);
        color: #ffffff;
        box-shadow: 0 2px 8px var(--primary-glow);
      }

      .user-avatar {
        background: var(--bg-card);
        border: 1px solid var(--border-default);
        color: var(--text-secondary);
      }

      .message-content-wrapper {
        max-width: 85%;
        display: flex;
        flex-direction: column;
      }

      .user-row .message-content-wrapper {
        align-items: flex-end;
      }

      .bubble {
        border-radius: var(--radius-lg);
        position: relative;
        word-break: break-word;
      }

      .user-bubble {
        background: var(--bg-bubble-user);
        border: 1px solid var(--border-default);
        color: var(--text-primary);
        padding: 0.75rem 1rem;
        border-bottom-right-radius: var(--radius-sm);
        box-shadow: var(--shadow-sm);

        .user-text {
          font-size: 0.95rem;
          line-height: 1.5;
          white-space: pre-wrap;
        }
      }

      .assistant-bubble {
        background: transparent;
        color: var(--text-primary);
        padding: 0.25rem 0.5rem 0.5rem 0.25rem;
        font-size: 0.95rem;
        line-height: 1.6;
      }

      .message-meta {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        font-size: 0.72rem;
        color: var(--text-muted);
        margin-top: 0.35rem;
        padding: 0 0.25rem;
      }

      .copy-btn {
        display: inline-flex;
        align-items: center;
        gap: 0.25rem;
        color: var(--text-muted);
        transition: color var(--transition-fast);
        &:hover {
          color: var(--text-primary);
        }
      }
    `
  ],
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class MessageBubbleComponent {
  public readonly message = input.required<ChatMessage>();
  public readonly copied = signal<boolean>(false);

  public formatTime(dateStr?: string): string {
    if (!dateStr) return '';
    const date = new Date(dateStr);
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  }

  public copyContent(): void {
    const text = this.message().content;
    if (!text) return;
    navigator.clipboard.writeText(text).then(() => {
      this.copied.set(true);
      setTimeout(() => this.copied.set(false), 2000);
    });
  }
}

