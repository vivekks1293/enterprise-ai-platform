import { Component, ChangeDetectionStrategy, input, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Citation } from '@data/models/chat.dto';
import { IconComponent } from '@shared/components/icon.component';

@Component({
  selector: 'app-citation-chips',
  standalone: true,
  imports: [CommonModule, IconComponent],
  template: `
    @if (citations() && citations()!.length > 0) {
      <div class="citations-container">
        <div class="citations-header">
          <app-icon name="sparkles" [size]="14"></app-icon>
          <span>Sources & Citations ({{ citations()!.length }})</span>
        </div>

        <div class="chips-row">
          @for (citation of citations()!; track citation.chunkId + $index) {
            <button
              type="button"
              class="citation-chip"
              [class.active]="selectedCitation()?.chunkId === citation.chunkId"
              (click)="toggleCitation(citation)"
              title="Click to preview source excerpt"
            >
              <app-icon name="file-text" [size]="13"></app-icon>
              <span class="filename">{{ citation.filename }}</span>
              @if (citation.pageNumber) {
                <span class="page-badge">p.{{ citation.pageNumber }}</span>
              }
              <span class="score-badge">{{ formatScore(citation.similarityScore) }}</span>
            </button>
          }
        </div>

        <!-- Inline Expandable Grounding Card -->
        @if (selectedCitation(); as active) {
          <div class="citation-detail-card">
            <div class="detail-header">
              <div class="detail-title">
                <app-icon name="file-text" [size]="15"></app-icon>
                <strong>{{ active.filename }}</strong>
                @if (active.pageNumber) {
                  <span class="detail-page">Page {{ active.pageNumber }}</span>
                }
              </div>
              <div class="detail-actions">
                <span class="score-pill">Match: {{ formatScore(active.similarityScore) }}</span>
                <button type="button" class="close-btn" (click)="clearSelection()" title="Close details">
                  &times;
                </button>
              </div>
            </div>

            <div class="detail-body">
              <p class="chunk-meta">
                <span>Chunk ID: <code>{{ active.chunkId }}</code></span>
                <span>Document ID: <code>{{ active.documentId.slice(0, 8) }}...</code></span>
              </p>
              @if (active.contentSnippet) {
                <div class="snippet-box">
                  <p>{{ active.contentSnippet }}</p>
                </div>
              } @else {
                <p class="snippet-fallback">
                  This response was verified and grounded against this indexed document section.
                </p>
              }
            </div>
          </div>
        }
      </div>
    }
  `,
  styles: [
    `
      .citations-container {
        margin-top: 1rem;
        padding-top: 0.75rem;
        border-top: 1px solid var(--border-subtle);
      }

      .citations-header {
        display: flex;
        align-items: center;
        gap: 0.4rem;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: var(--text-muted);
        margin-bottom: 0.5rem;

        app-icon {
          color: var(--primary-light);
        }
      }

      .chips-row {
        display: flex;
        flex-wrap: wrap;
        gap: 0.45rem;
      }

      .citation-chip {
        display: inline-flex;
        align-items: center;
        gap: 0.35rem;
        background: var(--bg-chip);
        border: 1px solid var(--border-subtle);
        padding: 0.25rem 0.55rem;
        border-radius: var(--radius-full);
        font-size: 0.78rem;
        color: var(--text-secondary);
        transition: all var(--transition-fast);

        app-icon {
          color: var(--primary-light);
        }

        .filename {
          max-width: 140px;
          white-space: nowrap;
          overflow: hidden;
          text-overflow: ellipsis;
          font-weight: 500;
        }

        .page-badge {
          background: rgba(255, 255, 255, 0.06);
          padding: 0.1rem 0.35rem;
          border-radius: var(--radius-sm);
          font-size: 0.72rem;
          color: var(--text-muted);
        }

        .score-badge {
          font-size: 0.7rem;
          color: var(--success);
          font-weight: 600;
        }

        &:hover {
          background: var(--bg-chip-hover);
          border-color: var(--primary);
          color: var(--text-primary);
          transform: translateY(-1px);
        }

        &.active {
          background: var(--primary);
          border-color: var(--primary-light);
          color: #ffffff;

          app-icon {
            color: #ffffff;
          }

          .page-badge,
          .score-badge {
            background: rgba(255, 255, 255, 0.2);
            color: #ffffff;
          }
        }
      }

      .citation-detail-card {
        margin-top: 0.75rem;
        background: var(--bg-card);
        border: 1px solid var(--border-default);
        border-radius: var(--radius-md);
        padding: 0.85rem;
        box-shadow: var(--shadow-md);
        animation: fadeIn 0.2s ease-out;
      }

      .detail-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 0.5rem;
        padding-bottom: 0.4rem;
        border-bottom: 1px solid var(--border-subtle);
      }

      .detail-title {
        display: flex;
        align-items: center;
        gap: 0.4rem;
        font-size: 0.85rem;
        color: var(--text-primary);

        app-icon {
          color: var(--primary);
        }

        .detail-page {
          font-size: 0.75rem;
          background: var(--bg-chip);
          padding: 0.1rem 0.4rem;
          border-radius: var(--radius-sm);
          color: var(--primary-light);
        }
      }

      .detail-actions {
        display: flex;
        align-items: center;
        gap: 0.5rem;
      }

      .score-pill {
        font-size: 0.72rem;
        font-weight: 600;
        padding: 0.15rem 0.5rem;
        border-radius: var(--radius-full);
        background: var(--success-bg);
        color: var(--success);
      }

      .close-btn {
        font-size: 1.1rem;
        line-height: 1;
        color: var(--text-muted);
        padding: 0.1rem 0.3rem;
        border-radius: var(--radius-sm);
        &:hover {
          color: var(--text-primary);
          background: var(--bg-card-hover);
        }
      }

      .detail-body {
        font-size: 0.82rem;
        color: var(--text-secondary);
      }

      .chunk-meta {
        display: flex;
        gap: 1rem;
        font-size: 0.73rem;
        color: var(--text-muted);
        margin-bottom: 0.4rem;
      }

      .snippet-box {
        background: rgba(0, 0, 0, 0.2);
        border-left: 2px solid var(--primary);
        padding: 0.5rem 0.75rem;
        border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
        font-size: 0.82rem;
        line-height: 1.45;
        color: var(--text-primary);
      }

      .snippet-fallback {
        font-style: italic;
        color: var(--text-muted);
        font-size: 0.78rem;
      }

      @keyframes fadeIn {
        from {
          opacity: 0;
          transform: translateY(4px);
        }
        to {
          opacity: 1;
          transform: translateY(0);
        }
      }
    `
  ],
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class CitationChipsComponent {
  public readonly citations = input<readonly Citation[] | undefined>();
  public readonly selectedCitation = signal<Citation | null>(null);

  public toggleCitation(citation: Citation): void {
    if (this.selectedCitation()?.chunkId === citation.chunkId) {
      this.selectedCitation.set(null);
    } else {
      this.selectedCitation.set(citation);
    }
  }

  public clearSelection(): void {
    this.selectedCitation.set(null);
  }

  public formatScore(score: number): string {
    if (!score) return '';
    // If score is normalized between 0-1, show percentage; else show fixed decimal
    if (score <= 1) {
      return `${Math.round(score * 100)}%`;
    }
    return score.toFixed(2);
  }
}

