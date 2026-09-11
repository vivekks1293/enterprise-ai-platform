import {
  Component,
  ChangeDetectionStrategy,
  output,
  input,
  signal,
  ViewChild,
  ElementRef
} from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { IconComponent } from '@shared/components/icon.component';

@Component({
  selector: 'app-prompt-input',
  standalone: true,
  imports: [CommonModule, FormsModule, IconComponent],
  template: `
    <div class="prompt-dock">
      <div class="dock-container" [class.dock-focused]="isFocused()">
        <!-- Auto-expanding Textarea -->
        <textarea
          #textareaRef
          [(ngModel)]="promptText"
          (keydown)="onKeyDown($event)"
          (input)="autoResize()"
          (focus)="isFocused.set(true)"
          (blur)="isFocused.set(false)"
          placeholder="Ask a question about your documents, policies, or data..."
          rows="1"
          [disabled]="disabled()"
        ></textarea>

        <!-- Right Side Action Dock -->
        <div class="action-buttons">
          @if (isStreaming()) {
            <button
              type="button"
              class="dock-btn stop-btn"
              (click)="stop.emit()"
              title="Stop generation"
            >
              <app-icon name="stop" [size]="14"></app-icon>
            </button>
          } @else {
            <button
              type="button"
              class="dock-btn send-btn"
              [disabled]="!hasText() || disabled()"
              (click)="submitPrompt()"
              title="Send message (Enter)"
            >
              <app-icon name="send" [size]="14"></app-icon>
            </button>
          }
        </div>
      </div>

      <div class="dock-footer">
        <span>Enterprise AI • Grounded retrieval & verification</span>
      </div>
    </div>
  `,
  styles: [
    `
      :host {
        display: block;
        width: 100%;
        max-width: 860px;
        margin: 0 auto;
        padding: 0 1rem 1rem 1rem;
      }

      .prompt-dock {
        position: relative;
      }

      .dock-container {
        display: flex;
        align-items: flex-end;
        background: var(--bg-card);
        border: 1px solid var(--border-default);
        border-radius: var(--radius-xl);
        padding: 0.6rem 0.75rem 0.6rem 1.1rem;
        box-shadow: var(--shadow-lg);
        transition: all var(--transition-fast);

        &.dock-focused {
          border-color: var(--border-focus);
          box-shadow: 0 0 0 1px var(--primary), var(--shadow-lg);
        }
      }

      textarea {
        flex: 1;
        max-height: 180px;
        resize: none;
        font-size: 0.95rem;
        line-height: 1.45;
        color: var(--text-primary);
        background: transparent;
        padding-top: 0.2rem;
        padding-bottom: 0.2rem;

        &::placeholder {
          color: var(--text-muted);
        }
      }

      .action-buttons {
        display: flex;
        align-items: center;
        gap: 0.4rem;
        margin-left: 0.5rem;
        flex-shrink: 0;
      }

      .dock-btn {
        width: 34px;
        height: 34px;
        border-radius: var(--radius-full);
        display: flex;
        align-items: center;
        justify-content: center;
        transition: all var(--transition-fast);
      }

      .send-btn {
        background: var(--primary);
        color: #ffffff;

        &:hover:not(:disabled) {
          background: var(--primary-hover);
          transform: scale(1.05);
        }

        &:disabled {
          opacity: 0.35;
          cursor: not-allowed;
        }
      }

      .stop-btn {
        background: var(--danger);
        color: #ffffff;
        &:hover {
          opacity: 0.9;
          transform: scale(1.05);
        }
      }

      .dock-footer {
        text-align: center;
        margin-top: 0.4rem;
        font-size: 0.72rem;
        color: var(--text-muted);
        letter-spacing: 0.02em;
      }
    `
  ],
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class PromptInputComponent {
  @ViewChild('textareaRef') private textareaRef!: ElementRef<HTMLTextAreaElement>;

  public readonly disabled = input<boolean>(false);
  public readonly isStreaming = input<boolean>(false);

  public readonly send = output<string>();
  public readonly stop = output<void>();

  public promptText = '';
  public readonly isFocused = signal<boolean>(false);

  public hasText(): boolean {
    return this.promptText.trim().length > 0;
  }

  public onKeyDown(event: KeyboardEvent): void {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      this.submitPrompt();
    }
  }

  public submitPrompt(): void {
    const text = this.promptText.trim();
    if (!text || this.disabled() || this.isStreaming()) return;

    this.send.emit(text);
    this.promptText = '';
    this.resetTextareaHeight();
  }

  public autoResize(): void {
    if (!this.textareaRef) return;
    const el = this.textareaRef.nativeElement;
    el.style.height = 'auto';
    el.style.height = `${Math.min(el.scrollHeight, 180)}px`;
  }

  private resetTextareaHeight(): void {
    if (!this.textareaRef) return;
    const el = this.textareaRef.nativeElement;
    el.style.height = 'auto';
  }
}

