import { Component, ChangeDetectionStrategy, input, signal, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Citation } from '@data/models/chat.dto';
import { IconComponent } from '@shared/components/icon.component';

export interface GroupedSource {
  readonly documentId: string;
  readonly filename: string;
  readonly pagesLabel: string;
  readonly bestScore: number;
  readonly excerptsCount: number;
  readonly chunks: readonly Citation[];
}

@Component({
  selector: 'app-citation-chips',
  standalone: true,
  imports: [CommonModule, IconComponent],
  template: `
    @if (groupedSources().length > 0) {
      <div class="citations-container">
        <div class="citations-header">
          <app-icon name="sparkles" [size]="14"></app-icon>
          <span>Sources ({{ groupedSources().length }})</span>
        </div>

        <div class="chips-row">
          @for (source of groupedSources(); track source.documentId) {
            <button
              type="button"
              class="citation-chip"
              [class.active]="selectedSource()?.documentId === source.documentId"
              (click)="toggleSource(source)"
              title="Click to preview source excerpts"
            >
              <app-icon name="file-text" [size]="13"></app-icon>
              <span class="filename">{{ source.filename }}</span>
              @if (source.pagesLabel) {
                <span class="page-badge">{{ source.pagesLabel }}</span>
              }
              <span class="score-badge">{{ formatScore(source.bestScore) }}</span>
            </button>
          }
        </div>

        <!-- Inline Expandable Grounding Card -->
        @if (selectedSource(); as active) {
          <div class="citation-detail-card">
            <div class="detail-header">
              <div class="detail-title">
                <app-icon name="file-text" [size]="15"></app-icon>
                <strong>{{ active.filename }}</strong>
                @if (active.pagesLabel) {
                  <span class="detail-page">{{ active.pagesLabel }}</span>
                }
              </div>
              <div class="detail-actions">
                <span class="score-pill">Top Match: {{ formatScore(active.bestScore) }}</span>
                <button type="button" class="close-btn" (click)="clearSelection()" title="Close details">
                  &times;
                </button>
              </div>
            </div>

            <div class="detail-body">
              <p class="chunk-meta">
                <span>Document ID: <code>{{ active.documentId.slice(0, 8) }}...</code></span>
                <span>{{ active.excerptsCount }} referenced excerpt{{ active.excerptsCount > 1 ? 's' : '' }}</span>
              </p>

              <div class="excerpts-list">
                @for (chunk of active.chunks; track chunk.chunkId) {
                  <div class="excerpt-item">
                    <div class="excerpt-header">
                      <span class="chunk-tag">Chunk #{{ chunk.chunkId }}</span>
                      @if (chunk.pageNumber) {
                        <span class="page-tag">Page {{ chunk.pageNumber }}</span>
                      }
                      <span class="match-tag">{{ formatScore(chunk.similarityScore) }}</span>
                    </div>
                    @if (chunk.contentSnippet) {
                      <div class="snippet-box">
                        <p>{{ chunk.contentSnippet }}</p>
                      </div>
                    }
                  </div>
                }
              </div>

              @if (!hasAnySnippet(active.chunks)) {
                <p class="snippet-fallback">
                  This response was verified and grounded against this indexed enterprise document.
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
        cursor: pointer;

        app-icon {
          color: var(--primary-light);
        }

        .filename {
          max-width: 160px;
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
        cursor: pointer;
        background: transparent;
        border: none;
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

      .excerpts-list {
        display: flex;
        flex-direction: column;
        gap: 0.45rem;
        margin-top: 0.4rem;
        max-height: 220px;
        overflow-y: auto;
      }

      .excerpt-item {
        background: rgba(0, 0, 0, 0.15);
        border: 1px solid var(--border-subtle);
        border-radius: var(--radius-sm);
        padding: 0.45rem 0.6rem;
      }

      .excerpt-header {
        display: flex;
        align-items: center;
        gap: 0.45rem;
        font-size: 0.72rem;
        margin-bottom: 0.25rem;

        .chunk-tag {
          font-family: monospace;
          color: var(--text-muted);
        }

        .page-tag {
          background: rgba(255, 255, 255, 0.06);
          padding: 0.05rem 0.3rem;
          border-radius: var(--radius-sm);
          color: var(--text-secondary);
        }

        .match-tag {
          font-weight: 600;
          color: var(--success);
          margin-left: auto;
        }
      }

      .snippet-box {
        background: rgba(0, 0, 0, 0.2);
        border-left: 2px solid var(--primary);
        padding: 0.4rem 0.6rem;
        border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
        font-size: 0.8rem;
        line-height: 1.45;
        color: var(--text-primary);
      }

      .snippet-fallback {
        font-style: italic;
        color: var(--text-muted);
        font-size: 0.78rem;
        margin-top: 0.4rem;
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
  public readonly selectedSource = signal<GroupedSource | null>(null);

  public readonly groupedSources = computed<GroupedSource[]>(() => {
    const raw = this.citations();
    if (!raw || raw.length === 0) return [];

    const map = new Map<string, {
      documentId: string;
      filename: string;
      pages: Set<number>;
      bestScore: number;
      chunks: Citation[];
    }>();

    for (const c of raw) {
      const key = c.documentId || c.filename;
      let entry = map.get(key);
      if (!entry) {
        entry = {
          documentId: c.documentId || key,
          filename: c.filename,
          pages: new Set<number>(),
          bestScore: c.similarityScore ?? 0,
          chunks: []
        };
        map.set(key, entry);
      }

      if (c.pageNumber != null) {
        entry.pages.add(c.pageNumber);
      }
      if (c.similarityScore != null && c.similarityScore > entry.bestScore) {
        entry.bestScore = c.similarityScore;
      }
      if (!entry.chunks.some((existing) => existing.chunkId === c.chunkId)) {
        entry.chunks.push(c);
      }
    }

    return Array.from(map.values()).map((entry) => {
      const sortedPages = Array.from(entry.pages).sort((a, b) => a - b);
      let pagesLabel = '';
      if (sortedPages.length === 1) {
        pagesLabel = `p.${sortedPages[0]}`;
      } else if (sortedPages.length > 1) {
        pagesLabel = `p.${sortedPages.join(', ')}`;
      }

      return {
        documentId: entry.documentId,
        filename: entry.filename,
        pagesLabel,
        bestScore: entry.bestScore,
        excerptsCount: entry.chunks.length,
        chunks: entry.chunks
      };
    });
  });

  public toggleSource(source: GroupedSource): void {
    if (this.selectedSource()?.documentId === source.documentId) {
      this.selectedSource.set(null);
    } else {
      this.selectedSource.set(source);
    }
  }

  public clearSelection(): void {
    this.selectedSource.set(null);
  }

  public hasAnySnippet(chunks: readonly Citation[]): boolean {
    return chunks.some((c) => !!c.contentSnippet);
  }

  public formatScore(score: number): string {
    if (!score) return '';
    if (score <= 1) {
      return `${Math.round(score * 100)}%`;
    }
    return score.toFixed(2);
  }
}
