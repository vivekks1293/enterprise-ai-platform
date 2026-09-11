import { Injectable, signal } from '@angular/core';
import { KnowledgeDocument } from '@data/models/document.dto';

@Injectable()
export class KnowledgeStateService {
  public readonly documents = signal<readonly KnowledgeDocument[]>([]);
  public readonly isLoading = signal<boolean>(false);
  public readonly isUploading = signal<boolean>(false);
  public readonly uploadProgress = signal<number>(0);
  public readonly indexingIds = signal<ReadonlySet<string>>(new Set());
  public readonly deletingIds = signal<ReadonlySet<string>>(new Set());
  public readonly searchTerm = signal<string>('');

  public setDocuments(docs: readonly KnowledgeDocument[]): void {
    this.documents.set(docs);
  }

  public addDocument(doc: KnowledgeDocument): void {
    this.documents.update((list) => [doc, ...list.filter((d) => d.id !== doc.id)]);
  }

  public removeDocument(id: string): void {
    this.documents.update((list) => list.filter((d) => d.id !== id));
  }

  public updateDocumentStatus(id: string, status: KnowledgeDocument['status']): void {
    this.documents.update((list) =>
      list.map((d) => (d.id === id ? { ...d, status, updatedAt: new Date().toISOString() } : d))
    );
  }

  public setIndexing(id: string, indexing: boolean): void {
    this.indexingIds.update((set) => {
      const copy = new Set(set);
      if (indexing) copy.add(id);
      else copy.delete(id);
      return copy;
    });
  }

  public setDeleting(id: string, deleting: boolean): void {
    this.deletingIds.update((set) => {
      const copy = new Set(set);
      if (deleting) copy.add(id);
      else copy.delete(id);
      return copy;
    });
  }
}

