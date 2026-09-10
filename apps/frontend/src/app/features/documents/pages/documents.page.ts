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
import { NotificationService } from '@core/services/notification.service';

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
  private static readonly MAX_DOCUMENT_SIZE_BYTES = 5 * 1024 * 1024;

  protected readonly facade = inject(KnowledgeFacade);
  private readonly notificationService = inject(NotificationService);

  @ViewChild('fileInput') private readonly fileInput?: ElementRef<HTMLInputElement>;

  /** Local UI-only state (which document's delete confirmation is
   *  open) — not Facade state, same reasoning as LoginPage's
   *  `passwordVisible` signal staying component-local. */
  protected readonly pendingDelete = signal<KnowledgeDocument | null>(null);
  protected readonly uploadDialogOpen = signal(false);
  protected readonly selectedFile = signal<File | null>(null);
  protected readonly uploadValidationMessage = signal<string | null>(null);

  public ngOnInit(): void {
    this.facade.loadDocuments();
  }

  protected triggerFilePicker(): void {
    this.fileInput?.nativeElement.click();
  }

  protected openUploadDialog(): void {
    this.selectedFile.set(null);
    this.uploadValidationMessage.set(null);
    this.uploadDialogOpen.set(true);
  }

  protected closeUploadDialog(): void {
    this.uploadDialogOpen.set(false);
    this.selectedFile.set(null);
    this.uploadValidationMessage.set(null);
  }

  protected onFileSelected(event: Event): void {
    const input = event.target as HTMLInputElement;
    const file = input.files?.[0];
    this.uploadValidationMessage.set(null);
    if (file && !this.isPdf(file)) {
      this.showUploadValidationError('Unsupported file type. Please select a PDF document.');
    } else if (file && file.size > DocumentsPageComponent.MAX_DOCUMENT_SIZE_BYTES) {
      this.showUploadValidationError('File is too large. Maximum file size is 5 MB.');
    } else if (file) {
      this.selectedFile.set(file);
    }
    // Reset so selecting the exact same file again still fires 'change'.
    input.value = '';
  }

  protected uploadSelectedFile(): void {
    const file = this.selectedFile();
    if (file) {
      this.facade.uploadDocument(file);
      this.closeUploadDialog();
    }
  }

  private isPdf(file: File): boolean {
    return file.type === 'application/pdf' || file.name.toLowerCase().endsWith('.pdf');
  }

  private showUploadValidationError(message: string): void {
    this.uploadValidationMessage.set(message);
    this.notificationService.notify(message, 'error');
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
