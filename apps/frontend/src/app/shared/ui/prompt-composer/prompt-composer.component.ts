import {
  ChangeDetectionStrategy,
  Component,
  ElementRef,
  ViewChild,
  computed,
  input,
  output,
  signal
} from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

/**
 * Purely presentational. Emits `submit(text)` and nothing else — it
 * has no idea a Chat feature, an AI provider, or a backend exists.
 * That's deliberate: this component is meant to be reused anywhere an
 * "ask AI" input is needed later, not just in the Chat workspace.
 *
 * Attachment and microphone buttons are permanently `disabled` per
 * this phase's scope — a disabled button never fires a click, so
 * there is intentionally no handler wired to them at all yet.
 */
@Component({
  selector: 'eap-prompt-composer',
  standalone: true,
  imports: [CommonModule, FormsModule],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './prompt-composer.component.html',
  styleUrl: './prompt-composer.component.scss'
})
export class PromptComposerComponent {
  public readonly disabled = input<boolean>(false);
  public readonly loading = input<boolean>(false);
  public readonly placeholder = input<string>('Send a message…');
  public readonly maxLength = input<number>(4000);
  /** true = plain Enter sends, Shift+Enter for a newline (default).
   *  false = only Ctrl/Cmd+Enter sends, plain Enter always inserts a newline. */
  public readonly sendOnEnter = input<boolean>(true);
  /** When true, the send button becomes a Stop button that emits
   *  `stop` instead of `submit` — set by the parent while a response
   *  is actively generating. Generic (not chat-specific): any
   *  long-running generation this composer drives can use it. */
  public readonly showStop = input<boolean>(false);

  public readonly submit = output<string>();
  public readonly stop = output<void>();

  @ViewChild('textareaRef') private readonly textareaRef?: ElementRef<HTMLTextAreaElement>;

  protected readonly text = signal('');

  protected readonly shortcutHint = computed(() =>
    this.sendOnEnter() ? 'Press Enter to send, Shift+Enter for a new line' : 'Press Ctrl+Enter to send'
  );

  protected onInput(value: string): void {
    this.text.set(value);
    this.resizeTextarea();
  }

  protected onKeydown(event: KeyboardEvent): void {
    if (event.key !== 'Enter') {
      return;
    }

    const isSendCombo = event.ctrlKey || event.metaKey;
    const isPlainEnterSend = this.sendOnEnter() && !event.shiftKey && !event.ctrlKey && !event.metaKey;

    if (isSendCombo || isPlainEnterSend) {
      event.preventDefault();
      this.trySend();
    }
    // Otherwise (Shift+Enter, or plain Enter when sendOnEnter is false) — let the newline through.
  }

  protected trySend(): void {
    const trimmed = this.text().trim();
    if (!trimmed || this.disabled() || this.loading()) {
      return;
    }
    this.submit.emit(trimmed);
    this.text.set('');
    this.resizeTextarea(true);
  }

  private resizeTextarea(reset = false): void {
    const el = this.textareaRef?.nativeElement;
    if (!el) {
      return;
    }
    if (reset) {
      el.style.height = 'auto';
      return;
    }
    el.style.height = 'auto';
    el.style.height = `${el.scrollHeight}px`;
  }
}
