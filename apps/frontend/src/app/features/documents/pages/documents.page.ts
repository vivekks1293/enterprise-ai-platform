import { ChangeDetectionStrategy, Component, ElementRef, OnInit, ViewChild, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { KnowledgeFacade } from '@features/documents/services/knowledge.facade';
import { KnowledgeStateService } from '@features/documents/state/knowledge-state.service';
import { KnowledgeDocument } from '@features/documents/models/knowledge-document.model';
import { CardComponent } from '@shared/ui/card/card.component';
import { ButtonComponent } from '@shared/ui/button/button.component';
import { BadgeComponent } from '@shared/ui/badge/badge.component';
import { ModalComponent } from '@shared/ui/modal/modal.component';
import { EmptyStateComponent } from '@shared/ui/empty-state/empty-state.component';
import { LoadingStateComponent } from '@shared/ui/loading-state/loading-state.component';
import { ErrorStateComponent } from '@shared/ui/error-state/error-state.component';
import { RelativeTimePipe } from '@shared/pipes/relative-time.pipe';
import { FileSizePipe } from '@shared/pipes/file-size.pipe';
import { MimeTypeLabelPipe } from '@shared/pipes/mime-type-label.pipe';
import { UiVariant } from '@shared/types/ui.types';

/**
 * The only component in the Documents feature that injects
 * KnowledgeFacade — same container/presentational reasoning as
 * Auth/Chat, just a single-page feature so there's no deeper tree to
 * drill through this time.
 */
@Component({
  selector: 'eap-documents-page',
  standalone: true,
  imports: [
    CommonModule,
    CardComponent,
    ButtonComponent,
    BadgeComponent,
    ModalComponent,
    EmptyStateComponent,
    LoadingStateComponent,
    ErrorStateComponent,
    RelativeTimePipe,
    FileSizePipe,
    MimeTypeLabelPipe
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
  providers: [KnowledgeStateService, KnowledgeFacade],
  templateUrl: './documents.page.html',
  styleUrl: './documents.page.scss'
})
export class DocumentsPageComponent implements OnInit {
  protected readonly facade = inject(KnowledgeFacade);

  @ViewChild('fileInput') private readonly fileInput?: ElementRef<HTMLInputElement>;

  /** Local UI-only state (which document's delete confirmation is
   *  open) — not Facade state, same reasoning as LoginPage's
   *  `passwordVisible` signal staying component-local. */
  protected readonly pendingDelete = signal<KnowledgeDocument | null>(null);

  public ngOnInit(): void {
    this.facade.loadDocuments();
  }

  protected triggerFilePicker(): void {
    this.fileInput?.nativeElement.click();
  }

  protected onFileSelected(event: Event): void {
    const input = event.target as HTMLInputElement;
    const file = input.files?.[0];
    if (file) {
      this.facade.uploadDocument(file);
    }
    // Reset so selecting the exact same file again still fires 'change'.
    input.value = '';
  }

  protected onDownload(document: KnowledgeDocument): void {
    this.facade.downloadDocument(document);
  }

  protected onIndex(document: KnowledgeDocument): void {
    this.facade.indexDocument(document.id);
  }

  protected confirmDelete(document: KnowledgeDocument): void {
    this.pendingDelete.set(document);
  }

  protected cancelDelete(): void {
    this.pendingDelete.set(null);
  }

  protected onDeleteConfirmed(): void {
    const document = this.pendingDelete();
    if (document) {
      this.facade.deleteDocument(document.id);
      this.pendingDelete.set(null);
    }
  }

  /** available: uploaded, not yet searchable (neutral).
   *  indexing: in progress (info/blue).
   *  indexed: ready for AI search (success/green).
   *  failed: indexing failed (danger/red) — the file itself is still
   *  downloadable, only the AI-search step failed. */
  protected statusVariant(status: KnowledgeDocument['status']): UiVariant {
    switch (status) {
      case 'available':
        return 'secondary';
      case 'indexing':
        return 'info';
      case 'indexed':
        return 'success';
      case 'failed':
        return 'danger';
    }
  }
}
