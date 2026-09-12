import {
  Component,
  ChangeDetectionStrategy,
  input,
  signal,
  computed,
  effect,
  OnInit,
  OnDestroy
} from '@angular/core';
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
            @if (message().isStreaming && !message().content) {
              <!-- Modern Minimalist Thinking / Retrieving State -->
              <div class="thinking-container">
                <div class="thinking-header">
                  <div class="thinking-sparkle-pulse">
                    <app-icon name="sparkles" [size]="14"></app-icon>
                  </div>
                  <span class="thinking-status-text">{{ currentThinkingText() }}</span>
                  <div class="typing-dots">
                    <span class="dot"></span>
                    <span class="dot"></span>
                    <span class="dot"></span>
                  </div>
                </div>

                <div class="shimmer-placeholder">
                  <div class="shimmer-bar shimmer-bar-wide"></div>
                  <div class="shimmer-bar shimmer-bar-mid"></div>
                </div>
              </div>
            } @else {
              <div class="assistant-markdown" [innerHTML]="message().content | markdown"></div>
              @if (message().isStreaming) {
                <span class="streaming-cursor"></span>
              }

              <!-- Bottom Inline Citations -->
              <app-citation-chips [citations]="message().citations"></app-citation-chips>
            }
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

      .thinking-container {
        display: flex;
        flex-direction: column;
        gap: 0.65rem;
        padding: 0.25rem 0.15rem;
        min-width: 270px;
        animation: fadeIn 0.2s ease-in-out;
      }

      .thinking-header {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        background: var(--bg-card);
        border: 1px solid var(--border-subtle);
        padding: 0.35rem 0.75rem;
        border-radius: var(--radius-full);
        width: fit-content;
        box-shadow: var(--shadow-sm);
      }

      .thinking-sparkle-pulse {
        color: var(--primary-light);
        display: flex;
        align-items: center;
        justify-content: center;
        animation: pulse-glow 1.5s ease-in-out infinite;
      }

      .thinking-status-text {
        font-size: 0.8rem;
        font-weight: 500;
        color: var(--text-secondary);
        letter-spacing: -0.01em;
      }

      .typing-dots {
        display: inline-flex;
        align-items: center;
        gap: 0.25rem;
        padding-left: 0.1rem;

        .dot {
          width: 3.5px;
          height: 3.5px;
          border-radius: 50%;
          background: var(--primary-light);
          animation: dot-jump 1.4s infinite ease-in-out both;

          &:nth-child(1) { animation-delay: -0.32s; }
          &:nth-child(2) { animation-delay: -0.16s; }
          &:nth-child(3) { animation-delay: 0s; }
        }
      }

      .shimmer-placeholder {
        display: flex;
        flex-direction: column;
        gap: 0.45rem;
        padding: 0.25rem 0;
      }

      .shimmer-bar {
        height: 10px;
        border-radius: var(--radius-sm);
        background: linear-gradient(
          90deg,
          var(--bg-card) 25%,
          var(--bg-card-hover) 50%,
          var(--bg-card) 75%
        );
        background-size: 200% 100%;
        animation: shimmer 1.8s infinite linear;
      }

      .shimmer-bar-wide {
        width: 70%;
      }

      .shimmer-bar-mid {
        width: 42%;
      }

      .streaming-cursor {
        display: inline-block;
        width: 6px;
        height: 15px;
        background: var(--primary);
        margin-left: 4px;
        vertical-align: -2px;
        border-radius: 2px;
        animation: cursor-pulse 0.7s infinite alternate ease-in-out;
        box-shadow: 0 0 8px var(--primary-glow);
      }

      @keyframes pulse-glow {
        0%, 100% {
          transform: scale(1);
          filter: drop-shadow(0 0 2px var(--primary-glow));
        }
        50% {
          transform: scale(1.15);
          filter: drop-shadow(0 0 6px var(--primary-glow));
        }
      }

      @keyframes dot-jump {
        0%, 80%, 100% {
          transform: scale(0.6);
          opacity: 0.4;
        }
        40% {
          transform: scale(1.2);
          opacity: 1;
        }
      }

      @keyframes shimmer {
        0% { background-position: 200% 0; }
        100% { background-position: -200% 0; }
      }

      @keyframes cursor-pulse {
        0% { opacity: 0.25; transform: scaleY(0.85); }
        100% { opacity: 1; transform: scaleY(1); }
      }

      @keyframes fadeIn {
        from { opacity: 0; transform: translateY(3px); }
        to { opacity: 1; transform: translateY(0); }
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
export class MessageBubbleComponent implements OnInit, OnDestroy {
  public readonly message = input.required<ChatMessage>();
  public readonly copied = signal<boolean>(false);
  public readonly thinkingPhase = signal<number>(0);

  private timerId?: ReturnType<typeof setInterval>;

  private readonly thinkingPhrases = [
    'Searching knowledge base...',
    'Analyzing relevant passages...',
    'Synthesizing verified answer...'
  ];

  public readonly currentThinkingText = computed(() => {
    return this.thinkingPhrases[this.thinkingPhase() % this.thinkingPhrases.length];
  });

  constructor() {
    effect(
      () => {
        const msg = this.message();
        if (msg.role === 'assistant' && msg.isStreaming && !msg.content) {
          this.startThinkingTimer();
        } else {
          this.stopThinkingTimer();
        }
      },
      { allowSignalWrites: true }
    );
  }

  public ngOnInit(): void {
    const msg = this.message();
    if (msg.role === 'assistant' && msg.isStreaming && !msg.content) {
      this.startThinkingTimer();
    }
  }

  public ngOnDestroy(): void {
    this.stopThinkingTimer();
  }

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

  private startThinkingTimer(): void {
    if (this.timerId) return;
    this.thinkingPhase.set(0);
    this.timerId = setInterval(() => {
      this.thinkingPhase.update((p) => {
        if (p < this.thinkingPhrases.length - 1) {
          return p + 1;
        }
        return p;
      });
    }, 1800);
  }

  private stopThinkingTimer(): void {
    if (this.timerId) {
      clearInterval(this.timerId);
      this.timerId = undefined;
    }
  }
}

