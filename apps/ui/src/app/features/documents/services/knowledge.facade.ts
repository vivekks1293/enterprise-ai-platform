import { Injectable, inject, computed } from '@angular/core';
import { KnowledgeStateService } from '../state/knowledge-state.service';
import { KnowledgeRepository } from '@data/repositories/knowledge.repository';
import { NotificationService } from '@core/services/notification.service';
import { KnowledgeDocument } from '@data/models/document.dto';

@Injectable()
export class KnowledgeFacade {
  private readonly state = inject(KnowledgeStateService);
  private readonly repository = inject(KnowledgeRepository);
  private readonly toast = inject(NotificationService);

  public readonly documents = this.state.documents;
  public readonly isLoading = this.state.isLoading;
  public readonly isUploading = this.state.isUploading;
  public readonly indexingIds = this.state.indexingIds;
  public readonly deletingIds = this.state.deletingIds;
  public readonly searchTerm = this.state.searchTerm;

  public readonly filteredDocuments = computed(() => {
    const term = this.state.searchTerm().trim().toLowerCase();
    const list = this.state.documents();
    if (!term) return list;
    return list.filter((d) => d.filename.toLowerCase().includes(term));
  });

  public readonly stats = computed(() => {
    const docs = this.state.documents();
    const total = docs.length;
    const indexed = docs.filter((d) => d.status === 'indexed').length;
    const totalBytes = docs.reduce((acc, d) => acc + d.sizeBytes, 0);
    return { total, indexed, totalBytes };
  });

  public loadDocuments(): void {
    this.state.isLoading.set(true);
    this.repository.listDocuments().subscribe({
      next: (docs) => {
        this.state.setDocuments(docs);
        this.state.isLoading.set(false);
      },
      error: () => {
        this.state.isLoading.set(false);
        this.toast.error('Failed to load documents list');
      }
    });
  }

  public uploadFile(file: File): void {
    // 25MB max size check
    const maxBytes = 25 * 1024 * 1024;
    if (file.size > maxBytes) {
      this.toast.error(`File is too large (${(file.size / 1024 / 1024).toFixed(1)}MB). Max limit is 25MB.`);
      return;
    }

    this.state.isUploading.set(true);
    this.repository.uploadDocument(file).subscribe({
      next: (doc) => {
        this.state.addDocument(doc);
        this.state.isUploading.set(false);
        this.toast.success(`"${file.name}" uploaded and indexed into vector store!`);
      },
      error: () => {
        this.state.isUploading.set(false);
        this.toast.error(`Failed to upload "${file.name}"`);
      }
    });
  }

  public indexDocument(id: string): void {
    this.state.setIndexing(id, true);
    this.state.updateDocumentStatus(id, 'indexing');
    this.repository.indexDocument(id).subscribe({
      next: (res) => {
        this.state.setIndexing(id, false);
        this.state.updateDocumentStatus(id, 'indexed');
        this.toast.success(`Document indexed into vector store (${res.chunk_count ?? 0} chunks created)`);
      },
      error: () => {
        this.state.setIndexing(id, false);
        this.state.updateDocumentStatus(id, 'failed');
        this.toast.error('Failed to index document');
      }
    });
  }

  public deleteDocument(id: string, filename: string): void {
    this.state.setDeleting(id, true);
    this.repository.deleteDocument(id).subscribe({
      next: () => {
        this.state.removeDocument(id);
        this.state.setDeleting(id, false);
        this.toast.success(`"${filename}" removed`);
      },
      error: () => {
        this.state.setDeleting(id, false);
        this.toast.error(`Failed to delete "${filename}"`);
      }
    });
  }

  public downloadDocument(doc: KnowledgeDocument): void {
    this.repository.downloadDocument(doc.id).subscribe({
      next: (res) => {
        const blob = res.body;
        if (!blob) return;
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = doc.filename;
        a.click();
        window.URL.revokeObjectURL(url);
      },
      error: () => {
        this.toast.error(`Could not download "${doc.filename}"`);
      }
    });
  }

  public setSearchTerm(term: string): void {
    this.state.searchTerm.set(term);
  }
}

