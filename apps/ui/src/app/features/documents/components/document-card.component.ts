import { Component, ChangeDetectionStrategy, input, output } from '@angular/core';
import { CommonModule } from '@angular/common';
import { KnowledgeDocument } from '@data/models/document.dto';
import { IconComponent } from '@shared/components/icon.component';

@Component({
  selector: 'app-document-card',
  standalone: true,
  imports: [CommonModule, IconComponent],
  template: `
    <div class="document-row" [class.is-indexing]="isIndexing()" [class.is-deleting]="isDeleting()">
      <!-- File Icon & Details -->
      <div class="doc-main-info">
        <div class="doc-icon-badge" [attr.data-type]="getFileType(document().filename)">
          <app-icon name="file-text" [size]="18"></app-icon>
        </div>

        <div class="doc-text-meta">
          <h4 class="doc-filename" [title]="document().filename">{{ document().filename }}</h4>
          <div class="doc-submeta">
            <span>{{ formatBytes(document().sizeBytes) }}</span>
            <span class="dot-separator">•</span>
            <span>Uploaded {{ formatDate(document().createdAt) }}</span>
          </div>
        </div>
      </div>

      <!-- Status Badge -->
      <div class="doc-status-col">
        @switch (document().status) {
          @case ('indexed') {
            <span class="status-badge status-indexed" title="Indexed and ready for AI chat grounding">
              <app-icon name="check" [size]="12"></app-icon>
              Indexed
            </span>
          }
          @case ('indexing') {
            <span class="status-badge status-indexing">
              <div class="badge-spinner"></div>
              Indexing...
            </span>
          }
          @case ('failed') {
            <span class="status-badge status-failed">
              <app-icon name="alert-circle" [size]="12"></app-icon>
              Failed
            </span>
          }
          @default {
            <span class="status-badge status-uploaded">
              Uploaded
            </span>
          }
        }
      </div>

      <!-- Action Buttons -->
      <div class="doc-actions-col">
        <!-- Retry Action only if failed -->
        @if (document().status === 'failed') {
          <button
            type="button"
            class="action-btn retry-btn"
            [disabled]="isIndexing() || isDeleting()"
            (click)="index.emit(document().id)"
            title="Retry indexing into vector database"
          >
            @if (isIndexing()) {
              <div class="btn-spinner"></div>
              <span>Retrying...</span>
            } @else {
              <app-icon name="refresh-cw" [size]="13"></app-icon>
              <span>Retry Indexing</span>
            }
          </button>
        }

        <!-- Download Action -->
        <button
          type="button"
          class="action-icon-btn"
          (click)="download.emit(document())"
          title="Download original file"
          [disabled]="isDeleting()"
        >
          <app-icon name="download" [size]="15"></app-icon>
        </button>

        <!-- Delete Action -->
        <button
          type="button"
          class="action-icon-btn delete-btn"
          (click)="onDelete()"
          title="Delete document"
          [disabled]="isDeleting()"
        >
          <app-icon name="trash" [size]="15"></app-icon>
        </button>
      </div>
    </div>
  `,
  styles: [
    `
      :host {
        display: block;
        margin-bottom: 0.5rem;
      }

      .document-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 1rem;
        background: var(--bg-card);
        border: 1px solid var(--border-subtle);
        border-radius: var(--radius-md);
        padding: 0.85rem 1.15rem;
        transition: all var(--transition-fast);

        &:hover {
          background: var(--bg-card-hover);
          border-color: var(--border-default);
          transform: translateX(2px);
        }

        &.is-deleting {
          opacity: 0.4;
          pointer-events: none;
        }
      }

      .doc-main-info {
        display: flex;
        align-items: center;
        gap: 0.85rem;
        min-width: 0;
        flex: 1;
      }

      .doc-icon-badge {
        width: 38px;
        height: 38px;
        border-radius: var(--radius-md);
        background: var(--bg-chip);
        color: var(--primary-light);
        display: flex;
        align-items: center;
        justify-content: center;
        flex-shrink: 0;

        &[data-type='pdf'] {
          background: rgba(239, 68, 68, 0.12);
          color: #ef4444;
        }
        &[data-type='docx'] {
          background: rgba(59, 130, 246, 0.12);
          color: #3b82f6;
        }
        &[data-type='md'],
        &[data-type='txt'] {
          background: rgba(16, 185, 129, 0.12);
          color: #10b981;
        }
      }

      .doc-text-meta {
        min-width: 0;
      }

      .doc-filename {
        font-size: 0.92rem;
        font-weight: 600;
        color: var(--text-primary);
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        max-width: 380px;
      }

      .doc-submeta {
        display: flex;
        align-items: center;
        gap: 0.4rem;
        font-size: 0.75rem;
        color: var(--text-muted);
        margin-top: 0.15rem;
      }

      .dot-separator {
        opacity: 0.4;
      }

      .status-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.3rem;
        font-size: 0.75rem;
        font-weight: 600;
        padding: 0.2rem 0.6rem;
        border-radius: var(--radius-full);
        white-space: nowrap;
      }

      .status-indexed {
        background: var(--success-bg);
        color: var(--success);
      }

      .status-indexing {
        background: rgba(59, 130, 246, 0.15);
        color: #60a5fa;
      }

      .status-uploaded {
        background: var(--warning-bg);
        color: var(--warning);
      }

      .status-failed {
        background: var(--danger-bg);
        color: var(--danger);
      }

      .badge-spinner {
        width: 10px;
        height: 10px;
        border: 2px solid rgba(96, 165, 250, 0.3);
        border-top-color: #60a5fa;
        border-radius: 50%;
        animation: spin 0.8s linear infinite;
      }

      .doc-actions-col {
        display: flex;
        align-items: center;
        gap: 0.45rem;
      }

      .action-btn {
        display: inline-flex;
        align-items: center;
        gap: 0.35rem;
        font-size: 0.78rem;
        font-weight: 600;
        padding: 0.35rem 0.75rem;
        border-radius: var(--radius-md);
        transition: all var(--transition-fast);
      }

      .retry-btn {
        background: rgba(239, 68, 68, 0.12);
        color: #f87171;
        border: 1px solid rgba(239, 68, 68, 0.3);

        &:hover:not(:disabled) {
          background: rgba(239, 68, 68, 0.22);
          border-color: #f87171;
          transform: translateY(-1px);
        }

        &:disabled {
          opacity: 0.6;
          cursor: not-allowed;
        }
      }

      .action-icon-btn {
        width: 32px;
        height: 32px;
        border-radius: var(--radius-md);
        display: flex;
        align-items: center;
        justify-content: center;
        color: var(--text-muted);
        transition: all var(--transition-fast);

        &:hover:not(:disabled) {
          background: var(--bg-card-hover);
          color: var(--text-primary);
        }

        &.delete-btn:hover:not(:disabled) {
          background: var(--danger-bg);
          color: var(--danger);
        }
      }

      .btn-spinner {
        width: 12px;
        height: 12px;
        border: 2px solid rgba(255, 255, 255, 0.4);
        border-top-color: #ffffff;
        border-radius: 50%;
        animation: spin 0.8s linear infinite;
      }

      @keyframes spin {
        to { transform: rotate(360deg); }
      }

      @media (max-width: 680px) {
        .document-row {
          flex-direction: column;
          align-items: flex-start;
          gap: 0.75rem;
        }
        .doc-actions-col {
          width: 100%;
          justify-content: flex-end;
        }
      }
    `
  ],
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class DocumentCardComponent {
  public readonly document = input.required<KnowledgeDocument>();
  public readonly isIndexing = input<boolean>(false);
  public readonly isDeleting = input<boolean>(false);

  public readonly index = output<string>();
  public readonly download = output<KnowledgeDocument>();
  public readonly delete = output<{ id: string; filename: string }>();

  public getFileType(filename: string): string {
    const ext = filename.split('.').pop()?.toLowerCase();
    return ext || 'txt';
  }

  public formatBytes(bytes: number): string {
    if (!bytes) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return `${parseFloat((bytes / Math.pow(k, i)).toFixed(1))} ${sizes[i]}`;
  }

  public formatDate(dateStr: string): string {
    if (!dateStr) return '';
    const date = new Date(dateStr);
    return date.toLocaleDateString([], { month: 'short', day: 'numeric', year: 'numeric' });
  }

  public onDelete(): void {
    if (confirm(`Are you sure you want to delete "${this.document().filename}"?`)) {
      this.delete.emit({ id: this.document().id, filename: this.document().filename });
    }
  }
}

