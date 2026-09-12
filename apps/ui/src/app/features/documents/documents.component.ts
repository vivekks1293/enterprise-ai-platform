import { Component, ChangeDetectionStrategy, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { KnowledgeFacade } from './services/knowledge.facade';
import { KnowledgeStateService } from './state/knowledge-state.service';
import { UploadDropzoneComponent } from './components/upload-dropzone.component';
import { DocumentCardComponent } from './components/document-card.component';
import { IconComponent } from '@shared/components/icon.component';

@Component({
  selector: 'app-documents',
  standalone: true,
  imports: [CommonModule, FormsModule, UploadDropzoneComponent, DocumentCardComponent, IconComponent],
  providers: [KnowledgeFacade, KnowledgeStateService],
  template: `
    <div class="documents-viewport">
      <!-- Top Header -->
      <header class="doc-header">
        <div class="header-left">
          <h2>Knowledge Base</h2>
          <span class="header-badge">
            <app-icon name="database" [size]="13"></app-icon>
            RAG Grounding Engine
          </span>
        </div>

        <div class="header-right">
          <!-- Quick Search -->
          <div class="search-box">
            <app-icon name="search" [size]="14"></app-icon>
            <input
              type="text"
              placeholder="Filter documents..."
              [ngModel]="facade.searchTerm()"
              (ngModelChange)="facade.setSearchTerm($event)"
            />
          </div>
        </div>
      </header>

      <!-- Main Content Area -->
      <div class="doc-scroll-content">
        <div class="content-container">
          <!-- Summary Cards -->
          <div class="stats-grid">
            <div class="stat-card">
              <div class="stat-meta">
                <span class="stat-label">Total Documents</span>
                <h3 class="stat-value">{{ facade.stats().total }}</h3>
              </div>
              <div class="stat-icon-wrapper">
                <app-icon name="file-text" [size]="20"></app-icon>
              </div>
            </div>

            <div class="stat-card stat-indexed-card">
              <div class="stat-meta">
                <span class="stat-label">Indexed in Vector Store</span>
                <h3 class="stat-value">{{ facade.stats().indexed }}</h3>
              </div>
              <div class="stat-icon-wrapper">
                <app-icon name="sparkles" [size]="20"></app-icon>
              </div>
            </div>
          </div>

          <!-- Upload Dropzone Section -->
          <section class="upload-section">
            <app-upload-dropzone
              [isUploading]="facade.isUploading()"
              (fileDropped)="onFileDropped($event)"
            ></app-upload-dropzone>
          </section>

          <!-- Document List Section -->
          <section class="list-section">
            <div class="section-title-row">
              <h3>Uploaded Documents ({{ facade.filteredDocuments().length }})</h3>
              <span class="hint-text">Indexed documents are automatically grounded into AI chat answers</span>
            </div>

            @if (facade.isLoading()) {
              <div class="loading-state">
                <div class="spinner"></div>
                <p>Loading documents repository...</p>
              </div>
            } @else if (facade.filteredDocuments().length === 0) {
              <div class="empty-docs-box">
                <app-icon name="file-text" [size]="36"></app-icon>
                <p class="empty-title">No documents found</p>
                <p class="empty-desc">
                  Upload a PDF, DOCX, or text file above to build your private knowledge repository.
                </p>
              </div>
            } @else {
              <div class="documents-list">
                @for (doc of facade.filteredDocuments(); track doc.id) {
                  <app-document-card
                    [document]="doc"
                    [isIndexing]="facade.indexingIds().has(doc.id)"
                    [isDeleting]="facade.deletingIds().has(doc.id)"
                    (index)="facade.indexDocument($event)"
                    (download)="facade.downloadDocument($event)"
                    (delete)="facade.deleteDocument($event.id, $event.filename)"
                  ></app-document-card>
                }
              </div>
            }
          </section>
        </div>
      </div>
    </div>
  `,
  styles: [
    `
      :host {
        display: block;
        height: 100%;
        overflow: hidden;
      }

      .documents-viewport {
        display: flex;
        flex-direction: column;
        height: 100%;
        background: var(--bg-app);
      }

      .doc-header {
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

        h2 {
          font-size: 1.05rem;
          font-weight: 600;
          color: var(--text-primary);
        }
      }

      .header-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.35rem;
        font-size: 0.72rem;
        background: var(--bg-chip);
        border: 1px solid var(--border-subtle);
        color: var(--primary-light);
        padding: 0.15rem 0.5rem;
        border-radius: var(--radius-full);
      }

      .search-box {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        background: var(--bg-card);
        border: 1px solid var(--border-default);
        padding: 0.35rem 0.75rem;
        border-radius: var(--radius-md);
        width: 220px;

        app-icon {
          color: var(--text-muted);
        }

        input {
          width: 100%;
          font-size: 0.85rem;
          color: var(--text-primary);
          &::placeholder {
            color: var(--text-muted);
          }
        }
      }

      .doc-scroll-content {
        flex: 1;
        overflow-y: auto;
        padding: 2rem 1.5rem;
      }

      .content-container {
        max-width: 900px;
        margin: 0 auto;
      }

      .stats-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 1rem;
        margin-bottom: 1.5rem;
      }

      .stat-card {
        display: flex;
        align-items: center;
        justify-content: space-between;
        background: var(--bg-card);
        border: 1px solid var(--border-subtle);
        border-radius: var(--radius-lg);
        padding: 1.25rem 1.5rem;
        box-shadow: var(--shadow-sm);
      }

      .stat-label {
        font-size: 0.8rem;
        font-weight: 500;
        color: var(--text-muted);
        text-transform: uppercase;
        letter-spacing: 0.04em;
      }

      .stat-value {
        font-size: 1.75rem;
        font-weight: 700;
        color: var(--text-primary);
        margin-top: 0.2rem;
      }

      .stat-icon-wrapper {
        width: 44px;
        height: 44px;
        border-radius: var(--radius-md);
        background: var(--bg-chip);
        color: var(--primary-light);
        display: flex;
        align-items: center;
        justify-content: center;
      }

      .stat-indexed-card .stat-icon-wrapper {
        background: var(--success-bg);
        color: var(--success);
      }

      .upload-section {
        margin-bottom: 2rem;
      }

      .section-title-row {
        display: flex;
        align-items: baseline;
        justify-content: space-between;
        margin-bottom: 1rem;

        h3 {
          font-size: 1.05rem;
          font-weight: 600;
          color: var(--text-primary);
        }

        .hint-text {
          font-size: 0.78rem;
          color: var(--text-muted);
        }
      }

      .documents-list {
        display: flex;
        flex-direction: column;
      }

      .empty-docs-box {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 3.5rem 1rem;
        background: var(--bg-card);
        border: 1px dashed var(--border-default);
        border-radius: var(--radius-lg);
        text-align: center;
        color: var(--text-muted);

        app-icon {
          color: var(--text-muted);
          opacity: 0.5;
          margin-bottom: 0.75rem;
        }

        .empty-title {
          font-size: 1rem;
          font-weight: 600;
          color: var(--text-primary);
          margin-bottom: 0.25rem;
        }

        .empty-desc {
          font-size: 0.85rem;
          max-width: 380px;
        }
      }

      .loading-state {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 3rem 0;
        color: var(--text-muted);
        gap: 0.75rem;
      }

      .spinner {
        width: 24px;
        height: 24px;
        border: 2px solid var(--border-default);
        border-top-color: var(--primary);
        border-radius: 50%;
        animation: spin 0.8s linear infinite;
      }

      @keyframes spin {
        to { transform: rotate(360deg); }
      }

      @media (max-width: 640px) {
        .stats-grid {
          grid-template-columns: 1fr;
        }
        .section-title-row {
          flex-direction: column;
          gap: 0.25rem;
        }
      }
    `
  ],
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class DocumentsComponent implements OnInit {
  public readonly facade = inject(KnowledgeFacade);

  public ngOnInit(): void {
    this.facade.loadDocuments();
  }

  public onFileDropped(file: File): void {
    this.facade.uploadFile(file);
  }
}

