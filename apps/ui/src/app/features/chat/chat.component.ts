import {
  Component,
  ChangeDetectionStrategy,
  inject,
  OnInit,
  ViewChild,
  ElementRef,
  effect
} from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute } from '@angular/router';
import { ChatFacade } from './services/chat.facade';
import { ChatStateService } from './state/chat-state.service';
import { MessageBubbleComponent } from './components/message-bubble.component';
import { PromptInputComponent } from './components/prompt-input.component';
import { IconComponent } from '@shared/components/icon.component';

@Component({
  selector: 'app-chat',
  standalone: true,
  imports: [CommonModule, MessageBubbleComponent, PromptInputComponent, IconComponent],
  providers: [ChatFacade, ChatStateService],
  template: `
    <div class="chat-viewport">
      <!-- Top Conversation Bar -->
      <header class="chat-header">
        <div class="header-left">
          <h2 class="conversation-title">
            {{ facade.activeConversation()?.title || 'New Conversation' }}
          </h2>
          <span class="model-badge">
            <app-icon name="sparkles" [size]="12"></app-icon>
            gpt-4.1-mini
          </span>
        </div>

        <div class="header-right">
          <button type="button" class="header-action-btn" (click)="facade.startNewChat()" title="Start New Chat">
            <app-icon name="plus" [size]="16"></app-icon>
            <span>New Chat</span>
          </button>
        </div>
      </header>

      <!-- Scrollable Message Stream -->
      <div #scrollContainer class="messages-scroll-area">
        @if (facade.isMessagesLoading()) {
          <div class="loading-state">
            <div class="loading-spinner"></div>
            <p>Loading messages...</p>
          </div>
        } @else if (facade.messages().length === 0) {
          <!-- Modern Minimalist Empty State -->
          <div class="empty-state">
            <div class="empty-icon-circle">
              <app-icon name="sparkles" [size]="32"></app-icon>
            </div>
            <h3>How can I assist your enterprise today?</h3>
            <p class="empty-subtitle">
              Ask questions grounded directly in your uploaded documentation, agreements, and knowledge base.
            </p>

            <div class="starter-prompts">
              @for (prompt of starterPrompts; track prompt) {
                <button type="button" class="starter-card" (click)="onPromptSend(prompt)">
                  <span>{{ prompt }}</span>
                  <app-icon name="chevron-right" [size]="14"></app-icon>
                </button>
              }
            </div>
          </div>
        } @else {
          <div class="messages-list">
            @for (msg of facade.messages(); track msg.id) {
              <app-message-bubble [message]="msg"></app-message-bubble>
            }
          </div>
        }
      </div>

      <!-- Floating Prompt Bar -->
      <footer class="chat-input-area">
        <app-prompt-input
          [disabled]="facade.isSending()"
          [isStreaming]="facade.isStreaming()"
          (send)="onPromptSend($event)"
          (stop)="facade.stopGeneration()"
        ></app-prompt-input>
      </footer>
    </div>
  `,
  styles: [
    `
      :host {
        display: block;
        height: 100%;
        overflow: hidden;
      }

      .chat-viewport {
        display: flex;
        flex-direction: column;
        height: 100%;
        position: relative;
        background: var(--bg-app);
      }

      .chat-header {
        height: 56px;
        padding: 0 1.5rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
        background: var(--glass-bg);
        backdrop-filter: blur(16px);
        border-bottom: 1px solid var(--border-subtle);
        z-index: 10;
        flex-shrink: 0;
      }

      .header-left {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        min-width: 0;
      }

      .conversation-title {
        font-size: 0.95rem;
        font-weight: 600;
        color: var(--text-primary);
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        max-width: 380px;
      }

      .model-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.35rem;
        font-size: 0.72rem;
        font-weight: 500;
        background: var(--bg-chip);
        border: 1px solid var(--border-subtle);
        color: var(--primary-light);
        padding: 0.15rem 0.5rem;
        border-radius: var(--radius-full);
      }

      .header-action-btn {
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        font-size: 0.82rem;
        font-weight: 500;
        padding: 0.35rem 0.75rem;
        border-radius: var(--radius-md);
        background: var(--bg-card);
        border: 1px solid var(--border-default);
        color: var(--text-secondary);
        transition: all var(--transition-fast);

        &:hover {
          background: var(--bg-card-hover);
          color: var(--text-primary);
          border-color: var(--primary);
        }
      }

      .messages-scroll-area {
        flex: 1;
        overflow-y: auto;
        padding: 1.5rem 0 1rem 0;
        scroll-behavior: smooth;
      }

      .messages-list {
        display: flex;
        flex-direction: column;
      }

      .chat-input-area {
        flex-shrink: 0;
        background: linear-gradient(to top, var(--bg-app) 75%, transparent);
        padding-top: 1rem;
      }

      .loading-state {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        height: 100%;
        color: var(--text-muted);
        gap: 0.75rem;
      }

      .loading-spinner {
        width: 24px;
        height: 24px;
        border: 2px solid var(--border-default);
        border-top-color: var(--primary);
        border-radius: 50%;
        animation: spin 0.8s linear infinite;
      }

      .empty-state {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        height: 100%;
        max-width: 640px;
        margin: 0 auto;
        text-align: center;
        padding: 2rem 1rem;
      }

      .empty-icon-circle {
        width: 64px;
        height: 64px;
        border-radius: var(--radius-xl);
        background: linear-gradient(135deg, var(--bg-card), var(--bg-chip));
        border: 1px solid var(--border-subtle);
        color: var(--primary-light);
        display: flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 1.25rem;
        box-shadow: 0 4px 20px rgba(99, 102, 241, 0.15);
      }

      .empty-state h3 {
        font-size: 1.35rem;
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: 0.5rem;
      }

      .empty-subtitle {
        font-size: 0.9rem;
        color: var(--text-secondary);
        margin-bottom: 2rem;
        max-width: 480px;
      }

      .starter-prompts {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 0.75rem;
        width: 100%;
      }

      .starter-card {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0.85rem 1rem;
        background: var(--bg-card);
        border: 1px solid var(--border-subtle);
        border-radius: var(--radius-md);
        text-align: left;
        font-size: 0.85rem;
        color: var(--text-secondary);
        transition: all var(--transition-fast);

        app-icon {
          color: var(--text-muted);
          transition: transform var(--transition-fast);
        }

        &:hover {
          background: var(--bg-card-hover);
          border-color: var(--primary);
          color: var(--text-primary);
          transform: translateY(-1px);

          app-icon {
            color: var(--primary);
            transform: translateX(2px);
          }
        }
      }

      @keyframes spin {
        to { transform: rotate(360deg); }
      }

      @media (max-width: 640px) {
        .starter-prompts {
          grid-template-columns: 1fr;
        }
      }
    `
  ],
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class ChatComponent implements OnInit {
  @ViewChild('scrollContainer') private scrollContainer!: ElementRef<HTMLDivElement>;

  public readonly facade = inject(ChatFacade);
  private readonly route = inject(ActivatedRoute);

  public readonly starterPrompts = [
    'What key policies or guidelines are documented here?',
    'Summarize the primary deliverables from the uploaded docs',
    'Extract any important deadlines and milestones',
    'Find mentions of pricing, terms, and conditions'
  ];

  constructor() {
    // Auto-scroll to bottom whenever new message tokens stream in
    effect(() => {
      const messages = this.facade.messages();
      if (messages.length > 0) {
        setTimeout(() => this.scrollToBottom(), 30);
      }
    });
  }

  public ngOnInit(): void {
    this.facade.loadConversations();

    this.route.paramMap.subscribe((params) => {
      const id = params.get('id');
      if (id) {
        this.facade.selectConversation(id);
      }
    });
  }

  public onPromptSend(prompt: string): void {
    this.facade.sendPrompt(prompt);
  }

  private scrollToBottom(): void {
    if (!this.scrollContainer) return;
    const el = this.scrollContainer.nativeElement;
    el.scrollTop = el.scrollHeight;
  }
}

